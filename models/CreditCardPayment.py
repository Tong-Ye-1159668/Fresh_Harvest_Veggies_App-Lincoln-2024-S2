from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date

from Payment import Payment

class CreditCardPayment(Payment):
    __tablename__ = 'credit_card_payments'

    __paymentID = Column(Integer, ForeignKey('payments.paymentID'), primary_key = True)
    __cardExpiryDate = Column(Date)
    __cardNumber = Column(String(20))
    __cardType = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'CreditCardPayment'
    }

    def __init__(self, paymentAmount, paymentDate, cardExpiryDate, cardNumber, cardType):
        super().__init__(paymentAmount, paymentDate)
        self.__cardExpiryDate = cardExpiryDate
        self.__cardNumber = cardNumber
        self.__cardType = cardType

    # Getter and setter for cardExpiryDate
    @property
    def cardExpiryDate(self):
        return self.__cardExpiryDate

    @cardExpiryDate.setter
    def cardExpiryDate(self, value):
        self.__cardExpiryDate = value

    # Getter and setter for cardNumber
    @property
    def cardNumber(self):
        return self.__cardNumber

    @cardNumber.setter
    def cardNumber(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Card number must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Card number cannot be empty")

        # Check if the length is between 1 and 20 characters
        if len(value) > 20:
            raise ValueError("Card number must be between 1 and 20 characters")

        self.__cardNumber = value

    # Getter and setter for cardType
    @property
    def cardType(self):
        return self.__cardType

    @cardType.setter
    def cardType(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Card type must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Card type cannot be empty")

        # Check if the length is between 1 and 20 characters
        if len(value) > 20:
            raise ValueError("Card type must be between 1 and 20 characters")

        self.__cardType = value