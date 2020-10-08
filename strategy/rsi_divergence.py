import logging
from queue import Queue

import talib
from datetime import datetime

from antman.telstra import send_to_admin
from binance.client import Client

from binance_client.constants import get_timeframe_name
from binance_client.kline import get_kline_dataframe
from event.event import SignalEvent, SignalAction, TimeFrameEvent
from binance_client import constants
from signals.divergence import check_long_divergence, check_short_divergence
from strategy.base import StrategyBase
from utils.time import calculate_time_delta

logger = logging.getLogger(__name__)


class RSIDivStrategy(StrategyBase):
    """
    RSI Divergence
    """
    name = 'RSI-Div'
    version = '1.0'
    magic_number = '20201005'
    source = 'https://www.babypips.com/trading/forex-hlhb-system-20190128'

    timeframes = {constants.PERIOD_M5,
                  constants.PERIOD_M15,
                  constants.PERIOD_M30,
                  constants.PERIOD_H1,
                  constants.PERIOD_H4,
                  constants.PERIOD_D1}

    subscribes = [TimeFrameEvent.type]
    symbols = ('BTCUSDT', 'ETHUSDT')  # 'ETHUSDT'

    def signal_symbol(self, symbol, event):
        to_datetime = datetime.utcnow()
        to_timestamp = to_datetime.timestamp()
        for timeframe in event.timeframes:
            if timeframe not in self.timeframes:
                continue

            delta = calculate_time_delta(timeframe, 55)
            from_datetime = to_datetime - delta
            from_timestamp = from_datetime.timestamp()
            timeframe_name = get_timeframe_name(timeframe)

            df = get_kline_dataframe(symbol, timeframe_name, str(from_timestamp), str(to_timestamp))
            df["candle_low"] = df[["open", "close"]].min(axis=1)
            df["candle_high"] = df[["open", "close"]].max(axis=1)
            df["rsi13"] = talib.RSI(df['close'], timeperiod=13)

            newest_index, long_start_indexes = check_long_divergence(df["candle_low"], df["rsi13"])

            newest_index, short_start_indexes = check_short_divergence(df["candle_high"], df["rsi13"])

            if long_start_indexes or short_start_indexes:
                msg_title = f'{datetime.now().strftime("%H:%M")},{symbol},{timeframe},{self.name}'
            else:
                return

            if long_start_indexes:
                from_index = long_start_indexes[0]
                to_index = len(df) - 3
                msg = f'''{msg_title},LONG
{df.loc[from_index].open_time.strftime('%H:%M')}    > {df.loc[to_index].open_time.strftime('%H:%M')}
{df.loc[from_index].candle_low} \ {df.loc[to_index].candle_low}
{df.loc[from_index].rsi13:.2f}    / {df.loc[to_index].rsi13:.2f}
    '''
                print(msg)
                send_to_admin(msg)
            if short_start_indexes:
                from_index = short_start_indexes[0]
                to_index = len(df) - 3
                msg = f'''{msg_title},SHORT
{df.loc[from_index].open_time.strftime('%H:%M')}    > {df.loc[to_index].open_time.strftime('%H:%M')}
{df.loc[from_index].candle_high} / {df.loc[to_index].candle_high}
{df.loc[from_index].rsi13:.2f}    \ {df.loc[to_index].rsi13:.2f}
    '''
                print(msg)
                send_to_admin(msg)


if __name__ == '__main__':
    # how to use
    from strategy.rsi_divergence import RSIDivStrategy

    tf_event = TimeFrameEvent(constants.PERIOD_M5,
                              datetime.utcnow(),
                              datetime.utcnow(),
                              0,
                              datetime.utcnow())
    import queue

    q = queue.Queue(maxsize=2000)
    s = RSIDivStrategy(q)
    s.process(tf_event)
