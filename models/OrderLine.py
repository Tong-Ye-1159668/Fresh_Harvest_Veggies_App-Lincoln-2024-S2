from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from . import PremadeBox, WeightedVeggie, PackVeggie, UnitPriceVeggie
from .base import Base

class OrderLine(Base):
    __tablename__ = 'orderlines'

    id = Column(Integer, primary_key=True)
    itemNumber = Column(Integer)
    lineTotal = Column(Float, default=0.0)
    order_id = Column(Integer, ForeignKey('orders.id'))
    item_id = Column(Integer, ForeignKey('items.id'))

    # Relationships
    order = relationship("Order", back_populates="orderLines")
    item = relationship("Item")

    def __init__(self, itemNumber, lineTotal):
        self.itemNumber = itemNumber
        self.lineTotal = lineTotal

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

    def validateItemQuantity(self):
        """Validate if the requested quantity is available"""
        if isinstance(self.item, UnitPriceVeggie):
            return self.itemNumber <= self.item.quantity
        elif isinstance(self.item, PackVeggie):
            return self.itemNumber <= self.item.numberOfPacks
        return True

    def getItemDetails(self):
        """Get formatted item details"""
        if isinstance(self.item, PremadeBox):
            return f"Premade Box ({self.item.boxSize}) x {self.itemNumber}"
        elif isinstance(self.item, WeightedVeggie):
            return f"{self.item.vegName} (Kg) x {self.itemNumber}"
        elif isinstance(self.item, PackVeggie):
            return f"{self.item.vegName} (Pack) x {self.itemNumber}"
        elif isinstance(self.item, UnitPriceVeggie):
            return f"{self.item.vegName} (Unit) x {self.itemNumber}"
        return "Unknown Item"

    def __str__(self):
        return f"Line Item: {self.getItemDetails()} | Total: ${self.lineTotal:.2f}"