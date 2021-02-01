import hashlib
import os

from flask import request, Response, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _
from wtforms import Form, RadioField, IntegerField, FormField, FieldList, TextField, StringField, validators

from order.order_service import OrderService
from order.order_enums import *
from order.product_order_dto import ProductOrderDTO

from base_render import render_template
from order.order_list_dto import OrderListDTO
import threading

lock = threading.Semaphore()

class OrderForm(Form):

    invoice = RadioField(_('Invoice'), choices=[(x, x) for x in get_enum_list(InvoiceOptions)])
    message = RadioField(_('Message'), choices=[(x, x) for x in get_enum_list(MessageOptions)])
    address = StringField(_('Address'), validators=[validators.DataRequired()])
    clientName = StringField(_('Client name'), validators=[validators.DataRequired()])


@login_required
def order(service: OrderService):
    orderId = int(request.args.get('orderId') or -1)
    userOrder = service.get_order_for_user(orderId)

    form = OrderForm(request.form)
    if request.method == 'POST':
        lock.acquire()
        if form.validate():
            success, invoice = service.finalize(form.invoice.data, form.message.data, form.address.data, form.clientName.data)
            lock.release()
            if not success:
                return Response('', status=400)
            if invoice is not None:
                return send_from_directory(directory=os.getenv('invoices'), filename=invoice)
        lock.release()

    if userOrder is None:
        return Response('', status = 400)

    dtos = ([ ProductOrderDTO(x) for x in userOrder.get_products()])
    dtos.sort(key = lambda x: x.code)

    return render_template('order.html',
                           form = form,
                           dtos = dtos,
                           totalPrice = userOrder.calculate_total_price(),
                           status = userOrder.status.name,
                           id = userOrder.id)

@login_required
def add_to_order(service: OrderService):
    productId = int(request.args.get('productId') or -1)
    service.add_to_order(productId)
    return Response('', status = 200)

@login_required
def remove_from_order(service: OrderService):
    productId = int(request.args.get('productId') or -1)
    service.remove_from_order(productId)
    return Response('', status = 200)

@login_required
def change_quantity(service: OrderService):
    productId = int(request.args.get('productId') or -1)
    quantity = int(request.args.get('quantity') or 1)

    totalPrice= service.change_quantity_and_get_price(productId, quantity)

    if totalPrice is None:
        return Response('', status = 400)

    return { 'totalPrice' : f'{totalPrice}$' }

@login_required
def orders(service: OrderService):
    page = int(request.args.get('page') or 1)
    dtos, hasPrev, hasNext =  service.get_orders(page, pageSize= 20)

    return render_template('order_list.html', dtos = dtos, hasPrev = hasPrev, hasNext = hasNext, pageNumber = page)

#@admin_only
def decide(service: OrderService):
    orderId = int(request.args.get('orderId') or -1)
    accepted = bool(int(request.args.get('isAccepted')))
    service.decide_on_order(orderId, accepted)
    return Response('', status = 200)