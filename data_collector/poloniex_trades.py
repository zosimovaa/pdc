import time
import logging
import numpy as np

from poloniex import PublicAPI, PublicAPIError

logger = logging.getLogger(__name__)


class PoloniexDataCollectorTrades(PublicAPI):
    TEMPL = "{:.8f}"

    def __init__(self, config_manager):
        PublicAPI.__init__(self)
        self.orderbook = []
        self.last_update = int(time.time())
        self.config_manager = config_manager

    def get_orderbook_data(self):
        self.orderbook = self.get_orderbook('all', 99)
        self.last_update = int(time.time())

        data = []
        for key in self.orderbook:
            asks = dict(self.orderbook[key]["asks"])
            bids = dict(self.orderbook[key]["bids"])

            if len(asks.keys()) and len(bids.keys()):
                asks_resampled, bids_resampled = self._resample_ob(asks, bids)

                is_frozen = bool(int(self.orderbook[key]["isFrozen"]))
                post_only = bool(int(self.orderbook[key]["postOnly"]))

                lowest_ask = min(np.array(list(map(float, asks.keys()))))
                highest_bid = max(np.array(list(map(float, bids.keys()))))

                record = [
                    self.last_update,
                    key,
                    lowest_ask,
                    highest_bid,
                    asks_resampled,
                    bids_resampled,
                    is_frozen,
                    post_only
                ]
                data.append(record)

        return data

    def get_history_data(self):
        pass






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

        runtime_config = self.config_manager.get_config().get("runtime", dict())
        levels = runtime_config.get("levels", [0, 1, 2, 3, 5, 8, 13])

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
