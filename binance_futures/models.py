import logging
from root_models import Candle

logger = logging.getLogger()

class BinanceCandle(Candle):
    def __init__(self, candle_info, timeframe: str, exchange="binance_futures"):

        """
        :param candle_info: Direct REST API response form binance futures client
        :param timeframe: candle timeframe as requested from API
        :param exchange:
        """
        super().__init__(exchange)
        self.info = candle_info
        self.timeframe = timeframe
        self.timestamp = int(candle_info[0] / 1000)
        self.open = float(candle_info[1])
        self.high = float(candle_info[2])
        self.low = float(candle_info[3])
        self.close = float(candle_info[4])
        self.volume = float(candle_info[5])
        self.exchange = exchange

        self.info_det = {
            "Kline open time": candle_info[0],
            "Open price": candle_info[1],
            "High price": candle_info[2],
            "Low price": candle_info[3],
            "Close price": candle_info[4],
            "Volume": candle_info[5],
            "Kline Close time": candle_info[6],
            "Quote asset volume": candle_info[7],
            "Number of trades": candle_info[8],
            "Taker buy base asset volume": candle_info[9],
            "Taker buy quote asset volume": candle_info[10],
            "Unused field, ignore.": candle_info[11],
        }



class BinanceContract:
    def __init__(self, contract_info):
        self.info = contract_info
        self.symbol: str = contract_info['symbol']
        self.base_asset: str = contract_info['baseAsset']
        self.quote_asset: str = contract_info['quoteAsset']
        self.price_decimals = float(contract_info['quoteAssetPrecision'])
        self.quantity_decimals = float(contract_info['baseAssetPrecision'])
        self.tick_size = 1 / pow(10, contract_info['quoteAssetPrecision'])
        self.lot_size = 1 / pow(10, contract_info['baseAssetPrecision'])
        try:
            for filter_dict in contract_info['filters']:
                if filter_dict['filterType'] == 'NOTIONAL':
                    self.min_notion = filter_dict['minNotional']
                    self.max_notion = filter_dict['maxNotional']
        except Exception as e:
            self.min_notion = 5.0
            self.max_notion = 5000.0
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