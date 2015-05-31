#!/usr/bin/python
import sys
import talib

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


def calculate_stoch_rsi(close, period=DEFAULT_PERIOD):
    talib.STOCHRSI(close, period)

