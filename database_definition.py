import datetime

from flask import Flask
from flask_login import UserMixin, current_user
from flask_migrate import Migrate
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Numeric, Date, Enum as Enum, \
    ForeignKey

from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.orm import relationship, sessionmaker

from enum import Enum
from flask_sqlalchemy import SQLAlchemy

from Synchronization.order_request_service import OrderRequestService
from product import vote_calc_fabric
from __init__ import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:12offdeff4388@localhost/shop'


class SynchStatus(Enum):
    OK = 0
    Failure = 1


class SynchAction(Enum):
    Added = 0
    Deleted = 1
    ModifiedQuantity = 2
    ModifiedPrice = 3

class Synchronization(db.Model):
    __tablename__ = 'synchronizations'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    status = db.Column(db.Enum(SynchStatus))
    logs = relationship("SynchLog", back_populates = "synchronization")

    def get_number_of_modifications(self):
        uniqueCodes = set()
        for log in self.logs:
            uniqueCodes.add(log.productCode)

        return len(uniqueCodes)

    # def __repr__(self):
    # return "<Product(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)

class SynchLog(db.Model):
    __tablename__ = 'synchlogs'

    id = db.Column(db.Integer, primary_key=True)
    productCode = db.Column(db.String)
    synchronizationId = db.Column(db.Integer, ForeignKey('synchronizations.id'))
    synchronization = relationship("Synchronization", back_populates = "logs")
    action = db.Column(db.Enum(SynchAction))
    original = db.Column(db.String)
    new = db.Column(db.String)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    joinDate = db.Column(db.Date)
    isActive = db.Column(db.Boolean)
    isAdmin = db.Column(db.Boolean)
    votes = relationship("Vote", back_populates = "user")
    orders = relationship("Order", back_populates = "user")


    @property
    def is_active(self):
        return self.isActive

    def get_active_order(self):
        for o in self.orders:
            if (o.status == OrderStatus.Ongoing):
                return o

        order = Order(user=self, status=OrderStatus.Ongoing)
        db.session.add(order)

        return order


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

class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer, ForeignKey('products.id'))
    userId = db.Column(db.Integer, ForeignKey('users.id'))
    vote = db.Column(db.Integer)
    product = relationship("Product", back_populates="votes")
    user = relationship("User", back_populates = "votes")


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
            products = { p.code : p for p in Product.query.all() }
            for snapshot in self.snapshots:
                product = products[snapshot.code]
                product.quantity += snapshot.quantity


class ProductCategory(Enum):
    Computer = "computer"
    Keyboard = "keyboard"
    Mouse = "mouse"
    Screen = "screen"


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    code = db.Column(db.String(10))
    price = db.Column(db.Numeric)
    quantity = db.Column(db.Integer)
    category = db.Column(db.Enum(ProductCategory))
    votes = relationship("Vote", back_populates="product", cascade="all, delete-orphan")
    orders = relationship("OrderHasProducts", back_populates="product", cascade="all, delete-orphan")

    def calculate_votes(self):

        calculator = vote_calc_fabric.get_calculator()

        entireWeight = 0
        voteSum = 0

        for vote in self.votes:
            weight = calculator.calculate(vote.user)
            voteSum += vote.vote * weight
            entireWeight += weight

        if entireWeight == 0:
            return 0

        return voteSum / entireWeight

    def get_formatted_votes(self):
        return  "%.2f" % round(self.calculate_votes(), 2)

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


db.create_all()
#User.query.first().isAdmin = True
#db.session.commit()