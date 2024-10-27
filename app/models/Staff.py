from app import db
from .Person import Person

class Staff(Person):
    __tablename__ = 'staffs'

    id = db.Column(db.Integer, db.ForeignKey('persons.id'), primary_key=True)
    dateJoined = db.Column(db.Date)
    deptName = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'staff'  # Unique identifier for polymorphism
    }

    # Relationships to manage Customers, PremadeBoxes, and Veggies
    customers = db.relationship("Customer", backref="staff")
    premadeBoxes = db.relationship("PremadeBox", backref="staff")
    veggies = db.relationship("Veggie", backref="staff")

    def __init__(self, firstName, lastName, username, password, dateJoined, deptName):
        super().__init__(firstName=firstName, lastName=lastName, username=username, password=password)
        self.dateJoined = dateJoined
        self.deptName = deptName