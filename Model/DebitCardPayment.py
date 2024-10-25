from sqlalchemy import Column, Integer, String, Float

from Payment import Payment

class DebitCardPayment(Payment):
    __tablename__ = 'debit_card_payments'

    __paymentID = Column(Integer, primary_key=True, autoincrement=True)
    __bankName = Column(String(20))
    __debitCardNumber = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'DebitCardPayment'
    }

    def __init__(self, paymentAmount, paymentDate, bankName, debitCardNumber):
        super().__init__(paymentAmount, paymentDate)
        self.__bankName = bankName
        self.__debitCardNumber = debitCardNumber

    # Getter and setter for bankName
    @property
    def bankName(self):
        return self.__bankName

    @bankName.setter
    def bankName(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Bank name must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Bank name cannot be empty")

        # Check if the length is between 1 and 20 characters
        if len(value) > 20:
            raise ValueError("Bank name must be between 1 and 20 characters")

        self.__bankName = value

    # Getter and setter for debitCardNumber
    @property
    def debitCardNumber(self):
        return self.__debitCardNumber

    @debitCardNumber.setter
    def debitCardNumber(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Debit card number must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Debit card number cannot be empty")

        # Check if the length is between 1 and 20 characters
        if len(value) > 20:
            raise ValueError("Debit card number must be between 1 and 20 characters")