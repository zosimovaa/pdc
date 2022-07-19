import os
import time
import logging
import traceback

from basic_application import BasicApplication
from db_connector import DBConnector
from controllers import TradeHistoryController
from controllers import OrderbookController
from poloniex import PublicAPI, PublicAPIError


logging.raiseExceptions = True
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class PdcLiteApp(BasicApplication):
    NAME = "Poloniex Data Collector"
    VERSION = "3.0.0"
    MAX_TIMEOUT = 180

    def __init__(self, config):
        BasicApplication.__init__(self, config_path=config)

    def run(self):
        while True:
            try:
                logger.critical("{0} v.{1} started".format(self.NAME, self.VERSION))

                db_config = self.config_manager.get_config().get("db")

                with DBConnector(db_config) as db:
                    trade_controller = TradeHistoryController(db, self.config_manager)
                    orderbook_controller = OrderbookController(db, self.config_manager)

                    start_time = time.time()
                    while True:
                        # 1. Check stop signal
                        if self.halt.is_set():
                            break

                        # 2. Business logic
                        runtime_config = self.config_manager.get_config().get("runtime")
                        for ticker in runtime_config["tickers"]:
                            trade_controller.update(ticker)
                            orderbook_controller.update(ticker)

                        # 3. Sleep
                        exec_time = time.time() - start_time
                        wait_time = max(0, runtime_config.get("updateTimeout") - exec_time)
                        time.sleep(wait_time)
                        start_time = time.time()

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
