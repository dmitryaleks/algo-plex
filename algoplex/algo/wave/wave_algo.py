#!/usr/bin/python3

from algoplex.api.common.maket_data_subscriber import MarketDataSubscriber
import time

class WaveAlgo(MarketDataSubscriber):

    def __init__(self, market_data, exchange_access, audit,
                 sleep_sec, max_order_qty, drop_trigger_delta_yen,
                 bounce_back_trigger_delta_yen,
                 profit_delta_yen, loss_cut_trigger_delta_yen):
        self.max_order_qty = max_order_qty
        self.drop_trigger_delta_yen = drop_trigger_delta_yen
        self.bounce_back_trigger_delta_yen = bounce_back_trigger_delta_yen
        self.profit_delta_yen = profit_delta_yen
        self.loss_cut_trigger_delta_yen = loss_cut_trigger_delta_yen
        self.safety_margin_yen = 20
        self.active = True
        self.arrival_price = None
        self.last_trade_price = None
        self.highest_price = None
        self.lowest_price = None
        self.bought_price = None
        self.sold_price = None
        self.drop_price_reached = False
        self.drop_price = None
        self.order_outstanding = False
        self.buying = False
        self.bought = False
        self.sold = False
        self.market_data = market_data
        self.buy_order_id = None
        self.sell_order_id = None
        self.selling = False
        self.cutting_the_loss = False
        self.exch_access = exchange_access
        self.audit = audit
        self.sleep_sec = sleep_sec

    def log(self, msg):
        self.audit.log(msg)

    def start(self):
        self.log('Starting Wave algo: max ordr {}, drop: {}, bounce: {}, profit: {}'.format(
           self.max_order_qty,
           self.drop_trigger_delta_yen,
           self.bounce_back_trigger_delta_yen,
           self.profit_delta_yen
        ))

        # safety check - there should be no unsettled orders at the start
        unsettled_ord_ids = self.exch_access.get_unsettled_orders()
        if(unsettled_ord_ids.__len__() > 0):
            self.log('Unsettled orders found - cancelling them:')
            for unsettled_ord_id in unsettled_ord_ids:
                self.log('Cancelling {}'.format(unsettled_ord_id))
                self.exch_access.delete_order(unsettled_ord_id)
            return
        else:
            self.log('No unsettled orders found. Starting the algo');

        self.arrival_price = self.market_data.get_last_price()
        self.highest_price = self.arrival_price
        self.lowest_price = self.arrival_price
        self.log('Arrival price: {}'.format(self.arrival_price))

        self.market_data.subscribe(self)

        # TODO: WaveAlgo should not hold the main thread when under test,
        #       but this needs to be addressed for the production usage
        #while(self.active):
        #    time.sleep(0.1)

    def on_data_end(self):
        # complete
        self.active = False

    def is_active(self):
        return self.active

    def update(self, last_trade_price):

        self.log('Last trade price update: {}'.format(last_trade_price))
        self.last_trade_price = last_trade_price

        if(self.last_trade_price < self.lowest_price):
            self.lowest_price = self.last_trade_price
            self.log('New lowest price: {}'.format(self.lowest_price))
        elif(self.last_trade_price > self.highest_price):
            self.highest_price = self.last_trade_price
            self.log('New highest price: {}'.format(self.highest_price))

        # see if price has dropped enough
        if((self.drop_price_reached == False and last_trade_price <= self.highest_price - self.drop_trigger_delta_yen or
           (self.drop_price_reached == True  and last_trade_price < self.drop_price))
           and not self.buying and not self.bought):

            self.log('Drop-price has been reached: {}'.format(self.last_trade_price))
            self.drop_price = self.last_trade_price
            self.drop_price_reached = True
            # NOTE: will send a stop loss buy order right away to minimize the risk of missing a chance to buy

        # see if it is time to enter a stop loss Buy order
        if(self.drop_price_reached == True
           #and last_trade_price >= self.drop_price + self.bounce_back_trigger_delta_yen
           #and last_trade_price < self.drop_price + self.bounce_back_trigger_delta_yen + self.profit_delta_yen - self.safety_margin_yen
           and not self.bought and not self.buying and not self.order_outstanding):
            target_price = self.drop_price + self.bounce_back_trigger_delta_yen
            stop_loss_price = target_price - 50
            self.log('Buying {}@{}, stop-loss-level: {}'.format(self.max_order_qty, target_price, stop_loss_price))
            self.buy_order_id = self.exch_access.enter_stop_loss_order(target_price, self.max_order_qty, stop_loss_price, 'buy', 'btc_jpy')
            # TODO fetch bought price via transactions API
            self.bought_price = self.last_trade_price
            if(self.buy_order_id != None):
                self.buying = True
                time.sleep(self.sleep_sec)

        # keep watching the buy order - need to either get a fill or cancel the order
        if(self.buying):
            # TODO check if order got filled: GET: /api/exchange/orders/opens
            # TODO if it has been more than 60 minutes since the sell order has been entered -
            #      change order to be market price to minimize the risk of keeping a position
            unsettled_ord_ids = self.exch_access.get_unsettled_orders()
            if(unsettled_ord_ids != None and
               not unsettled_ord_ids.__contains__(self.buy_order_id)):
                self.buying = False
                self.bought = True
                #TODO fetch the actual buy price
            else:
                self.log('Buy order is outstanding: {}'.format(unsettled_ord_ids))

        # progress report
        if(self.drop_price_reached == True):

            if(self.bought != True):
                self.log('LTP: {}, HIGH: {}, LOW: {}, DROPPED@{}, WILL BUY @{}'.format(
                    self.last_trade_price,
                    self.highest_price,
                    self.lowest_price,
                    self.drop_price,
                    self.drop_price + self.bounce_back_trigger_delta_yen))
            else:
                self.log('LTP: {}, HIGH: {}, LOW: {}, DROPPED@{}, BOUGHT @{}, WILL SELL @{}'.format(
                    self.last_trade_price,
                    self.highest_price,
                    self.lowest_price,
                    self.drop_price,
                    self.bought_price,
                    self.bought_price + self.bounce_back_trigger_delta_yen))
        else:
            self.log('LTP: {}, HIGH: {}, LOW: {}, DROP TARGET@{}'.format(
                self.last_trade_price,
                self.highest_price,
                self.lowest_price,
                self.highest_price - self.drop_trigger_delta_yen))


        # make profit
        if(self.bought and self.bought_price != None and not self.order_outstanding
           and not self.sold
           and not self.selling):
            sell_price = self.bought_price + self.profit_delta_yen
            self.log('Selling {}@{}'.format(self.max_order_qty, sell_price))
            # TODO: send a sell order
            self.sell_order_id = self.exch_access.enter_order(sell_price, self.max_order_qty, 'sell', 'btc_jpy')
            # TODO: after sell order got filled
            self.sold_price = sell_price
            if(self.sell_order_id != None):
                self.selling = True
                time.sleep(self.sleep_sec)

        # loss cut
        if(self.bought and self.bought_price != None and not self.order_outstanding
           and not self.sold
           and last_trade_price <= self.bought_price - self.loss_cut_trigger_delta_yen):

            unsettled_ord_ids = self.exch_access.get_unsettled_orders()
            if(unsettled_ord_ids.__len__() > 0):
                self.log('Unsettled orders found - cancelling them:')
                for unsettled_ord_id in unsettled_ord_ids:
                    self.log('Cancelling {}'.format(unsettled_ord_id))
                    self.exch_access.delete_order(unsettled_ord_id)

            self.log('Selling to cut losses {}@{}'.format(self.max_order_qty, self.last_trade_price))
            self.sell_order_id = self.exch_access.enter_order(self.last_trade_price, self.max_order_qty, 'sell', 'btc_jpy')
            self.sold_price = last_trade_price
            # TODO capture selling order entry time
            if(self.sell_order_id != None):
                self.selling = True
            self.cutting_the_loss = True

        # keep watching the sell order - need to close position one way or another
        if(self.selling):
            # TODO check if order got filled: GET: /api/exchange/orders/opens
            # TODO if it has been more than 60 minutes since the sell order has been entered -
            #      change order to be market price to minimize the risk of keeping a position
            unsettled_ord_ids = self.exch_access.get_unsettled_orders()
            if(unsettled_ord_ids != None and
               not unsettled_ord_ids.__contains__(self.sell_order_id)):
                self.selling = False
                self.sold = True
                # TODO fetch the actual sell price
            else:
                self.log('Sell order is outstanding: {}'.format(unsettled_ord_ids))

        if(self.bought and self.sold):
            self.log('Finished the cycle with a profit of {} yen'.format(self.max_order_qty*(self.sold_price - self.bought_price)))
            self.market_data.unsubscribe(self)
            self.active = False

        if(self.cutting_the_loss):
            self.log('Stopping the algo for now as there was a loss cut')
