from poloniex import PublicAPI, PublicAPIError
from poloniex import Ticker
import time
import logging


logger = logging.getLogger(__name__)


class HttpDataCollector(PublicAPI):
    def __init__(self):
        PublicAPI.__init__(self)
        self.tickers = dict()
        self.last_update = int(time.time())

    def _update(self):
        orderbook = self.get_orderbook('all', 99)
        self.last_update = int(time.time())

        for key in orderbook:
            if key not in self.tickers:
                self.tickers[key] = Ticker(key)
            self.tickers[key].update(orderbook[key])

        ticker_keys = self.tickers.keys()
        for key in ticker_keys:
            if key not in orderbook:
                del self.tickers[key]

    def get_data(self):
        ts = int(time.time())
        self._update()
        data = []
        for key in self.tickers:
            lowest_ask, highest_bid = self.tickers[key].get_prices()
            asks, bids = self.tickers[key].get_volumes()
            if lowest_ask and highest_bid:
                record = [ts, key, lowest_ask, highest_bid, asks, bids]
                data.append(record)
        return data
