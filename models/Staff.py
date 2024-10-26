from sqlalchemy import Column, Integer, String, Date, ForeignKey
from .Person import Person

class Staff(Person):
    __tablename__ = 'staffs'

    id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
    dateJoined = Column(Date)
    deptName = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'staff'  # Unique identifier for polymorphism
    }

    def __init__(self, firstName, lastName, username, password, dateJoined, deptName):
        super().__init__(firstName=firstName, lastName=lastName, username=username, password=password)
        self.dateJoined = dateJoined
        self.deptName = deptName