#!/usr/bin/python
import os
import sys
from encoder.quote_file import QuoteFile
from encoder.encoder import Encoder
from encoder.utils.utils import print_err

__author__ = 'sajarora'

def print_usage_and_exit():
    print_err("\n" + sys.argv[0] + " <quote_file_path> <use_existing_tp>")
    print_err("\nquote_file_path\tpath for the quote file")
    print_err("use_existing_tp\tTrue of False: improve learning")
    exit(1)

def check_command_line_args():
    if len(sys.argv) < 2:
        print_usage_and_exit()
    if not os.path.exists(sys.argv[1]):
        print_err("ERROR: " + sys.argv[1] + " is not a file")
        print_usage_and_exit()
    if not str(sys.argv[2]).lower() == "true" or str(sys.argv[2]).lower() == "false":
        print_err("ERROR: " + sys.argv[2] + " is not true of false")
        print_usage_and_exit()
    return sys.argv[1], True if str(sys.argv[2]).lower() == "true" else False

def main(quote_file_path, improve_learning):
    encoder = Encoder(improve_learning)

    quote_file = QuoteFile(quote_file_path)
    stock = quote_file.get_stock()
    training_buy_datasets, training_sell_datasets = stock.get_training_datasets()

    total_datasets = len(training_buy_datasets)
    total_trained = 0
    for i, dataset in enumerate(training_buy_datasets):
        encoder.run_encoder(dataset)
        total_trained += len(dataset)
        print "Completed " + str(i) + "/" + str(total_datasets) + " sets...Trained on: " + \
              str(total_trained) + " records."

    encoder.output_tp_file()

if __name__ == "__main__":
    quote_file, improve_learning = check_command_line_args()
    main(quote_file, improve_learning)