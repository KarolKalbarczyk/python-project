import os

from __init__ import app, db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:12offdeff4388@localhost/shop'
from product.entities import Product
from order.entities import OrderHasProducts, Order, ProductSnapshot
from Synchronization.entities import Synchronization, SynchLog
from account.user import User
db.create_all()
