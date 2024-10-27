from app import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    orderCustomer = db.Column(db.Integer, db.ForeignKey('customers.id'))
    orderDate = db.Column(db.Date)
    orderNumber = db.Column(db.String(20), unique=True)  # Unique order/tracking number
    orderStatus = db.Column(db.String(20))

    # Relationships
    customer = db.relationship("Customer", back_populates="orders")
    orderLines = db.relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")

    def __init__(self, orderCustomer, orderDate, orderNumber, orderStatus):
        self.orderCustomer = orderCustomer
        self.orderDate = orderDate
        self.orderNumber = orderNumber
        self.orderStatus = orderStatus
