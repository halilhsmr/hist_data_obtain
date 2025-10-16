from dataclasses import dataclass
import typing as ty

TF_EQUIV = {"1s":1, "1m": 60,"3m":180, "5m":300, "15m":900, "30m":1800, "1h":3600, "2h":3600*2,"4h":14400,
            "8h":14400*2, "12h":14400*3, "1d":14400*6, "3d":14400*18, "1w":14400*42, "1M": 14400*6*30}


@dataclass
class Candle:
    def __init__(self, exchange):
        self.info: ty.Union[dict, list] = []
        self.timeframe: str = ""
        self.timestamp: int = 0
        self.open: float = 0.0
        self.high: float = 0.0
        self.low: float = 0.0
        self.close: float = 0.0
        self.volume: float = 0.0

        self.exchange: str = exchange

        self.info_det: ty.Dict[str, ty.Any] = dict()

    def get_all_info(self):
        return self.info


class Strategy:
    def __init__(self):
        pass


