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

    def __str__(self):
        veggie_str = super().__str__()
        return f"{veggie_str} | Storage: {self.quantity} units, Price: ${self.pricePerUnit:.2f}/unit"