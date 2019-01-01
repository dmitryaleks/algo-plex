from algoplex.api.common.maket_data_subscriber import MarketDataSubscriber

class MarketDataSubscriberMock(MarketDataSubscriber):

    received_data = []
    is_ended = False

    def update(self, price):
        self.received_data.append(price)

    def on_data_end(self):
        self.is_ended = True

    def get_data(self):
        return self.received_data

    def get_is_ended(self):
        return self.is_ended
