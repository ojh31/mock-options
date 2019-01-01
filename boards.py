from currencies import Price
from markets import Market
from strings import spaces
from structures import Option, Structure
from expiries import years_to_expiry
from scipy.stats import norm
import numpy as np
import pandas as pd
import random
import copy

Phi = norm.cdf
opttypes = ["call", "put", "put&stock", "buywrite"]


class Board(object):
    # Mock board parent class with options, stock and r/c

    def PV(self, arr):
        # Get Present Value
        return arr * np.exp(-self.rate * self.expiry)

    def copy(self):
        return copy.deepcopy(self)

    def loc(self, strike, opt):
        return self.df.loc[strike, opt]

    def iloc(self, row, col):
        strike = self.get_strikes(self.S)[row]
        return self.df.loc[strike, col]

    def pos(self, iterable):
        strike, opt = iterable
        return self.ix(strike, opt)

    def __getitem__(self, key):
        if len(key) == 1:
            return self.df[key]
        row, col = key
        if row < 5:
            return self.iloc(row, col)
        else:
            return self.loc(row, col)

    def __setitem__(self, key, value):
        if len(key) == 1:
            self.df[key] = value
        row, col = key
        if row < 5:
            strike = self.get_strikes()[row]
        else:
            strike = row
        self.df.loc[strike, col] = value

    def get_strikes(self, S=None):
        if S is None:
            S = self.S
        box = int(self.box)
        atm = int(Price(S, box).round())
        return [atm - 2 * box, atm - box, atm, atm + box, atm + 2 * box]

    def get_rc(self, S):
        K = np.array(self.get_strikes(S))
        return Price(np.mean(K - self.PV(K)))

    def get_straddle(self):
        atm = self.df.index[2]
        return Option(atm, Structure.STRADDLE, self)

    def infer_board_as_df(self, S):
        # Infer dataframe of option Prices from stock price using Black-Scholes
        sigma = self.sigma
        t = self.expiry
        r = self.rate
        strikes = self.get_strikes(S)
        K = np.array(strikes)
        rc = self.get_rc(S)
        df = pd.DataFrame(columns=["call", "strike", "put", "put&stock",
                                   "buywrite", "callspread", "calldelta"])
        d_plus = np.log(S / K)
        d_plus += (r + 0.5 * (sigma ** 2)) * t
        d_plus /= sigma * np.sqrt(t)
        d_minus = d_plus - sigma * np.sqrt(t)
        df["calldelta"] = 100 * Phi(d_plus)
        df["call"] = Phi(d_plus) * S - Phi(d_minus) * self.PV(K)
        df["put"] = Phi(-d_minus) * self.PV(K) - Phi(-d_plus) * S
        df["callspread"] = df.call - df.call.shift(-1)
        df["put&stock"] = df.call - rc
        df["buywrite"] = df.put + rc
        df["strike"] = strikes
        df = df.set_index("strike")
        df = df.applymap(Price)
        df.calldelta = df.calldelta.map(int)
        return df

    def __repr__(self):
        # Basic string representation of board
        board_str = self.get_stock_and_rc()
        board_str += "\n" + str(self.df)
        return board_str

    def get_stock_and_rc(self):
        # String representation of stock and r/c
        return "S = {}, r/c = {}".format(self.S, self.rc)


class PriceBoard(Board):
    # A board of Prices

    def __init__(self, S=None):
        self.rate = 0.1
        self.sigma = 0.8
        self.expiry = years_to_expiry()
        self.box = 5
        if S is None:
            S = random.uniform(30, 120)
        self.S = Price(S)
        self.rc = self.get_rc(S)
        self.df = self.infer_board_as_df(S)
        self.V = self.get_straddle().get_price()


class MarketBoard(Board):
    # A board of markets, tied to a Price Board

    def __init__(self, S=None, board=None):
        if S is not None and board is not None:
            raise AttributeError('Marketboard over-specified by: ',
                                 'S = ',
                                 S,
                                 'board = ',
                                 board)
        elif board is not None:
            S = board.S
        else:
            board = PriceBoard(S)
        df = board.df.copy()
        for op in opttypes:
            df[op] = df[op].map(Market.from_price)
        self.S = Market.from_price(board.S, width=.20)
        self.V = Market.from_price(board.V, width=.30)
        self.box = board.box
        self.rc = board.rc
        self.df = df
        self.fair = board
        self.bot_orders = {}

    def __str__(self):
        # Prettified string representation of options board
        s = chr(27) + "[2J"
        s += self.get_stock_and_rc()
        s += "\n"
        s += spaces(5)
        s += "PutsAndStock        Call        "
        s += "|  Strike   |"
        s += "        Put         Buywrite"
        for strike, row in self.df.iterrows():
            s += "\n"
            s += spaces(7)
            rowarray = [row["put&stock"],
                        row["call"],
                        "|",
                        "{:3d}".format(strike),
                        "|",
                        row["put"],
                        row["buywrite"]]
            rowstrs = map(str, rowarray)
            s += spaces(4).join(rowstrs)
            if strike != self.df.index[-1]:
                s += "\n{}<".format(row["callspread"])
        s += f"\n{self.get_straddle()}: {self.V}"
        if self.bot_orders:
            s += "\n"
            s += "\n".join([str(order) for order in self.bot_orders.values()])
        return s

    def clear(self):
        for op in opttypes:
            self.df[op] = self.df[op].map(lambda mkt: mkt.nullify())
        return self

    def make_babies(self):
        bw_pos = (0, 'buywrite')
        pns_pos = (-1, 'put&stock')
        call_fair = self.fair[pns_pos]
        put_fair = self.fair[bw_pos]
        self[bw_pos] = Market.from_price(put_fair, width=.2)
        self[pns_pos] = Market.from_price(call_fair, width=.2)
        return self

    def append(self, order):
        opt = order.option
        dirn = order.direction
        key = (opt, dirn)
        if key in self.bot_orders.keys():
            self.bot_orders[key] += order
        else:
            self.bot_orders[key] = order


class PublicBoard(MarketBoard):

    def __init__(self):
        MarketBoard.__init__(self)
        self = self.clear().make_babies()


if __name__ == "__main__":
    public_board = PublicBoard()
    print(public_board.fair)
    input("")
    print(public_board)
