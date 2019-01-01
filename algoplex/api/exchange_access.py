import requests
import hashlib
import hmac
import time
import json
from algoplex.api import execution

class ExchangeAccess():

    base_api_url          = 'https://coincheck.com/api/exchange'
    order_api_url         = base_api_url + '/orders'
    ord_txn_api_url       = base_api_url + '/orders/transactions'
    unsettled_ord_api_url = base_api_url + '/orders/opens'

    def __init__(self, access_key, access_secret):
        self.access_key = access_key
        self.access_secret = access_secret

    def enter_order(self, rate, amount, order_type, pair):
        return self.enter_stop_loss_order(rate, amount, 'null', order_type, pair)

    def enter_stop_loss_order(self, rate, amount, stop_loss_rate, order_type, pair):

        nonce =  str(int(time.time()*1000000000))
        body = { 'rate': rate, 'amount': amount, 'stop_loss_rate': stop_loss_rate,
                 'order_type': order_type, 'pair': pair }
        body = 'rate={rate}&amount={amount}&stop_loss_rate={stop_loss_rate}&' \
               'order_type={order_type}&pair={pair}'.format(**body)
        msg = nonce + self.order_api_url + body
        sig = hmac.new(self.access_secret.encode('utf-8'),
                       msg.encode('utf-8'),
                       hashlib.sha256).hexdigest()
        headers = {'ACCESS-KEY': self.access_key, 'ACCESS-NONCE': nonce, 'ACCESS-SIGNATURE': sig}
        r = requests.post(self.order_api_url, headers=headers, data=body)
        id = None
        if(r.ok):
            print("Order has been placed successfully")
            js = json.loads(r.text)
            id = int(js['id'])
        else:
            print("Failed to place an order")
        print(r.status_code, r.reason)
        print(r.text[:800] + '...')
        return id

    def delete_order(self, order_id):

        cancel_url = '{}/{}'.format(self.order_api_url, order_id)
        nonce =  str(int(time.time()*1000000000))
        msg = nonce + cancel_url
        sig = hmac.new(self.access_secret.encode('utf-8'),
                       msg.encode('utf-8'),
                       hashlib.sha256).hexdigest()
        headers = {'ACCESS-KEY': self.access_key, 'ACCESS-NONCE': nonce, 'ACCESS-SIGNATURE': sig}

        r = requests.delete(cancel_url, headers = headers)
        print(r.status_code, r.reason)
        print(r.text[:300] + '...')
        if(r.ok):
            print("Order has been cancelled successfully")
            js = json.loads(r.text)
            success = js['success']
            print('Success: {}'.format(success))
            return True
        else:
            print("Failed to cancel an order")
            return False

    def get_unsettled_orders(self):

        nonce =  str(int(time.time()*1000000000))
        msg = nonce + self.unsettled_ord_api_url
        sig = hmac.new(self.access_secret.encode('utf-8'),
                       msg.encode('utf-8'),
                       hashlib.sha256).hexdigest()
        headers = {'ACCESS-KEY': self.access_key, 'ACCESS-NONCE': nonce, 'ACCESS-SIGNATURE': sig}

        r = requests.get(self.unsettled_ord_api_url, headers = headers)
        print(r.status_code, r.reason)
        print(r.text[:300] + '...')
        if(r.ok):
            print('Fetched unsettled orders successfully');
            js = json.loads(r.text)
            success = js['success']
            print('Success: {}'.format(success))
            orders = js['orders']
            order_ids = []
            for order in orders:
                order_id = order['id']
                order_ids.append(order_id)
            # NOTE: returning empty list means there are no unsettled orders
            return order_ids
        else:
            print('Failed to get a list of unsettled orders');
            return None


    def get_my_transactions(self):

        nonce =  str(int(time.time()*1000000000))
        msg = nonce + self.ord_txn_api_url
        sig = hmac.new(self.access_secret.encode('utf-8'),
                       msg.encode('utf-8'),
                       hashlib.sha256).hexdigest()
        headers = {'ACCESS-KEY': self.access_key, 'ACCESS-NONCE': nonce, 'ACCESS-SIGNATURE': sig}

        r = requests.get(self.ord_txn_api_url, headers = headers)
        print(r.status_code, r.reason)
        print(r.text[:300] + '...')
        if(r.ok):
            print('Fetched unsettled orders successfully');
            js = json.loads(r.text)
            success = js['success']
            print('Success: {}'.format(success))
            ord_txns = js['transactions']
            txns = []
            for txn in ord_txns:
                exec_id  = txn['id']
                order_id = txn['order_id']
                size     = abs(float(txn['funds']['btc']))
                rate     = float(txn['rate'])
                side     = txn['side']
                exec = execution.Execution(exec_id, order_id, size, rate, side)
                txns.append(exec)
            # NOTE: returning empty list means there are no recorded transactions
            return txns
        else:
            print('Failed to get a list of transactions');
            return None

    def get_fills_for_order(self, order):
        all_fills = self.get_my_transactions()
        order_fills = list(filter(lambda f: f.order_id == int(order.id), all_fills))
        for fill in order_fills:
            order.add_fill(fill)
