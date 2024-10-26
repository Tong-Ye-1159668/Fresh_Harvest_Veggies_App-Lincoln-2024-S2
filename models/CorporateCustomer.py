from sqlalchemy import Column, Integer, Float, ForeignKey
from .Customer import Customer

class CorporateCustomer(Customer):
    __tablename__ = 'corporate_customers'

    id = Column(Integer, ForeignKey('customers.id'), primary_key = True)
    discountRate = Column(Float, default = 0.10) # Default 10% discount
    maxCredit = Column(Float)
    minBalance = Column(Float)

    __mapper_args__ = {
        'polymorphic_identity': 'Corporate Customer'
    }

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0,
                 discountRate=0.10, maxCredit=0, minBalance=0):
        super().__init__(firstName, lastName, username, password, custAddress, custBalance)
        self.discountRate = discountRate
        self.maxCredit = maxCredit
        self.minBalance = minBalance