# test_customer.py
import pytest
from models.Customer import Customer
from models.CorporateCustomer import CorporateCustomer

def test_customer_basic():
    customer = Customer(
        firstName="John",
        lastName="Doe",
        username="johndoe",
        password="password123",
        custAddress="123 Main St"
    )
    assert customer.firstName == "John"
    assert customer.lastName == "Doe"
    assert customer.username == "johndoe"
    assert customer.custAddress == "123 Main St"
    assert customer.custBalance == 0  # default value
    assert customer.maxOwing == 100  # default value

def test_corporate_customer_basic():
    corp_customer = CorporateCustomer(
        firstName="Jane",
        lastName="Corp",
        username="janecorp",
        password="password123",
        custAddress="456 Business Ave"
    )
    assert corp_customer.firstName == "Jane"
    assert corp_customer.lastName == "Corp"
    assert corp_customer.discountRate == 0.10  # default value
    assert corp_customer.maxCredit == 200  # default value
    assert corp_customer.minBalance == 0  # default value

@pytest.mark.parametrize("first_name, last_name, expected_repr", [
    ("John", "Doe", "Customer(John Doe, Address: Test St, Balance: 0)"),
    ("Jane", "Smith", "Customer(Jane Smith, Address: Test St, Balance: 0)"),
    ("Bob", "Brown", "Customer(Bob Brown, Address: Test St, Balance: 0)")
])
def test_customer_repr(first_name, last_name, expected_repr):
    customer = Customer(
        firstName=first_name,
        lastName=last_name,
        username="test",
        password="test123",
        custAddress="Test St"
    )
    assert str(customer) == expected_repr