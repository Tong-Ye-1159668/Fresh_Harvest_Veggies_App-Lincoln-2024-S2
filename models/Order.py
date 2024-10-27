from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from .base import Base

class OrderStatus(Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    FULFILLED = "Fulfilled"
    CANCELLED = "Cancelled"
    DELIVERED = "Delivered"

class DeliveryMethod(Enum):
    PICKUP = "Pickup"
    DELIVERY = "Delivery"


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    orderCustomer = Column(Integer, ForeignKey('customers.id'))
    orderDate = Column(Date)
    orderNumber = Column(String(20), unique=True)  # Unique order/tracking number for shipment or pick-up
    orderStatus = Column(String(20))
    deliveryMethod = Column(SQLEnum(DeliveryMethod))
    deliveryAddress = Column(String(255))
    deliveryDistance = Column(Float)
    deliveryFee = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    orderLines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")

    def __init__(self, orderCustomer, orderNumber, deliveryMethod = DeliveryMethod.PICKUP):
        self.orderCustomer = orderCustomer
        self.orderDate = datetime.now().date()
        self.orderNumber = orderNumber
        self.orderStatus = OrderStatus.PENDING
        self.deliveryMethod = deliveryMethod

    def calcTotalPrice(self):
        """Calculate order total including delivery fee and discounts"""
        self.subtotal = sum(line.calcLineTotal() for line in self.orderLines)

        # Apply corporate customer discount if applicable
        if hasattr(self.customer, 'discountRate'):
            self.discount = self.subtotal * self.customer.discountRate

        # Add delivery fee if applicable
        if self.deliveryMethod == DeliveryMethod.DELIVERY:
            self.deliveryFee = 10.0  # $10 delivery fee

        self.total = self.subtotal - self.discount + self.deliveryFee
        return self.total

    def ifCanCancel(self):
        """Check if the order can be cancelled"""
        return self.orderStatus == OrderStatus.PENDING

    def cancelOrder(self):
        """Cancel the order if possible"""
        if self.ifCanCancel():
            self.orderStatus = OrderStatus.CANCELLED
            return True
        return False

    def updateOrderStatus(self, newStatus):
        """Update order status"""
        if isinstance(newStatus, OrderStatus):
            self.orderStatus = newStatus
            return True
        return False

    def validateDelivery(self):
        """Validate delivery distance"""
        if self.deliveryMethod == DeliveryMethod.DELIVERY:
            return self.deliveryDistance <= 20  # 20km radius limit
        return True