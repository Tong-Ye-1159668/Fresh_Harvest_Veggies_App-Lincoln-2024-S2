from sqlalchemy import Column, Integer, String, ForeignKey
from .Payment import Payment

class DebitCardPayment(Payment):
    __tablename__ = 'debit_card_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key = True)
    bankName = Column(String(20))
    debitCardNumber = Column(String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'DebitCardPayment'  # Unique identifier for polymorphism
    }

    def __init__(self, paymentAmount, paymentDate, bankName, debitCardNumber):
        super().__init__(paymentAmount=paymentAmount, paymentDate=paymentDate)
        self.bankName = bankName
        self.debitCardNumber = debitCardNumber