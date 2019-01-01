import time
import unittest

from algoplex.api.simulator.market_data_sim import MarketDataSim
from algoplex.api.simulator.market_data_subscriber_mock import MarketDataSubscriberMock


class MarketDataSimTest(unittest.TestCase):

    def test_market_data_sim(self):
        mock_subscriber = MarketDataSubscriberMock()
        sim_md = MarketDataSim('sample_price_series.csv')
        sim_md.subscribe(mock_subscriber)
        time.sleep(1)
        self.assertTrue(mock_subscriber.get_data().__len__() > 0)
