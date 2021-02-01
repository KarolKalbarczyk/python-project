import os

from flask import url_for
from sqlalchemy import and_, or_

from database_definition import db

from auth import get_current_user
from product.entities import Vote, ProductCategory, Product
from product.product_dto import ProductDTO
from utils import find


class ProductService():
    def get_product_list(self, filter, page, minPrice, maxPrice, categories,  numberOnPage):
        query = Product.query.filter(Product.quantity > 0)

        categories = list(map(lambda x: ProductCategory(x), categories))

        if filter is not None and filter != '':
            query = query.filter(Product.name.like(f'%{filter}%'))

        user = get_current_user()
        if not user.isAdmin:
            query = query.filter(and_(Product.price > minPrice, Product.price < maxPrice))
        else:
            query = query.filter(or_(and_(Product.price > minPrice, Product.price < maxPrice), Product.price.is_(None)))

        if (len(categories) > 0):
            query = query.filter(Product.category.in_(categories))

        query = query.paginate(page, numberOnPage, False)

        products = query.items
        userVotes = Vote.query.filter_by(userId=user.id).filter(Vote.productId.in_(list(map(lambda p : p.id, products)))).all()

        dtos = []
        for p in products:
            vote = find(userVotes, lambda x: x.productId == p.id)
            if vote is None:
                value = 0
            else:
                value = vote.vote
            path = os.getenv('photo_dir') + fr'/{p.code}.jpg'
            dtos.append(ProductDTO(p, value, path[7:] if os.path.exists(path) else ""))

        return dtos, query.has_prev, query.has_next

    def update_rating(self, productId, rating):
        userId = get_current_user().id

        vote = Vote.query.filter_by(productId=productId, userId=userId).first() or \
               Vote(productId=productId, userId=userId)

        vote.vote = rating

        db.session.add(vote)
        db.session.commit()
        return Product.query.get(productId).get_formatted_votes()
