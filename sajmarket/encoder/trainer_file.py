#!/usr/bin/python
import csv
import datetime
from candleencoder import CandlestickEncoder
from utils.utils import DotDictify, get_first_average, get_next_average
from stock import Stock, StockRecord

__author__ = 'sajarora'

PRECEDING_TIMEDELTA = datetime.timedelta(days=40)
DEFAULT_STOCH_PERIOD = 14


class Moment(object):
    def __init__(self, symbol, date):
        self.symbol = symbol
        self.date = date

class Column(object):
    def __init__(self, field_name, field_type, flag):
        self.field_name = field_name
        self.field_type = field_type
        self.flag = flag


class TrainerFile(object):
    def __init__(self, filepath, stock=None,
                 windows=[], parse=False):
        self.filepath = filepath
        self.stock = stock
        if parse:
            self.windows = self._read_file()
        else:
            self.windows = windows

    def save(self):
        if self.stock is None:
            raise Exception("Unexpected case: TrainerFile must have a stock symbol to save!")

        columns = []
        columns.append(Column("symbol", "string", ""))
        columns.append(Column("start", "datetime", ""))
        columns.append(Column("open_low", "float", ""))
        columns.append(Column("open_low_date", "datetime", ""))
        columns.append(Column("close_high", "float", ""))
        columns.append(Column("close_high_date", "datetime", ""))
        columns.append(Column("delta", "float", ""))
        columns.append(Column("end", "datetime", ""))

        with open(self.filepath, "w") as f:
            for window in self.windows:
                row = []
                row.append(self.stock.get_filepath())
                row.append(window["start"].strftime("%Y%m%d"))
                row.append(str(window["open_low"]))
                row.append(window["open_low_date"].strftime("%Y%m%d"))
                row.append(str(window["close_high"]))
                row.append(window["close_high_date"].strftime("%Y%m%d"))
                row.append(str(window["delta"]))
                row.append(window["end"].strftime("%Y%m%d"))
                f.write(",".join(row) + "\n")

    def get_windows(self):
        return self.windows

    def get_preceding_pattern(self, buy):
        data = []
        for window in self.get_windows():
            if buy:
                data.append(self._get_preceding_data(window.symbol, window.open_low_date))
            else:
                data.append(self._get_preceding_data(window.symbol, window.close_high_date))
        return data

    def _get_preceding_data(self, filepath, start_date):
        stock = Stock(filepath)
        datapoints = stock.get_datapoints()
        preceding_data = []
        for datapoint in datapoints:
            if datapoint.get_date() > start_date - PRECEDING_TIMEDELTA:
                if datapoint.get_date() < start_date:
                    preceding_data.append(datapoint)
                else:
                    break
        return preceding_data

    def parse_quote_line(self, quote_line):
        symbol, start, open_low, open_low_date, close_high, close_high_date, delta, end = quote_line
        window = {
                "symbol": symbol,
                "start": datetime.datetime.strptime(start, "%Y%m%d").date(),
                "open_low": open_low,
                "open_low_date": datetime.datetime.strptime(open_low_date, "%Y%m%d").date(),
                "close_high": close_high,
                "close_high_date": datetime.datetime.strptime(close_high_date, "%Y%m%d").date(),
                "delta": delta,
                "end": datetime.datetime.strptime(end, "%Y%m%d").date()
            }
        return DotDictify(window)

    def _read_file(self):
        with open(self.filepath, 'rb') as csvfile:
            moments = csv.reader(csvfile, delimiter=',')
            datapoints = []
            for index, line in enumerate(moments):
                datapoints.append(self.parse_quote_line(line))
            return datapoints


    def get_encoded_data(self, buy, stoch_period=DEFAULT_STOCH_PERIOD):
        data_pattern = self.get_preceding_pattern(buy)
        datapoints = self.get_encoded_data_from_array(data_pattern, buy, stoch_period)
        datasets = []
        for dataset in datapoints:
            stock_records = []
            for record in dataset:
                stock_records.append(StockRecord(self, record))
            datasets.append(stock_records)
        return datasets

    @staticmethod
    def get_encoded_data_from_array(data_array, buy, stoch_period=DEFAULT_STOCH_PERIOD):
        datapoints = []
        for moment in data_array:
            # calculate first average gain/loss
            avg_gain, avg_loss = get_first_average(moment, stoch_period)

            # iterate through all datapoints adding appropriate stoch values
            dataset = []
            last_rsi = []
            for i in range(stoch_period + 1, len(moment)):
                if len(last_rsi) > stoch_period - 1:
                    last_rsi.pop(0)
                # get the next average
                datapoint = get_next_average(moment[i], moment[i - 1], avg_gain, avg_loss, stoch_period)
                last_rsi.append(datapoint.get_rsi()) # add to last rsi

                lowest_low_rsi = 100
                highest_high_rsi = 0
                for rsi in last_rsi:
                    lowest_low_rsi = rsi if rsi < lowest_low_rsi else lowest_low_rsi
                    highest_high_rsi = rsi if rsi > highest_high_rsi else highest_high_rsi
                if highest_high_rsi - lowest_low_rsi > 0:
                    datapoint.stoch_rsi = (datapoint.rsi - lowest_low_rsi)/(highest_high_rsi - lowest_low_rsi)
                else:
                    continue

                # encode candlestick data
                candlestick = CandlestickEncoder(moment[i], moment[i - 1])
                datapoint.candlestick = candlestick.encode()

                dataset.append(datapoint)
            datapoints.append(dataset)
        return datapoints