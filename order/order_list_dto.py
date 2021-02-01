
class OrderListDTO():

    def __init__(self, order):
        self.id = order.id
        self.status=  order.status
        self.date = order.creationDate
        self.owner = order.user.email