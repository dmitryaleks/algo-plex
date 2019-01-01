

class Execution():

    def __init__(self, exec_id, order_id, size, price, side):
        self.exec_id = exec_id
        self.order_id = order_id
        self.size  = size
        self.price = price
        self.side = side