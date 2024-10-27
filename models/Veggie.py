from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .Item import Item

class Veggie(Item):
    __tablename__ = 'veggies'

    id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    vegName = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'Veggie'  # Unique identifier for polymorphism
    }

    def __init__(self, vegName):
        super().__init__()
        self.vegName = vegName