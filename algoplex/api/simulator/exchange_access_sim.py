from algoplex.api.common.exchange_access import ExchangeAccess
from algoplex.api.common.maket_data_subscriber import MarketDataSubscriber
from algoplex.api.order import Order
from algoplex.api.execution import Execution
import time

class ExchangeAccessSim(ExchangeAccess, MarketDataSubscriber):

    def __init__(self, market_data):
        self.market_data = market_data
        self.stop_loss_orders = []
        self.orders = []
        self.transactions = []
        self.last_trade_price = None
        market_data.subscribe(self)

    def update(self, price):
        self.last_trade_price = price

        # promote eligible stop loss orders to regular orders
        self.__promote_stop_loss_orders()

        # generate a fill if price is suitable
        self.__do_matching(False)

    def on_data_end(self):
        pass

    def enter_order(self, rate, amount, order_type, pair):
        return self.enter_stop_loss_order(rate, amount, None, order_type, pair)

    def enter_stop_loss_order(self, rate, amount, stop_loss_rate, order_type, pair):
        order_id = self.__get_unique_id('ORD')
        ord = Order(order_type, pair, amount, rate, stop_loss_rate, order_id)

        if(stop_loss_rate != None):
            self.stop_loss_orders.append(ord)
        else:
            self.orders.append(ord)

        # promote eligible stop loss orders to regular orders
        self.__promote_stop_loss_orders()

        # generate a fill if price is suitable
        self.__do_matching(True)
        return order_id

    def delete_order(self, order_id):
        ord = next((x for x in self.orders if x.id == order_id), None)
        if(ord != None):
            self.orders.remove(ord)
        else:
            ord = next((x for x in self.stop_loss_ordersorders if x.id == order_id), None)
            if(ord != None):
                self.orders.remove(ord)
            else:
               raise Exception("Order not found: " + order_id)

    def delete_order_by_ref(self, ord):
        self.orders.remove(ord)

    def get_unsettled_orders(self):
        return list(map(lambda o: o.id, self.orders + self.stop_loss_orders))

    def get_my_transactions(self):
        return self.transactions

    def get_fills_for_order(self, order):
        pass

    def __get_unique_id(self, suffix):
        return str(int(time.time()*1000000000)) + suffix

    def __is_crossing_price(self, last_trade_price, order_price, side):
        if(last_trade_price == None):
            return False

        if(side == 'buy'):
            return last_trade_price <= order_price
        else:
            return last_trade_price >= order_price

    def __do_matching(self, is_order_price_change):
        for ord in self.orders:
            if(self.__is_crossing_price(self.last_trade_price, ord.price, ord.side)):
                exec_id = self.__get_unique_id('EXC')
                if(is_order_price_change):
                    exec_price = ord.price
                else:
                    exec_price = self.last_trade_price
                exec = Execution(exec_id, ord.id, ord.size, exec_price, ord.side)
                print('Adding new execution: {}'.format(is_order_price_change))
                self.transactions.append(exec)
                self.delete_order_by_ref(ord)

    def __promote_stop_loss_orders(self):
        for ord in self.stop_loss_orders:
            if(self.__is_crossing_price(self.last_trade_price, ord.stop_loss_price, ord.size)):
                self.stop_loss_orders.remove(ord)
                self.orders.append(ord)
                self.__do_matching(True)

    def clear_history(self):
        self.orders[:] = []
        self.stop_loss_orders[:] = []
        self.transactions[:] = []
        self.last_trade_price = None

