#!/usr/bin/python
# Class to encode a candlestick as a sparse distributed representation
# ============================================================================
class CandlestickEncoder(object):
    def __init__(self, quotes, symbol):
        data = [[d["open"], d["high"], d["low"], d["close"]] for d in quotes[symbol]]
        self.opens = [o for o, _, _, _ in data]
        self.closes = [c for _, _, _, c in data]
        self.tops = [max(o, c) for o, _, _, c in data]
        self.mids = [(o + c) / 2.0 for o, _, _, c in data]
        self.bottoms = [min(o, c) for o, _, _, c in data]
        self.highs = [h for _, h, _, _ in data]
        self.lows = [l for _, _, l, _ in data]
    
    def encode(self, i):
        relative_position_bits = self.encode_relative_position(i)
        body_length_bits = self.encode_body_length(i)
        body_color_bits = self.encode_body_color(i)
        upper_shadow_bits = self.encode_upper_shadow(i)
        lower_shadow_bits = self.encode_lower_shadow(i)
        bits = relative_position_bits + body_length_bits + body_color_bits + upper_shadow_bits + lower_shadow_bits
        return bits
    
    def encode_relative_position(self, i):
        bottoms = self.bottoms
        tops = self.tops
        mids = self.mids
        if bottoms[i] > tops[i-1]:  # gapped up
            bits = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        elif bottoms[i] <= tops[i-1] and bottoms[i] > mids[i-1] and tops[i] > tops[i-1]:  # pierced high
            bits = [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        elif bottoms[i] <= tops[i-1] and bottoms[i] <= mids[i-1] and tops[i] > tops[i-1]:  # overlapped high
            bits = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        elif bottoms[i] == bottoms[i-1] and tops[i] == tops[i-1]:  # equal
            bits = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0]
        elif bottoms[i] <= bottoms[i-1] and tops[i] >= tops[i-1]:  # engulfing
            bits = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0]
        elif bottoms[i] >= bottoms[i-1] and tops[i] <= tops[i-1]:  # engulfed
            bits = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1]
        elif tops[i] >= bottoms[i-1] and tops[i] >= mids[i-1] and tops[i] < tops[i-1]:  # overlapped low
            bits = [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0]
        elif tops[i] >= bottoms[i-1] and tops[i] < mids[i-1] and tops[i] < tops[i-1]:  # pierced low
            bits = [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]
        elif tops[i] < bottoms[i-1]:  # gapped down
            bits = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0]
        else:
            raise Exception("Unexpected case:  Couldn't encode candlestick relative position: " + str(data[i]) + ", previos: " + str(data[i-1]))
        return bits
    
    def encode_body_length(self, i):
        opens = self.opens
        closes = self.closes
        tops = self.tops
        body_length = 100 * (abs(opens[i] - closes[i]) / tops[i])
        # 0, extra small, small, med small, med, med large, large, extra large, huge
        # % in {0, 1} => 0
        # % in {1, 5} => extra small
        # % in {5, 20} => small
        # % in {20, 40} => med small
        # % in {40, 60} => med
        # % in {60, 80} => med large
        # % in {80, 100} => large
        # % in {100, 150} => extra large
        # % > 150 => huge
        if body_length < 1:
            body_length_bits = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif body_length < 5:
            body_length_bits = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif body_length < 10:
            body_length_bits = [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif body_length < 15:
            body_length_bits = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif body_length < 20:
            body_length_bits = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        elif body_length < 25:
            body_length_bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        elif body_length < 30:
            body_length_bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0]
        elif body_length < 35:
            body_length_bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0]
        else:
            body_length_bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
        return body_length_bits
    
    def encode_body_color(self, i):
        change = self.closes[i] - self.opens[i]
        if change > 0:
            body_color_bits = [1, 1, 0, 0, 0, 0]  # white
        elif change == 0:
            body_color_bits = [0, 0, 1, 1, 0, 0]  # doji
        else:
            body_color_bits = [0, 0, 0, 0, 1, 1]  # black
        return body_color_bits
    
    def encode_upper_shadow(self, i):
        upper_shadow_length = 100 * abs(highs[i] - tops[i]) / max(1, highs[i] - lows[i])
        if upper_shadow_length < 5:
            upper_shadow_bits = [1, 1, 1, 0, 0, 0, 0]
        elif upper_shadow_length < 35:
            upper_shadow_bits = [0, 0, 1, 1, 1, 0, 0]
        else:
            upper_shadow_bits = [0, 0, 0, 0, 1, 1, 1]
        return upper_shadow_bits
    
    def encode_lower_shadow(self, i):
        lower_shadow_length = 100 * abs(bottoms[i] - lows[i]) / max(1, highs[i] - lows[i])
        if lower_shadow_length < 5:
            lower_shadow_bits = [1, 1, 1, 0, 0, 0, 0]
        elif lower_shadow_length < 35:
            lower_shadow_bits = [0, 0, 1, 1, 1, 0, 0]
        else:
            lower_shadow_bits = [0, 0, 0, 0, 1, 1, 1]
        return lower_shadow_bits

