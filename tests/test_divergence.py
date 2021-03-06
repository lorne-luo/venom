import talib
from datetime import datetime, timedelta
import numpy as np

from binance.client import Client
from signals.divergence import check_price_cross
from binance_client.constants import SignalDirection
from binance_client.configs import get_binance_client
from binance_client.kline import check_divergence, get_kline_dataframe
from signals.divergence import long_divergence, short_divergence


def test_check_divergence():
    result = check_divergence([0, 0, 1, 0, 0, 0, 0, 2, 0, 0], [0, 0, 2, 0, 0, 0, 0, 1, 0, 0])
    assert result == SignalDirection.SHORT

    result = check_divergence([3, 3, 2, 3, 3, 3, 3, 1, 3, 3], [3, 3, 1, 3, 3, 3, 3, 2, 3, 3])
    assert result == SignalDirection.LONG

    result = check_divergence([0, 0, 1, 0, 0, 0, 2, 0, 0], [0, 0, 2, 0, 0, 0, 1, 0, 0])
    assert result == None

    result = check_divergence([3, 3, 2, 3, 3, 3, 1, 3, 3], [3, 3, 1, 3, 3, 3, 2, 3, 3])
    assert result == None


def test_check_divergence_with_real_case():
    end_dt = datetime(year=2020, month=9, day=23, hour=22, minute=1)
    end_ts = end_dt.timestamp()  # timestamp in milliseconds
    start_dt = datetime(year=2020, month=9, day=21, hour=10, minute=1) - timedelta(hours=14)
    start_ts = start_dt.timestamp()  # timestamp in milliseconds
    client = get_binance_client()
    klines = [kline for kline in
              client.get_historical_klines_generator('BTCUSDT', Client.KLINE_INTERVAL_1HOUR, str(start_ts),
                                                     str(end_ts))]

    low_prices = [min(float(k[1]), float(k[4])) for k in klines]
    high_prices = [max(float(k[1]), float(k[4])) for k in klines]

    rsi = talib.RSI(np.array(low_prices), timeperiod=14)
    result = check_divergence(low_prices, rsi)

    for k in low_prices:
        print(k)
    print(len(klines))

    for r in rsi:
        print(r)


def test_reversal_divergence():
    end_dt = datetime(year=2020, month=9, day=23, hour=22, minute=1)
    end_ts = end_dt.timestamp()  # timestamp in milliseconds
    start_dt = datetime(year=2020, month=9, day=21, hour=10, minute=1) - timedelta(hours=14)
    start_ts = start_dt.timestamp()  # timestamp in milliseconds

    symbol = 'BTCUSDT'
    timeframe_name = '1h'
    df = get_kline_dataframe(symbol, timeframe_name, str(start_ts), str(end_ts))
    df["candle_low"] = df[["open", "close"]].min(axis=1)
    df["candle_high"] = df[["open", "close"]].max(axis=1)
    df["rsi"] = talib.RSI(df['close'], timeperiod=14)

    newest_index, long_start_indexes, long_continue_indexes = long_divergence(df["candle_low"], df["rsi"])
    assert newest_index == 71
    assert long_start_indexes == [19]
    assert long_continue_indexes == []


def test_continue_divergence():
    end_dt = datetime(year=2020, month=10, day=10, hour=13, minute=55)
    end_ts = end_dt.timestamp()
    start_dt = end_dt - timedelta(hours=7)
    start_ts = start_dt.timestamp()

    symbol = 'BTCUSDT'
    timeframe_name = '5m'
    df = get_kline_dataframe(symbol, timeframe_name, str(start_ts), str(end_ts))

    df["candle_low"] = df[["open", "close"]].min(axis=1)
    df["candle_high"] = df[["open", "close"]].max(axis=1)
    df["rsi"] = talib.RSI(df['close'], timeperiod=14)

    newest_index, short_start_indexes, short_continue_indexes = short_divergence(df["candle_high"], df["rsi"])
    assert newest_index == 82
    assert short_start_indexes == []
    assert short_continue_indexes == [32, 25]


def test_check_price_cross():
    result = check_price_cross(SignalDirection.SHORT, [20, 18, 17, 16, 15, 14, 13, 12, 11, 10, 10])
    assert result == False
    result = check_price_cross(SignalDirection.SHORT, [20, 18, 17, 16, 15, 17, 13, 12, 11, 10, 1])
    assert result == True

    result = check_price_cross(SignalDirection.LONG, [10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20])
    assert result == False
    result = check_price_cross(SignalDirection.LONG, [0, 2, 3, 4, 2, 6, 7, 8, 9, 10, 10])
    assert result == True
