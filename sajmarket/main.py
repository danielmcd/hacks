#!/usr/bin/python
import getopt
from optparse import OptionParser
import sys
from encoder.encoder import Encoder
from encoder.utils.utils import print_err
from encoder.trainer_file import TrainerFile
from encoder.stock import Stock, StockRecord
from encoder.trainer import Trainer

__author__ = 'sajarora'

def print_usage_and_exit():
    print_err("\n" + sys.argv[0] + " --train|--model -q <quote_file_path> -t <train_file>")
    print_err("\nquote_file_path\tpath for the quote file")
    print_err("use_existing_tp\tTrue of False: improve learning")
    exit(1)

def check_command_line_args():
    parser = OptionParser()
    parser.add_option("-q", "--quote_file", dest="quote_file_path",
                      help="parse a quote file", metavar="FILE")
    parser.add_option("--t", "--train",
                      action="store_true", dest="train", default=True,
                      help="train the nupic model")
    parser.add_option("-f", "--train_file", dest="train_data_file",
                      help="training file with preselected dates and quote file paths")

    return parser.parse_args()



def start_training(quote_file_path, train_data_file, buy=True):
    encoder = Encoder(True)
    if train_data_file is not None and train_data_file != '':
        trainer_file = TrainerFile(train_data_file, parse=True)
    else:
        stock = Stock(quote_file_path)
        trainer = Trainer(stock)
        trainer_file, _ = trainer.calculate_windows(True)

    encoded_data = trainer_file.get_encoded_data(buy)
    total_datasets = len(encoded_data)
    total_trained = 0
    for i, dataset in enumerate(encoded_data):
        encoder.run_encoder(dataset)
        total_trained += len(dataset)
        print "Completed " + str(i) + "/" + str(total_datasets) + " sets...Trained on: " + \
              str(total_trained) + " records."

    encoder.output_tp_file()


def start_modeling():
    pass


def main(train=True, quote_file_path=None, train_data_file=None):
    if train:
        start_training(quote_file_path, train_data_file)
    else:
        start_modeling()

if __name__ == "__main__":
    options, args = check_command_line_args()
    main(options.train, options.quote_file_path, options.train_data_file)