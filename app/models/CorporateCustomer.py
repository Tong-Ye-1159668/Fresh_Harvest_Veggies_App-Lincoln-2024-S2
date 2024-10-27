from app import db
from .Customer import Customer

class CorporateCustomer(Customer):
    __tablename__ = 'corporate_customers'

    id = db.Column(db.Integer, db.ForeignKey('customers.id'), primary_key=True)
    discountRate = db.Column(db.Float, default=0.10)  # Default 10% discount
    maxCredit = db.Column(db.Float)
    minBalance = db.Column(db.Float)

    __mapper_args__ = {
        'polymorphic_identity': 'Corporate Customer'
    }

    def __init__(self, firstName, lastName, username, password, custAddress, custBalance=0,
                 discountRate=0.10, maxCredit=0, minBalance=0):
        super().__init__(firstName=firstName, lastName=lastName, username=username, password=password,
                         custAddress=custAddress, custBalance=custBalance)
        self.discountRate = discountRate
        self.maxCredit = maxCredit
        self.minBalance = minBalance