from algoplex.api.common.market_data import MarketData

class MarketDataSimManual(MarketData):

    def __init__(self, initial_price):
        self.subscribers = []
        self.subscribed = False
        self.watcher = None
        self.last_trade_price = initial_price
        self.watcher = None
        self.active = False
        self.prices = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        if(self.subscribers.__len__() >1 and not self.subscribed):
            self.start_subscription()

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)
        if(self.subscribers.__len__() == 0):
            self.active = False

    def start_subscription(self):
        self.active = True

    def pick_and_publish_data_update(self, new_trade_price):
        try:
            if(new_trade_price != self.last_trade_price
               and new_trade_price != None):
                self.last_trade_price = new_trade_price
                for subscriber in self.subscribers:
                    subscriber.update(new_trade_price)
        except Exception as e:
            for subscriber in self.subscribers:
                subscriber.on_data_end()

    def complete(self):
        for subscriber in self.subscribers:
            subscriber.on_data_end()

    def get_last_price(self):
        if(self.last_trade_price != None):
            return self.last_trade_price
        else:
            print("No more data")
            raise Exception("No more data")
