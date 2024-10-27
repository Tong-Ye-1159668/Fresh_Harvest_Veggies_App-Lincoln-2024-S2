from sqlalchemy import Column, Integer, String
from .base import Base


class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    firstName = Column(String(50))
    lastName = Column(String(50))
    username = Column(String(50), unique=True)
    password = Column(String(50))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'Person',  # Use 'type' column to distinguish subclasses
        'polymorphic_on': type
    }

    def __init__(self, firstName, lastName, username, password):
        self.firstName = firstName
        self.lastName = lastName
        self.username = username
        self.password = password

    def __repr__(self):
        return f"Person({self.firstName} {self.lastName})"