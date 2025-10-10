import logging
import requests
import datetime as dt
from binance_futures.models import BinanceContract, BinanceCandle

TF_EQUIV = {"1s":1, "1m": 60,"3m":180, "5m":300, "15m":900, "30m":1800, "1h":3600, "2h":3600*2,"4h":14400,
            "8h":14400*2, "12h":14400*3, "1d":14400*6, "3d":14400*18, "1w":14400*42, "1M": 14400*6*30}


logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self, testnet: bool, public_api: str, secret_api: str):
        self.demo = testnet
        url_dic = self.get_base_url()
        self.base_url, self.wss_url = url_dic['base_url'], url_dic["wss_url"]
        self.api_public = public_api
        self.api_secret = secret_api

        self.contracts = dict()
        self._get_contracts()

    def get_base_url(self) -> dict[str, str]:
        if self.demo:
            urls = {
                "base_url": "https://testnet.binancefuture.com",
                "wss_url": "wss://stream.binancefuture.com/ws"
            }
        else:
            urls = {
                "base_url": "https://api.binance.com",
                "wss_url": "wss://stream.binance_futures.com:9443"
            }
        return urls

    def _make_request(self, method: str, endpoint: str, data: None | dict = None):
        method = method.upper().strip()
        header = {'X-MBX-APIKEY': self.api_public}

        try:
            if method == "GET":
                response = requests.get(self.base_url + endpoint, params=data, headers=header)
            elif method == "POST":
                response = requests.post(self.base_url + endpoint, params=data, headers=header)

            elif method == "DELETE":
                response = requests.delete(self.base_url + endpoint, params=data, headers=header)

            else:
                raise ValueError("Invalid Request Method")

            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Error while making %s request to %s: %s (error code %s)",
                             method, endpoint, response.json(), response.status_code)
                return None
        except Exception as e:
            logger.error("Connection error while making %s request to %s endpoint: %s",
                         method, endpoint, e)
            return None

    def _get_contracts(self):
        content = self._make_request("GET", "/fapi/v1/exchangeInfo")
        if content:
            for contract_data in content["symbols"]:
                self.contracts[contract_data['symbol']] = BinanceContract(contract_data)
        else:
            logger.error("Error while getting contracts...")

    def _time_to_timestamp(self, year, month, day, hour=0, mnt=0, sec=0) -> int:
        """
        :param year: integer
        :param month: integer
        :param day: integer
        :param hour: integer
        :param mnt: integer
        :param sec: integer
        :return: timestamp integer in milliseconds
        """
        full_format = dt.datetime(year, month, day, hour, mnt, sec)
        full_ts = int(dt.datetime.timestamp(full_format) * 1000)
        return full_ts

    def get_historical_candles(self, contract:BinanceContract, interval: str, start_time: dt.datetime|None=None,
                               end_time: dt.datetime|None=None, limit: int=0):
        """
        1/3 of start_time, end_time and limit must be entered
        :param contract:
        :param interval:
        :param start_time:
        :param end_time:
        :param limit:
        :return:
        """

        candles = []

        endpoint = "/api/v3/klines"
        symbol = contract.symbol
        data = {
            'symbol': symbol.upper(),
            'interval': interval,
        }

        if limit==0 and start_time==None and end_time==None:
            logger.error("Not enough variables are entered in get_historical_candles method of BinanceFuturesClient")
            return None

        # if both start time and end time are entered, we'll ignore the limit and get candle data from start to end
        if start_time and end_time:
            limit = 0
            candle_count = (end_time - start_time) // TF_EQUIV[interval]
        # if there are more than 1000 candles, we'd exceed the max weight. So we need to send multiple requests
            if candle_count > 1000:
                num_of_requests = (candle_count//1000) + 1
        # if there are less than 1000 candles, we'd send a single request
            else:
                num_of_requests = 1

        # if limit and one of start or end_time are entered;
        if limit > 0:
            if limit < 1000:
                num_of_requests = 1
            else:
                num_of_requests = (limit // 1000) + 1

        # at this point, we should have a num_of_request.
        # if start time and limit are entered, we'll start from the time and return limit number of candles
        if start_time and limit > 0:
            pass

        # if end time and limit are entered, we'll finish at end time and go back limit number of candles
        elif end_time:
            pass

