from abc import ABCMeta, abstractmethod

class ExchangeAccess(metaclass=ABCMeta):

    @abstractmethod
    def enter_order(self, rate, amount, order_type, pair):
        pass

    @abstractmethod
    def enter_stop_loss_order(self, rate, amount, stop_loss_rate, order_type, pair):
        pass

    @abstractmethod
    def delete_order(self, order_id):
        pass

    @abstractmethod
    def get_unsettled_orders(self):
        pass

    @abstractmethod
    def get_my_transactions(self):
        pass

    @abstractmethod
    def get_fills_for_order(self, order):
        pass
