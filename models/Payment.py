from sqlalchemy import Column, Integer, String, Float, Date
from .base import Base

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    paymentAmount = Column(Float)
    paymentDate = Column(Date)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'Payment',  # The base identity for this class
        'polymorphic_on': type              # SQLAlchemy uses 'type' to distinguish subclasses
    }

    def __init__(self, paymentAmount, paymentDate):
        self.paymentAmount = paymentAmount
        self.paymentDate = paymentDate