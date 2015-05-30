#!/usr/bin/python
# Find examples of a movement
# Copyright 2015 Daniel McDonald, All rights reserved
# ============================================================================
from __future__ import print_function
from __future__ import division
import csv
import datetime
import glob
import numpy as np
import os
import os.path
import re
import sys


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class TimeUnit(object):
    def __init__(self, unit):
        if unit not in ['d', 'w']:
	    raise Exception("Invalid time unit: " + unit)
        self.unit_type = unit

    def __str__(self):
    	return self.unit_type

class Window(object):
    def __init__(self, arg):
        p = re.compile(r'^([1-9][0-9]*)([dw])$')
	m = p.match(arg)
	self.duration = int(m.group(1))
	self.unit = TimeUnit(m.group(2))

    def accommodates(self, start_date, end_date):
    	''' Determine if the two dates are within a time window of each other. '''
	if str(self.unit) == 'd':
	    #print(end_date - start_date, start_date, end_date)
	    return end_date - start_date <= datetime.timedelta(days=self.duration)  # TODO Move the timedelta into TimeUnit
	elif str(self.unit) == 'w':
	    return end_date - start_date <= datetime.timedelta(weeks=self.duration)
	raise Exception("Invalid window unit: " + str(self.unit))


def print_usage_and_exit():
    print_err("\n" + sys.argv[0] + " <quote_dir> <amount> <window>")
    print_err("\nquote_dir\tdirectory containing quote files")
    print_err("amount\t\tamount of movement (e.g., 2, -2)")
    print_err("window\t\ttime for movement to occur (e.g., 1d, 2w)")
    exit(1)


def is_number(s):
    try:
	float(s)
	return True
    except ValueError:
	return False


def check_command_line_args():
    if len(sys.argv) < 4:
	print_usage_and_exit()
    if not os.path.exists(sys.argv[1]):
    	print_err("ERROR: " + sys.argv[1] + " is not a file or directory")
	print_usage_and_exit()
    if not is_number(sys.argv[2]):
    	print_err("ERROR: " + sys.argv[2] + " is not a number")
	print_usage_and_exit()
    if not re.match(r'^[1-9][0-9]*[dw]$', sys.argv[3]):
    	print_err("ERROR: " + sys.argv[3] + " is not a time window")
	print_usage_and_exit()
    return sys.argv[1], float(sys.argv[2]), Window(sys.argv[3])


def load_quotes(quote_path):
    quotes = dict()
    add_quotes_from_folder(quotes, quote_path)
    return quotes


def add_quotes_from_folder(quotes, quote_path):
    for path in glob.iglob(os.path.join(quote_path, "*")):
	if os.path.isdir(path):
	    add_quotes_from_folder(quotes, path)
	elif path.endswith(".csv"):
	    #print("File: ", path)
	    add_quotes_from_file(quotes, path)


def add_quotes_from_file(quotes, quote_path):
    try:
	symbol = re.match(r'.*_([a-z.]+?)\.csv', quote_path).group(1)
    except:
    	print_err("ERROR: Cannot determine symbol from file name: " + quote_path)
	return
    with open(quote_path, 'rb') as csvfile:
    	quote_reader = csv.reader(csvfile, delimiter=',')
	quote_history = []
	for quote_line in quote_reader:
	    quote_history.append(parse_quote_line(quote_line))
	quotes[symbol] = quote_history


def parse_quote_line(quote_line):
    date_str, time_str, open_str, high_str, low_str, close_str, volume_str = quote_line
    return {"date": datetime.datetime.strptime(date_str, "%Y%m%d").date(),
            "open": float(open_str),
	    "high": float(high_str),
	    "low": float(low_str),
	    "close": float(close_str),
	    "volume": float(volume_str)}


def find_movements(quotes, movement, window):
    movements = []
    for symbol in quotes.keys():
    	for i, quote in enumerate(quotes[symbol]):
	    # If there's a movement within the following window, record symbol and date
	    j = i
	    for k, q in enumerate(quotes[symbol][i + 1:]):
	    	if window.accommodates(quote["date"], q["date"]):
		    j = i + 1 + k
		else:
		    break
	    if j > i:
		close = [q["close"] for q in quotes[symbol][i:j + 1]]
		moves = [close[v] - close[u] for u in xrange(0, len(close) - 1) for v in xrange(u + 1, len(close))]
		if (movement > 0 and max(moves) >= movement) or (movement < 0 and min(moves) <= movement):
		    movements.append({"symbol": symbol, "date": quote["date"]})
		    #print(symbol, i, j, quote["date"], moves)
    return movements


if __name__ == "__main__":
    quote_path, movement, window = check_command_line_args()
    # load data from files
    quotes = load_quotes(quote_path)
    # find movement matches
    movements = find_movements(quotes, movement, window)
    # write movements
    for m in movements:
    	print(m["symbol"], m["date"])

