from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .Customer import Customer


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    orderCustomer = Column(Integer, ForeignKey('customers.id'))
    orderDate = Column(Date)
    orderNumber = Column(String(20), unique=True)  # Unique order/tracking number for shipment or pick-up
    orderStatus = Column(String(20))

    # Relationship to Customer
    customer = relationship("Customer", back_populates="orders")

    # Relationship to OrderLine; 'order' refers back to this Order
    orderLines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")

    def __init__(self, orderCustomer, orderDate, orderNumber, orderStatus):
        self.orderCustomer = orderCustomer
        self.orderDate = orderDate
        self.orderNumber = orderNumber
        self.orderStatus = orderStatus