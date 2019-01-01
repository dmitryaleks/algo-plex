#!/usr/bin/python3 -u

from algoplex.api import exchange_access
import os.path
import unittest

class APICheck(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(APICheck, self).__init__(*args, **kwargs)
        self.initialize()

    def initialize(self):
        with open(os.path.dirname(__file__) + '/../../../cfg/accessKey') as f:
            lines = f.readlines()
            firstLine = lines[0]
            access_key = (firstLine.split('APIKey: ')[1]).strip()
            secondLine = lines[1]
            access_secret = (secondLine.split('APISecret: ')[1]).strip()
        self.exch_access = exchange_access.ExchangeAccess(access_key, access_secret)

    def test_get_my_transaction(self):

        ord_txns = self.exch_access.get_my_transactions()
        print('Transactions: {}'.format(ord_txns))
        self.assertTrue(ord_txns.__len__() > 0)

    def test_stop_loss_order_entry(self):

        price           = 800000
        size            = 0.005
        stop_loss_price = 778000
        side            = 'buy'
        pair            = 'btc_jpy'

        ord_ids = self.exch_access.get_unsettled_orders()
        print("Number of outstanding orders before cancellation: {}".format(ord_ids.__len__()))
        self.assertTrue(ord_ids.__len__() == 0)

        self.exch_access.enter_stop_loss_order(price, size, stop_loss_price, side, pair)
        ord_ids = self.exch_access.get_unsettled_orders()

        self.assertTrue(ord_ids.__len__() > 0)
        print('Entered order: {}'.format(ord_ids))

        # TODO fetch order details and check that stop loss price is correct

        for ord_id in ord_ids:
            self.exch_access.delete_order(ord_id)
        ord_ids = self.exch_access.get_unsettled_orders()
        print("Number of outstanding orders after cancellation: {}".format(ord_ids.__len__()))
        self.assertTrue(ord_ids.__len__() == 0)

if __name__ == '__main__':
    unittest.main()
