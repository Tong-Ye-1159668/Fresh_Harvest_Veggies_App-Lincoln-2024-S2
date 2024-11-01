from sqlalchemy import Column, Integer, Float, ForeignKey
from .Customer import Customer

class CorporateCustomer(Customer):
    __tablename__ = 'corporate_customers'

    id = Column(Integer, ForeignKey('customers.id'), primary_key = True)
    discountRate = Column(Float, default = 0.10) # Default 10% discount
    maxCredit = Column(Float, default = 200)
    minBalance = Column(Float, default = 10)

    __mapper_args__ = {
        'polymorphic_identity': 'Corporate Customer'
    }

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0,
                 discountRate=0.10, maxCredit=200, minBalance=0):
        super().__init__(firstName=firstName, lastName=lastName, username=username, password=password,
                         custAddress=custAddress, custBalance=custBalance)
        self.discountRate = discountRate
        self.maxCredit = maxCredit
        self.minBalance = minBalance

    def __str__(self):
        customer_str = super().__str__()
        corp_info = f"Discount Rate: {self.discountRate*100}% | Max Credit: ${self.maxCredit:.2f} | Min Balance: ${self.minBalance:.2f}"
        return f"{customer_str} | {corp_info}"
