from sqlalchemy import Column, Integer, String, Float, ForeignKey

from Veggie import Veggie

class PackVeggie(Veggie):
    __tablename__ = 'pack_veggies'

    __packVeggieID = Column(Integer, ForeignKey('veggies.veggieID'), primary_key = True)
    __numberOfPacks = Column(Integer)
    __pricePerPack = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity': 'Pack Veggie'
    }

    def __init__(self, vegName, numberOfPacks, pricePerPack):
        super().__init__(vegName)
        self.__numberOfPacks = numberOfPacks
        self.__pricePerPack = pricePerPack

    # Getter and setter for numberOfPack
    @property
    def numberOfPacks(self):
        return self.__numberOfPacks

    @numberOfPacks.setter
    def numberOfPacks(self, value):
        if value > 0:
            self.__numberOfPacks = value
        else:
            raise ValueError("Number of packs must be greater than 0.")

    # Getter and setter for pricePerPack
    @property
    def pricePerPack(self):
        return self.__pricePerPack

    @pricePerPack.setter
    def pricePerPack(self, value):
        if value > 0:
            self.__pricePerPack = value
        else:
            raise ValueError("Price per pack must be greater than 0.")