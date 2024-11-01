# test_order.py
import pytest
from datetime import datetime

from models import CorporateCustomer
from models.Order import Order, OrderStatus, DeliveryMethod


def test_order_creation():
    order = Order(
        orderCustomer=1,
        orderNumber="ORD001"
    )
    assert order.orderCustomer == 1
    assert order.orderNumber == "ORD001"
    assert order.orderStatus == OrderStatus.PENDING.value
    assert order.deliveryMethod == DeliveryMethod.PICKUP
    # Initialize values that are None by default
    assert order.total is None
    assert order.subtotal is None
    assert order.discount is None
    assert order.deliveryFee is None


def test_order_delivery():
    order = Order(
        orderCustomer=1,
        orderNumber="ORD002",
        deliveryMethod=DeliveryMethod.DELIVERY
    )
    assert order.deliveryMethod == DeliveryMethod.DELIVERY

    # Initialize the required values before calculation
    order.subtotal = 0
    order.discount = 0
    order.deliveryFee = 0

    order.calcTotalPrice()
    assert order.deliveryFee == 10.0
    assert order.total == 10.0


@pytest.mark.parametrize("current_status, can_cancel", [
    (OrderStatus.PENDING.value, True),
    (OrderStatus.SUBMITTED.value, True),
    (OrderStatus.PROCESSING.value, False),
    (OrderStatus.READY_TO_PICKUP.value, False),
    (OrderStatus.DELIVERED.value, False),
    (OrderStatus.COMPLETED.value, False)
])
def test_order_cancellation(current_status, can_cancel):
    order = Order(orderCustomer=1, orderNumber="ORD003")
    order.orderStatus = current_status
    success, _ = order.cancelOrder()
    assert success == can_cancel


def test_order_status_update():
    order = Order(orderCustomer=1, orderNumber="ORD004")
    assert order.orderStatus == OrderStatus.PENDING.value

    # Test status update
    order.updateOrderStatus(OrderStatus.SUBMITTED)
    assert order.orderStatus == OrderStatus.SUBMITTED

    order.updateOrderStatus(OrderStatus.PROCESSING)
    assert order.orderStatus == OrderStatus.PROCESSING


def test_delivery_validation():
    order = Order(
        orderCustomer=1,
        orderNumber="ORD005",
        deliveryMethod=DeliveryMethod.DELIVERY
    )

    # Test within delivery radius
    order.deliveryDistance = 15
    assert order.validateDelivery() == True

    # Test outside delivery radius
    order.deliveryDistance = 25
    assert order.validateDelivery() == False


def test_calc_total_price_with_delivery():
    order = Order(
        orderCustomer=1,
        orderNumber="ORD006",
        deliveryMethod=DeliveryMethod.DELIVERY
    )
    # Initialize required values
    order.subtotal = 100
    order.discount = 0
    order.deliveryFee = 0

    order.calcTotalPrice()
    assert order.deliveryFee == 10.0
    assert order.total == 110.0  # 100 + 10 delivery fee


def test_calc_total_price_with_corporate_customer():
    # Create a corporate customer
    corporate_customer = CorporateCustomer(
        firstName="Test",
        lastName="Customer",
        username="testcorp",
        password="password",
        custAddress="123 Test St",
        custBalance=0,
        discountRate=0.10
    )

    order = Order(
        orderCustomer=1,
        orderNumber="ORD007"
    )
    # Initialize required values
    order.subtotal = 100
    order.discount = 0
    order.deliveryFee = 0
    order.customer = corporate_customer

    order.calcTotalPrice()
    assert order.discount == 10.0  # 10% of 100
    assert order.total == 90.0  # 100 - 10 discount


def test_calc_total_price_with_corporate_customer_and_delivery():
    # Create a corporate customer
    corporate_customer = CorporateCustomer(
        firstName="Test",
        lastName="Customer",
        username="testcorp2",
        password="password",
        custAddress="123 Test St",
        custBalance=0,
        discountRate=0.10
    )

    order = Order(
        orderCustomer=1,
        orderNumber="ORD008",
        deliveryMethod=DeliveryMethod.DELIVERY
    )
    # Initialize required values
    order.subtotal = 100
    order.discount = 0
    order.deliveryFee = 0
    order.customer = corporate_customer

    order.calcTotalPrice()
    assert order.deliveryFee == 10.0
    assert order.discount == 10.0  # 10% of 100
    assert order.total == 100.0  # 100 - 10 discount + 10 delivery fee