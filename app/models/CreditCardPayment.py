from app import db
from .Payment import Payment


class CreditCardPayment(Payment):
    __tablename__ = 'credit_card_payments'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    cardExpiryDate = db.Column(db.Date)
    cardNumber = db.Column(db.String(30))
    cardType = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'CreditCardPayment'  # Unique identifier for polymorphism
    }

    def __init__(self, paymentAmount, paymentDate, cardExpiryDate, cardNumber, cardType):
        super().__init__(paymentAmount=paymentAmount, paymentDate=paymentDate)
        self.cardExpiryDate = cardExpiryDate
        self.cardNumber = cardNumber
        self.cardType = cardType