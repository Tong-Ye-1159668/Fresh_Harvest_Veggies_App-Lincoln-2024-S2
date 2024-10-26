from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from Item import Item

class Veggie(Item):
    __tablename__ = 'veggies'

    __veggieId = Column(Integer, ForeignKey('items.itemId'), primary_key=True)
    __vegName = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'Veggie'
    }

    def __init__(self, vegName):
        self.__vegName = vegName

    # Getter and setter for vegName
    @property
    def vegName(self):
        return self.__vegName

    @vegName.setter
    def vegName(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Veggie name must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Veggie name cannot be empty")

        # Check if the length is between 1 and 50 characters
        if len(value) > 20:
            raise ValueError("Veggie name must be between 1 and 20 characters")

        self.__vegName = value