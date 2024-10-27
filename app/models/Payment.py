from app import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paymentAmount = db.Column(db.Float)
    paymentDate = db.Column(db.Date)
    customerId = db.Column(db.Integer, db.ForeignKey('customers.id'))
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'Payment',  # The base identity for this class
        'polymorphic_on': type  # SQLAlchemy uses 'type' to distinguish subclasses
    }

    # Relationship to Customer
    customer = db.relationship("Customer", back_populates="payments")

    def __init__(self, paymentAmount, paymentDate):
        self.paymentAmount = paymentAmount
        self.paymentDate = paymentDate
