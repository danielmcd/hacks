#!/usr/bin/python
import random
from trainer_file import TrainerFile
from window import Window

__author__ = 'sajarora'

SPLIT_PROPORTION_TRAINING = 0.7

DATA_TRAIN_FILE = 'train_file.csv'
DATA_TEST_FILE = 'test_file.csv'

class Trainer:
    def __init__(self, stock):
        self.stock = stock
        self.train_buy_raw_data = []
        self.train_sell_raw_data = []
        self.test_buy_raw_data = []
        self.test_sell_raw_data = []

    def calculate_windows(self, save):
        window = Window(self.stock)
        windows = window.get_opportune_moments()
        train_data, test_data = self._split_shuffle_data(windows)

        train_file = self.make_trainer_file(train_data, DATA_TRAIN_FILE, save)
        test_file = self.make_trainer_file(test_data, DATA_TEST_FILE, save)
        return train_file, test_file

    @staticmethod
    def _split_shuffle_data(data):
        random.shuffle(data)
        train_data_length = int(len(data) * SPLIT_PROPORTION_TRAINING)
        train_data = data[:train_data_length]
        test_data = data[train_data_length+1:]
        return train_data, test_data

    def make_trainer_file(self, data, path, save):
        print self.stock
        trainer_file = TrainerFile(path,
                                   stock=self.stock,
                                   windows=data)
        if save:
            trainer_file.save()
        return trainer_file