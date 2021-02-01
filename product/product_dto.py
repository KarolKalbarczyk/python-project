
from flask_babel import _

class ProductDTO():

    def __init__(self, product, userVote, photo):
        self.id = product.id
        self.name = product.name
        self.code = product.code
        self.price = product.price
        self.vote = product.get_formatted_votes()
        self.quantity = product.quantity
        self.userVote = userVote
        self.photo = photo

class ProductDetailDTO():
    def __init__(self, product):
        self.id = product.id
        self.name = product.name
        self.code = product.code
        self.price = product.price
        self.vote = product.get_formatted_votes()
        self.quantity = product.quantity
        self.description = _(product.code)
