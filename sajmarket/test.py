#!/usr/bin/python
from encoder.quote_file import QuoteFile
from encoder.trainer import Trainer

__author__ = 'sajarora'


def test():
    quote_file = QuoteFile('table_goog.csv')
    stock = quote_file.get_stock()
    print stock.get_symbol()
    buy_data, sell_data = stock.get_training_data()

    for data in buy_data:
        print data

    # for moment in windows.get_opportune_moments():
    #     print "Buy @: " + str(moment.buy_datapoint.get_date()) + " and Sell @: " + str(moment.sell_datapoint.get_date())



if __name__ == "__main__":
    test()