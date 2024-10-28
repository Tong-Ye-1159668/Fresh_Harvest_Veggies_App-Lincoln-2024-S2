from sqlalchemy import Column, Integer, Float, ForeignKey

from .Veggie import Veggie

class UnitPriceVeggie(Veggie):
    __tablename__ = 'unit_price_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key = True)
    quantity = Column(Integer)
    pricePerUnit = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity': 'UnitPriceVeggie' # Unique identifier for SQLAlchemy polymorphism
    }

    def __init__(self, vegName, quantity, pricePerUnit):
        super().__init__(vegName=vegName)
        self.quantity = quantity
        self.pricePerUnit = pricePerUnit