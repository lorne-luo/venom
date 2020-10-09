import logging
import traceback
from collections import defaultdict
from datetime import datetime

import settings
from event.event import TimeFrameEvent, OrderHoldingEvent, StartUpEvent
from runner.handlers import BaseHandler
from runner.timeframe import TimeframePublisher
from utils.time import get_candle_time, get_now

logger = logging.getLogger(__name__)


class StrategyBase(BaseHandler):
    name = None
    version = None
    magic_number = None
    queue = None

    weekdays = {0, 1, 2, 3, 4, 6, 7}  # Mon to Fri
    timeframes = tuple()
    hours = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}  # GMT hour

    symbols = ()
    subscribes = (TimeFrameEvent.type,)

    def __init__(self, context):
        super(StrategyBase, self).__init__(context)

        now = get_now(settings.TIMEZONE)
        self._candle_times = defaultdict(dict)

        for symbol in self.symbols:
            for timeframe in self.timeframes:
                self._candle_times[symbol][timeframe] = get_candle_time(now, timeframe)

    def __str__(self):
        return '%s v%s #%s' % (self.name, self.version, self.magic_number)

    def signal(self, event):
        for symbol in self.symbols:
            try:
                self.signal_symbol(symbol, event)
            except Exception as ex:
                traceback_detail = traceback.format_exc()
                logger.error(f'[STRATEGY_SIGNAL] {symbol}={ex}')
                logger.error(traceback_detail)

    def signal_symbol(self, symbol, event):
        raise NotImplementedError

    def can_open(self):
        return True

    def process(self, event):
        if event.type == TimeFrameEvent.type:
            self.signal(event)

    def send_event(self, event):
        self.put(event)
