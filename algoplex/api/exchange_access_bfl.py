import requests
import hashlib
import hmac
import time
import json
import urllib
from algoplex.api import execution

class ExchangeAccessBFL():

    base_api_url          = 'https://api.bitflyer.jp'
    unsettled_ord_api_url_endpoint = '/v1/me/getchildorders'
    enter_child_order_url_endpoint = '/v1/me/sendchildorder'
    get_positions_url_endpoint = '/v1/me/getpositions'

    def __init__(self, access_key, access_secret):
        self.access_key = access_key
        self.access_secret = access_secret

    def enter_order(self, rate, amount, order_type, pair):
        return self.enter_stop_loss_order(rate, amount, 'null', order_type, pair)

    def enter_stop_loss_order(self, price, size, stop_loss_rate, order_type, pair):

        body = {
            "product_code": "BTC_JPY",
            "child_order_type": "LIMIT",
            "side": order_type,
            "price": price,
            "size": size
        }

        msg = json.dumps(body)

        reply = self.make_request('POST', self.enter_child_order_url_endpoint, msg, None)
        print(reply.status_code, reply.reason)
        order_id = ''
        reply_data = reply.json()
        if(reply.ok):
            print('Order has been placed successfully')
            if('child_order_acceptance_id' in reply_data):
                order_id = reply_data['child_order_acceptance_id']
            # TODO fetch and return order ID
        else:
            print('Failed to place an order: ' + reply_data['error_message'])
        return order_id


    def delete_order(self, order_id):
        cancel_child_order = '/v1/me/cancelchildorder'

        body = {
            "product_code": "BTC_JPY",
            "child_order_acceptance_id": order_id
        }
        msg = json.dumps(body)

        reply = self.make_request('POST', cancel_child_order, msg, None)
        print(reply.status_code, reply.reason)
        if(reply.ok):
            print('Cancelled child order {}'.format(order_id))
            return True
        else:
            reply_data = reply.json()
            print('Failed to cancel child order {} due to {}'.
                  format(order_id, reply_data['error_message']))
            return False

    def delete_all_orders(self):
        cancel_all_child_orders_url_endpoint = '/v1/me/cancelallchildorders'

        body = {
            "product_code": "BTC_JPY"
        }
        msg = json.dumps(body)

        reply = self.make_request('POST', cancel_all_child_orders_url_endpoint, msg, None)
        print(reply.status_code, reply.reason)
        if(reply.ok):
            print('All outstanding child orders have been placed successfully')
            return True
        else:
            reply_data = reply.json()
            print('Failed to cancel outstanding child orders: ' + reply_data['error_message'])
            return False

    def get_positions(self, product):

        payload = { 'product_code': product }

        r = self.make_request('GET', self.get_positions_url_endpoint, "", payload)

        print(r.status_code, r.reason)
        print(r.text[:300] + '...')
        if(r.ok):
            print('Fetched positions successfully');
            js = json.loads(r.text)
            positions = []
            return positions
        else:
            print('Failed to get positions');
            return None

    def get_unsettled_orders(self):

        payload = { 'product_code': 'BTC_JPY', 'count': 100, 'before': 0, 'after': 0 }
        r = self.make_request('GET', self.unsettled_ord_api_url_endpoint, "", payload)

        print(r.status_code, r.reason)
        print(r.text[:300] + '...')
        if(r.ok):
            print('Fetched unsettled orders successfully');
            js = json.loads(r.text)
            order_ids = []
            for ord in js:
                order_id = ord['child_order_id']
                order_ids.append(order_id)
            # NOTE: returning empty list means there are no unsettled orders
            return order_ids
        else:
            print('Failed to get a list of unsettled orders');
            return None

    def get_my_transactions(self):
        list_executions_url_endpoint = '/v1/me/getexecutions'

        payload = { 'product_code': 'BTC_JPY', 'count': 100, 'before': 0, 'after': 0 }
        r = self.make_request('GET', list_executions_url_endpoint, "", payload)

        print(r.status_code, r.reason)
        print(r.text[:300] + '...')
        if(r.ok):
            print('Fetched executions')
            js = json.loads(r.text)
            executions = []
            for exec in js:
                exec_id = exec['id']
                side = exec['side']
                order_id = exec['child_order_id']
                size = exec['size']
                rate = exec['price']
                exec = execution.Execution(exec_id, order_id, size, rate, side)
                executions.append(exec)
            return executions
        else:
            print('Failed to get a list of executions');
            return None

    def get_fills_for_order(self, order):
        list_executions_url_endpoint = '/v1/me/getexecutions'

        payload = { 'product_code': 'BTC_JPY', 'count': 100, 'before': 0, 'after': 0, 'child_order_id': order.id }
        r = self.make_request('GET', list_executions_url_endpoint, "", payload)

        print(r.status_code, r.reason)
        print(r.text[:300] + '...')
        if(r.ok):
            print('Fetched executions')
            js = json.loads(r.text)
            executions = []
            for exec in js:
                exec_id = exec['id']
                side = exec['side']
                order_id = exec['child_order_id']
                size = exec['size']
                rate = exec['price']
                exec = execution.Execution(exec_id, order_id, size, rate, side)
                executions.append(exec)
            return executions
        else:
            print('Failed to get a list of executions');
            return None


    def make_request(self, req_type, endpoint, body, payload):

        time_now = str(time.time())

        if(req_type == 'GET' and payload):
            body = '?' + urllib.parse.urlencode(payload)

        text = str.encode(time_now + req_type + endpoint + body)

        sig = hmac.new(self.access_secret.encode('utf-8'),
                       text,
                       hashlib.sha256).hexdigest()

        headers = {'ACCESS-KEY': self.access_key, 'ACCESS-TIMESTAMP': time_now,
                   'ACCESS-SIGN': sig, 'Content-Type': 'application/json'}

        if(req_type == 'GET'):
            return requests.get(self.base_api_url + endpoint,
                                headers = headers, params=payload)
        elif(req_type == 'POST'):
            return requests.post(self.base_api_url + endpoint,
                                 headers = headers, data = body)
        else:
            raise Exception('Unknown request type: ' + req_type)
