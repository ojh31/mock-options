import math
import numpy as np
from strings import spaces


class Price(object):
    # A single price, rounded to appropriate tick size
    default_tick_size = 0.01
    prec = 2

    def __init__(self, price=np.nan, tick_size=None):
        price = float(price)
        self.price = price
        if tick_size is None:
            tick_size = self.default_tick_size
        self.tick_size = tick_size

    def round(self):
        # Round to bases other than 10
        # prec = # d.p. of base
        base = self.tick_size
        return round(base * round(float(self.price)/base), self.prec)

    def ceil(self):
        # Round to bases other than 10
        # prec = # d.p. of base
        base = self.tick_size
        return round(base * math.ceil(float(self.price)/base), self.prec)

    def floor(self):
        # Round to bases other than 10
        # prec = # d.p. of base
        base = self.tick_size
        return round(base * math.floor(float(self.price)/base), self.prec)

    def change(self, val):
        # Change to alternate value
        return Price(val)

    def __repr__(self):
        # Basic string representation
        return repr(self.price)

    def __str__(self):
        # Prettified string representation taking up 5 horizontal spaces
        price = self.price
        if np.isnan(price):
            return spaces(5)
        else:
            return "{:>5.2f}".format(price)

    def __format__(self, align=">"):
        # Horizontally aligned string representation
        price = self.price
        if np.isnan(price):
            return spaces(5)
        else:
            return "{:{align}5.2f}".format(self.price, align=align)

    def __add__(self, other):
        # Scalar addition
        return Price(float(self) + float(other))

    def __radd__(self, other):
        # Scalar addition
        return Price(float(self) + float(other))

    def __sub__(self, other):
        # Scalar subtraction
        return Price(float(self) - float(other))

    def __rsub__(self, other):
        # Scalar difference
        return Price(float(other) - float(self))

    def __mul__(self, other):
        # Scalar multiplication
        return Price(float(self) * float(other))

    def __rmul__(self, other):
        # Scalar multiplication
        return Price(float(self) * float(other))

    def __truediv__(self, other):
        # Scalar division
        return Price(float(self) / float(other))

    def __float__(self):
        # Python float representation
        return self.price

    def __int__(self):
        # Python int representation
        return int(self.price)

    def __gt__(self, other):
        return self.price > other

    def __lt__(self, other):
        return self.price < other

    def __bool__(self):
        return not np.isnan(self.price)


class OptionPrice(Price):
    """
    The price of an option with an inferred tick size
    """

    def __init__(self, px):
        if px < 2:
            tick_size = 0.05
        else:
            tick_size = 0.10
        Price.__init__(self, px, tick_size)


if __name__ == "__main__":
    pass
