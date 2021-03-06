import numpy as np
from datetime import datetime, timedelta
import talib
from scipy.signal import argrelmin, argrelmax

from binance_client.constants import OrderSide, SignalDirection


def short_divergence(prices, indicators):
    """
    :return:  direction, len(prices) - 3, [33,34]
    """
    prices = np.array(prices)
    indicators = np.array(indicators)
    (rsi_max_indexes,) = argrelmax(indicators)
    current_index = len(prices) - 3

    if len(rsi_max_indexes) < 2:
        return current_index, []

    reversal_start_indexes = []
    continue_start_indexes = []
    # short divergence
    if rsi_max_indexes[-1] == current_index:
        for i in range(-2, -1 * (len(rsi_max_indexes) + 1), -1):
            if not indicators[rsi_max_indexes[i]]:
                break  # indicator is None
            if current_index - rsi_max_indexes[i] < 4:
                continue  # too close

            # short reversal divergence
            if prices[current_index] > prices[rsi_max_indexes[i]] and \
                    indicators[current_index] < indicators[rsi_max_indexes[i]]:
                if not check_price_cross(SignalDirection.SHORT, prices[rsi_max_indexes[i]:current_index + 1]):
                    reversal_start_indexes.append(rsi_max_indexes[i])

            # hidden continue divergence
            if prices[current_index] < prices[rsi_max_indexes[i]] and \
                    indicators[current_index] > indicators[rsi_max_indexes[i]]:
                if not check_price_cross(SignalDirection.SHORT, prices[rsi_max_indexes[i]:current_index + 1]):
                    continue_start_indexes.append(rsi_max_indexes[i])
    return current_index, reversal_start_indexes, continue_start_indexes


def long_divergence(prices, indicators):
    """
    :return:  direction, len(prices) - 3, [33,34]
    """
    prices = np.array(prices)
    indicators = np.array(indicators)
    (rsi_min_indexes,) = argrelmin(indicators)
    current_index = len(prices) - 3

    if len(rsi_min_indexes) < 2:
        return current_index, []

    reversal_start_indexes = []
    continue_start_indexes = []
    # long divergence
    if rsi_min_indexes[-1] == current_index:
        for i in range(-2, -1 * (len(rsi_min_indexes) + 1), -1):
            if not indicators[rsi_min_indexes[i]]:
                break  # indicator is None
            if current_index - rsi_min_indexes[i] < 4:
                continue  # too close

            # long reversal divergence
            if prices[current_index] < prices[rsi_min_indexes[i]] and \
                    indicators[current_index] > indicators[rsi_min_indexes[i]]:
                if not check_price_cross(SignalDirection.LONG, prices[rsi_min_indexes[i]:current_index + 1]):
                    reversal_start_indexes.append(rsi_min_indexes[i])

            # hidden continue divergence
            if prices[current_index] > prices[rsi_min_indexes[i]] and \
                    indicators[current_index] < indicators[rsi_min_indexes[i]]:
                if not check_price_cross(SignalDirection.LONG, prices[rsi_min_indexes[i]:current_index + 1]):
                    continue_start_indexes.append(rsi_min_indexes[i])

    return current_index, reversal_start_indexes, continue_start_indexes


def check_price_cross(direction, prices):
    """
    LONG: cant be lower
    SHORT: cant be higher
    """
    count = len(prices)
    slope = (prices[-1] - prices[0]) / (count - 1)

    if direction == SignalDirection.LONG:
        if prices[0] > prices[1] or prices[count - 3] < prices[-1]:
            return True
    elif direction == SignalDirection.SHORT:
        if prices[0] < prices[1] or prices[count - 3] > prices[-1]:
            return True

    for i in range(2, count - 2):
        compare_value = slope * i + prices[0]
        if direction == SignalDirection.LONG:
            if prices[i] < compare_value:
                return True
        elif direction == SignalDirection.SHORT:
            if prices[i] > compare_value:
                return True
    return False
