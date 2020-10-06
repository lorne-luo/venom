from pprint import pprint

import numpy as np
import pandas as pd
from datetime import datetime
import talib
from binance.client import Client
from scipy.signal import argrelmin, argrelmax

from binance_client.configs import get_binance_client
from binance_client.constants import OrderSide, SignalDirection


def get_kline(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_5MINUTE, start_str='24 hours ago UTC', end_str=None):
    """
    [
      [
        1499040000000,      // Open time
        "0.01634790",       // Open
        "0.80000000",       // High
        "0.01575800",       // Low
        "0.01577100",       // Close
        "148976.11427815",  // Volume
        1499644799999,      // Close time
        "2434.19055334",    // Quote asset volume
        308,                // Number of trades
        "1756.87402397",    // Taker buy base asset volume
        "28.46694368",      // Taker buy quote asset volume
        "17928899.62484339" // Ignore.
      ]
    ]
    """
    client = get_binance_client()
    return [kline for kline in client.get_historical_klines_generator(symbol, interval, start_str, end_str)]


def get_kline_dataframe(symbol='BTCUSDT',
                        interval=Client.KLINE_INTERVAL_5MINUTE,
                        from_str='24 hours ago UTC',
                        to_str=None):
    client = get_binance_client()
    klines = [kline for kline in client.get_historical_klines_generator(symbol, interval, from_str, to_str)]
    labels = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
              'quote_asset_volume', 'number_of_trades', 'base_asset_volume', 'quote_asset_volume', 'ignore']
    df = pd.DataFrame.from_records(klines, columns=labels)

    df.astype({"open": np.float16, "high": np.float16, "low": np.float16, "close": np.float16})
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    return df


def parse_kline(kline):
    open_time, open, high, low, close, volume, close_time, _, trade_number, _, _, _ = kline
    return


def get_ohlc_array(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_5MINUTE, start_str='24 hours ago UTC',
                   end_str=None):
    klines = get_kline(symbol, interval, start_str, end_str)
    data = []
    for k in klines:
        open_time, o, h, l, c, _, close_time, _, _, _, _, _ = k
        data.append((float(o), float(h), float(l), float(c)))
    return data


def get_close_array(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_5MINUTE, start_str='24 hours ago UTC',
                    end_str=None):
    data = get_ohlc_array(symbol, interval, start_str, end_str)
    return [d[3] for d in data]


def check_divergence(prices, indicators):
    prices = np.array(prices)
    indicators = np.array(indicators)

    (price_min_indexes,) = argrelmin(prices)
    (price_max_indexes,) = argrelmax(prices)

    (rsi_min_indexes,) = argrelmin(indicators)
    (rsi_max_indexes,) = argrelmax(indicators)

    print('################')
    print(rsi_min_indexes)
    print('################')
    print(rsi_max_indexes)

    # bearish divergence
    if len(price_max_indexes) >= 2 and len(rsi_max_indexes) >= 2:
        if price_max_indexes[-1] == rsi_max_indexes[-1] == len(prices) - 3 and \
                price_max_indexes[-2] == rsi_max_indexes[-2] and \
                rsi_max_indexes[-1] - rsi_max_indexes[-2] > 4:
            if prices[price_max_indexes[-1]] > prices[price_max_indexes[-2]] and \
                    indicators[price_max_indexes[-1]] < indicators[price_max_indexes[-2]]:
                # print('bearish divergence')
                return SignalDirection.SHORT

    if len(price_min_indexes) >= 2 and len(rsi_min_indexes) >= 2:
        if price_min_indexes[-1] == rsi_min_indexes[-1] == len(prices) - 3 and \
                price_min_indexes[-2] == rsi_min_indexes[-2] and \
                rsi_min_indexes[-1] - rsi_min_indexes[-2] > 4:
            if prices[price_min_indexes[-1]] < prices[price_min_indexes[-2]] and \
                    indicators[price_min_indexes[-1]] > indicators[price_min_indexes[-2]]:
                # print('bullish divergence')
                return SignalDirection.LONG


if __name__ == '__main__':
    close_prices = get_close_array(interval=Client.KLINE_INTERVAL_5MINUTE, start_str='3 hours ago UTC')
    rsi = talib.RSI(np.array(close_prices), timeperiod=13)
    print(check_divergence(close_prices, rsi))
