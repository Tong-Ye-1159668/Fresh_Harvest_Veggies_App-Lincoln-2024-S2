from sqlalchemy import Column, Integer, Float, ForeignKey
from .Veggie import Veggie

class PackVeggie(Veggie):
    __tablename__ = 'pack_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key = True)
    numberOfPacks = Column(Integer)
    pricePerPack = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity': 'PackVeggie'  # Unique identifier for SQLAlchemy polymorphism
    }

    def __init__(self, vegName, numberOfPacks, pricePerPack):
        super().__init__(vegName=vegName)
        self.numberOfPacks = numberOfPacks
        self.pricePerPack = pricePerPack