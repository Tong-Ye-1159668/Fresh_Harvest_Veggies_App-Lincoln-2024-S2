from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from .Person import Person

class Customer(Person):
    __tablename__ = 'customers'

    id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
    custAddress = Column(String(255))
    custBalance = Column(Float, default=0)
    maxOwing = Column(Integer, default=100)

    __mapper_args__ = {
        'polymorphic_identity': 'customer'  # Unique identifier for polymorphism
    }

    # Relationships
    orders = relationship("Order", back_populates="customer")

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0, maxOwing=100):
        super().__init__(firstName=firstName, lastName=lastName, username=username, password=password)
        self.custAddress = custAddress
        self.custBalance = custBalance
        self.maxOwing = maxOwing

    def __str__(self):
        person_str = super().__str__()
        balance_str = f"${self.custBalance:.2f}" if self.custBalance >= 0 else f"-${abs(self.custBalance):.2f}"
        return f"{person_str} | Balance: {balance_str} | Address: {self.custAddress}"