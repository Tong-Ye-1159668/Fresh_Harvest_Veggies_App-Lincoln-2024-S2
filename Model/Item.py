from abc import ABC, abstractmethod

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Item(Base, ABC):
    __tablename__ = 'items'

    __itemID = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'Item', # Use 'type' column to distinguish subclasses
        'polymorphic_on': type
    }