# Implement a trading strategy based on the trained buy and sell models

import datetime

BUFFER_TRADE = datetime.timedelta(days=3)

class Trader(object):
    def __init__(self, symbol, start_date, trade_window):
        self.symbol = symbol
        self.start_date = start_date
        self.trade_window = trade_window
        self.earnings = 0

    def is_expired(self, day):
        ''' @return true if day is outside the trade_window of the trade '''
        return day > self.day + self.trade_window

    def get_earnings(self):
        return self.earnings

    def set_earnings(self, earnings):
        self.earnings = earnings


    def start_trading(self):


        def __init__(self, start_date, end_date, trade_window, pattern_window, buy_model, buy_threshold, sell_model, sell_threshold, quotes):
            '''
        @param start_date: (datetime) the date to start running the model.  Quotes must include data for
                           this date and prior dates within pattern_window.

        @param end_date:  (datetime) the date to end running the model.  Quotes must include data for
                  this date and subsequent dates within trade_window to ensure all trades are closed.

        @param trade_window:  (timedelta) a time duration during which a trade will be made.  All positions
                              are held open no longer than this duration.

        @param pattern_window:  (timedelta) a time duration corresponding to the length of the pattern used
                                for training the buy and sell models.

        @param buy_model:  a Decoder model containing a TP trained to recognize lead-in patterns for entering
                           trades.

        @param buy_threshold:  threshold [0, 1] below which the buy model anomaly score predicts a buy pattern

        @param sell_model:  a Decoder model containing a TP trained to recognize lead-in patterns for closing
                            trades.

        @param sell_threshold:  threshold [0, 1] below which the sell model anomaly score predicts a sell pattern

        @param quotes:  historical price data for all stocks to be traded using the given models
        '''
            if start_date > end_date:
                raise Exception("Invalid date range: " + str(start_date) + " - " + str(end_date))
            self.start_date = start_date
            self.end_date = end_date
            self.trade_window = trade_window
            self.pattern_window = pattern_window
            self.buy_model = buy_model
            self.buy_threshold = buy_threshold
            self.sell_model = sell_model
            self.sell_threshold = sell_threshold
            self.quotes = quotes
            self.open_trades = []

        # Approach:
        #   Evaluate the model on the time window up to and including today
        #   If anomaly is low, open a trade for tomorrow
        #   For each open trade:
        #       Evaluate the sell model
        #       if anomaly is low or trade window is exceeded, sell and close the position
        #       calculate the cumulative gain/loss
        #   Graph the activity
        #       Line 1: cumulative gain/loss
        #       Line 2: # open trades
        def run_trader(self):
            '''
        Run the trading models, execute trades, and track cumulative earnings.
        @return list of TradeStat objects containing day, number of open trades, cumulative earnings
        '''
            cumulative_earnings = 0
            stats = []
            for day in self._get_trading_days():
                # only open trades between the date endpoints
                # additional days are included to allow closing of all trades
                if day <= self.end_date:
                    for symbol in self._get_symbols():
                        score = self.buy_model.run_decoder(self._get_pattern_dataset(symbol, day))
                        if score <= self.buy_threshold:
                            # if model works, consider adding RSI < 40 as an additional safety check
                            self._open_trade(symbol, day)
                for trade in self.open_trades:
                    score = self.sell_model.run_decoder(self._get_pattern_dataset(symbol, day))
                    if (score <= self.sell_threshold and day - trade.day >= datetime.timedelta(days=3)) or trade.is_expired(day):
                        # if model works, consider adding RSI > 60 as an additional safety check
                        self._close_trade(trade, day)
                        cumulative_earnings += trade.get_earnings()
                stats.append(TradeStat(day, len(self.open_trades), cumulative_earnings))
            return stats

        def _get_trading_days(self):
            '''
        @return the dates present in the quote history which fall between the start and end dates
                include additional trade window days on the end to allow for closing final trades
        '''
            days = []
            date = self.day
            while self.day < date < self.trade_window + self.day + BUFFER_TRADE:
                days.append(date)
                date += datetime.timedelta(days=1)
            return days

        def _get_symbols(self):
            '''
        @return the symbols to be traded
        '''
            raise Exception("not implemented yet")

        def _get_pattern_dataset(self, symbol, day):
            '''
        @return a dataset starting for the given symbol at the given day and going back for pattern window
        '''
            raise Exception("not implemented yet")

        def _open_trade(self, symbol, day):
            self.open_trades.append(Trade(symbol, day, self.trade_window))

        def _close_trade(self, trade, day):
            '''
        Close the given trade, remove it from open trades and calculate the earnings
        Updates trade with its earnings
        '''
            raise Exception("not implemented yet")


    def print_usage_and_exit():
        print_err("\n" + sys.argv[0] + " <quote_file_path> <buy_model_name> <sell_model_name> <year> <pattern_window> <trade_window> <buy_threshold> <sell_threshold>")
        print_err("\nquote_file_path\tpath to file containing quote data")
        print_err("buy_model_name\tname of buy model without extension")
        exit(1)


    def check_command_line_args():
        if len(sys.argv) < 9:
            print_usage_and_exit()

    if __name__ == "__main__":
        # Args:  quote_file_path, buy_model_name, sell_model_name, year, pattern_window, trade_window, buy_threshold, sell_threshold
        quote_file_path, buy_model_name, sell_model_name, year, pattern_window, trade_window, buy_threshold, sell_threshold = check_command_line_args()
