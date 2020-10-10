import logging
import talib
from datetime import datetime
import settings
from binance_client.constants import get_timeframe_name
from binance_client.kline import get_kline_dataframe
from event.event import SignalEvent, SignalAction, TimeFrameEvent
from binance_client import constants
from signals.divergence import long_divergence, short_divergence
from strategy.base import StrategyBase
from utils.time import calculate_time_delta, get_candle_time, get_now
from antman.telstra import send_to_admin

logger = logging.getLogger(__name__)


class RSIDivStrategy(StrategyBase):
    """
    RSI Divergence
    """
    name = 'RSIDiv'
    version = '1.0'
    magic_number = '20201005'
    source = 'https://www.babypips.com/trading/forex-hlhb-system-20190128'

    timeframes = sorted((constants.PERIOD_M15,
                         constants.PERIOD_M30,
                         constants.PERIOD_H1,
                         constants.PERIOD_H4,
                         constants.PERIOD_D1),
                        reverse=True)

    subscribes = [TimeFrameEvent.type]
    symbols = ('BTCUSDT', 'ETHUSDT')

    def check_run_history(self, symbol, timeframe, now):
        """True already run ,skip
        False doesnt run, go ahead"""
        candle_time = get_candle_time(now, timeframe)
        if self._candle_times[symbol][timeframe] >= candle_time:
            return True

        self._candle_times[symbol][timeframe] = candle_time
        return False

    def signal_symbol(self, symbol, event):
        to_datetime = datetime.utcnow()
        to_timestamp = to_datetime.timestamp()

        now = get_now(settings.TIMEZONE)

        for timeframe in self.timeframes:
            if self.check_run_history(symbol, timeframe, now):
                # already processed
                continue

            delta = calculate_time_delta(timeframe, 60)
            from_datetime = to_datetime - delta
            from_timestamp = from_datetime.timestamp()
            timeframe_name = get_timeframe_name(timeframe)

            # get dataframe
            df = get_kline_dataframe(symbol, timeframe_name, str(from_timestamp), str(to_timestamp))
            df["candle_low"] = df[["open", "close"]].min(axis=1)
            df["candle_high"] = df[["open", "close"]].max(axis=1)
            df["rsi"] = talib.RSI(df['close'], timeperiod=14)

            newest_index, long_reversal_indexes, long_continue_indexes = long_divergence(df["candle_low"], df["rsi"])

            newest_index, short_reversal_indexes, short_continue_indexes = short_divergence(df["candle_high"],
                                                                                            df["rsi"])

            # print(from_datetime, to_datetime)
            # print(newest_index, long_start_indexes, short_reversal_indexes)

            newest_price = df.loc[len(df) - 1].close
            if long_reversal_indexes or short_reversal_indexes or long_continue_indexes or short_continue_indexes:
                msg_title = f'{timeframe}|{datetime.now().strftime("%H:%M")},{symbol.replace("USDT","")},{self.name}@{newest_price},R'
                self.send_sms(df, msg_title,
                              long_reversal_indexes, short_reversal_indexes,
                              long_continue_indexes, short_continue_indexes)

    def send_sms(self, df, msg_title,
                 long_start_indexes, short_start_indexes,
                 long_continue_indexes, short_continue_indexes):
        to_index = len(df) - 3

        if long_start_indexes:
            from_index = long_start_indexes[0]
            msg = f'''{msg_title},RL
{df.loc[from_index].open_time.strftime('%m-%d %H:%M')}-{df.loc[to_index].open_time.strftime('%m-%d %H:%M')}
{df.loc[from_index].candle_low} \ {df.loc[to_index].candle_low}
{df.loc[from_index].rsi:.2f} / {df.loc[to_index].rsi:.2f}
'''
            print(datetime.now())
            print(msg)
            send_to_admin(msg)

        if short_start_indexes:
            from_index = short_start_indexes[0]
            msg = f'''{msg_title},RS
{df.loc[from_index].open_time.strftime('%m-%d %H:%M')}-{df.loc[to_index].open_time.strftime('%m-%d %H:%M')}
{df.loc[from_index].candle_high} / {df.loc[to_index].candle_high}
{df.loc[from_index].rsi:.2f} \ {df.loc[to_index].rsi:.2f}
'''
            print(datetime.now())
            print(msg)
            send_to_admin(msg)

        if long_continue_indexes:
            from_index = long_continue_indexes[0]
            msg = f'''{msg_title},CL
{df.loc[from_index].open_time.strftime('%m-%d %H:%M')}-{df.loc[to_index].open_time.strftime('%m-%d %H:%M')}
{df.loc[from_index].candle_low} / {df.loc[to_index].candle_low}
{df.loc[from_index].rsi:.2f} \ {df.loc[to_index].rsi:.2f}
'''
            print(datetime.now())
            print(msg)
            send_to_admin(msg)

        if short_continue_indexes:
            from_index = short_continue_indexes[0]
            msg = f'''{msg_title},CS
{df.loc[from_index].open_time.strftime('%m-%d %H:%M')}-{df.loc[to_index].open_time.strftime('%m-%d %H:%M')}
{df.loc[from_index].candle_high} \ {df.loc[to_index].candle_high}
{df.loc[from_index].rsi:.2f} / {df.loc[to_index].rsi:.2f}
'''
            print(datetime.now())
            print(msg)
            send_to_admin(msg)


if __name__ == '__main__':
    # how to use
    from strategy.rsi_divergence import RSIDivStrategy

    tf_event = TimeFrameEvent(constants.PERIOD_H1,
                              datetime.utcnow(),
                              datetime.utcnow(),
                              0,
                              datetime.utcnow())

    s = RSIDivStrategy()
    s.process(tf_event)
