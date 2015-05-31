#!/usr/bin/python
# Class to encode a candlestick as a sparse distributed representation
# ============================================================================
class CandlestickEncoder(object):
    def __init__(self, current_datapoint, prev_datapoint):
        self.current_datapoint = current_datapoint
        self.prev_datapoint = prev_datapoint
        self.prev_top = max(prev_datapoint.get_open(), prev_datapoint.get_close())
        self.current_top = max(current_datapoint.get_open(), current_datapoint.get_close())
        self.prev_mid = (prev_datapoint.get_open() + prev_datapoint.get_close())/2.0
        self.current_mid = (current_datapoint.get_open() + current_datapoint.get_close())/2.0
        self.prev_bottom = min(prev_datapoint.get_open(), prev_datapoint.get_close())
        self.current_buttom = min(current_datapoint.get_open(), current_datapoint.get_close())

    def encode(self):
        relative_position_bits = self.encode_relative_position()
        body_length_bits = self.encode_body_length()
        body_color_bits = self.encode_body_color()
        upper_shadow_bits = self.encode_upper_shadow()
        lower_shadow_bits = self.encode_lower_shadow()
        bits = relative_position_bits + body_length_bits + body_color_bits + upper_shadow_bits + lower_shadow_bits
        return bits
    
    def encode_relative_position(self):
        current_bottom = self.current_buttom
        prev_bottom = self.prev_bottom
        current_top = self.current_top
        prev_top = self.prev_top
        current_mid = self.current_mid
        prev_mid = self.prev_mid

        if current_bottom > prev_top:  # gapped up
            bits = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        elif current_bottom <= prev_top and current_bottom > prev_mid and current_top > prev_top:  # pierced high
            bits = [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        elif current_bottom <= prev_top and current_bottom <= prev_mid and current_top > prev_top:  # overlapped high
            bits = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        elif current_bottom == prev_bottom and current_top == prev_top:  # equal
            bits = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0]
        elif current_bottom <= prev_bottom and current_top >= prev_top:  # engulfing
            bits = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0]
        elif current_bottom >= prev_bottom and current_top <= prev_top:  # engulfed
            bits = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1]
        elif current_top >= prev_bottom and current_top >= prev_mid and current_top < prev_top:  # overlapped low
            bits = [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0]
        elif current_top >= prev_bottom and current_top < prev_mid and current_top < prev_top:  # pierced low
            bits = [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]
        elif current_top < prev_bottom:  # gapped down
            bits = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0]
        else:
            raise Exception("Unexpected case:  Couldn't encode candlestick relative position: " + str(self.current_datapoint) +
                            ", previous: " + str(self.prev_datapoint))
        return bits

    def encode_body_length(self):
        open = self.current_datapoint.get_open()
        close = self.current_datapoint.get_close()
        top = self.current_top
        body_length = 100 * (abs(open - close) / top)
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

    def encode_body_color(self):
        change = self.current_datapoint.get_close() - self.current_datapoint.get_open()
        if change > 0:
            body_color_bits = [1, 1, 0, 0, 0, 0]  # white
        elif change == 0:
            body_color_bits = [0, 0, 1, 1, 0, 0]  # doji
        else:
            body_color_bits = [0, 0, 0, 0, 1, 1]  # black
        return body_color_bits

    def encode_upper_shadow(self):
        upper_shadow_length = 100 * abs(self.current_datapoint.get_high()
                                        - self.current_top) / max(1, self.current_datapoint.get_high() -
                                                                  self.current_datapoint.get_low())
        if upper_shadow_length < 5:
            upper_shadow_bits = [1, 1, 1, 0, 0, 0, 0]
        elif upper_shadow_length < 35:
            upper_shadow_bits = [0, 0, 1, 1, 1, 0, 0]
        else:
            upper_shadow_bits = [0, 0, 0, 0, 1, 1, 1]
        return upper_shadow_bits

    def encode_lower_shadow(self):
        lower_shadow_length = 100 * abs(self.current_buttom - self.current_datapoint.get_low()) / \
                              max(1, self.current_datapoint.get_high() - self.current_datapoint.get_low())
        if lower_shadow_length < 5:
            lower_shadow_bits = [1, 1, 1, 0, 0, 0, 0]
        elif lower_shadow_length < 35:
            lower_shadow_bits = [0, 0, 1, 1, 1, 0, 0]
        else:
            lower_shadow_bits = [0, 0, 0, 0, 1, 1, 1]
        return lower_shadow_bits

