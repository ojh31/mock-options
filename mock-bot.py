from copy import deepcopy
import pandas as pd
import numpy as np
from scipy.stats import norm
import math
import random

Phi = norm.cdf
r = 0.01
sigma = 0.7
t = 0.1
interval = 5
buywords = set(["buy", "bid", "long", "mine", "buying"])
sellwords = set(["ask", "offer", "sell", "short", "yours", "your's",
                 "selling"])
opttypes = ["call", "put", "put&stock", "buywrite"]


def PV(arr):
    # Get Present Value
    return arr * np.exp(-r * t)


def getSupCode(n):
    codes = {1: u"\u00B9",
             2: u"\u00B2",
             3: u"\u00B3",
             4: u"\u2074",
             5: u"\u2075",
             6: u"\u2076",
             7: u"\u2077"}
    return unicode(codes[n])


def getSubCode(n):
    return "\u208{:d}".format(n)


def spaces(num):
    # Wrapper for creating blankspace
    return " " * num


def round_to_base(flt, prec=2, base=.05):
    # Round to bases other than 10
    # prec = # d.p. of base
    return round(base * round(float(flt)/base), prec)


def ceil_to_base(flt, prec=2, base=.05):
    # Round to bases other than 10
    # prec = # d.p. of base
    return round(base * math.ceil(float(flt)/base), prec)


def floor_to_base(flt, prec=2, base=.05):
    # Round to bases other than 10
    # prec = # d.p. of base
    return round(base * math.floor(float(flt)/base), prec)


class Value(object):
    # A single fair value, rounded to appropriate tick size

    @classmethod
    def infer_tick_size(cls, px):
        # Smallest allowed tick size based on price
        if px < 2:
            return 0.05
        else:
            return 0.10

    def __init__(self, price=np.nan, tick_size=None):
        if hasattr(price, tick_size) and tick_size is None:
            tick_size = price.tick_size
        price = float(price)
        if np.isnan(price):
            self.price = price
        else:
            if tick_size is None:
                tick_size = Value.infer_tick_size(price)
            self.price = round_to_base(float(price), base=tick_size)

    def change(self, val):
        # Change to alternate value
        return Value(val)

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
        return Value(float(self) + float(other))

    def __radd__(self, other):
        # Scalar addition
        return Value(float(self) + float(other))

    def __sub__(self, other):
        # Scalar subtraction
        return Value(float(self) - float(other))

    def __rsub__(self, other):
        # Scalar difference
        return Value(float(other) - float(self))

    def __mul__(self, other):
        # Scalar multiplication
        return Value(float(other) * float(self))

    def __div__(self, other):
        # Scalar division
        return Value(float(self) / float(other))

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

    @classmethod
    def from_string(cls, strmkt):
        # Infer Market from a string
        bid, ask = strmkt.replace(" ", "").replace("-", "@").split("@")
        bid = float(bid)
        ask = float(ask)
        return Market(bid, ask)

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
            tick_size = Value.infer_tick_size(mid)
            bid = ceil_to_base(bid, base=tick_size)
            bid = max(float(bid), 0)
            ask = floor_to_base(ask, base=tick_size)
        else:
            raise AttributeError('Too many prices passed for Market init',
                                 prices)
        max_width = Market.infer_max_width(bid)
        if bid > ask:
            raise IOError('Bid cannot exceed ask price!', prices)
        if ask - bid > max_width + 0.01:
            raise IOError('Maximum width exceeded', bid, ask, prices)
        self.bid = Value(bid)
        self.ask = Value(ask)

    def get_mid(self):
        # get mid market
        mid = (self.bid + self.ask) / 2
        return Value(mid)

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


class Board(object):
    # Mock board parent class with options, stock and r/c

    def copy(self):
        return deepcopy(self)

    def ix(self, strike, opt):
        return self.df.loc[strike, opt]

    def pos(self, iterable):
        strike, opt = iterable
        return self.ix(strike, opt)

    @staticmethod
    def get_strikes():
        strikes = [60, 65, 70, 75, 80]
        K = np.array(strikes)
        return K

    @staticmethod
    def get_rc():
        K = Board.get_strikes()
        return Value(np.mean(K - PV(K)))

    @staticmethod
    def infer_board_as_df(S):
        # Infer dataframe of option Values from stock price using Black-Scholes
        K = Board.get_strikes()
        rc = Board.get_rc()
        df = pd.DataFrame(columns=["call", "strike", "put", "put&stock",
                                   "buywrite", "callspread", "calldelta"])
        d_plus = np.log(S / K)
        d_plus += (r + 0.5 * (sigma ** 2)) * t
        d_plus /= sigma * np.sqrt(t)
        d_minus = d_plus - sigma * np.sqrt(t)
        df["calldelta"] = 100 * Phi(d_plus)
        df["call"] = Phi(d_plus) * S - Phi(d_minus) * PV(K)
        df["put"] = Phi(-d_minus) * PV(K) - Phi(-d_plus) * S
        df["callspread"] = df.call - df.call.shift(-1)
        df["put&stock"] = df.call - rc
        df["buywrite"] = df.put + rc
        df["strike"] = K
        df = df.set_index("strike")
        df = df.applymap(Value)
        df.calldelta = df.calldelta.map(int)
        df.index = df.index.map(int)
        print S, rc
        print df
        return df

    def __repr__(self):
        # Basic string representation of board
        board_str = self.get_stock_and_rc()
        board_str += "\n" + str(self.df)
        return board_str

    def get_stock_and_rc(self):
        # String representation of stock and r/c
        return "S = {}, r/c = {}".format(self.S, self.rc)


class ValueBoard(Board):
    # A board of values

    def __init__(self, S=None):
        if S is None:
            S = random.uniform(50, 80)
        self.S = Value(S)
        self.rc = Board.get_rc()
        self.df = Board.infer_board_as_df(S)


class MarketBoard(Board):
    # A board of markets, tied to a Value Board

    def __init__(self, valueBoard):
        board = valueBoard.copy()
        self.valueBoard = board.copy()
        self.S = board.S.to_market()
        self.rc = board.rc
        self.df = board.df
        for op in opttypes:
            self.df[op] = self.df[op].map(lambda val: val.to_market())

    def __str__(self):
        # Prettified string representation of options board
        s = chr(27) + "[2J"
        s += self.get_stock_and_rc()
        s += "\n"
        s += spaces(5)
        s += "Delta      Call        "
        s += "|  Strike  |"
        s += "        Put         Buywrite       Put&Stock"
        for strike, row in self.df.iterrows():
            s += "\n"
            s += spaces(7)
            rowarray = ["{:2d}".format(row["calldelta"]),
                        row["call"],
                        "|",
                        strike,
                        "|",
                        row["put"],
                        row["buywrite"],
                        row["put&stock"]]
            rowstrs = map(str, rowarray)
            s += spaces(4).join(rowstrs)
            if strike != self.df.index[-1]:
                s += "\n{}<".format(row["callspread"])
        return s


class PublicBoard(MarketBoard):
    # This is the board shown to the player

    def __init__(self, fairBoard):
        self.fairBoard = fairBoard
        board = fairBoard.copy()
        self.initialFairBoard = board.copy()
        board = MarketBoard(board)
        self.S = board.S
        self.rc = board.rc
        self.df = board.df
        for op in opttypes:
            self.df[op] = self.df[op].map(lambda mkt: mkt.nullify())
        self.df.loc[65, "put&stock"] = fairBoard.df.loc[65, "put&stock"]
        self.df.loc[80, "buywrite"] = fairBoard.df.loc[80, "buywrite"]

    def get_user_market(self, row, col):
        # Ask user for their market in an option
        query = "What is your market in the {} {}s?\n".format(row, col)
        try:
            market = raw_input(query)
            if market:
                market = Market.from_string(market)
                fair = self.initialFairBoard.df.loc[row, col]
                if market.contains(fair):
                    self.df.loc[row, col] = market
                else:
                    print "Sorry that market does not contain the fair value!"
                    print "Please try again."
                    self.get_user_market(row, col)
            else:
                raise IOError(market)
        except (ValueError, IOError):
            print "Sorry, that doesn't look like a valid market"
            self.get_user_market(row, col)

    def get_user_markets_in_col(self, col):
        # getMarket for all missing options in a column
        for strike, row in self.df.iterrows():
            if row[col].hasNull():
                print self
                self.get_user_market(strike, col)

    def get_user_markets_all(self):
        # getMarket for all missing calls and puts
        self.get_user_markets_in_col("call")
        self.get_user_markets_in_col("put")


class Mock(object):
    # Game of mock against a bot

    def __init__(self):
        self.valueBoard = ValueBoard()
        self.publicBoard = PublicBoard(self.valueBoard)
        self.publicBoard.get_user_markets_all()
        self.play()

    def play(self):
        self.botBoard.update()
        print self.botBoard
        order = raw_input("").lower()
        if any(buywords in order):
            self.buy(order)
        elif any(sellwords in order):
            self.sell(order)
        else:
            print "Sorry I can't understand if you're buying or selling."


if __name__ == "__main__":
    mock = Mock()

### TO DO
# Merge PublicBoard and MarketBoard
# Check markets against *current* fair (may need to update)
# Make stock tick in 5 cents, r/c in 1 cent
