#!/usr/bin/python
import datetime
from trader import Trader


TRADE_WINDOW = datetime.timedelta(days=17)

def start_prediction():
    trader = Trader('GOOG', datetime.datetime.now() - datetime.timedelta(days=200), TRADE_WINDOW)
    trader.start_trading()

if __name__ == "__main__":
    start_prediction()

