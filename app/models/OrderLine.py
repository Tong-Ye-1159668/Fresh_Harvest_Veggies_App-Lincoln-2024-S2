from app import db


class OrderLine(db.Model):
    __tablename__ = 'orderlines'

    id = db.Column(db.Integer, primary_key=True)
    itemNumber = db.Column(db.Integer)

    # Foreign keys and relationships
    orderId = db.Column(db.Integer, db.ForeignKey('orders.id'))
    itemId = db.Column(db.Integer, db.ForeignKey('items.id'))

    # Relationships
    order = db.relationship("Order", back_populates="orderLines")
    item = db.relationship("Item")

    def __init__(self, itemNumber, orderId, itemId):
        self.itemNumber = itemNumber
        self.orderId = orderId
        self.itemId = itemId
