# Implement a trading strategy based on the trained buy and sell models

import datetime
import ystockquote
from encoder.data_point import DataPoint
from encoder.encoder import Encoder
from encoder.stock import StockRecord
from encoder.trainer_file import TrainerFile

BUFFER_TRADE = 14
MIN_TRADE_DAYS = datetime.timedelta(days=3)
MAX_TRADE_DAYS = datetime.timedelta(days=14)
MAX_OPEN_TRADES = 4

class Trade(object):
    def __init__(self,
                 start_date,
                 start_price,
                 end_date,
                 end_price):
        self.start_date = start_date
        self.start_price = start_price
        self.end_date = end_date
        self.end_price = end_price
        self.is_open = True

    def get_earnings(self):
        return self.end_price - self.start_price

    def close_trade(self):
        self.is_open = False

class Trader(object):
    def __init__(self, symbol, start_date, trade_window):
        self.symbol = symbol
        self.start_date = start_date
        self.trade_window = trade_window
        self.earnings = 0

    def is_expired(self, day):
        ''' @return true if day is outside the trade_window of the trade '''
        return day > self.start_date + self.trade_window

    def get_earnings(self):
        return self.earnings

    def set_earnings(self, earnings):
        self.earnings = earnings

    def start_trading(self):
        encoder = Encoder(enableLearn=False)
        counter = 0
        score_buffer = []
        open_trades = []
        while self.start_date <= datetime.datetime.now():
            if len(score_buffer) > 14:
                score_buffer.pop(0)

            datasets = self._get_stock_data()
            for index, dataset in enumerate(datasets):
                score = encoder.run_decoder(index, dataset)
                #score_buffer.append({counter: score})
                print score.score

            counter += 1
            self.start_date += datetime.timedelta(days=1)



    def _get_stock_data(self):
        data = ystockquote.get_historical_prices(self.symbol,
                                          datetime.datetime.strftime(self.start_date, '%Y-%m-%d'),
                                          datetime.datetime.strftime(self.start_date + self.trade_window, '%Y-%m-%d'))
        datapoints = []
        for key, record in data.iteritems():
            datapoint = {
                "date": datetime.datetime.strptime(key, '%Y-%m-%d').date(),
                "high": float(record["High"]),
                "low": float(record["Low"]),
                "open": float(record["Open"]),
                "close": float(record["Close"]),
                "volume": float(record["Volume"])
            }
            datapoints.append(DataPoint(datapoint))

        datapoints = TrainerFile.get_encoded_data_from_array([datapoints,], True)
        datasets = []
        for dataset in datapoints:
            stock_records = []
            for record in dataset:
                stock_records.append(StockRecord(self.symbol, record))
            datasets.append(stock_records)
        return datasets
