#!/usr/bin/python
import sys
__author__ = 'sajarora'

DEFAULT_PERIOD = 14


class DotDictify(dict):
    marker = object()
    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError, 'expected dict'

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, DotDictify):
            value = DotDictify(value)
        super(DotDictify, self).__setitem__(key, value)

    def __getitem__(self, key):
        found = self.get(key, DotDictify.marker)
        if found is DotDictify.marker:
            found = DotDictify()
            super(DotDictify, self).__setitem__(key, found)
        return found

    __setattr__ = __setitem__
    __getattr__ = __getitem__


def print_err(*args, **kwargs):
    print(args, sys.stderr, kwargs)


def get_first_average(datapoints, stoch_period):
    avg_gains = 0
    avg_losses = 0
    counter = 0
    for index, datapoint in enumerate(datapoints):
        if index == 0:
            continue

        if index <= stoch_period:
            avg_gains += max(0, datapoint.get_close() - datapoints[index - 1].get_close())
            avg_losses += (abs(min(0, datapoint.get_close() - datapoints[index - 1].get_close())))
            counter += 1
        else:
            avg_gains /= counter
            avg_losses /= counter
            break
    return avg_gains, avg_losses


def get_next_average(datapoint, prev_datapoint, avg_gain, avg_loss, stoch_period):
        avg_gain = ((avg_gain * stoch_period - 1) +
                    max(0, datapoint.get_close() - prev_datapoint.get_close()))/stoch_period
        avg_loss = ((avg_loss * stoch_period - 1) +
                    abs(min(0, datapoint.get_close() - prev_datapoint.get_close())))/stoch_period
        datapoint.avg_gain = avg_gain
        datapoint.avg_loss = avg_loss
        datapoint.rs = avg_gain/avg_loss
        datapoint.rsi = 100 - (100/(1+datapoint.rs))
        return datapoint

