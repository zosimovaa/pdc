import numpy as np
import datetime


class Ticker:
    LEVELS = [0.005, 0.01, 0.015, 0.02, 0.03, 0.05]

    def __init__(self, pair):
        self.pair = pair
        self.asks = dict()
        self.bids = dict()
        self.ts = None
        self.asks_vol_balance = np.zeros(len(self.LEVELS))
        self.bids_vol_balance = np.zeros(len(self.LEVELS))

    def update(self, message):
        self.asks = dict(message["asks"])
        self.bids = dict(message["bids"])
        self.ts = int(datetime.datetime.now().timestamp())

    def get_status(self):
        if len(self.asks) == 0 or len(self.bids) == 0:
            is_initialized = False
        else:
            is_initialized = True
        return is_initialized

    def get_volumes(self):
        status = self.get_status()
        if status:
            keys_asks = np.array(list(map(float, self.asks.keys())))
            vols_asks = np.array(list(map(float, self.asks.values())))
            keys_bids = np.array(list(map(float, self.bids.keys())))
            vols_bids = np.array(list(map(float, self.bids.values())))

            lowest_ask, highest_bid = self.get_prices()

            asks, bids = [], []

            for coef in self.LEVELS:
                mask_ask = keys_asks < lowest_ask * (1 + coef)
                asks.append(sum(vols_asks[mask_ask]))

                mask_bid = keys_bids > highest_bid * (1 - coef)
                bids.append(sum(vols_bids[mask_bid]))
        else:
            asks, bids = None, None

        return asks, bids

    def get_prices(self):
        status = self.get_status()
        if status:
            lowest_ask = np.min(np.array(list(map(float, self.asks.keys()))))
            highest_bid = np.max(np.array(list(map(float, self.bids.keys()))))
        else:
            lowest_ask, highest_bid = None, None
        return lowest_ask, highest_bid




