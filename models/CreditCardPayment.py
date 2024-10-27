from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from .Payment import Payment

class CreditCardPayment(Payment):
    __tablename__ = 'credit_card_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key = True)
    cardExpiryDate = Column(Date)
    cardNumber = Column(String(30))
    cardType = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'CreditCardPayment'  # Unique identifier for polymorphism
    }

    def __init__(self, paymentAmount, paymentDate, cardExpiryDate, cardNumber, cardType):
        super().__init__(paymentAmount=paymentAmount, paymentDate=paymentDate)
        self.cardExpiryDate = cardExpiryDate
        self.cardNumber = cardNumber
        self.cardType = cardType