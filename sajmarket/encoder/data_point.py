#!/usr/bin/python
from utils.utils import DotDictify

__author__ = 'sajarora'


class DataPoint:
    def __init__(self, data):
        self.data = DotDictify(data)

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






