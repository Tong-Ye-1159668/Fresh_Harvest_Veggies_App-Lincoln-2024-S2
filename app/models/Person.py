from sqlalchemy import Integer, String

from app import db


class Person(db.Model):
    __tablename__ = 'persons'

    id = db.Column(Integer, primary_key=True)
    firstName = db.Column(String(50))
    lastName = db.Column(String(50))
    username = db.Column(String(50), unique=True)
    password = db.Column(String(50))
    type = db.Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'Person',  # Use 'type' column to distinguish subclasses
        'polymorphic_on': type
    }

    def __init__(self, firstName, lastName, username, password):
        self.firstName = firstName
        self.lastName = lastName
        self.username = username
        self.password = password