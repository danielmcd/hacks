import calendar
import numpy
import os
import pickle
from nupic.encoders import ScalarEncoder, MultiEncoder, PassThroughEncoder
from nupic.research.TP import TP

__author__ = 'sajarora'

# date
COL_DAY_OF_WEEK = "day_of_week"
COL_DAY_OF_MONTH = "day_of_month"
COL_FIRST_LAST_MONTH = "first_last_of_month"
COL_WEEK_OF_MONTH = "week_of_month"
COL_MONTH_OF_YEAR = "month_of_year"
COL_QUART_OF_YEAR = "quart_of_year"
COL_HALF_OF_YEAR = "half_of_year"
COL_YEAR_OF_DECADE = "year_of_decade"

#semantics
COL_STOCH_RSI = "stoch_rsi"
COL_SYMBOL = "symbol"
COL_CANDLESTICK = "candlestick"


class Encoder(object):
    def __init__(self, improve_learning = True):
        self.tp = None
        self.improve_learning = improve_learning
        if self.improve_learning and os.path.isfile('tp.p'):
            print "Loading TP from tp.p and tp.tp"
            with open("tp.p", "r") as f:
                self.tp = pickle.load(f)
            self.tp.loadFromFile("tp.tp")
        else:
            self.tp = self._init_tp()

    def _get_encoder(self):
        # date encoding
        day_of_week_enc = ScalarEncoder(w=3, minval=0, maxval=7, radius=1.5,
                                        periodic=True, name=COL_DAY_OF_WEEK, forced=True)
        day_of_month_enc = ScalarEncoder(w=3, minval=1, maxval=31, radius=1.5,
                                         periodic=False, name=COL_DAY_OF_MONTH, forced=True)
        first_last_of_month_enc = ScalarEncoder(w=1, minval=0, maxval=2, radius=1, periodic=False,
                                                name=COL_FIRST_LAST_MONTH, forced=True)
        week_of_month_enc = ScalarEncoder(w=3, minval=0, maxval=6, radius=1.5,
                                          periodic=True, name=COL_WEEK_OF_MONTH, forced=True)
        month_of_year_enc = ScalarEncoder(w=3, minval=1, maxval=13, radius=1.5,
                                          periodic=True, name=COL_MONTH_OF_YEAR, forced=True)
        quarter_of_year_enc = ScalarEncoder(w=3, minval=0, maxval=4, radius=1.5,
                                            periodic=True, name=COL_QUART_OF_YEAR, forced=True)
        half_of_year_enc = ScalarEncoder(w=1, minval=0, maxval=2,
                                         radius=1, periodic=True, name=COL_HALF_OF_YEAR, forced=True)
        year_of_decade_enc = ScalarEncoder(w=3, minval=0, maxval=10, radius=1.5,
                                           periodic=True, name=COL_YEAR_OF_DECADE, forced=True)

        # semantics encoder
        stoch_rsi_enc = ScalarEncoder(w=5, minval=0, maxval=1,
                                      radius=1.2, periodic=False, name=COL_STOCH_RSI, forced=True)
        symbol_enc = ScalarEncoder(w=5, minval=0, maxval=1, radius=1.2, periodic=False, name=COL_SYMBOL, forced=True)
        candlestick_enc = PassThroughEncoder(50, name=COL_CANDLESTICK, forced=True)

        encoder = MultiEncoder()
        encoder.addEncoder(day_of_week_enc.name, day_of_week_enc)
        encoder.addEncoder(day_of_month_enc.name, day_of_month_enc)
        encoder.addEncoder(first_last_of_month_enc.name, first_last_of_month_enc)
        encoder.addEncoder(week_of_month_enc.name, week_of_month_enc)
        encoder.addEncoder(year_of_decade_enc.name, year_of_decade_enc)
        encoder.addEncoder(month_of_year_enc.name, month_of_year_enc)
        encoder.addEncoder(quarter_of_year_enc.name, quarter_of_year_enc)
        encoder.addEncoder(half_of_year_enc.name, half_of_year_enc)

        encoder.addEncoder(stoch_rsi_enc.name, stoch_rsi_enc)
        encoder.addEncoder(symbol_enc.name, symbol_enc)
        encoder.addEncoder(candlestick_enc.name, candlestick_enc)

        return encoder

    def _init_tp(self):
        return TP(numberOfCols=self._get_encoder().width, cellsPerColumn=1795,
                  initialPerm=0.5, connectedPerm=0.5,
                  minThreshold=10, newSynapseCount=10,
                  permanenceInc=0.1, permanenceDec=0.01,
                  activationThreshold=5,
                  globalDecay=0, burnIn=1,
                  checkSynapseConsistency=False,
                  pamLength=7)

    def run_encoder(self, stock_records):
        encoder = self._get_encoder()
        input_array = numpy.zeros(encoder.width, dtype="int32")

        for i, record in enumerate(stock_records):
            input_array[:] = numpy.concatenate(encoder.encodeEachField(record))
            self.tp.compute(input_array, enableLearn=True, computeInfOutput=False)
        self.tp.reset()

    def output_tp_file(self):
        print "saving TP to tp.p and tp.tp"
        self.tp.saveToFile("tp.tp")
        with open("tp.p", "w") as f:
            pickle.dump(self.tp, f)