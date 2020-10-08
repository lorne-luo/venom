import logging
import sys
import traceback
from abc import abstractmethod

from .handlers import BaseHandler

logger = logging.getLogger(__name__)


class BaseRunner:
    loop_counter = 0
    handlers = []
    running = True
    initialized = False

    def __init__(self, enqueue, dequeue):
        self._enqueue = enqueue
        self._dequeue = dequeue

    def put(self, event):
        return self._enqueue(event)

    def get(self):
        return self._dequeue()

    def run(self):
        raise NotImplementedError

    def register(self, *args):
        for handler in args:
            if isinstance(handler, BaseHandler):
                # todo register runner as context
                handler.set_context(self)
                self.handlers.append(handler)

    def handle_event(self, event):
        """loop handlers to process event"""
        re_put = False
        for handler in self.handlers:
            if '*' in handler.subscribes:
                result = self.process_event(handler, event)
                re_put = result or re_put
                continue
            elif event.type in handler.subscribes:
                result = self.process_event(handler, event)
                re_put = result or re_put
        if re_put:
            if event.tried > 3:
                logger.error('[EVENT_RETRY] tried to many times abort, event=%s' % event)
            else:
                event.tried += 1
                self.put(event)

    def process_event(self, handler, event):
        """process event by single handler"""
        try:
            return handler.process(event)
        except Exception as ex:
            logger.error('[EVENT_PROCESS] %s, event=%s' % (ex, event.__dict__))
            # print trace stack
            extracted_list = traceback.extract_tb(ex.__traceback__)
            for item in traceback.StackSummary.from_list(extracted_list).format()[:8]:
                logger.error(item.strip())
            self.handle_error(ex)

    @abstractmethod
    def handle_error(self, ex):
        ...

    def print(self):
        print(self.handlers)

    def stop(self):
        self.running = False
        sys.exit(0)
