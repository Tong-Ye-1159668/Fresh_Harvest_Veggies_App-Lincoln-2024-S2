from app import db
from .Veggie import Veggie


class WeightedVeggie(Veggie):
    __tablename__ = 'weighted_veggies'

    id = db.Column(db.Integer, db.ForeignKey('veggies.id'), primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    pricePerKilo = db.Column(db.Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'WeightedVeggie'  # Unique identifier for polymorphism
    }

    def __init__(self, vegName, weight, pricePerKilo):
        super().__init__(vegName=vegName)
        self.weight = weight
        self.pricePerKilo = pricePerKilo