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
	tp = TP(numberOfCols=date_enc.width, cellsPerColumn=1795,
		initialPerm=0.5, connectedPerm=0.5,
		minThreshold=10, newSynapseCount=10,
		permanenceInc=0.1, permanenceDec=0.01,
		activationThreshold=5,
		globalDecay=0, burnIn=1,
		checkSynapseConsistency=False,
		pamLength=7)

    days = [datetime.date(y, m, d) for y in range(1998, 2013) for m in range(1, 13) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
    print days[0], days[1], days[-2], days[-1]

    input_array = numpy.zeros(date_enc.width, dtype="int32")
    for pres in xrange(10):
    	print 'Pass', pres
	for i, d in enumerate(days):
	    if (i + 1) % 100 == 0:
	    	print i + 1
	    if (i + 1) % 28 == 0:
		tp.reset()
	    input_array[:] = numpy.concatenate(date_enc.encodeEachField(DateRecord(d)))
	    tp.compute(input_array, enableLearn=True, computeInfOutput=False)
	    #input_array[:] = numpy.concatenate(date_enc.encodeEachField(DateRecord(days[i + 1])))
	    #tp.compute(input_array, enableLearn=True, computeInfOutput=False)

    print "saving TP to tp.p and tp.tp"
    tp.saveToFile("tp.tp")
    with open("tp.p", "w") as f:
	    pickle.dump(tp, f)

