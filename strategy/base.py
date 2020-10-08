import logging
import traceback
from datetime import datetime

from event.event import TimeFrameEvent, OrderHoldingEvent, StartUpEvent
from runner.handlers import BaseHandler

logger = logging.getLogger(__name__)


class StrategyBase(BaseHandler):
    name = None
    version = None
    magic_number = None
    queue = None

    weekdays = {0, 1, 2, 3, 4, 6, 7}  # Mon to Fri
    timeframes = set()
    hours = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}  # GMT hour

    symbols = ()
    subscribes = (TimeFrameEvent.type,)

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
        if event.type == TimeFrameEvent.type and set(event.timeframes).intersection(self.timeframes):
            self.signal(event)

    def send_event(self, event):
        self.put(event)
