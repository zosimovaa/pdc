import time
import logging
from poloniex import PublicAPI, PublicAPIError
from basic_application import BasicApplication

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
        data_length_total = 0

        config = self.config_manager.get_config().get("trades", dict())

        if ts is None:
            ts = int(time.time())

        last_update = self.last_updates.get(ticker, 0)
        logger.debug("[{0}] Local last update: {1}".format(ticker, last_update))
        if not last_update:
            last_update = self._get_max_ts(ticker)
            logger.debug("[{0}] DB last update: {1}".format(ticker, last_update))


        ts_end = ts
        ts_start = max(last_update, ts_end - config.get("depth", self.DEPTH_DEFAULT))

        logger.debug("[{0}] download period: {1} - {2}. Depth: {3}".format(ticker, ts_start, ts_end, ts_end-ts_start) )
        try:
            for batch in self.api.get_trade_history_batch(ticker, ts_start, ts_end):
                data = self._make_db_data(ticker, batch)
                if len(data):
                    self.conn.cursor.executemany(self.PUT_DATA_QUERY, data)
                    data_length = self.conn.cursor.rowcount
                    data_length_total += data_length
                    logger.info("{0}: {1} records was written into db".format(ticker, data_length))
                else:
                    logger.info("{0}: No data to write".format(ticker))
            self.last_updates[ticker] = ts_end

        except PublicAPIError as e:
            logger.error("{0}: Data request error: {1}".format(ticker, e))
        return data_length_total

    def _get_max_ts(self, ticker):
        params = {"pair": ticker}
        self.conn.cursor.execute(self.GET_MAX_TS_QUERY, parameters=params)
        raw_data = self.conn.cursor.fetchall()
        max_ts = raw_data[0][0]
        logger.debug("{0} max ts in db: {1}".format(ticker, max_ts))
        return max_ts

    def _make_db_data(self, ticker, trades):
        data = []

        for trade in trades:
            order_number = self._convert(trade.get("orderNumber", 0))
            g_trade_id = self._convert(trade.get("globalTradeID", 0))
            trade_id = self._convert(trade.get("tradeID", 0))

            if order_number is not None:
                order_number

            record = [
                self.api.date_to_unix_ts_in_utc(trade.get("date")),
                ticker,
                trade.get("type", "No_info"),
                float(trade.get("rate", 0.)),
                float(trade.get("amount", 0.)),
                float(trade.get("total", 0.)),
                order_number,
                g_trade_id,
                trade_id
            ]
            data.append(record)
        return data

    @staticmethod
    def _convert(value):
        try:
            converted = int(value)
        except Exception:
            converted = 0
        return converted



