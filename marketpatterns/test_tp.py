#!/usr/bin/python
from __future__ import division

import calendar
import datetime
import numpy
import os.path
import pickle
from random import randrange, random, shuffle
import sys
import time

import nupic
from nupic.encoders import ScalarEncoder, MultiEncoder
from nupic.bindings.algorithms import SpatialPooler as SP
from nupic.research.TP10X2 import TP10X2 as TP




class Month(object):
    def __init__(self, date):
        monthrange = calendar.monthrange(date.year, date.month)
        self.first_day_of_week = monthrange[0]
        self.last_day = monthrange[1]
        self.quarter = (date.month - 1) // 3
        self.half = (date.month - 1) // 6



def get_week_of_month(date):
    month = Month(date)
    week_of_month = (date.day - 1 + month.first_day_of_week) // 7
    first_full_week_offset = 1 if month.first_day_of_week == 0 else 0  # month starts on Monday
    return week_of_month + first_full_week_offset


class DateRecord(object):
    def __init__(self, date):
        month = Month(date)
        self.dayOfWeek = date.weekday()
        self.dayOfMonth = date.day
        self.firstLastOfMonth = 0 if date.day == 1 else 2 if date.day == month.last_day else 1
        self.weekOfMonth = get_week_of_month(date)
        self.yearOfDecade = date.year % 10
        self.monthOfYear = date.month
        self.quarterOfYear = month.quarter
        self.halfOfYear = month.half


if __name__ == "__main__":
    day_of_week_enc = ScalarEncoder(w=3, minval=0, maxval=7, radius=1.5, periodic=True, name="dayOfWeek", forced=True)
    day_of_month_enc = ScalarEncoder(w=3, minval=1, maxval=31, radius=1.5, periodic=False, name="dayOfMonth", forced=True)
    first_last_of_month_enc = ScalarEncoder(w=1, minval=0, maxval=2, radius=1, periodic=False, name="firstLastOfMonth", forced=True)
    week_of_month_enc = ScalarEncoder(w=3, minval=0, maxval=6, radius=1.5, periodic=True, name="weekOfMonth", forced=True)
    month_of_year_enc = ScalarEncoder(w=3, minval=1, maxval=13, radius=1.5, periodic=True, name="monthOfYear", forced=True)
    quarter_of_year_enc = ScalarEncoder(w=3, minval=0, maxval=4, radius=1.5, periodic=True, name="quarterOfYear", forced=True)
    half_of_year_enc = ScalarEncoder(w=1, minval=0, maxval=2, radius=1, periodic=True, name="halfOfYear", forced=True)
    year_of_decade_enc = ScalarEncoder(w=3, minval=0, maxval=10, radius=1.5, periodic=True, name="yearOfDecade", forced=True)

    date_enc = MultiEncoder()
    date_enc.addEncoder(day_of_week_enc.name, day_of_week_enc)
    date_enc.addEncoder(day_of_month_enc.name, day_of_month_enc)
    date_enc.addEncoder(first_last_of_month_enc.name, first_last_of_month_enc)
    date_enc.addEncoder(week_of_month_enc.name, week_of_month_enc)
    date_enc.addEncoder(year_of_decade_enc.name, year_of_decade_enc)
    date_enc.addEncoder(month_of_year_enc.name, month_of_year_enc)
    date_enc.addEncoder(quarter_of_year_enc.name, quarter_of_year_enc)
    date_enc.addEncoder(half_of_year_enc.name, half_of_year_enc)

    if os.path.isfile('tp.p'):
	print "loading TP from tp.p and tp.tp"
	with open("tp.p", "r") as f:
	    tp = pickle.load(f)
	tp.loadFromFile("tp.tp")
    else:
	raise Exception("Missing tp")

    days = [datetime.date(y, m, d) for y in range(1998, 2013) for m in range(1, 13) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
    print days[0], days[1], days[-2], days[-1]

    inputs = [list(numpy.concatenate(numpy.nonzero(numpy.concatenate(date_enc.encodeEachField(DateRecord(d)))))) for d in days]
    input_sets = [set(i) for i in inputs]
    overlaps = []
    lengths = []
    days_predicted = []
    predicteds = []
    input_array = numpy.zeros(date_enc.width, dtype="int32")
    for i in xrange(len(days) - 1):
	if i == 0:
	    input_array[inputs[i]] = 1  # numpy.concatenate(date_enc.encodeEachField(DateRecord(days[i])))
	tp.compute(input_array, enableLearn=False, computeInfOutput=True)
	predicted = set(tp.getPredictedState().max(axis=1).nonzero()[0].flat)
	predicteds.append(predicted)
	input_array[inputs[i]] = 0
	input_array[inputs[i+1]] = 1
	actual = input_sets[i+1]
	overlaps.append(len(predicted & actual))
	lengths.append(len(predicted))
	# count how many days are precisely predicted by this actual
	num_days_predicted = 0
	for j in xrange(len(days)):
	    test = input_sets[j]
	    if len(predicted & test) == 20:
		num_days_predicted += 1
	days_predicted.append(num_days_predicted)
	if i % 100 == 0:
	    print i

    minimum = numpy.min(overlaps)
    print "Min =", minimum
    print "Mean=", numpy.mean(overlaps)
    maximum = numpy.max(overlaps)
    print "Max =", maximum

    min_length = numpy.min(lengths)
    max_length = numpy.max(lengths)
    avg_length = numpy.mean(lengths)
    print "Length Min =", min_length
    print "Length Max =", max_length
    print "Length Avg =", avg_length

    for i, o in enumerate(overlaps):
    	if o < maximum:
	    print "Overlap =", o, days[i], days[i+1]

    for i, p in enumerate(days_predicted):
	if p > 1:
	    print "Ambiguous days predicted =", p, "predicted length =", len(predicteds[i]), days[i], days[i+1]


