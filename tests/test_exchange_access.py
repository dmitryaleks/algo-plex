import unittest
from algoplex.api.simulator.exchange_access_sim import ExchangeAccessSim
from algoplex.api.simulator.market_data_sim import MarketDataSim
import time

class ExchangeAccessTest(unittest.TestCase):

    def test_order_entry(self):
        sim_md = MarketDataSim('sample_price_series.csv')
        ea = ExchangeAccessSim(sim_md)
        order_id = ea.enter_order(480000, 0.05, 'buy', 'jpy_btc')
        my_unsettled_orders = ea.get_unsettled_orders()
        self.assertTrue(my_unsettled_orders.__contains__(order_id))

    def test_order_fill(self):
        sim_md = MarketDataSim('sample_price_series.csv')
        ea = ExchangeAccessSim(sim_md)
        order_id = ea.enter_order(498430, 0.05, 'buy', 'jpy_btc')
        time.sleep(3)
        trnscs = ea.get_my_transactions()
        [print(txn.order_id) for txn in trnscs]
        my_txn = list(filter(lambda txn: txn.order_id == order_id, trnscs))
        self.assertTrue(my_txn.__len__() == 1)
        self.assertTrue(ea.get_unsettled_orders().__len__() == 0)
