


class HeartbeatRunner(Runner):
    def __init__(self, queue, heartbeat=5, *args, **kwargs):
        super(HeartbeatRunner, self).__init__(queue)
        self.heartbeat = heartbeat or 1  # seconds
        self.register(*args)

    def run(self):
        print('%s statup.' % self.__class__.__name__)
        print('Registered handler: %s' % ', '.join([x.__class__.__name__ for x in self.handlers]))

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
                        print(f"New {event.type} Event: {event.__dict__ if event.type !=EventType.HEARTBEAT else ''}")
                    else:
                        logger.debug(f"New {event.type} Event: {event.__dict__}")

                    self.handle_event(event)


class StreamRunnerBase(Runner):
    broker = ''
    account = None

    def __init__(self, queue, pairs, *args, **kwargs):
        super(StreamRunnerBase, self).__init__(queue)
        if args:
            self.register(*args)
        self.pairs = pairs
        self.prices = self._set_up_prices_dict()

    def _set_up_prices_dict(self):
        prices_dict = dict(
            (k, v) for k, v in [
                (p, {"bid": None, "ask": None, "time": None, "spread": None}) for p in self.pairs
            ]
        )

        return prices_dict


