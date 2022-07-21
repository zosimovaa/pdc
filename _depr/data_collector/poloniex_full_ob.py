import time
import logging
import numpy as np

from poloniex import PublicAPI, PublicAPIError

logger = logging.getLogger(__name__)


class PoloniexDataCollectorFullOb(PublicAPI):
    def __init__(self):
        PublicAPI.__init__(self)
        self.orderbook = []
        self.last_update = int(time.time())

    def get_data(self):
        self.orderbook = self.get_orderbook('all', 99)
        self.last_update = int(time.time())

        data = []
        for key in self.orderbook:
            asks = dict(self.orderbook[key]["asks"])
            bids = dict(self.orderbook[key]["bids"])

            if len(asks.keys()) and len(bids.keys()):

                is_frozen = bool(int(self.orderbook[key]["isFrozen"]))
                post_only = bool(int(self.orderbook[key]["postOnly"]))

                lowest_ask = min(np.array(list(map(float, asks.keys()))))
                highest_bid = max(np.array(list(map(float, bids.keys()))))

                record = [self.last_update, key, lowest_ask, highest_bid, asks, bids, is_frozen, post_only]
                data.append(record)

        return data
