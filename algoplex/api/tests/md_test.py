#!/usr/bin/python3 -u

import time
import unittest

from algoplex.api.market_data_bfl import MarketDataBFL
from algoplex.api.simulator import market_data_subscriber_mock


class APICheck(unittest.TestCase):

    def bfl_md_test(self):
        mock_subscriber = market_data_subscriber_mock.MarketDataSubscriberMock()
        md = MarketDataBFL(1)
        md.subscribe(mock_subscriber)
        time.sleep(10)
        self.assertTrue(mock_subscriber.get_data().__len__() > 0)
        print("Data: {}".format(mock_subscriber.get_data()))
        md.unsubscribe(mock_subscriber)

