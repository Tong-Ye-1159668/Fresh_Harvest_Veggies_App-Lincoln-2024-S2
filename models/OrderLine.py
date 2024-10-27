from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from . import PremadeBox, WeightedVeggie, PackVeggie, UnitPriceVeggie
from .base import Base

class OrderLine(Base):
    __tablename__ = 'orderlines'

    id = Column(Integer, primary_key=True)
    itemNumber = Column(Integer)
    order_id = Column(Integer, ForeignKey('orders.id'))
    item_id = Column(Integer, ForeignKey('items.id'))

    # Relationships
    order = relationship("Order", back_populates="orderlines")
    item = relationship("Item")

    def __init__(self, itemNumber):
        self.itemNumber = itemNumber

    def calcLineTotal(self):
        """Calculate total for this line item based on item type"""
        if isinstance(self.item, PremadeBox):
            return self.calcPremadeboxTotal()
        elif isinstance(self.item, WeightedVeggie):
            return self.itemNumber * self.item.weight * self.item.pricePerKilo
        elif isinstance(self.item, PackVeggie):
            return self.itemNumber * self.item.pricePerPack
        elif isinstance(self.item, UnitPriceVeggie):
            return self.itemNumber * self.item.pricePerUnit
        return 0.0

    def calcPremadeboxTotal(self):
        """Calculate total for premade box"""
        boxPrices = {
            'S': 5.0,  # Small box base price
            'M': 8.0,  # Medium box base price
            'L': 10.0  # Large box base price
        }
        return self.itemNumber * boxPrices.get(self.item.boxSize, 0.0)