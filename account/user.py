from flask_login import UserMixin
from sqlalchemy.orm import relationship
from __init__ import db
from order.entities import OrderStatus, Order


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

