from abc import ABCMeta, abstractmethod

class MarketData(metaclass=ABCMeta):

    @abstractmethod
    def subscribe(self, subscriber):
        pass

    @abstractmethod
    def unsubscribe(self, subscriber):
        pass
