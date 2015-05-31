#!/usr/bin/python
from encoder.quote_file import QuoteFile
from encoder.encoder import Encoder

__author__ = 'sajarora'


def test():
    encoder = Encoder()

    quote_file = QuoteFile('table_goog.csv')
    stock = quote_file.get_stock()
    stock.get_training_data()

    # for moment in windows.get_opportune_moments():
    #     print "Buy @: " + str(moment.buy_datapoint.get_date()) + " and Sell @: " + str(moment.sell_datapoint.get_date())



if __name__ == "__main__":
    test()