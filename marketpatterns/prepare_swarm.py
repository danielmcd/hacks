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

from find_move import *
from train_tp import DateRecord


def print_usage_and_exit():
    print_err("\n" + sys.argv[0] + " <quote_dir> <moves_file> <before_window> <after_window> <swarm_data_file>")
    print_err("\nquote_dir\tdirectory containing quote files")
    print_err("moves_file\tfile containing symbol and date of movement")
    print_err("before_window\ttime to include before the movement date (e.g., 1d, 2w)")
    print_err("after_window\ttime to include after the movement date (e.g., 1d, 2w)")
    print_err("swarm_data_file\toutput file to contain extracted data to use as input to swarming")
    exit(1)


def check_command_line_args():
    if len(sys.argv) < 6:
	print_usage_and_exit()
    if not os.path.exists(sys.argv[1]):
    	print_err("ERROR: " + sys.argv[1] + " is not a file or directory")
	print_usage_and_exit()
    if not os.path.isfile(sys.argv[2]):
    	print_err("ERROR: " + sys.argv[2] + " is not a file")
	print_usage_and_exit()
    if not re.match(r'^[1-9][0-9]*[dw]$', sys.argv[3]):
    	print_err("ERROR: " + sys.argv[3] + " is not a time window")
	print_usage_and_exit()
    if not re.match(r'^[1-9][0-9]*[dw]$', sys.argv[4]):
    	print_err("ERROR: " + sys.argv[4] + " is not a time window")
	print_usage_and_exit()
    return sys.argv[1], sys.argv[2], Window(sys.argv[3]), Window(sys.argv[4]), sys.argv[5]


def load_moves(moves_file):
    moves = []
    with open(moves_file, "r") as csvfile:
    	move_reader = csv.reader(csvfile, delimiter=" ")
	for move_line in move_reader:
	    moves.append(parse_move_line(move_line))
    return moves


class Move(object):
    def __init__(self, symbol, date):
    	self.symbol = symbol
	self.date = date


def parse_move_line(move_line):
    symbol, date_str = move_line
    return Move(symbol, datetime.datetime.strptime(date_str, "%Y-%m-%d").date())


class QuoteData(object):
    def __init__(self, symbol, quotes):
    	self.symbol = symbol
	self.quotes = quotes  # list of dicts containing parsed daily quote rows


def extract_quotes_around_moves(quotes, moves, before_window, after_window):
    data = []
    for move in moves:
    	# quotes is a dict keyed by symbol where the value is a list of dicts containing
	# each row of data given a symbol, search the history for that symbol to find all
	# rows accommodated by the before and after windows from the move date
	try:
	    quote_history = quotes[move.symbol]
	    extract = []
	    # TODO make this more efficient
	    for q in quote_history:
	        qdate = q["date"]
	    	if (qdate < move.date and before_window.accommodates(qdate, move.date)) or (qdate >= move.date and after_window.accommodates(move.date, qdate)):
		    extract.append(q)
	    data.append(QuoteData(move.symbol, extract))
	    print(move.symbol, len(extract))
	except KeyError:
	    print_err("ERROR: Movement symbol was not found in the quote data: " + move.symbol)
    return data


class Column(object):
    def __init__(self, field_name, field_type, flag):
    	self.field_name = field_name
	self.field_type = field_type
	self.flag = flag


def write_swarm_data_file(swarm_data_file, data):
    columns = []
    columns.append(Column("reset", "bool", "R"))
    columns.append(Column("symbol", "string", ""))
    columns.append(Column("dayOfWeek", "int", ""))
    columns.append(Column("dayOfMonth", "int", ""))
    columns.append(Column("firstLastOfMonth", "int", ""))
    columns.append(Column("weekOfMonth", "int", ""))
    columns.append(Column("yearOfDecade", "int", ""))
    columns.append(Column("monthOfYear", "int", ""))
    columns.append(Column("quarterOfYear", "int", ""))
    columns.append(Column("halfOfYear", "int", ""))
    # TODO convert to candlestick description
    # relative position (up, down, gapped up, gapped down, engulfing, above/below midpoint)
    # length of body
    # color of body
    # length of upper shadow (long, short, or missing - hammer, marubozu)
    # length of lower shadow (long, short, or missing - inverted hammer, marubozu)
    columns.append(Column("date", "datetime", ""))
    columns.append(Column("open", "float", ""))
    columns.append(Column("high", "float", ""))
    columns.append(Column("low", "float", ""))
    columns.append(Column("close", "float", ""))
    columns.append(Column("volume", "float", ""))
    # TODO add stat columns
    #columns.append(Column("gain", "float", ""))
    #columns.append(Column("loss", "float", ""))
    #columns.append(Column("avgGain14", "float", ""))
    #columns.append(Column("avgLoss14", "float", ""))
    #columns.append(Column("gainWk", "float", ""))
    #columns.append(Column("lossWk", "float", ""))
    #columns.append(Column("avgGainWk14", "float", ""))
    #columns.append(Column("avgLossWk14", "float", ""))
    #columns.append(Column("RSI14", "float", ""))
    #columns.append(Column("RSIWk14", "float", ""))
    #columns.append(Column("StochRSI14", "float", ""))
    #columns.append(Column("StochRSIWk14", "float", ""))
    #columns.append(Column("MovingAvg14", "float", ""))
    #columns.append(Column("MovingAvgWk14", "float", ""))

    with open(swarm_data_file, "w") as f:
    	f.write(",".join([c.field_name for c in columns]) + "\n")
    	f.write(",".join([c.field_type for c in columns]) + "\n")
    	f.write(",".join([c.flag for c in columns]) + "\n")
	for quote_data in data:
	    reset_flag = True
	    for quote in quote_data.quotes:
		row = []
	    	if reset_flag:
		    row.append("1")
		    reset_flag = False
		else:
		    row.append("0")
		row.append(quote_data.symbol)
		date = DateRecord(quote["date"])
		row.append(str(date.dayOfWeek))
		row.append(str(date.dayOfMonth))
		row.append(str(date.firstLastOfMonth))
		row.append(str(date.weekOfMonth))
		row.append(str(date.yearOfDecade))
		row.append(str(date.monthOfYear))
		row.append(str(date.quarterOfYear))
		row.append(str(date.halfOfYear))
		row.append(str(quote["date"]))
		row.append(str(quote["open"]))
		row.append(str(quote["high"]))
		row.append(str(quote["low"]))
		row.append(str(quote["close"]))
		row.append(str(quote["volume"]))
		f.write(",".join(row) + "\n")


if __name__ == "__main__":
    # parse command line to get moves file and window
    quote_path, moves_file, before_window, after_window, swarm_data_file = check_command_line_args()

    # load quotes
    quotes = load_quotes(quote_path)

    # load moves
    moves = load_moves(moves_file)

    # add statistics for selected symbols
    #add_statistics(quotes, set([m.symbol for m in moves]))

    # extract quotes within window
    data = extract_quotes_around_moves(quotes, moves, before_window, after_window)

    # write swarm data file
    write_swarm_data_file(swarm_data_file, data)

