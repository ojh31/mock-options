from currencies import Price, OptionPrice
import numpy as np


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

    @classmethod
    def from_price(cls, mid, width=None):
            mid = float(mid)
            max_width = Market.infer_max_width(mid)
            max_width = Market.infer_max_width(mid - 0.5 * max_width)
            if width is None:
                width = max_width
            bid = mid - 0.5 * width
            ask = mid + 0.5 * width
            tick_size = OptionPrice(mid).tick_size
            bid = Price(bid, tick_size).ceil()
            bid = max(float(bid), 0)
            ask = Price(ask, tick_size).floor()
            return cls(bid, ask)

    def __init__(self, bid, ask):
        bid = float(bid)
        ask = float(ask)
        max_width = Market.infer_max_width(bid)
        if bid > ask:
            raise IOError('Bid cannot exceed ask price!', bid, ask)
        if ask - bid >= max_width + 0.01:
            raise IOError('Maximum width exceeded', bid, ask)
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
        return float(self.get_mid().round())


if __name__ == '__main__':
    pass
    # should demonstrate Market.from_price
    # need to deal with widths correctly
