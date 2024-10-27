from app import db
from .Veggie import Veggie


class PackVeggie(Veggie):
    __tablename__ = 'pack_veggies'

    id = db.Column(db.Integer, db.ForeignKey('veggies.id'), primary_key=True)
    numberOfPacks = db.Column(db.Integer)
    pricePerPack = db.Column(db.Float)

    __mapper_args__ = {
        'polymorphic_identity': 'PackVeggie'  # Unique identifier for SQLAlchemy polymorphism
    }

    def __init__(self, vegName, numberOfPacks, pricePerPack):
        super().__init__(vegName=vegName)
        self.numberOfPacks = numberOfPacks
        self.pricePerPack = pricePerPack
