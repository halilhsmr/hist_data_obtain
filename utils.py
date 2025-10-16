import logging
from root_models import Candle
import datetime as dt
import pandas as pd
import numpy as np


logger = logging.getLogger()


def candle_to_df(candle_list: list[Candle]) -> pd.DataFrame:
    """
    Converts list of candles to pandas dataframe. only OHLCV values are presented.
    :param candle_list: List of Candles (or Candles parent) objects
    :return: pandas dataframe object
    """
    df_index = [dt.datetime.fromtimestamp(c.timestamp) for c in candle_list]
    df_values = [[c.open, c.high, c.low, c.close, c.volume] for c in candle_list]
    cols = ["open", "high", "low", "close", "volume"]
    df = pd.DataFrame(data=df_values, index=df_index,
                      columns=cols)
    return df


def candle_to_df_detailed(candle_list: list[Candle], *args):
    """
    Converts list of Candle (or candle parent) objects to pandas dataframe.

    :param candle_list: List of Candles (or Candles parent) objects
    :param args: information required in the dataframe exactly in Candle.info_det keys.
                For parent classes, each key must be looked separately from its own self.info_det
                dictionary.
    :return: pandas dataframe object
    """


    df_index = [dt.datetime.fromtimestamp(c.timestamp) for c in candle_list]
    df_values = [[c.open, c.high, c.low, c.close, c.volume] for c in candle_list]
    cols = ["open", "high", "low", "close", "volume"]

    for arg in args:
        cols.append(arg.lower().replace(" ", "_"))
        for i, row in enumerate(df_values):
            if arg not in candle_list[i].info_det.keys():
                logger.error("%s not in %s th candle's details. Inserting np.nan", arg, i)
                row.append(np.nan)
            else:
                row.append(candle_list[i].info_det[arg])

    df = pd.DataFrame(data=df_values, index=df_index,
                      columns=cols)
    return df


