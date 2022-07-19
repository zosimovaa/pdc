"""
Модуль реализует преобращование ордербука по заданным уровням изменения курса.
Т.е. позволяет сократить количество уровней (курсов) в адресбуке.
"""
import numpy as np


class OrderbookResampled:
    TEMPL = "{:.8f}"

    def __init__(self, orderbook, levels=(0, 1, 2, 3, 5, 8, 13)):
        self.orderbook = orderbook
        self.levels = levels
        self.initialized = self.get_init_status()

    def get_init_status(self):
        asks = dict(self.orderbook.get("asks", []))
        bids = dict(self.orderbook.get("bids", []))

        vols_asks = np.array(list(map(float, asks.values())))
        vols_bids = np.array(list(map(float, bids.values())))

        if sum(vols_asks) and sum(vols_bids):
            return True
        else:
            return False

    def get_orderbook_resampled(self):
        asks = dict(self.orderbook["asks"])
        bids = dict(self.orderbook["bids"])

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

        for idx in np.arange(1, len(self.levels)):
            mask_ask = (keys_asks > lowest_ask * (1 + self.levels[idx - 1] / 100.)) & (
                    keys_asks <= lowest_ask * (1 + self.levels[idx] / 100.))
            value = np.round(sum(vols_asks[mask_ask]), 8)
            key = self.TEMPL.format(lowest_ask * (1 + self.levels[idx] / 100.))
            asks_resampled[key] = value

            mask_bid = (keys_bids < highest_bid * (1 - self.levels[idx - 1] / 100.)) & (
                    keys_bids >= highest_bid * (1 - self.levels[idx] / 100.))
            value = np.round(sum(vols_bids[mask_bid]), 8)
            key = self.TEMPL.format(highest_bid * (1 - self.levels[idx] / 100.))
            bids_resampled[key] = value

        return asks_resampled, bids_resampled

