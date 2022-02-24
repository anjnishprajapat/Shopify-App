import time
import hashlib
import hmac
import requests
import json

class RestGate():
    
    def __init__(self, key, secret):
        self.host = "https://fx-api-testnet.gateio.ws"
        self.prefix = "/api/v4"
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.key = key          # api_key
        self.secret = secret   # api_secret


    def gen_sign(self,method, url, query_string=None, payload_string=None):
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(self.secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': self.key, 'Timestamp': str(t), 'SIGN': sign}


    def ticker_price(self,contract):
        url = '/futures/usdt/order_book'
        query_param = 'contract={}'.format(contract)
        r = requests.request('GET', self.host + self.prefix + url + "?" + query_param, headers=self.headers)
        return r.json()


    def position_size(self,contract):
        url = '/futures/usdt/positions/{}'.format(contract)
        query_param = ''

        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = self.gen_sign('GET', self.prefix + url, query_param)
        self.headers.update(sign_headers)
        r = requests.request('GET', self.host + self.prefix + url, headers=self.headers)
        # print(r.json())
        return r.json()

    
    def future_orders(self,contract,status):
        url = '/futures/usdt/orders'
        query_param = 'contract={0}&status={1}'.format(contract,status)

        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = self.gen_sign('GET', self.prefix + url, query_param)
        self.headers.update(sign_headers)
        r = requests.request('GET',self.host + self.prefix + url + "?" + query_param, headers=self.headers)
        return r.json()


    def currency_pair(self,contract):
        # url = '/spot/currency_pairs/{}'.format(contract)
        # query_param = ''
        # r = requests.request('GET', self.host + self.prefix + url, headers=self.headers)
        # return (r.json())
        d = {'id': 'BTC_USDT', 'base': 'BTC', 'quote': 'USDT', 'fee': '0.2', 'min_base_amount': '0.0001', 'min_quote_amount': '1', 'amount_precision': 4, 'precision': 2, 'trade_status': 'tradable', 'sell_start': 0, 'buy_start': 0}
        return d


    def open_limit_order(self,contract, size, price, reduce_only): #contract,size,price,reuce_only
        url = '/futures/usdt/orders'
        query_param = ''

        body={"contract":contract,"size":size,"price":price,"reduce_only":reduce_only}
        body = json.dumps(body)

        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = self.gen_sign('POST', self.prefix + url, query_param, body)
        self.headers.update(sign_headers)
        r = requests.request('POST', self.host + self.prefix + url, headers=self.headers, data=body)
        
        return r.json()


    def update_order(self, order_id, size, price):
        #cancel existing order.
        data =  self.cancel_limit_order(order_id)

        if data['is_reduce_only'] == False:
            reduce_only = 'false'
        else:
            reduce_only = 'true'

        if data['size'] < 0:
            size = -size
        #create new order.
        update_data =self.open_limit_order(data['contract'], size, price, reduce_only)
        
        return update_data


    def cancel_limit_order(self,order_id):
        url = '/futures/usdt/orders/{}'.format(order_id)
        query_param = ''
        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = self.gen_sign('DELETE', self.prefix + url, query_param)
        self.headers.update(sign_headers)
        r = requests.request('DELETE', self.host + self.prefix + url, headers=self.headers)
        return r.json()
    

    def cancel_all(self,contract):
        url = '/futures/usdt/orders'
        query_param = 'contract={}'.format(contract)
        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = self.gen_sign('DELETE', self.prefix + url, query_param)
        self.headers.update(sign_headers)
        r = requests.request('DELETE', self.host + self.prefix + url + "?" + query_param, headers=self.headers)



