#!/usr/bin/python
from encoder.data_aggregator import QuoteFile

__author__ = 'sajarora'


def test():
    quote_file = QuoteFile('table_goog.csv')
    stock = quote_file.get_stock()
    print stock.get_symbol()

if __name__ == "__main__":
    test()