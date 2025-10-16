from dataclasses import dataclass, field
import typing as ty
import datetime as dt
import pandas as pd

@dataclass
class Candle:
    def __init__(self):
        self.info: ty.Dict= dict()
        self.timeframe: ty.AnyStr
        self.timestamp: ty.Union[int, dt.datetime, pd.Timestamp]
        self.open: float
        self.high: float
        self.low: float
        self.close: float
        self.volume: float

        self.exchange: str

    def get_all_info(self):
        return self.info