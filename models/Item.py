from sqlalchemy import Column, Integer, String
from .base import Base


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50))

    # This dictionary tells SQLAlchemy to use 'type' to differentiate subclasses
    __mapper_args__ = {
        'polymorphic_identity': 'Item', # The base identity for this class
        'polymorphic_on': type          # SQLAlchemy uses 'type' to distinguish subclasses
    }