import os
import time
import logging
import traceback

from basic_application import BasicApplication
from clickhouse_connector import ClickHouseConnector
from controllers import TradeHandler
from controllers import OrderbookHandler


logging.raiseExceptions = True
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class PdcLiteApp(BasicApplication):
    NAME = "Poloniex Data Collector"
    VERSION = "5.0.1"
    MAX_TIMEOUT = 180

    def __init__(self, cfg, env):
        BasicApplication.__init__(self, config_path=cfg)
        self.env = env
        self.orderbook_handlers = dict()
        self.trades_handlers = dict()
        self.symbols = []

    def run(self):
        while True:
            try:
                logger.critical("[{2}] {0} v.{1} started".format(self.NAME, self.VERSION, self.env))
                db_config = self.config_manager.get_config().get("db")
                with ClickHouseConnector(db_config) as conn:
                    self.orderbook_handlers = dict()
                    self.trades_handlers = dict()

                    start_time = int(time.time())
                    while True:
                        # 1. Check stop signal
                        if self.halt.is_set():
                            logger.warning("Halt signal set. Exit.")
                            break

                        # 2. Business logic
                        runtime_config = self.config_manager.get_config().get("runtime")

                        self.symbols = runtime_config.get("symbols")
                        logger.debug("Symbols update: {}".format(self.symbols))
                        self.add_handler(conn)
                        self.cleanup_handlers()

                        cycle_stat_ob = 0
                        cycle_stat_trades = 0
                        for symbol in self.symbols:
                            records = self.orderbook_handlers[symbol].update()
                            cycle_stat_ob += records
                            records = self.trades_handlers[symbol].update()
                            cycle_stat_trades += records

                        exec_time = time.time() - start_time
                        logger.warning("Cycle {0:.2f} | Symbols: {1}, Orderbook: {2} | Trades {3}".format(
                            exec_time, len(self.symbols), cycle_stat_ob, cycle_stat_trades))

                        # 3. Sleep
                        # todo Вынести в отдельный метод в BasicApplication

                        wait_time = max(0, runtime_config.get("updateTimeout") - exec_time)
                        time.sleep(wait_time)
                        start_time = int(time.time())

            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
                time.sleep(runtime_config.get("errorTimeout"))

    def add_handler(self, conn):
        for symbol in self.symbols:
            if symbol not in self.orderbook_handlers:
                self.orderbook_handlers[symbol] = OrderbookHandler(symbol, conn)
                logger.info("Orderbook handler was added for {0} symbol".format(symbol))

            if symbol not in self.trades_handlers:
                self.trades_handlers[symbol] = TradeHandler(symbol, conn)
                logger.info("Trade handler was added for {0} symbol".format(symbol))

    def cleanup_handlers(self):
        actual_symbol_list = self.orderbook_handlers.keys()
        for symbol in actual_symbol_list:
            if symbol not in self.symbols:
                del self.orderbook_handlers[symbol]
                logger.info("Orderbook handler was deleted for {0} symbol".format(symbol))

        actual_symbol_list = self.trades_handlers.keys()
        for symbol in actual_symbol_list:
            if symbol not in self.symbols:
                del self.trades_handlers[symbol]
                logger.info("Trade handler was deleted for {0} symbol".format(symbol))


# =================================================
if __name__ == "__main__":
    env_var = os.getenv("ENV", "TEST")
    if env_var == "PROD":
        config = "config.yaml"
    else:
        config = "config_test.yaml"

    app = PdcLiteApp(config, env_var)
    app.start()
    app.join()
    time.sleep(10)
