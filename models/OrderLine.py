from sqlalchemy import Column, Integer
from .base import Base

class OrderLine(Base):
    __tablename__ = 'orderlines'

    id = Column(Integer, primary_key=True)
    itemNumber = Column(Integer)

    def __init__(self, itemNumber):
        self.itemNumber = itemNumber