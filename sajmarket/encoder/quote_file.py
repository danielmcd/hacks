#!/usr/bin/python
import csv
import datetime
from data_point import DataPoint

__author__ = 'sajarora'

##
# Class that encapsulates a csv quote file
# extracts datapoints from the file and converts them
# to a Stock object
##
class QuoteFile:
    def __init__(self, file):
        self.filename = file

    def parse_quote_line(self, quote_line):
        date_str, time_str, open_str, high_str, low_str, close_str, volume_str = quote_line
        return DataPoint({"date": datetime.datetime.strptime(date_str, "%Y%m%d").date(),
                "open": float(open_str),
                "high": float(high_str),
                "low": float(low_str),
                "close": float(close_str),
                "volume": float(volume_str)})

    def get_datapoints(self):
        with open(self.filename, 'rb') as csvfile:
            quote_reader = csv.reader(csvfile, delimiter=',')
            datapoints = []
            for quote_line in quote_reader:
                datapoints.append(self.parse_quote_line(quote_line))
            return datapoints