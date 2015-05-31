#!/usr/bin/python
from trainer import Trainer
from utils.utils import DotDictify

__author__ = 'sajarora'


class Stock:
    def __init__(self, symbol, datapoints=[]):
        self.symbol = symbol
        self.datapoints = datapoints

    def get_symbol(self):
        return self.symbol


    def add_datapoint(self, datapoint):
        self.datapoints.append(datapoint)


    def clear_datapoints(self):
        self.datapoints = []


    def get_datapoints(self):
        return self.datapoints

    def get_training_data(self):
        trainer = Trainer(self)
        return trainer.get_encoded_data()