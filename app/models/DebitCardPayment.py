from app import db  # Import the `db` instance from your Flask app
from .Payment import Payment


class DebitCardPayment(Payment):
    __tablename__ = 'debit_card_payments'

    id = db.Column(db.Integer, db.ForeignKey('payments.id'), primary_key=True)
    bankName = db.Column(db.String(20))
    debitCardNumber = db.Column(db.String(30))

    __mapper_args__ = {
        'polymorphic_identity': 'DebitCardPayment'  # Unique identifier for polymorphism
    }

    def __init__(self, paymentAmount, paymentDate, bankName, debitCardNumber):
        super().__init__(paymentAmount=paymentAmount, paymentDate=paymentDate)
        self.bankName = bankName
        self.debitCardNumber = debitCardNumber