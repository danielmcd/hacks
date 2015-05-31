#!/usr/bin/python
import calendar
import numpy
import talib
from trainer import Trainer
from utils.utils import DotDictify, get_first_average, get_next_average

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

        #semantics
        self.symbol = stock.get_symbol()
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

    def get_training_data(self, stoch_period=14):
        trainer = Trainer(self)
        buy_moments, sell_moments = trainer.get_training_data()

        trainable_buy_data = self._analyze_data(buy_moments, stoch_period)
        trainable_sell_data = self._analyze_data(buy_moments, stoch_period)
        return trainable_buy_data, trainable_sell_data

    def _analyze_data(self, moments, stoch_period):
        trainable_moments = []
        for moment in moments:
            # calculate first average gain/loss
            avg_gain, avg_loss = get_first_average(moment, stoch_period)

            # iterate through all datapoints adding appropriate stoch values
            trainable_data = []
            last_rsi = []
            for i in range(stoch_period + 1, len(moment)):
                if len(last_rsi) > stoch_period - 1:
                    last_rsi.pop(0)
                datapoint = get_next_average(moment[i], moment[i - 1], avg_gain, avg_loss, stoch_period)
                last_rsi.append(datapoint.get_rsi())

                lowest_low_rsi = 100
                highest_high_rsi = 0
                for rsi in last_rsi:
                    lowest_low_rsi = rsi if rsi < lowest_low_rsi else lowest_low_rsi
                    highest_high_rsi = rsi if rsi > highest_high_rsi else highest_high_rsi
                if highest_high_rsi - lowest_low_rsi > 0:
                    datapoint.stoch_rsi = (datapoint.rsi - lowest_low_rsi)/(highest_high_rsi - lowest_low_rsi)
                else:
                    continue
                trainable_data.append(StockRecord(self, datapoint))
            trainable_moments.append(trainable_data)
        return trainable_moments