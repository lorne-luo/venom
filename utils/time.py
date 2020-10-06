import time
from datetime import datetime, timedelta
from dateparser import parse
from dateutil.relativedelta import relativedelta, MO

from settings import constants
from utils.string import extract_number


def parse_timestamp(timestamp, utc=False):
    if utc:
        return datetime.utcfromtimestamp(timestamp)
    else:
        return datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())


def datetime_to_str(dt, format='%Y-%m-%d %H:%M:%S:%f'):
    if dt:
        return dt.strftime(format)
    return None


def str_to_datetime(string, format='%Y-%m-%d %H:%M:%S:%f'):
    if string:
        try:
            dt = datetime.strptime(string, format)
        except:
            dt = parse(string)

        return dt
    return None


def timestamp_to_str(timestamp, datetime_fmt="%Y/%m/%d %H:%M:%S:%f"):
    return datetime.fromtimestamp(timestamp).strftime(datetime_fmt)


def calculate_time_delta(interval, count):
    number = int(interval)
    k_count = number * (count + 1)
    if interval in [constants.PERIOD_M1, constants.PERIOD_M5, constants.PERIOD_M15, constants.PERIOD_M30]:
        return timedelta(minutes=k_count)
    elif interval in [constants.PERIOD_H1, constants.PERIOD_H4]:
        return timedelta(hours=k_count)
    elif interval == constants.PERIOD_D1:
        return timedelta(days=k_count)
    elif interval == constants.PERIOD_W1:
        return timedelta(days=7 * k_count)
    elif interval == constants.PERIOD_W1:
        return timedelta(days=31 * k_count)


def get_candle_time(time, timeframe):
    """
    return newest candle stick start time
    2020-10-05 23:34:45 -> 2020-10-05 23:30:00 in M5
    """

    t = time.replace(second=0, microsecond=0)

    if timeframe in [constants.PERIOD_M1, constants.PERIOD_M5, constants.PERIOD_M15, constants.PERIOD_M30]:
        minute = t.minute // timeframe * timeframe
        return t.replace(minute=minute)
    if timeframe in [constants.PERIOD_H1, constants.PERIOD_H4]:
        t = t.replace(minute=0)
        hourframe = int(timeframe / 60)
        hour = t.hour // hourframe * hourframe
        return t.replace(hour=hour)
    if timeframe in [constants.PERIOD_D1]:
        return t.replace(hour=0, minute=0)
    if timeframe in [constants.PERIOD_W1]:
        monday = time + relativedelta(weekday=MO(-1))
        return monday.replace(hour=0, minute=0, second=0, microsecond=0)
    if timeframe in [constants.PERIOD_MN1]:
        return t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    raise NotImplementedError
