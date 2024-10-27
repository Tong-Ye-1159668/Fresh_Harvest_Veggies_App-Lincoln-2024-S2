from app import db
from .Veggie import Veggie


class UnitPriceVeggie(Veggie):
    __tablename__ = 'unit_price_veggies'

    id = db.Column(db.Integer, db.ForeignKey('veggies.id'), primary_key=True)
    pricePerUnit = db.Column(db.Float)
    quantity = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'UnitPriceVeggie'  # Unique identifier for SQLAlchemy polymorphism
    }

    def __init__(self, vegName, pricePerUnit, quantity):
        super().__init__(vegName=vegName)
        self.pricePerUnit = pricePerUnit
        self.quantity = quantity
