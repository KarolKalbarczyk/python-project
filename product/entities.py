from enum import Enum
from __init__ import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from product import vote_calc_fabric


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer, ForeignKey('products.id'))
    userId = db.Column(db.Integer, ForeignKey('users.id'))
    vote = db.Column(db.Integer)
    product = relationship("Product", back_populates="votes")
    user = relationship("User", back_populates = "votes")


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

