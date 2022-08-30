import time
import datetime
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class AbstractSymbolHandler:
    DATA_INSERT_QUERY = "INSERT INTO table_name VALUES"
    GET_MAX_TS_QUERY = "SELECT MAX(ts) FROM table_name WHERE symbol=%(symbol)s"

    def __init__(self, symbol, conn):
        self.symbol = symbol
        self.conn = conn
        self.last_update = 0
        self.ts = 0

    def update(self):
        self.ts = int(time.time())
        logger.debug("Update for {0} symbol at {1} ts".format(self.symbol, self.unix_ts_to_date(self.ts)))
        # step 1 - get data from stock
        df = self._get_data()
        # step 2 - format data
        data = self._transform_data(df)
        # step 3 - sava data
        records = self._store_data(data)
        return records

    def _get_data(self):
        return pd.DataFrame()

    def _transform_data(self, df):
        return list()

    def _store_data(self, data):
        row_count = 0
        if len(data):
            try:
                self.conn.cursor.executemany(self.DATA_INSERT_QUERY, data)
            except Exception as e:
                logger.error(str(e))
                logger.error(data[:5])
                raise Exception("DB connect error") from e
            else:
                self.last_update = self.ts
                row_count = self.conn.cursor.rowcount
                logger.info("{0}: {1} records was written into db".format(self.symbol, row_count))

        else:
            logger.info("{0}: No data to write".format(self.symbol))

        return row_count

    def _get_last_update_from_db(self):
        params = {"symbol": self.symbol}
        self.conn.cursor.execute(self.GET_MAX_TS_QUERY, parameters=params)
        raw_data = self.conn.cursor.fetchall()
        max_ts = raw_data[0][0]
        logger.debug("{0} max ts in db: {1}".format(self.symbol, self.unix_ts_to_date(max_ts)))
        return max_ts

    @staticmethod
    def unix_ts_to_date(unix_ts):
        return datetime.datetime.utcfromtimestamp(int(unix_ts)).strftime('%Y-%m-%d %H:%M:%S.%f')
