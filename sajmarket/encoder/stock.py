#!/usr/bin/python
import calendar
from trainer import Trainer
from utils.utils import DotDictify, calculate_stoch_rsi

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
        date = datapoint.get_date()
        month = Month(date)
        self.day_of_week = date.weekday()
        self.day_of_month = date.day
        self.first_last_of_month = 0 if date.day == 1 else 2 if date.day == month.last_day else 1
        self.week_of_month = get_week_of_month(date)
        self.year_of_decade = date.year % 10
        self.month_of_year = date.month
        self.quarter_of_year = month.quarter
        self.half_of_year = month.half
        self.stoch_rsi = datapoint.get_stoch_rsi()

class Stock:
    def __init__(self, symbol, datapoints=[]):
        self.symbol = symbol
        self.datapoints = datapoints

    def get_symbol(self):
        return self.symbol

    def add_datapoint(self, datapoint):
        self.datapoints.append(datapoint)

    def clear_datapoints(self):
        self.datapoints = []

    def get_datapoints(self):
        return self.datapoints

    def get_training_data(self):
        trainer = Trainer(self)
        buy_moments, sell_moments = trainer.get_training_data()

        for moment in buy_moments:
            records = []
            close_records = []
            for datapoint in moment:
                close_records.append(datapoint.get_close())
                datapoint.set_stoch_rsi(calculate_stoch_rsi(close_records))
                if datapoint.get_stoch_rsi() is None:
                    continue
                records.append(StockRecord(self, datapoint))
            print records