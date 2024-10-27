from app import db
from .Person import Person


class Customer(Person):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, db.ForeignKey('persons.id'), primary_key=True)
    custAddress = db.Column(db.String(255))
    custBalance = db.Column(db.Integer, default=0)
    maxOwing = db.Column(db.Integer, default=100)

    __mapper_args__ = {
        'polymorphic_identity': 'customer'  # Unique identifier for polymorphism
    }

    # Relationship to Order
    orders = db.relationship("Order", back_populates="customer")

    # Relationship to Payment
    payments = db.relationship("Payment", back_populates="customer")

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0, maxOwing=100):
        super().__init__(firstName=firstName, lastName=lastName, username=username, password=password)
        self.custAddress = custAddress
        self.custBalance = custBalance
        self.maxOwing = maxOwing
