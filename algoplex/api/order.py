class Order():

    def __init__(self, side, pair, size, price, stop_loss_price, id):
        self.side = side
        self.pair = pair
        self.size = size
        self.price = price
        self.stop_loss_price = stop_loss_price
        self.id = id
        self.fills = []

    def define_id(self, id):
        self.id = id

    def add_fill(self, execution):
        self.fills.append(execution)

    def get_fill_price(self):
        nominator = sum(map(lambda f: f.size * f.price, self.fills))
        fill_price = nominator/self.get_filled_quantity()
        return fill_price

    def get_filled_quantity(self):
        return sum(map(lambda f: f.size, self.fills))

    def get_fills(self):
        return self.fills
