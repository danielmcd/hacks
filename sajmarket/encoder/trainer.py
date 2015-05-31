#!/usr/bin/python
import random
import datetime
from window import Window

__author__ = 'sajarora'

SPLIT_PROPORTION_TRAINING = 0.7
PRECEDING_TIMEDELTA = datetime.timedelta(days=28)


class Trainer:
    def __init__(self, stock):
        self.stock = stock
        self.train_buy_raw_data = []
        self.train_sell_raw_data = []
        self.test_buy_raw_data = []
        self.test_sell_raw_data = []

    def get_training_data(self):
        return self._make_training_data()

    def _make_training_data(self):
        window = Window(self.stock)
        moments = window.get_opportune_moments()
        train_data, test_data = self._split_shuffle_data(moments)

        buy_data = []
        sell_data = []
        for moment in train_data:
            buy_data.append(self._get_preceding_data(moment.buy_datapoint.get_date()))
            sell_data.append(
                self._get_preceding_data(moment.sell_datapoint.get_date()))
        return buy_data, sell_data

    def _make_test_data(self):
        window = Window(self.stock)
        moments = window.get_opportune_moments()
        train_data, test_data = self._split_shuffle_data(moments)

        buy_data = []
        sell_data = []
        for moment in test_data:
            buy_data.append(self._get_preceding_data(moment.buy_datapoint.get_date()))
            sell_data.append(
                self._get_preceding_data(moment.sell_datapoint.get_date()))
        self.test_buy_raw_data = buy_data
        self.test_sell_raw_data = sell_data

    @staticmethod
    def _split_shuffle_data(data):
        random.shuffle(data)
        train_data_length = int(len(data) * SPLIT_PROPORTION_TRAINING)
        train_data = data[:train_data_length]
        test_data = data[train_data_length+1:]
        return train_data, test_data

    def _get_preceding_data(self, start_date):
        datapoints = self.stock.get_datapoints()
        preceding_data = []
        for datapoint in datapoints:
            if datapoint.get_date() > start_date - PRECEDING_TIMEDELTA:
                if datapoint.get_date() < start_date:
                    preceding_data.append(datapoint)
                else:
                    break
        return preceding_data

    def _get_during_data(self, buy_date, sell_date):
        datapoints = self.stock.get_datapoints()
        proceeding_data = []
        for datapoint in datapoints:
            if datapoint.get_date() > buy_date:
                if datapoint.get_date() < sell_date:
                    proceeding_data.append(datapoint)
                else:
                    break
        return proceeding_data