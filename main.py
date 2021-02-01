import flask
from flask_injector import FlaskInjector
from flask_login import LoginManager

import language_controller
from order import order_controller
from Synchronization import synchronization_controller
from account import account_controller
from product import product_controller

from __init__ import app


app.config['MAX_CONTENT_PATH'] = 100000000000

import os

from account.user import User
from dependencies import configure

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return flask.redirect(flask.url_for('login'))

if __name__ == '__main__':
    #manager.run()
    app.add_url_rule('/', view_func=account_controller.hello_world)

    app.add_url_rule('/signup', view_func=account_controller.sign_up, methods=['GET', 'POST'])
    app.add_url_rule('/login', view_func=account_controller.login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=account_controller.logout, methods=['GET', 'POST'])

    app.add_url_rule('/products', view_func=product_controller.products)
    app.add_url_rule('/product', view_func=product_controller.show_product, methods=['GET', 'POST'])
    app.add_url_rule('/vote', view_func=product_controller.vote, methods=['PUT'])

    app.add_url_rule('/synchronize', view_func=synchronization_controller.synchronize, methods=['POST'])
    app.add_url_rule('/stopJob', view_func=synchronization_controller.stop, methods=['POST'])
    app.add_url_rule('/synchronizations', view_func=synchronization_controller.synchronizations, methods=['GET', 'POST'])
    app.add_url_rule('/synchronization', view_func=synchronization_controller.get_synchronization)

    app.add_url_rule('/addToOrder', view_func=order_controller.add_to_order, methods=['POST'])
    app.add_url_rule('/order', view_func=order_controller.order, methods=['GET', 'POST'])
    app.add_url_rule('/orders', view_func=order_controller.orders)
    app.add_url_rule('/changeQuantity', view_func=order_controller.change_quantity, methods=['PATCH'])
    app.add_url_rule('/removeFromOrder', view_func=order_controller.remove_from_order, methods=['DELETE'])
    app.add_url_rule('/decide', view_func=order_controller.decide, methods=['PATCH'])

    app.add_url_rule('/setLang', view_func=language_controller.set_lang, methods=['PATCH'])


    FlaskInjector(app=app, modules=[configure])

    login_manager.init_app(app)
    app.run()
