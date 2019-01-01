from abc import ABCMeta, abstractmethod

class MarketDataSubscriber(metaclass=ABCMeta):

    @abstractmethod
    def update(self, price):
        pass

    @abstractmethod
    def on_data_end(self):
        pass

