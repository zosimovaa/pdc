import time
import logging
from poloniex import PublicAPI, PublicAPIError


logger = logging.getLogger(__name__)


class TradeHistoryController:
    DEPTH_DEFAULT = 86400
    PUT_DATA_QUERY = "insert into trades values"
    GET_MAX_TS_QUERY = "select max(ts) from trades where pair=%(pair)s"

    def __init__(self, conn, config_manager):
        self.conn = conn
        self.config_manager = config_manager
        self.api = PublicAPI()
        self.last_updates = dict()

    def update(self, ticker, ts=None):
        config = self.config_manager.get_config().get("trades", dict())

        if ts is None:
            ts = int(time.time())

        last_update = self.last_updates.get(ticker, 0)
        if not last_update:
            last_update = self._get_max_ts(ticker)

        ts_end = ts
        ts_start = max(last_update, ts_end - config.get("depth", self.DEPTH_DEFAULT))

        try:
            for batch in self.api.get_trade_history_batch(ticker, ts_start, ts_end):
                data = self._make_db_data(ticker, batch)
                if len(data):
                    self.conn.cursor.executemany(self.PUT_DATA_QUERY, data)
                    data_length = self.conn.cursor.rowcount
                    logger.info("{0}: {1} records was written into db".format(ticker, data_length))
                else:
                    logger.info("{0}: No data to write".format(ticker))

            self.last_updates[ticker] = ts_end

        except PublicAPIError as e:
            logger.info("{0}: Data request error: {1}".format(ticker, e))

    def _get_max_ts(self, ticker):
        params = {"pair": ticker}
        self.conn.cursor.execute(self.GET_MAX_TS_QUERY, parameters=params)
        raw_data = self.conn.cursor.fetchall()
        max_ts = raw_data[0][0]
        return max_ts

    def _make_db_data(self, ticker, trades):
        data = []

        for trade in trades:
            record = [
                self.api.date_to_unix_ts_in_utc(trade.get("date")),
                ticker,
                trade.get("type", "No_info"),
                float(trade.get("rate", 0.)),
                float(trade.get("amount", 0.)),
                float(trade.get("total", 0.)),
                int(trade.get("orderNumber", 0)),
                int(trade.get("globalTradeID", 0)),
                int(trade.get("tradeID", 0))
            ]
            data.append(record)
        return data


