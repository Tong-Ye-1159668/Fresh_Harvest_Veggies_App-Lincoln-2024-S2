import pytest
from datetime import date

from models import CorporateCustomer
from models.Payment import Payment
from models.CreditCardPayment import CreditCardPayment
from models.DebitCardPayment import DebitCardPayment
from models.Order import Order
from models.Customer import Customer


def test_base_payment_creation():
    payment = Payment(
        paymentAmount=100.0,
        paymentDate=date.today()
    )
    assert payment.paymentAmount == 100.0
    assert payment.paymentDate == date.today()
    assert payment.type == 'Payment'


def test_credit_card_payment_creation():
    payment = CreditCardPayment(
        paymentAmount=200.0,
        paymentDate=date.today(),
        cardExpiryDate=date(2025, 12, 31),
        cardNumber="4111111111111111",
        cardType="VISA"
    )
    assert payment.paymentAmount == 200.0
    assert payment.cardNumber == "4111111111111111"
    assert payment.cardType == "VISA"
    assert payment.type == "CreditCardPayment"


def test_debit_card_payment_creation():
    payment = DebitCardPayment(
        paymentAmount=150.0,
        paymentDate=date.today(),
        bankName="Test Bank",
        debitCardNumber="1234567890123456"
    )
    assert payment.paymentAmount == 150.0
    assert payment.bankName == "Test Bank"
    assert payment.debitCardNumber == "1234567890123456"
    assert payment.type == "DebitCardPayment"


def test_payment_processing():
    # Create a customer
    customer = Customer(
        firstName="Test",
        lastName="User",
        username="testuser",
        password="password123",
        custAddress="123 Test St",
        custBalance=50.00,
        maxOwing=100.00
    )

    # Create an order
    order = Order(
        orderCustomer=1,
        orderNumber="ORD001"
    )
    order.customer = customer
    order.total = 40.00

    # Create and process payment
    payment = Payment(
        paymentAmount=40.00,
        paymentDate=date.today()
    )
    payment.order = order

    assert payment.processPayment() == True
    assert payment.order.customer.custBalance == 10.00  # 50 - 40


def test_payment_validation():
    # Create a customer with low balance
    customer = Customer(
        firstName="Test",
        lastName="User",
        username="testuser",
        password="password123",
        custAddress="123 Test St",
        custBalance=10.0,
        maxOwing=100.0
    )

    # Create an order with high amount
    order = Order(
        orderCustomer=1,
        orderNumber="ORD002"
    )
    order.customer = customer
    order.total = 200.0

    # Create payment
    payment = Payment(
        paymentAmount=200.0,
        paymentDate=date.today()
    )
    payment.order = order

    assert payment.validatePayment() == False


def test_corporate_payment_validation():
    # Create corporate customer
    corporate_customer = CorporateCustomer(
        firstName="Corp",
        lastName="User",
        username="corpuser",
        password="password123",
        custAddress="123 Corp St",
        custBalance=1000.0,
        discountRate=0.10,
        minBalance=500.0
    )

    # Create order
    order = Order(
        orderCustomer=1,
        orderNumber="CORP001"
    )
    order.customer = corporate_customer
    order.total = 400.0

    # Create payment
    payment = Payment(
        paymentAmount=400.0,
        paymentDate=date.today()
    )
    payment.order = order

    # Should succeed as balance after payment (600) > minBalance (500)
    assert payment.validatePayment() == True


def test_corporate_payment_validation_insufficient_balance():
    # Create corporate customer with minimum balance requirement
    corporate_customer = CorporateCustomer(
        firstName="Corp",
        lastName="User",
        username="corpuser",
        password="password123",
        custAddress="123 Corp St",
        custBalance=1000.0,
        discountRate=0.10,
        minBalance=800.0
    )

    # Create order
    order = Order(
        orderCustomer=1,
        orderNumber="CORP002"
    )
    order.customer = corporate_customer
    order.total = 300.0

    # Create payment
    payment = Payment(
        paymentAmount=300.0,
        paymentDate=date.today()
    )
    payment.order = order

    # Should fail as balance after payment (700) < minBalance (800)
    assert payment.validatePayment() == False


def test_corporate_payment_processing():
    # Create corporate customer
    corporate_customer = CorporateCustomer(
        firstName="Corp",
        lastName="User",
        username="corpuser",
        password="password123",
        custAddress="123 Corp St",
        custBalance=2000.0,
        discountRate=0.10,
        minBalance=500.0
    )

    # Create order
    order = Order(
        orderCustomer=1,
        orderNumber="CORP003"
    )
    order.customer = corporate_customer
    order.total = 1000.0

    # Create payment
    payment = Payment(
        paymentAmount=1000.0,
        paymentDate=date.today()
    )
    payment.order = order

    # Process payment
    assert payment.processPayment() == True
    assert payment.order.customer.custBalance == 1000.0  # 2000 - 1000


def test_corporate_credit_card_payment():
    # Create corporate customer
    corporate_customer = CorporateCustomer(
        firstName="Corp",
        lastName="User",
        username="corpuser",
        password="password123",
        custAddress="123 Corp St",
        custBalance=1500.0,
        discountRate=0.10,
        minBalance=500.0
    )

    # Create order
    order = Order(
        orderCustomer=1,
        orderNumber="CORP004"
    )
    order.customer = corporate_customer
    order.total = 800.0

    # Create credit card payment
    payment = CreditCardPayment(
        paymentAmount=800.0,
        paymentDate=date.today(),
        cardExpiryDate=date(2025, 12, 31),
        cardNumber="4111111111111111",
        cardType="VISA"
    )
    payment.order = order

    assert payment.validatePayment() == True
    assert payment.processPayment() == True
    assert payment.order.customer.custBalance == 700.0  # 1500 - 800