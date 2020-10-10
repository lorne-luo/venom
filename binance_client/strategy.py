import numpy as np
from datetime import datetime, timedelta
import talib
from scipy.signal import argrelmin, argrelmax
from binance.client import Client

from binance_client.configs import get_binance_client
from binance_client.constants import SignalDirection
from binance_client.kline import get_kline_dataframe
from signals.divergence import long_divergence, short_divergence
from utils.string import extract_number
from utils.time import calculate_time_delta


def rsi_13(close_prices):
    return talib.RSI(np.array(close_prices), timeperiod=13)


def check_divergence(prices, indicators):
    prices = np.array(prices)
    indicators = np.array(indicators)

    (price_min_indexes,) = argrelmin(prices)
    (price_max_indexes,) = argrelmax(prices)

    (rsi_min_indexes,) = argrelmin(indicators)
    (rsi_max_indexes,) = argrelmax(indicators)

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


def check_symbol_divergence(symbol, interval, count, to_datetime=None):
    to_datetime = to_datetime or datetime.utcnow()
    to_timestamp = to_datetime.timestamp()
    delta = calculate_time_delta(interval, count)
    from_datetime = to_datetime - delta
    from_timestamp = from_datetime.timestamp()

    df = get_kline_dataframe(symbol, Client.KLINE_INTERVAL_1HOUR, str(from_timestamp), str(to_timestamp))
    df["candle_low"] = df[["open", "close"]].min(axis=1)
    df["candle_high"] = df[["open", "close"]].max(axis=1)
    df["rsi13"] = talib.RSI(df['close'], timeperiod=13)

    newest_index, long_start_indexes = long_divergence(df["candle_low"], df["rsi13"])

    newest_index, short_start_indexes = short_divergence(df["candle_high"], df["rsi13"])

    if long_start_indexes and not short_start_indexes:
        pass
    elif short_start_indexes and not long_start_indexes:
        pass


if __name__ == '__main__':
    check_symbol_divergence('BTCUSDT', Client.KLINE_INTERVAL_1HOUR, count)
    close_prices = get_close_array(interval=Client.KLINE_INTERVAL_5MINUTE, start_str='3 hours ago UTC')
    rsi = talib.RSI(np.array(close_prices), timeperiod=13)
    print(check_divergence(close_prices, rsi))
