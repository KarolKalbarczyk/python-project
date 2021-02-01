
class ProductOrderDTO():

    def __init__(self, orderHasProduct):
        self.id = orderHasProduct.id
        self.quantity = orderHasProduct.quantity
        self.name = orderHasProduct.name
        self.code = orderHasProduct.code
        self.price = orderHasProduct.price
