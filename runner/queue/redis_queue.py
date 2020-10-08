import logging
import pickle
import redis
import settings

logger = logging.getLogger(__name__)


class RedisQueue(object):
    """Simple Queue with Redis Backend"""

    def __init__(self, name, db, host, port):
        self.__db = redis.StrictRedis(host=host,
                                      port=port,
                                      db=db,
                                      decode_responses=True)
        self.key = 'queue:%s' % name

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        if item:
            self.__db.rpush(self.key, item)

    def get(self, block=False, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            return item
        else:
            return None

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)


queue = RedisQueue('default', db=settings.SYSTEM_CHANNEL, host=settings.REDIS_HOST,
                   port=settings.REDIS_PORT)


def get_msg():
    data = queue.get(block=False)
    return pickle.loads(data)


def put_msg(msg):
    try:
        data = pickle.dumps(msg)
        queue.put(data)
    except Exception as ex:
        logger.error('Enqueue error: %s' % ex)
