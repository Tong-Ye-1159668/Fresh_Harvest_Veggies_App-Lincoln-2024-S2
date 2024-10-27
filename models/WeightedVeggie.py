from sqlalchemy import Column, Integer, Float, ForeignKey
from .Veggie import Veggie

class WeightedVeggie(Veggie):
    __tablename__ = 'weighted_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key=True)
    weight = Column(Float, nullable=False)
    pricePerKilo = Column(Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'WeightedVeggie'  # Unique identifier for polymorphism
    }

    def __init__(self, vegName, weight, pricePerKilo):
        super().__init__(vegName=vegName)
        self.weight = weight
        self.pricePerKilo = pricePerKilo