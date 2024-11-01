from sqlalchemy import Column, Integer, CHAR, ForeignKey, CheckConstraint, Table
from sqlalchemy.orm import relationship

from . import Base
from .Item import Item

# Association table for PremadeBox and Veggie
box_veggies = Table('box_veggies', Base.metadata,
    Column('box_id', Integer, ForeignKey('premadeboxes.id')),
    Column('veggie_id', Integer, ForeignKey('veggies.id'))
)

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

    # Relationship with veggies
    veggies = relationship("Veggie", secondary=box_veggies, backref="boxes")

    def __init__(self, boxSize, numbOfBoxes):
        super().__init__()
        self.boxSize = boxSize
        self.numbOfBoxes = numbOfBoxes

    @staticmethod
    def getBoxPrice(size):
        """Get price for premade box by size"""
        boxPrices = {
            'S': 5.0,  # Small box base price
            'M': 8.0,  # Medium box base price
            'L': 10.0  # Large box base price
        }
        return f"${boxPrices.get(size, 0.0)}"

    @staticmethod
    def getMaxVeggies(size):
        """Get maximum number of veggies allowed for box size"""
        maxVeggies = {
            'S': 3,  # Small box: 3 veggies
            'M': 5,  # Medium box: 5 veggies
            'L': 8  # Large box: 8 veggies
        }
        return maxVeggies.get(size, 0)

    def canAddVeggie(self):
        """Check if more veggies can be added to the box"""
        return len(self.veggies) < self.getMaxVeggies(self.boxSize)

    def addVeggie(self, veggie):
        """Add a veggie to the box if possible"""
        if self.canAddVeggie():
            self.veggies.append(veggie)
            return True
        return False

    def removeVeggie(self, veggie):
        """Remove a veggie from the box"""
        if veggie in self.veggies:
            self.veggies.remove(veggie)
            return True
        return False