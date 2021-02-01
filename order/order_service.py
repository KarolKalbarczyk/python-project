from flask_login import current_user
from injector import inject
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from Synchronization.order_request_service import OrderRequestService
from __init__ import db
from account.user import User
from order.entities import OrderStatus, Order, OrderHasProducts
from product.entities import Product
from order.options_fabric import OptionsFabric
from order.order_list_dto import OrderListDTO


class OrderService():

    @inject
    def __init__(self, service: OrderRequestService, fabric: OptionsFabric):
        self.service = service
        self.fabric = fabric

    def finalize(self, invoiceOption, messageOption, address, clientName):
        order = self.get_order()

        succes = order.finalize()

        invoice = None
        if succes:
            self.fabric.get_message_service(messageOption).send_message(address, order.id)
            invoice = self.fabric.get_invoice_service(invoiceOption).generate(order, clientName)
            db.session.commit()
        return succes, invoice

    def get_user_with_orders(self):
        return User.query.filter_by(email = current_user.email).options(joinedload('orders')).first()

    def get_order(self):
        user = self.get_user_with_orders()
        order = user.get_active_order()

        return order

    def get_order_for_user(self, orderId):
        if orderId != -1:
            try:
                user = self.get_user_with_orders()
                if user.isAdmin:
                    return Order.query.filter_by(id = orderId).filter(Order.status.in_([OrderStatus.Finalized, OrderStatus.Accepted, OrderStatus.Declined])).first()
                return next(o for o in user.orders if o.id == orderId)
            except:
                return None
        else:
            return self.get_order()

    def add_to_order(self, productId):
        product = Product.query.get(productId)
        if product is None:
            return

        order = self.get_order()

        if productId not in [p.productId for p in order.products]:
            order.products.append(OrderHasProducts(productId=productId, order=order, quantity=1))

        db.session.commit()

    def remove_from_order(self, productId):
        order = self.get_order()
        OrderHasProducts.query.filter_by(orderId=order.id, productId=productId).delete()
        db.session.commit()

    def change_quantity_and_get_price(self, productId, quantity):
        order = self.get_order()

        ohp = OrderHasProducts.query.filter_by(orderId=order.id, productId=productId).options(
            joinedload('product')).first()

        if 0 >= quantity or quantity > ohp.product.quantity:
            return None

        ohp.quantity = quantity
        db.session.commit()
        return order.calculate_total_price()

    def get_orders(self, page, pageSize):
        user = self.get_user_with_orders()
        if user.isAdmin:
            query = Order.query.filter(Order.status.in_([OrderStatus.Finalized, OrderStatus.Accepted, OrderStatus.Declined])).paginate(page, pageSize, False)
            return [ OrderListDTO(o) for o in query.items ], query.has_prev, query.has_next
        else:
            query = Order.query.filter_by(userId = user.id).paginate(page, pageSize, False)
            return [ OrderListDTO(o) for o in query.items ], query.has_prev, query.has_next


    def decide_on_order(self, orderId, isAccepted):
        order = self.get_order_for_user(orderId)
        order.decide(isAccepted, self.service)

        db.session.commit()
