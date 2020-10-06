import settings
from binance.client import Client

BINANCE_API_KEY = settings.BINANCE_API_KEY

BINANCE_API_SECRET = settings.BINANCE_API_SECRET

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def get_binance_client():
    return client