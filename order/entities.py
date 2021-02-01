import datetime
from enum import Enum
from __init__ import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from Synchronization.order_request_service import OrderRequestService
from product.entities import Product


class ProductSnapshot(db.Model):
    __tablename__ = "snapshots"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    price = db.Column(db.Numeric)
    quantity = db.Column(db.Integer)
    orderId = db.Column(db.Integer, ForeignKey('orders.id'))
    description = db.Column(db.String)
    order = relationship("Order", back_populates="snapshots")
    name = db.Column(db.String)


class OrderStatus(Enum):
    Finalized = 0
    Accepted = 1
    Declined = 2
    Ongoing = 3


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    creationDate = db.Column(db.Date, default = datetime.date.today())

    status = db.Column(db.Enum(OrderStatus))
    userId = db.Column(db.Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates = "orders")

    products = relationship('OrderHasProducts', back_populates="order", lazy = "joined", cascade="all, delete-orphan")
    snapshots = relationship("ProductSnapshot", back_populates="order")

    def get_products(self):
        if self.status == OrderStatus.Ongoing:
            return self.products
        else:
            return self.snapshots

    def finalize(self):
        if self.status != OrderStatus.Ongoing:
            return False

        if len(self.products) == 0:
            return False

        for orderHasProduct in self.products:
            if orderHasProduct.product.quantity < orderHasProduct.quantity:
                return False
            orderHasProduct.product.quantity -= orderHasProduct.quantity

        self.snapshots = [ProductSnapshot(code = x.code, quantity = x.quantity, price = x.price, orderId = self.id, name = x.name) for x in self.products]
        self.products = []
        self.status = OrderStatus.Finalized

        return True

    def calculate_total_price(self):

        if len(self.products) == 0:
            sum = 0
            for p in self.snapshots:
                sum += p.price * p.quantity
            return sum

        else:
            sum = 0
            for p in self.products:
                sum += p.product.price * p.quantity
            return sum

    def decide(self, isAccepted, service: OrderRequestService):
        if self.status != OrderStatus.Finalized:
            return
        self.status = OrderStatus.Accepted if isAccepted else OrderStatus.Declined
        if isAccepted:
            service.request_products(self.snapshots)
        else:
            products = {p.code : p for p in Product.query.all()}
            for snapshot in self.snapshots:
                product = products[snapshot.code]
                product.quantity += snapshot.quantity


class OrderHasProducts(db.Model):
    __tablename__ = 'orderHasProducts'

    productId = db.Column(db.Integer, ForeignKey('products.id'), primary_key=True)
    orderId = db.Column(db.Integer, ForeignKey('orders.id'), primary_key=True)
    quantity = db.Column(db.Integer, default = 1)
    product = relationship("Product", back_populates="orders")
    order = relationship("Order", back_populates="products")

    @property
    def id(self):
        return self.product.id

    @property
    def code(self):
        return self.product.code

    @property
    def name(self):
        return self.product.name

    @property
    def price(self):
        return self.product.price

