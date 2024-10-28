from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from . import CorporateCustomer
from .base import Base

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    paymentAmount = Column(Float)
    paymentDate = Column(Date)
    type = Column(String(50))
    order_id = Column(Integer, ForeignKey('orders.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'Payment',  # The base identity for this class
        'polymorphic_on': type              # SQLAlchemy uses 'type' to distinguish subclasses
    }

    # Relationship
    order = relationship("Order", back_populates="payments")

    def __init__(self, paymentAmount, paymentDate):
        self.paymentAmount = paymentAmount
        self.paymentDate = paymentDate

    def processPayment(self):
        """Process the payment and update customer balance"""
        if self.validatePayment():
            self.order.customer.custBalance -= self.paymentAmount
            return True
        return False

    def validatePayment(self):
        """Validate payment based on customer type and limits"""
        customer = self.order.customer
        if isinstance(customer, CorporateCustomer):
            return customer.custBalance - self.paymentAmount >= customer.minBalance
        else:
            return customer.custBalance + self.order.total <= customer.maxOwing