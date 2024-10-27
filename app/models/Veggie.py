from app import db
from .Item import Item


class Veggie(Item):
    __tablename__ = 'veggies'

    id = db.Column(db.Integer, db.ForeignKey('items.id'), primary_key=True)
    vegName = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'Veggie'  # Unique identifier for polymorphism
    }

    def __init__(self, vegName):
        super().__init__()
        self.vegName = vegName