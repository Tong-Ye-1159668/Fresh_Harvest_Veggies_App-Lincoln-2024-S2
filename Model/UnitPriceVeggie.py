from sqlalchemy import Column, Integer, String, Float, ForeignKey

from Veggie import Veggie

class UnitPriceVeggie(Veggie):
    __tablename__ = 'unit_price_veggies'

    __veggieID = Column(Integer, ForeignKey('veggies.veggieID'), primary_key = True)
    __pricePerUnit = Column(Float)
    __quantity = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'Unit Price Veggie'
    }

    def __init__(self, pricePerUnit, quantity):
        super().__init__()
        self.__pricePerUnit = pricePerUnit
        self.__quantity = quantity

    # Getter and setter for pricePerUnit
    @property
    def pricePerUnit(self):
        return self.__pricePerUnit

    @pricePerUnit.setter
    def pricePerUnit(self, value):
        if value > 0:
            self.__pricePerUnit = value
        else:
            raise ValueError("Price per unit must be greater than 0.")

    # Getter and setter for quantity
    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        if value > 0:
            self.__quantity = value
        else:
            raise ValueError("Quantity must be greater than 0.")