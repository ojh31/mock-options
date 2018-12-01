import math
import numpy as np
from mock_strings import spaces


class Price(object):
    # A single price, rounded to appropriate tick size
    default_tick_size = prec = 0.01

    def __init__(self, price=np.nan, tick_size=None):
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
        return Price(float(other) * float(self))

    def __div__(self, other):
        # Scalar division
        return Price(float(self) / float(other))

    def to_market(self):
        # Create Market from price
        return Market(self.price)

    def __float__(self):
        # Python float representation
        return self.price

    def __int__(self):
        # Python int representation
        return int(self.price)


class Market(object):
    # A 2-tuple of (bid price, ask price) for an option

    @classmethod
    def infer_max_width(cls, px):
        # Minimum market width based on bid price
        if px < 2:
            return 0.25
        elif px < 5:
            return 0.4
        elif px < 10:
            return 0.8
        else:
            return 1.0

    def __init__(self, *prices, **kwargs):
        if len(prices) == 2:
            assert 'width' not in kwargs
            bid, ask = prices
        elif len(prices) == 1:
            (mid, ) = prices
            max_width = Market.infer_max_width(mid)
            max_width = Market.infer_max_width(mid - 0.5 * max_width)
            if 'width' in kwargs:
                width = kwargs['width']
            else:
                width = max_width
            bid = mid - 0.5 * width
            ask = mid + 0.5 * width
            tick_size = Price.infer_tick_size(mid)
            bid = Price(bid, tick_size).ceiling()
            bid = max(float(bid), 0)
            ask = Price(ask, tick_size).floor()
        else:
            raise AttributeError('Too many prices passed for Market init',
                                 prices)
        max_width = Market.infer_max_width(bid)
        if bid > ask:
            raise IOError('Bid cannot exceed ask price!', prices)
        if ask - bid > max_width + 0.01:
            raise IOError('Maximum width exceeded', bid, ask, prices)
        self.bid = Price(bid)
        self.ask = Price(ask)

    def get_mid(self):
        # get mid market
        mid = (self.bid + self.ask) / 2
        return Price(mid)

    def contains(self, val):
        # Test that value lies inside market
        bid = float(self.bid)
        ask = float(self.ask)
        mid = float(val)
        return (bid <= mid) and (mid <= ask)

    def change(self, bid, ask):
        # Change bid/ask values
        return Market(bid, ask)

    def nullify(self):
        # Set to blanks/nulls
        return self.change(np.nan, np.nan)

    def hasNull(self):
        # Test for blank/null in Market limits
        return np.isnan(self.ask.price) or np.isnan(self.bid.price)

    def __repr__(self):
        # Basic string representation
        return repr(tuple(self.bid, self.ask))

    def __str__(self):
        # Prettified string representation
        return "{:>}-{:<}".format(self.bid, self.ask)

    def __add__(self, other):
        # Componentwise addition
        if isinstance(other, float):
            return Market(self.bid + other, self.ask + other)
        elif isinstance(other, Market):
            return Market(self.bid + other.bid, self.ask + other.ask)

    def __getitem__(self, key):
        # List indexing
        if key == 0:
            return self.bid
        elif key == 1:
            return self.ask

    def __float__(self):
        # Python float representation
        return float(self.mid)


class OptionPrice(Price):
    """
    The price of an option with an inferred tick size
    """

    def __init__(self, px):
        if px < 2:
            tick_size = 0.05
        else:
            tick_size = 0.10
        return Price(px, tick_size)

if __name__ == "__main__":
    pass
