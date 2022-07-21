import os
import time
import logging
import traceback

from basic_application import BasicApplication
from clickhouse_connector import ClickHouseConnector
from controllers import TradeHistoryController
from controllers import OrderbookController


logging.raiseExceptions = True
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class PdcLiteApp(BasicApplication):
    NAME = "Poloniex Data Collector"
    VERSION = "3.1.0"
    MAX_TIMEOUT = 180

    def __init__(self, config):
        BasicApplication.__init__(self, config_path=config)
        self.tickers = dict()

    def run(self):
        while True:
            try:
                logger.critical("{0} v.{1} started".format(self.NAME, self.VERSION))

                db_config = self.config_manager.get_config().get("db")

                with ClickHouseConnector(db_config) as conn:
                    trade_controller = TradeHistoryController(conn, self.config_manager)
                    orderbook_controller = OrderbookController(conn, self.config_manager)

                    start_time = int(time.time())
                    while True:
                        # 1. Check stop signal
                        if self.halt.is_set():
                            break

                        # 2. Business logic
                        runtime_config = self.config_manager.get_config().get("runtime")
                        for ticker in runtime_config["tickers"]:
                            trade_controller.update(ticker, ts=start_time)
                            orderbook_controller.update(ticker, ts=start_time)

                        # 3. Sleep
                        exec_time = time.time() - start_time
                        wait_time = max(0, runtime_config.get("updateTimeout") - exec_time)
                        time.sleep(wait_time)
                        start_time = int(time.time())

            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                time.sleep(runtime_config.get("errorTimeout"))


if __name__ == "__main__":
    env_var = os.getenv("ENV", "TEST")
    if env_var == "PROD":
        config = "prod.yaml"
    else:
        config = "test.yaml"

    app = PdcLiteApp(config)
    app.start()
    app.join()
    time.sleep(10)
