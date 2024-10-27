from app import db  # Import the `db` instance from your Flask app
from .Item import Item


class PremadeBox(Item):
    __tablename__ = 'premadeboxes'

    id = db.Column(db.Integer, db.ForeignKey('items.id'), primary_key=True)
    boxSize = db.Column(db.CHAR(1))
    numbOfBoxes = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'PremadeBox'  # Unique identifier for polymorphism
    }

    # Applying the check constraint on the boxSize column
    __table_args__ = (
        db.CheckConstraint("boxSize IN ('S', 'M', 'L')", name="check_box_size"),
    )

    def __init__(self, boxSize, numbOfBoxes):
        super().__init__()
        self.boxSize = boxSize
        self.numbOfBoxes = numbOfBoxes