from random import random

import pandas as pd
import typing
import requests
from models import *
import time
import datetime as dt
import hashlib
import hmac
from urllib.parse import urlencode
import keys

TF_EQUIV = {"1s":1, "1m": 60,"3m":180, "5m":300, "15m":900, "30m":1800, "1h":3600, "2h":3600*2,"4h":14400,
            "8h":14400*2, "12h":14400*3, "1d":14400*6, "3d":14400*18, "1w":14400*42, "1M": 14400*6*30}

testnet = False

logger = logging.getLogger()


logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def generate_signature(data: dict) -> str:
    return hmac.new(keys.api_secret.encode(), urlencode(data).encode(),
                    hashlib.sha256).hexdigest()

def get_base_url(is_test: bool) -> dict[str, str]:
    if is_test:
        urls = {
            "base_url" : "https://testnet.binancefuture.com",
            "wss_url" : "wss://stream.binancefuture.com/ws"
        }
    else:
        urls = {
            "base_url" : "https://api.binance.com",
            "wss_url" : "wss://stream.binance_futures.com:9443"
        }
    return urls

url_dic = get_base_url(False)
base_url, wss_url = url_dic['base_url'], url_dic["wss_url"]

def make_request(method: str, endpoint: str, data: None | dict = None, base:str = base_url):
    method = method.upper().strip()
    header = {'X-MBX-APIKEY': keys.api_public}

    try:
        if method == "GET":
            response = requests.get(base + endpoint, params=data, headers=header)
        elif method == "POST":
            response = requests.post(base + endpoint, params=data, headers=header)

        elif method == "DELETE":
            response = requests.delete(base + endpoint, params=data, headers=header)

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


def get_contracts() -> dict[str, BinanceContract]:
    contracts = dict()

    content = make_request("GET", "/fapi/v1/exchangeInfo")
    if content:
        for contract_data in content["symbols"]:
            contracts[contract_data['symbol']] = BinanceContract(contract_data)

        return contracts

def get_historical_candles(sym:str, interval: str, start_time: int=0, end_time: int=0, limit=0):
    """
    Gets historical binance_futures kline data
    :param contract:
    :param interval:
    :param start_time:
    :param end_time:
    :param limit:
    :return:
    """
    endpoint = "/api/v3/klines"
    data = {
        'symbol': sym.upper(),
        'interval': interval,
    }

    if start_time:
        data['startTime'] = start_time
    if end_time:

        candle_count = (end_time - start_time) // TF_EQUIV[interval]
        print(candle_count)
        if candle_count < 1000:
            data['endTime'] = end_time
        else:
            data['limit'] = 1000

    elif limit > 1000:
        #TODO: we need a loop here to send consecutive kline requests
        data['limit'] = 1000
    else:
        data['limit'] = limit

    response = make_request("get", endpoint, data)
    return response


def time_to_timestamp(year, month, day, hour=0, mnt=0, sec=0) -> int:
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
    full_ts = int(dt.datetime.timestamp(full_format)*1000)
    return full_ts



ts_now = int(dt.datetime.timestamp(dt.datetime.now()) * 1000)

random_date = time_to_timestamp(2024,10,1)

hist = get_historical_candles(sym='BTCUSDT', interval="1h", limit=1000, start_time=random_date)
print(len(hist))
