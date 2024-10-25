from sqlalchemy import Column, Integer, Float, ForeignKey

from Veggie import Veggie

class WeightedVeggie(Veggie):
    __tablename__ = 'weighted_veggies'

    __veggieID = Column(Integer, ForeignKey('veggies.veggieID'), primary_key = True)
    __weight = Column(Float)
    __pricePerKilo = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity': 'Weighted Veggie'
    }

    def __init__(self, vegName, weight, pricePerKilo):
        super().__init__(vegName)
        self.__weight = weight
        self.__pricePerKilo = pricePerKilo

    # Getter and setter for weight
    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        if value > 0:
            self.__weight = value
        else:
            raise ValueError("Weight must be greater than 0.")

    # Getter and setter for pricePerKilo
    @property
    def pricePerKilo(self):
        return self.__pricePerKilo

    @pricePerKilo.setter
    def pricePerKilo(self, value):
        if value > 0:
            self.__pricePerKilo = value
        else:
            raise ValueError("Price per kilo must be greater than 0.")