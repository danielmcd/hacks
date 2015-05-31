#!/usr/bin/python
import calendar
import re
from quote_file import QuoteFile
from utils.utils import print_err

__author__ = 'sajarora'

class Month(object):
    def __init__(self, date):
        monthrange = calendar.monthrange(date.year, date.month)
        self.first_day_of_week = monthrange[0]
        self.last_day = monthrange[1]
        self.quarter = (date.month - 1) // 3
        self.half = (date.month - 1) // 6


def get_week_of_month(date):
    month = Month(date)
    week_of_month = (date.day - 1 + month.first_day_of_week) // 7
    first_full_week_offset = 1 if month.first_day_of_week == 0 else 0  # month starts on Monday
    return week_of_month + first_full_week_offset

class StockRecord(object):
    def __init__(self, stock, datapoint):
        self.date = date = datapoint.get_date()
        self.open_price = datapoint.get_open()
        self.close_price = datapoint.get_close()
        month = Month(date)
        self.day_of_week = date.weekday()
        self.day_of_month = date.day
        self.first_last_of_month = 0 if date.day == 1 else 2 if date.day == month.last_day else 1
        self.week_of_month = get_week_of_month(date)
        self.year_of_decade = date.year % 10
        self.month_of_year = date.month
        self.quart_of_year = month.quarter
        self.half_of_year = month.half

        #semantics
        self.symbol = 1 # symbol has to be encoded
        self.stoch_rsi = datapoint.get_stoch_rsi()
        self.candlestick = datapoint.get_candlestick()


class Stock(object):
    def __init__(self, filepath):
        self.filepath = filepath
        quote = QuoteFile(filepath)
        self.symbol = self._parse_symbol()
        self.datapoints = quote.get_datapoints()

    def _parse_symbol(self):
        try:
            return re.match(r'.*_([a-z.]+?)\.csv', self.filepath).group(1)
        except:
            print_err("ERROR: Cannot determine symbol from file name: " + self.filepath)
            return

    def get_filepath(self):
        return self.filepath

    def get_datapoints(self):
        return self.datapoints