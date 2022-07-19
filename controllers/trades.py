from poloniex import PublicAPI, PublicAPIError


class TradeHistoryController:
    def __init__(self, db, config_manager):
        self.db = db
        self.config_manager = config_manager
        self.api = PublicAPI()

    def update(self, ticker):
        pass
