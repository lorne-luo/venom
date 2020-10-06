import logging
import time
import queue
import settings

from event.event import EventType, HeartBeatEvent
from .base import Runner

logger = logging.getLogger(__name__)


class HeartbeatRunner(Runner):
    def __init__(self, queue, heartbeat=5, *args, **kwargs):
        super(HeartbeatRunner, self).__init__(queue)
        self.heartbeat = heartbeat or 1  # seconds
        self.register(*args)

    def run(self):
        print('%s statup.' % self.__class__.__name__)
        print('Registered handler: %s' % ', '.join([x.__class__.__name__ for x in self.handlers]))
        print('\n')
        while True:
            try:
                event = self.get(False)
                if not event:
                    raise queue.Empty
            except queue.Empty:
                time.sleep(self.heartbeat)
                self.put(HeartBeatEvent(self.loop_counter))
                self.loop_counter += 1
            else:
                if event:
                    if settings.DEBUG:
                        logger.debug(
                            f"New {event.type} Event: {event.__dict__ if event.type !=EventType.HEARTBEAT else ''}")
                    if event.type == EventType.TIMEFRAME:
                        print(f"New timeframe: {event.timeframe} {event.time}")

                    self.handle_event(event)


if __name__ == '__main__':
    # python -m event.runner
    from event.handler import *
    import queue

    q = queue.Queue(maxsize=2000)
    d = DebugHandler(q)
    timeframe_ticker = TimeFrameTicker(q, timezone=0)
    r = HeartbeatRunner(q, 1, d, timeframe_ticker)
    r.run()
