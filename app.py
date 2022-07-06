import os
import time
import logging
import traceback

from db_connector import DBConnector
from data_collector import HttpDataCollector
from data_collector import PoloniexDataCollectorFullOb
from data_collector import PoloniexDataCollectorResampledOb

from basic_application import BasicApplication

logging.raiseExceptions = True
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class PdcLiteApp(BasicApplication):
    NAME = "Poloniex Data Collector"
    VERSION = 1.2
    MAX_TIMEOUT = 180

    def __init__(self, config):
        BasicApplication.__init__(self, config_path=config)

    def run(self):
        while True:
            try:
                pdc = HttpDataCollector()
                pdc_ob = PoloniexDataCollectorResampledOb(self.config_manager)
                logger.critical("{0} v.{1} started".format(self.NAME, self.VERSION))

                db_config = self.config_manager.get_config().get("db")
                db_config["user"] = os.getenv("DB_USER")
                db_config["password"] = os.getenv("DB_PASS")

                with DBConnector(db_config) as db:
                    while True:
                        # 1. Business logic
                        cycle_start_time = time.time()

                        runtime_config = self.config_manager.get_config().get("runtime")

                        query = runtime_config.get("query", None)
                        if query is not None:
                            data = pdc.get_data()
                            db.write_data(query, data)

                        query = runtime_config.get("query_ob", None)
                        if query is not None:
                            data = pdc_ob.get_data()
                            db.write_data(query, data)

                        exec_time = time.time() - cycle_start_time
                        wait_time = max(0, runtime_config.get("updateTimeout") - exec_time)

                        # 2. Check stop signal
                        if self.halt.is_set():
                            break

                        # 3. Sleep
                        time.sleep(wait_time)

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
