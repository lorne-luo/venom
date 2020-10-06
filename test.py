from event.handler import *
import queue

from event.runner import HeartbeatRunner

q = queue.Queue(maxsize=2000)
d = DebugHandler(q)
t = TimeFrameTicker(q)
r = HeartbeatRunner(q, 5, *[d, t])
r.run()