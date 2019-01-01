#!/usr/bin/python3 -u

from algoplex.api.exchange_access_bfl import ExchangeAccessBFL
from algoplex.api.order import Order
import os.path
import unittest
import time

class BFLAPICheck(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BFLAPICheck, self).__init__(*args, **kwargs)
        self.initialize()

    def initialize(self):
        with open(os.path.dirname(__file__) + '/../../../cfg/accessKeyBFL') as f:
            lines = f.readlines()
            firstLine = lines[0]
            access_key = (firstLine.split('APIKey: ')[1]).strip()
            secondLine = lines[1]
            access_secret = (secondLine.split('APISecret: ')[1]).strip()
        self.exch_access = ExchangeAccessBFL(access_key, access_secret)

    def test_get_positions(self):
        self.exch_access.get_positions('BTC_JPY')

    def test_enter_order(self):

        price_safety_offset = 100000.0

        # pick a safe price form the market data API
        mock_subscriber = MarketDataSubscriberMock.MarketDataSubscriberMock()
        md = MarketDataBFL(1)
        md.subscribe(mock_subscriber)
        time.sleep(8)
        tick_num = mock_subscriber.get_data().__len__()
        self.assertTrue(tick_num > 0)
        last_trade_price = mock_subscriber.get_data()[tick_num - 1]

        safe_buy_price = last_trade_price - price_safety_offset
        size = 0.001
        order_id = self.exch_access.enter_stop_loss_order(safe_buy_price, size, 0, 'BUY', 'BTC_JPY')
        self.assertNotEqual(order_id, '')
        orders = self.exch_access.get_unsettled_orders()
        print('Orders: {}'.format(orders))
        time.sleep(10)
        is_cancelled = self.exch_access.delete_order(order_id)
        self.assertEqual(is_cancelled, True)
        res = self.exch_access.delete_all_orders()
        self.assertEqual(res, True)

        # this should stop the market data watcher
        md.unsubscribe(mock_subscriber)

        # an extra safety net - cancel all outstanding orders
        res = self.exch_access.delete_all_orders()
        self.assertEqual(res, True)

    def test_delete_all_orders(self):
        res = self.exch_access.delete_all_orders()
        self.assertEqual(res, True)

    def test_get_unsettled_orders(self):
        orders = self.exch_access.get_unsettled_orders()
        print('Orders: {}'.format(orders))
        self.assertTrue(orders.__len__() == 0)

    def test_get_executions_for_an_order(self):
        order = Order('BUY', 'BTC_JPY', 0.001, 800000, 800000, 'JOR20171116-083635-534813')
        fills = self.exch_access.get_fills_for_order(order)
        print('Fills: {}'.format(fills))
        self.assertTrue(fills.__len__() == 1)
        self.assertEqual(fills[0].price, 842999)

    def test_get_my_transactions(self):
        all_fills = self.exch_access.get_my_transactions()
        print('All fills: {}'.format(all_fills))
        self.assertTrue(all_fills.__len__() == 1)
        self.assertEqual(all_fills[0].price, 842999)


if __name__ == '__main__':
    unittest.main()
