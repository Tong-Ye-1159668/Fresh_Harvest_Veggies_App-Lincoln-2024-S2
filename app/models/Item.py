from app import db


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'Item',  # The base identity for this class
        'polymorphic_on': type  # SQLAlchemy uses 'type' to distinguish subclasses
    }
