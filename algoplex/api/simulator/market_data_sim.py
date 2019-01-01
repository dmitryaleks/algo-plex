from algoplex.api.common.market_data import MarketData
import threading
import os
import time

class MarketDataSim(MarketData):

    def __init__(self, market_data_file):
        self.market_data_file = market_data_file
        self.subscribers = []
        self.subscribed = False
        self.watcher = None
        self.last_trade_price = None
        self.watcher = None
        self.active = False
        self.prices = []
        full_path = os.path.dirname(__file__) + '/../../data/' + self.market_data_file
        with open(full_path) as f:
            lines = f.readlines()
            for line in lines:
                (time, price) = line.split(',')
                self.prices.append(float(price))
        self.cursor = 0

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        if(self.subscribers.__len__() > 0 and not self.subscribed):
            self.start_subscription()

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)
        if(self.subscribers.__len__() == 0):
            self.active = False

    def start_subscription(self):
        self.active = True
        self.watcher = threading.Thread(target=self.watch_market_data)
        self.watcher.start()
        #self.watcher.join()

    def watch_market_data(self):
        try:
            while self.active:
                new_trade_price = float(self.get_last_price())
                if(new_trade_price != self.last_trade_price
                   and new_trade_price != None):
                    self.last_trade_price = new_trade_price
                    for subscriber in self.subscribers:
                        subscriber.update(new_trade_price)
                    time.sleep(0.1)
        except Exception as e:
            for subscriber in self.subscribers:
                subscriber.on_data_end()

    def get_last_price(self):
        if(self.cursor < self.prices.__len__()):
            price = self.prices[self.cursor]
            self.cursor += 1
            return price
        else:
            raise Exception("No more data")



