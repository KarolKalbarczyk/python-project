import os

import flask
from flask import request, Response, url_for
from flask_login import login_required, current_user
from flask_babel import _
from flask_wtf.file import FileField
from wtforms import StringField, validators, FloatField, SubmitField, HiddenField
from wtforms import Form, StringField, PasswordField, validators, ValidationError

from product.product_dto import ProductDTO, ProductDetailDTO
from database_definition import Product, User, Vote, db
from product.product_service import ProductService
from base_render import render_template
from auth import get_current_user




class ProductForm(Form):
    name = StringField(_('Name'), [validators.DataRequired()])
    price = FloatField(_('Price'), [validators.DataRequired(), validators.NumberRange(min = 0, message=_('Price cannot be smaller than 0'))])
    photo = FileField(_('Photo'))
    submit = SubmitField(_('Submit'))
    hidden = HiddenField(_('hidden'))

@login_required
def products(service : ProductService):
    filter = request.args.get('filter')
    page = int(request.args.get('page') or 1)
    minPrice = int(request.args.get('minPrice') or 0)
    maxPrice = int(request.args.get('maxPrice') or 9999999)
    categories = request.args.get('categories')
    if categories is None:
        categories = []
    else:
        categories = categories.split(',')[:-1]

    dtos, hasPrev, hasNext = service.get_product_list(filter, page, minPrice, maxPrice, categories, numberOnPage=8)
    return render_template('product_list.html', dtos = dtos, pageNumber = page, hasNextPage = hasNext, hasPrevPage = hasPrev)

@login_required
def vote(service : ProductService):
    prodId = int(request.args.get('id'))
    voteNumber = int(request.args.get('vote'))
    newRating = service.update_rating(prodId, voteNumber)

    return {'rating': f'{newRating}'}

@login_required
def show_product():
    productId= int(request.args.get('productId'))
    form = ProductForm(request.form)

    product = Product.query.get(productId)
    dto = ProductDetailDTO(product)

    if request.method == 'POST':
        if not get_current_user().isAdmin:
            return Response('', status=401)

        if form.validate():
            product = Product.query.get(productId)
            product.price = form.price.data
            product.name = form.name.data
            if form.hidden.data == "1":
                photo = request.files['photo']
                photo.save(os.getenv('photo_dir') + fr'\{product.code}.jpg')
            db.session.commit()
            return flask.redirect(url_for('products'))
        return render_template('product.html', product = dto, form = form)

    form.price.default = product.price
    form.name.default = product.name
    form.process()
    return render_template('product.html', product = dto, form = form)