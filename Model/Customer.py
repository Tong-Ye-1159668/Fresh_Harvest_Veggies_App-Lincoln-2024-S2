from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Person import Person

class Customer(Person):
    __tablename__ = 'customers'

    __custId = Column(Integer, ForeignKey('persons.personId'), primary_key=True)
    __custAddress = Column(String(255))
    __custBalance = Column(Integer, default=0)
    __maxOwing = Column(Integer, default=100)

    __mapper_args__ = {
    'polymorphic_identity': 'Customer'
    }

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0, maxOwing=100):
        super().__init__(firstName, lastName, username, password)
        self.__custAddress = custAddress
        self.__custBalance = custBalance
        self.__maxOwing = maxOwing

    def getPersonRole(self):
        return 'Customer'

    # Getter and setter for custAddress
    @property
    def custAddress(self):
        return self.__custAddress

    @custAddress.setter
    def custAddress(self, value):
        if value:
            self.__custAddress = value
        else:
            raise ValueError("Address cannot be empty.")

    # Getter and setter for custBalance
    @property
    def custBalance(self):
        return self.__custBalance

    @custBalance.setter
    def custBalance(self, value):
        if value + self.__maxOwing > 0:
            self.__custBalance = value
        else:
            raise ValueError("The outstanding balance cannot exceed max owing.")

    # Getter and setter for maxOwing
    @property
    def maxOwing(self):
        return self.__maxOwing

    @maxOwing.setter
    def maxOwing(self, value):
        if value >= 0:
            self.__maxOwing = value
        else:
            raise ValueError("Max owing cannot be negative.")