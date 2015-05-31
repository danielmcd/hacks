#!/usr/bin/python
import datetime
from utils.utils import DotDictify

__author__ = 'sajarora'

WINDOW_MAX_TIMEDELTA = datetime.timedelta(days=14)
WINDOW_MIN_TIMEDELTA = datetime.timedelta(days=3)
CHANGE_THRESHOLD = 1.0

class Window:
    def __init__(self, stock):
        self.stock = stock
        self.datapoints = stock.get_datapoints()

    def get_opportune_moments(self):
        windows = []
        for i, current_datapoint in enumerate(self.datapoints):
            window_datapoints = []
            max_date = current_datapoint.get_date() + WINDOW_MAX_TIMEDELTA
            for j in range(i, len(self.datapoints)):
                if self.datapoints[j].get_date() <= max_date:
                    window_datapoints.append(self.datapoints[j])
                else:
                    break
            window = {
                "symbol": self.stock.get_filepath(),
                "start": current_datapoint.get_date(),
                "open_low": current_datapoint.get_open(),
                "open_low_date": current_datapoint.get_date(),
                "buy_datapoint": current_datapoint,
                "close_high": current_datapoint.get_close(),
                "close_high_date": current_datapoint.get_date(),
                "sell_datapoint": current_datapoint,
                "delta": 0,
                "end": 0
            }
            for datapoint in window_datapoints:
                if datapoint.get_close() > window["close_high"]:
                    window["close_high"] = datapoint.get_close()
                    window["close_high_date"] = datapoint.get_date()
                    window["sell_datapoint"] = datapoint
                window["end"] = datapoint.get_date()

            for datapoint in window_datapoints:
                if datapoint.get_date() < window["close_high_date"]:
                    if datapoint.get_open() < window["open_low"]:
                        window["open_low"] = datapoint.get_open()
                        window["open_low_date"] = datapoint.get_date()
                        window["buy_datapoint"] = datapoint
                    else:
                        break
            if window["close_high_date"] - window["open_low_date"] < WINDOW_MIN_TIMEDELTA:
                continue
            window["delta"] = window["close_high"] - window["open_low"]
            if window["delta"] < CHANGE_THRESHOLD:
                continue
            windows.append(window)

        opportune_buys = []

        #select windows
        skip = 0
        for i in range(0, len(windows)):
            if skip:
                skip -= 1
                continue
            current_end_date = windows[i]["close_high_date"]
            best_window = windows[i]
            max_change = windows[i]["delta"]
            for j in range(i, len(windows)):
                if windows[j]["close_high_date"] > current_end_date:
                    break
                skip += 1  # this record is already checked move forward
                change = windows[j]["delta"]
                if change > max_change:
                    max_change = change
                    best_window = windows[j]
            opportune_buys.append(DotDictify(best_window))

        # for window in opportune_buys:
        #     print "Low: " + str(window["open_low_date"]) + \
        #         " High: " + str(window["close_high_date"]) + " -- Change: " + str(window["close_high"] - window["open_low"])

        return opportune_buys
