import requests
from ast import literal_eval


class Share:
    base_url = 'https://api.iextrading.com/1.0/stock/{}/quote'

    def __init__(self, symbol):
        self.url = self.base_url.format(symbol)
        r = requests.get(self.url)
        if r.ok:
            self.data = literal_eval(r.text)
        else:
            raise ValueError('Request for URL {} failed.'.format(self.url))

    def get_price(self):
       return self.data['latestPrice']

    def get_prev_close(self):
        return self.data['previousClose']
