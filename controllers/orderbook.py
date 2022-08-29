import time
import logging
import numpy as np

from .abstract import AbstractSymbolHandler
from poloniex_api import PublicApiV2, PublicApiError

logger = logging.getLogger(__name__)


class OrderbookHandler(AbstractSymbolHandler):
    DATA_INSERT_QUERY = "INSERT INTO orderbook VALUES"
    GET_MAX_TS_QUERY = "SELECT MAX(ts) FROM orderbook WHERE symbol=%(symbol)s"

    CHECK_MAX_TS = False

    DIVIDER = 1000
    LEVELS_DEFAULT = [0, 1, 2, 3, 5, 8, 13]
    TEMPL = "{:.12f}"

    def __init__(self, symbol, conn, levels=(0, 1, 2, 3, 5, 8, 13)):
        super().__init__(symbol, conn)
        self.api = PublicApiV2()
        self.levels = levels

    def _get_data(self):
        """Получение данных биржи"""
        asks, bids = self.api.get_orderbook(self.symbol, scale=-1, limit=150)
        return asks, bids

    def _transform_data(self, data):
        """Преобразование данных для записи в БД"""
        asks, bids = data
        if len(asks) and len(bids):
            lowest_ask = min(map(float, asks.keys()))
            highest_bid = max(map(float, bids.keys()))

            record = [
                self.symbol,
                self.ts,
                lowest_ask,
                highest_bid,
                asks,
                bids
            ]
            data = [record]
        else:
            data = []
        return data
