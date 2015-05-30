#!/usr/bin/python
# Split moves into training and test sets
# Copyright 2015 Daniel McDonald, All rights reserved
# ============================================================================
from __future__ import print_function
from __future__ import division
import csv
import math
import os
import random
import sys


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def print_usage_and_exit():
    print_err("\n" + sys.argv[0] + " <moves_file> <split_pct>")
    print_err("\nmoves_file\tfile containing symbol and date of move")
    print_err("split_pct\t\tpercentage of moves to include in training set; remainder goes to test set")
    exit(1)


def is_number(s):
    try:
	float(s)
	return True
    except ValueError:
	return False


def check_command_line_args():
    if len(sys.argv) < 3:
	print_usage_and_exit()
    if not os.path.isfile(sys.argv[1]):
    	print_err("ERROR: " + sys.argv[1] + " is not a file")
	print_usage_and_exit()
    if not is_number(sys.argv[2]):
    	print_err("ERROR: " + sys.argv[2] + " is not a number")
	print_usage_and_exit()
    return sys.argv[1], float(sys.argv[2])


def do_split(moves_file, split_pct):
    print(moves_file, split_pct)
    with open(moves_file, "rb") as f:
    	lines = f.readlines()

    random.shuffle(lines)

    num_lines = len(lines)
    split_point = int(math.ceil(num_lines * split_pct/100))
    print("split point =", split_point)

    with open("train.txt", "w") as f:
    	print(len(lines[:split_point]))
    	for line in lines[:split_point]:
	    f.write(line)

    with open("test.txt", "w") as f:
    	print(len(lines[split_point:]))
    	for line in lines[split_point:]:
	    f.write(line)


if __name__ == "__main__":
    moves_file, split_pct = check_command_line_args()
    do_split(moves_file, split_pct)

