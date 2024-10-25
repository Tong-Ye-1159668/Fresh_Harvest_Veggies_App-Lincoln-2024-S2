from sqlalchemy import Column, Integer, String, Float, ForeignKey
from Customer import Customer

class CorporateCustomer(Customer):
    __tablename__ = 'corporate_customers'

    __corpCustID = Column(Integer, ForeignKey('customers.custID'), primary_key = True)
    __discountRate = Column(Float, default = 0.10) # Default 10% discount
    __maxCredit = Column(Float)
    __minBalance = Column(Float)

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0,
                 discountRate=0.10, maxCredit, minBalance):
        super.__init__(firstName, lastName, username, password, custAddress, custBalance)
        self.__discountRate = discountRate
        self.__maxCredit = maxCredit
        self.__minBalance = minBalance

    def getPersonRole(self):
        return 'Corporate Customer'

    # Getter and setter for discountRate
    @property
    def discountRate(self):
        return self.__discountRate

    @discountRate.setter
    def discountRate(self, value):
        if 0 <= value <= 1:
            self.__discountRate = value
        else:
            raise ValueError("Discount rate must be between 0 and 1.")

    # Getter and setter for maxCredit
    @property
    def maxCredit(self):
        return self.__maxCredit

    @maxCredit.setter
    def maxCredit(self, value):
        if value >= 0:
            self.__maxCredit = value
        else:
            raise ValueError("Max credit must be non-negative")

    # Getter and setter for minBalance
    @property
    def minBalance(self):
        return self.__minBalance

    @minBalance.setter
    def minBalance(self, value):
        if value >= 0:
            self.__minBalance = value
        else:
            raise ValueError("Min balance must be non-negative")