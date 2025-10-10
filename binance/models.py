import logging

logger = logging.getLogger()

class BinanceCandle:
    def __init__(self, candle_info, timeframe, exchange = "binance"):
        self.info = candle_info
        self.timeframe = timeframe
        self.timestamp = candle_info[0]
        self.open = float(candle_info[1])
        self.high = float(candle_info[2])
        self.low = float(candle_info[3])
        self.close = float(candle_info[4])
        self.volume = float(candle_info[5])
    def get_all_info(self):
        return self.info

class BinanceContract:
    def __init__(self, contract_info):
        self.info = contract_info
        self.symbol: str = contract_info['symbol']
        self.base_asset: str = contract_info['baseAsset']
        self.quote_asset: str = contract_info['quoteAsset']
        self.price_decimals = float(contract_info['pricePrecision'])
        self.quantity_decimals = float(contract_info['quantityPrecision'])
        self.tick_size = 1 / pow(10, contract_info['pricePrecision'])
        self.lot_size = 1 / pow(10, contract_info['quantityPrecision'])
        try:
            self.min_notion = contract_info['filters'][5]['notional']
        except Exception as e:
            self.min_notion = 5.0
            logger.error("Min_Notion not found in %s ... Adjusted to 5.0: %s", self.symbol, e)

    def get_all_info(self):
        return self.info

class Balance:
    def __init__(self, info):
        self.info = info
        self.asset = info['asset']
        self.initial_margin = float(info['initialMargin'])
        self.maintenance_margin = float(info['maintMargin'])
        self.margin_balance = float(info['marginBalance'])
        self.wallet_balance = float(info['walletBalance'])
        self.unrealized_pnl = float(info['unrealizedProfit'])
    def get_all_info(self):
        return self.info