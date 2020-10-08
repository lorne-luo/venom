import logging
import time
import queue
from abc import abstractmethod
from threading import Thread
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO

from binance_client import constants
from utils.time import get_candle_time

import settings

from event.event import EventType, HeartBeatEvent
from .base import BaseRunner
from event.event import TimeFrameEvent

logger = logging.getLogger(__name__)


class TimeframePublisher:
    """
    thread to send heartbeat
    """
    name = 'TimeframePublisher'
    heartbeat = None
    heartbeat_counter = 0
    timezone = 0
    TIMEFRAME_CHOICES = sorted(constants.PERIOD_CHOICES, reverse=True)

    def __init__(self, publish_method, heartbeat=None):
        if not publish_method:
            raise Exception('publish_method is mandatory.')
        self.publish_method = publish_method
        self.heartbeat = heartbeat
        self._active = False

        self._candle_times = {}
        now = self._get_now()
        for timeframe in self.TIMEFRAME_CHOICES:
            self._candle_times[timeframe] = get_candle_time(now, timeframe)

    def _get_now(self):
        now = datetime.utcnow() + relativedelta(hours=self.timezone)
        return now

    def run(self):
        while self._active:
            now = self._get_now()
            timestamp = int(now.timestamp())

            # heart beat
            if self.heartbeat and not timestamp % self.heartbeat:
                hbe = HeartBeatEvent(self.heartbeat_counter)
                self.publish_method(hbe)
                self.heartbeat_counter += 1
                # print(f'heartbeat, {now}')

            # publish timeframe event
            new_timeframes = []
            newest_time = None
            for timeframe in self.TIMEFRAME_CHOICES:
                newest_time = get_candle_time(now, timeframe)
                if self._candle_times[timeframe] != newest_time:
                    new_timeframes.append(timeframe)
                    self._candle_times[timeframe] = newest_time

            if new_timeframes:
                event = TimeFrameEvent(new_timeframes,
                                       newest_time,
                                       self._candle_times[new_timeframes[0]],
                                       self.timezone,
                                       now)
                self.publish_method(event)

            time.sleep(1)
        print('HeartbeatPublisher stopped.')

    def stop(self):
        self._active = False
        if self.heartbeat_counter:
            print(f'Total heartbeat = {self.heartbeat_counter}')

    def start(self):
        self._active = True
        self.timer = Thread(target=self.run)
        self.timer.setName(self.name)
        self.timer.setDaemon(True)
        self.timer.start()


class TimeframeRunner(BaseRunner):
    """Basic runner with a heartbeat and timeframe event"""

    def __init__(self, enqueue, dequeue, heartbeat=None, *args, **kwargs):
        super(TimeframeRunner, self).__init__(enqueue, dequeue)
        self.register(*args)

        self.timeframe_publisher = TimeframePublisher(enqueue, heartbeat=heartbeat)

    def run(self):
        print('%s statup.' % self.__class__.__name__)
        print('Registered handler: %s' % ', '.join([x.__class__.__name__ for x in self.handlers]))
        print('\n')
        self.timeframe_publisher.start()

        while self.running:
            event = self.get()

            if event:
                if settings.DEBUG:
                    logger.debug(
                        f"New {event.type} Event: {event.__dict__ if event.type !=EventType.HEARTBEAT else ''}")

                self.handle_event(event)

    def stop(self):
        self.timeframe_publisher.stop()
        super(TimeframeRunner, self).stop()


if __name__ == '__main__':
    timerhandler = TimeframePublisher(5, lambda: 2)
    timerhandler.handle = lambda msg: print(1)
    timerhandler.start()

    # python -m event.runner
    from event.handler import *
    import queue

    q = queue.Queue(maxsize=2000)
    d = DebugHandler(q)
    timeframe_ticker = TimeFrameTicker(q, timezone=0)
    r = TimeframeRunner(q, 1, d, timeframe_ticker)
    r.run()
