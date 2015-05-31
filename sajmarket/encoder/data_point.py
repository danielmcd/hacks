#!/usr/bin/python
from utils.utils import DotDictify

__author__ = 'sajarora'


class DataPoint:
    def __init__(self, data):
        self.data = DotDictify(data)
        self.avg_gain = 0
        self.avg_loss = 0
        self.rs = 0
        self.rsi = 0
        self.stoch_rsi = 0
        self.candlestick = []

    def get_date(self):
        return self.data.date

    def get_open(self):
        return self.data.open

    def get_close(self):
        return self.data.close

    def get_high(self):
        return self.data.high

    def get_low(self):
        return self.data.low

    def get_volume(self):
        return self.data.volume

    def set_stoch_rsi(self, value):
        self.stoch_rsi = value

    def get_stoch_rsi(self):
        return self.stoch_rsi

    def get_avg_gain(self):
        return self.avg_gain

    def get_avg_loss(self):
        return self.avg_loss

    def get_rs(self):
        return self.rs

    def get_rsi(self):
        return self.rsi

    def get_candlestick(self):
        return self.candlestick








