from sqlalchemy import Column, Integer, String, ForeignKey
from .Person import Person

class Customer(Person):
    __tablename__ = 'customers'

    id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
    custAddress = Column(String(255))
    custBalance = Column(Integer, default=0)
    maxOwing = Column(Integer, default=100)

    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0, maxOwing=100):
        super().__init__(firstName=firstName, lastName=lastName, username=username, password=password)
        self.type = 'customer'
        self.custAddress = custAddress
        self.custBalance = custBalance
        self.maxOwing = maxOwing

    def __repr__(self):
        return f"Customer({self.firstName} {self.lastName}, Address: {self.custAddress}, Balance: {self.custBalance})"