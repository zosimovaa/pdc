import time
import logging
import pandas as pd
from .abstract import AbstractSymbolHandler
from poloniex_api import PublicApiV2, PublicApiError

logger = logging.getLogger(__name__)


class TradeHandler(AbstractSymbolHandler):
    DATA_INSERT_QUERY = "INSERT INTO trades VALUES"
    GET_MAX_TS_QUERY = "SELECT MAX(ts) FROM trades WHERE symbol=%(symbol)s"

    LIMIT = 100
    LIMIT_MAX = 1000
    COLUMNS = ["symbol", "ts", "takerSide", "price", "quantity", "amount", "id"]

    def __init__(self, symbol, conn):
        super().__init__(symbol, conn)
        self.api = PublicApiV2()

    def _get_data(self):
        """
        Получение данных об объемах с биржи
        """
        if not self.last_update:
            self.last_update = self._get_last_update_from_db()

        ts = int(time.time())
        if ts - self.last_update > 300:
            limit = self.LIMIT_MAX
        else:
            limit = self.LIMIT
        data = self.api.get_trades(self.symbol, limit=limit)

        df = pd.DataFrame(data)
        df["price"] = df["price"].astype(float)
        df["quantity"] = df["quantity"].astype(float)
        df["amount"] = df["amount"].astype(float)
        df["ts"] = df["ts"].astype(int) / 1000
        df["ts"] = df["ts"].astype(int)
        df["createTime"] = df["createTime"].astype(int)
        df["symbol"] = self.symbol

        df = df[df["ts"] > self.last_update]
        df = df.reindex(columns=self.COLUMNS)
        if len(df):
            self.last_update = df["ts"].max()
        return df

    def _transform_data(self, df):
        return list(df.values)
