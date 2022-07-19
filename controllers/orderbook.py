import time
import numpy as np

from poloniex import PublicAPI, PublicAPIError
from .orderbook_resampled import OrderbookResampled


class OrderbookController:
    TEMPL = "{:.8f}"
    LEVELS_DEFAULT = [0, 1, 2, 3, 5, 8, 13]
    QUERY = "insert into orderbook values"

    def __init__(self, db, config_manager):
        self.db = db
        self.config_manager = config_manager
        self.api = PublicAPI()

    def update(self, ticker, ts=None):
        if ts is None:
            ts = int(time.time())

        orderbook = self.api.get_orderbook(ticker, 99)
        db_data = self._make_db_data(ts, ticker, orderbook)




    def _make_db_data(self, ts, ticker, orderbook):
        data = []

        asks = dict(orderbook["asks"])
        bids = dict(orderbook["bids"])

        if len(asks.keys()) and len(bids.keys()):
            asks_resampled, bids_resampled = self._resample_ob(asks, bids)

            is_frozen = bool(int(orderbook["isFrozen"]))
            post_only = bool(int(orderbook["postOnly"]))

            lowest_ask = min(np.array(list(map(float, asks.keys()))))
            highest_bid = max(np.array(list(map(float, bids.keys()))))

            record = [
                ts,
                ticker,
                lowest_ask,
                highest_bid,
                asks_resampled,
                bids_resampled,
                is_frozen,
                post_only
            ]
            data.append(record)

    def _resample_ob(self, asks, bids):
        keys_asks = np.array(list(map(float, asks.keys())))
        vols_asks = np.array(list(map(float, asks.values())))
        keys_bids = np.array(list(map(float, bids.keys())))
        vols_bids = np.array(list(map(float, bids.values())))

        lowest_ask = min(keys_asks)
        highest_bid = max(keys_bids)

        asks_resampled = dict()
        key = self.TEMPL.format(lowest_ask)
        asks_resampled[key] = asks[key]

        bids_resampled = dict()
        key = self.TEMPL.format(highest_bid)
        bids_resampled[key] = bids[key]

        config = self.config_manager.get_config().get("orderbook", dict())
        levels = config.get("levels", self.LEVELS_DEFAULT)

        for idx in np.arange(1, len(levels)):
            mask_ask = (keys_asks > lowest_ask * (1 + levels[idx - 1] / 100.)) & (
                    keys_asks <= lowest_ask * (1 + levels[idx] / 100.))
            value = np.round(sum(vols_asks[mask_ask]), 8)
            key = self.TEMPL.format(lowest_ask * (1 + levels[idx] / 100.))
            asks_resampled[key] = value

            mask_bid = (keys_bids < highest_bid * (1 - levels[idx - 1] / 100.)) & (
                    keys_bids >= highest_bid * (1 - levels[idx] / 100.))
            value = np.round(sum(vols_bids[mask_bid]), 8)
            key = self.TEMPL.format(highest_bid * (1 - levels[idx] / 100.))
            bids_resampled[key] = value

        return asks_resampled, bids_resampled



