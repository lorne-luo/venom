from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance_client.configs import get_binance_client
from pprint import pprint


def process_message(msg):
    print("message type: {}".format(msg['e']))
    pprint(msg)
    """
    {
      "e": "kline",     // Event type
      "E": 123456789,   // Event time
      "s": "BNBBTC",    // Symbol
      "k": {
        "t": 123400000, // Kline start time
        "T": 123460000, // Kline close time
        "s": "BNBBTC",  // Symbol
        "i": "1m",      // Interval
        "f": 100,       // First trade ID
        "L": 200,       // Last trade ID
        "o": "0.0010",  // Open price
        "c": "0.0020",  // Close price
        "h": "0.0025",  // High price
        "l": "0.0015",  // Low price
        "v": "1000",    // Base asset volume
        "n": 100,       // Number of trades
        "x": false,     // Is this kline closed?
        "q": "1.0000",  // Quote asset volume
        "V": "500",     // Taker buy base asset volume
        "Q": "0.500",   // Taker buy quote asset volume
        "B": "123456"   // Ignore
      }
    }
    """

client=get_binance_client()



bm = BinanceSocketManager(client, user_timeout=60)
# start any sockets here, i.e a trade socket
# conn_key = bm.start_trade_socket('BTCUSDT', process_message)
conn_key = bm.start_kline_socket('BTCUSDT', process_message, Client.KLINE_INTERVAL_1MINUTE)
# then start the socket manager
bm.start()
