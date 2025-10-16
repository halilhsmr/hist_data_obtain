import logging

import requests
import datetime as dt

from binance_futures import keys
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
        content = self._make_request("GET", "/api/v3/exchangeInfo")
        if content:
            for contract_data in content["symbols"]:
                self.contracts[contract_data['symbol']] = BinanceContract(contract_data)
        else:
            logger.error("Error while getting contracts...")

    def _time_to_timestamp(self, time_to_conv) -> int:
        """
        :param time_to_conv: dt.datetime object
        :return: timestamp integer in milliseconds
        """
        full_ts = int(dt.datetime.timestamp(time_to_conv) * 1000)
        return full_ts

    def get_historical_candles(self, contract:BinanceContract, interval: str, start_time: dt.datetime|None=None,
                               end_time: dt.datetime|None=None, limit: int=0):
        """
        1/3 of start_time, end_time and limit must be entered (only end-time not available)
        :param contract: Contract object of the desired pair
        :param interval: a key in TF_EQUIV dictionary
        :param start_time:
        :param end_time:
        :param limit: number of candles requested
        :return:
        """

        if limit:
            candle_count = limit

        candles = []

        endpoint = "/api/v3/klines"
        symbol = contract.symbol
        data = {
            'symbol': symbol.upper(),
            'interval': interval,
        }

        if limit==0 and start_time==None:
            logger.error("Not enough variables are entered in get_historical_candles method of BinanceFuturesClient")
            return None

        # if both start time and end time are entered, we'll ignore the limit and get candle data from start to end
        elif start_time and end_time and limit == 0:
            candle_count = (end_time - start_time) // TF_EQUIV[interval]

        # end time and limit are entered, we'll finish at end time and go back limit number of candles
        elif end_time and limit>0 and not start_time:
            total_time_in_sec = limit * TF_EQUIV[interval]
            start_time = end_time - dt.timedelta(seconds=total_time_in_sec)
            candle_count = limit

        elif start_time and limit>0 and not end_time: # start time and limit entered only
            candle_count = limit
            total_time_in_sec = limit * TF_EQUIV[interval]
            start_time = end_time - dt.timedelta(seconds=total_time_in_sec)
        else: # only limit has entered
            candle_count = limit
            total_time_in_sec = limit * TF_EQUIV[interval]
            start_time = dt.datetime.now(dt.UTC) - dt.timedelta(seconds=total_time_in_sec)

        # if there are more than 1000 candles, we'd exceed the max weight. So we need to send multiple requests
        if candle_count > 1000:
            num_of_requests = (candle_count // 1000) + 1
        else:
            num_of_requests = 1

        remaining_candles = candle_count
        cur_start = start_time
        cur_end = start_time + dt.timedelta(seconds=1000*TF_EQUIV[interval])

        for i in range(num_of_requests):
            data['startTime'] = self._time_to_timestamp(cur_start)

            if remaining_candles > 1000:
                data['limit'] = 1000
                remaining_candles -= 1000
                cur_start += dt.timedelta(seconds=1000*TF_EQUIV[interval])
            else:
                data['limit'] = remaining_candles
            candles += self._make_request("get", endpoint, data)

        candles = [BinanceCandle(i, interval) for i in candles]
        return candles


if __name__ == "__main__":
    client = BinanceFuturesClient(False, keys.api_public, keys.api_secret)
    btc_contract = client.contracts['BTCUSDT']

    contract_names = list(client.contracts.keys())
    usdc_contracts = [i for i in contract_names if i.endswith('USDC')]

    btc_historical = client.get_historical_candles(btc_contract, "1h", limit=1500)

    for candle in btc_historical:
        ts = candle.timestamp
        print(dt.datetime.fromtimestamp(ts))