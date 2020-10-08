import logging
import pickle
from queue import LifoQueue, Empty

queue = LifoQueue(maxsize=2000)

logger = logging.getLogger(__name__)


def get_msg():
    try:
        data = queue.get(block=False)
        return pickle.loads(data)
    except Empty:
        return None


def put_msg(msg):
    try:
        data = pickle.dumps(msg)
        queue.put(data)
    except Exception as ex:
        logger.error('Enqueue error: %s' % ex)
