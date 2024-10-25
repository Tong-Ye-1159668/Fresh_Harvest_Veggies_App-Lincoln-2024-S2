from abc import ABC, abstractmethod

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Payment(Base, ABC):
    __tablename__ = 'payments'

    __paymentID = Column(Integer, primary_key=True, autoincrement=True)
    __paymentAmount = Column(Float)
    __paymentDate = Column(String(50))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'Payment', # Use 'type' column to distinguish subclasses
        'polymorphic_on': type
    }

    def __init__(self, paymentAmount, paymentDate):
        self.__paymentAmount = paymentAmount
        self.__paymentDate = paymentDate

    # Getter and setter for paymentAmount
    @property
    def paymentAmount(self):
        return self.__paymentAmount

    @paymentAmount.setter
    def paymentAmount(self, value):
        # limit the payment amount to 2 decimals
        self.__paymentAmount = round(value, 2)

    # Getter and setter for paymentDate
    @property
    def paymentDate(self):
        return self.__paymentDate

    @paymentDate.setter
    def paymentDate(self, value):
        return self.__paymentDate