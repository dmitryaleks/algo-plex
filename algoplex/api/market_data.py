from algoplex.api.common.market_data import MarketData
import threading
import time
import requests
import json

class MarketData(MarketData):

    api_url = 'https://coincheck.com/api/ticker'

    def __init__(self, poll_period_sec):
        self.poll_period_sec = poll_period_sec
        self.subscribers = []
        self.subscribed = False
        self.watcher = None
        self.last_trade_price = None
        self.watcher = None
        self.active = False

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        if(not self.subscribed):
            self.start_subscription()

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)
        if(self.subscribers.__len__() == 0):
            self.active = False


    def start_subscription(self):
        self.active = True
        self.watcher = threading.Thread(target=self.watch_market_data)
        self.watcher.start()

    def watch_market_data(self):
        while self.active:
            try:
                new_trade_price = self.get_last_price()
                if(new_trade_price != self.last_trade_price
                   and new_trade_price != None):
                    self.last_trade_price = new_trade_price
                    for subscriber in self.subscribers:
                        subscriber.update(new_trade_price)
            except requests.exceptions.ConnectionError:
                print('Connection refused')
            time.sleep(self.poll_period_sec)

    def get_last_price(self):
        try:
            response = requests.get(self.api_url)
            if(response.ok):
                js = json.loads(response.text)
                new_trade_price = float(js['last'])
                return new_trade_price
        except requests.exceptions.ConnectionError:
            print('MarketData: connection refused')
            return None
