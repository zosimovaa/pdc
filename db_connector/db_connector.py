import time
import logging
from clickhouse_driver import connect
from basic_application import with_debug_time

logger = logging.getLogger(__name__)


class DBConnector(object):
    def __init__(self, params):
        self.params = params
        self.conn = None
        self.cursor = None

    def create_connection(self):
        return connect(**self.params)

    # @with_debug_time
    def write_data(self, query, data):
        logger.debug(query)
        logger.debug(len(data))
        if len(data):
            self.cursor.executemany(query, data)
            data_length = self.cursor.rowcount
            logger.debug(data_length)
            logger.info("{} records was written into db".format(data_length))
        else:
            logger.info("No data to write")

    def __enter__(self):
        self.conn = self.create_connection()
        self.cursor = self.conn.cursor()
        logger.warning("Cursor created, database connection established")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
