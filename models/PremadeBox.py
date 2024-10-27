from sqlalchemy import Column, Integer, CHAR, ForeignKey, CheckConstraint
from .Item import Item

class PremadeBox(Item):
    __tablename__ = 'premadeboxes'

    id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    boxSize = Column(CHAR(1))
    numbOfBoxes = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'PremadeBox'  # Unique identifier for polymorphism
    }

    # Applying the check constraint on the boxSize column
    __table_args__ = (
        CheckConstraint("boxSize IN ('S', 'M', 'L')", name="check_box_size"),
    )

    def __init__(self, boxSize, numbOfBoxes):
        super().__init__()
        self.boxSize = boxSize
        self.numbOfBoxes = numbOfBoxes