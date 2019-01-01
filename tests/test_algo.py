import unittest
from algoplex.api.simulator.exchange_access_sim import ExchangeAccessSim
from algoplex.api.simulator.market_data_sim_manual import MarketDataSimManual
from algoplex.api.simulator.algo_audit_sim import AlgoAuditSim
from algoplex.algo.wave import wave_algo

class WaveAlgoTest(unittest.TestCase):

    def test_profit_taking(self):

        sim_md = MarketDataSimManual(500000)
        ea = ExchangeAccessSim(sim_md)
        audit = AlgoAuditSim()

        qty    = 0.038
        drop   = 800
        bounce = 80
        profit = 500
        loss_cut    = 1200
        sleep_sec = 0

        n = 32
        for i in range(n):

            ea.clear_history()
            wa = wave_algo.WaveAlgo(sim_md, ea, audit, sleep_sec, qty, drop, bounce, profit, loss_cut)
            wa.start()

            sim_md.pick_and_publish_data_update(500000)
            sim_md.pick_and_publish_data_update(498000)
            sim_md.pick_and_publish_data_update(498080)
            sim_md.pick_and_publish_data_update(498200)

            # check that the Buy trade has happened at the expected price
            txns = ea.get_my_transactions()
            self.assertEqual(txns.__len__(), 1)
            buy_txn = txns[0]
            self.assertEqual(buy_txn.side, 'buy')
            self.assertEqual(buy_txn.size, qty)
            self.assertEqual(buy_txn.price, 498080.0)

            sim_md.pick_and_publish_data_update(499000)
            sim_md.pick_and_publish_data_update(500000)

            # check that Sell trade has happened at the expected price
            txns = ea.get_my_transactions()
            self.assertEqual(txns.__len__(), 2)
            buy_txn = txns[1]
            self.assertEqual(buy_txn.side, 'sell')
            self.assertEqual(buy_txn.size, qty)
            self.assertEqual(buy_txn.price, 499000.0)

            msgs = audit.get_messages()
            self.assertTrue(msgs.__len__() > 0)
            self.assertTrue(audit.contains_msg(".*Finished the cycle with a profit of 19.0 yen*"))


    def test_loss_cut(self):

        sim_md = MarketDataSimManual(500000)
        ea = ExchangeAccessSim(sim_md)
        audit = AlgoAuditSim()

        qty    = 0.038
        drop   = 800
        bounce = 80
        profit = 500
        loss_cut    = 1200
        sleep_sec = 0

        wa = wave_algo.WaveAlgo(sim_md, ea, audit, sleep_sec, qty, drop, bounce, profit, loss_cut)
        wa.start()

        sim_md.pick_and_publish_data_update(500000)
        sim_md.pick_and_publish_data_update(498000)

        # check that there are no buy fills at this point
        txns = ea.get_my_transactions()
        self.assertEqual(txns.__len__(), 0)

        # the following price move should activate stop-loss buy order
        sim_md.pick_and_publish_data_update(498080)

        # check that the Buy trade has happened at the expected price
        txns = ea.get_my_transactions()
        self.assertEqual(txns.__len__(), 1)
        buy_txn = txns[0]
        self.assertEqual(buy_txn.side, 'buy')
        self.assertEqual(buy_txn.size, qty)
        self.assertEqual(buy_txn.price, 498080.0)

        sim_md.pick_and_publish_data_update(497000)
        # check that no sell trade has happened yet
        txns = ea.get_my_transactions()
        self.assertEqual(txns.__len__(), 1)

        sim_md.pick_and_publish_data_update(495000)

        # check that a loss cut Sell trade has happened at the expected price
        txns = ea.get_my_transactions()
        self.assertEqual(txns.__len__(), 2)
        buy_txn = txns[1]
        self.assertEqual(buy_txn.side, 'sell')
        self.assertEqual(buy_txn.size, qty)
        self.assertEqual(buy_txn.price, 495000.0)

        self.assertTrue(audit.get_messages().__len__() > 0)
