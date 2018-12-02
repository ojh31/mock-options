from mock_ccy import Price
from mock_mkt import Market
from mock_strings import spaces
from scipy.stats import norm
import numpy as np
import pandas as pd
import random
import copy

Phi = norm.cdf
opttypes = ["call", "put", "put&stock", "buywrite"]


class Board(object):
    # Mock board parent class with options, stock and r/c
    rate = 0.01
    sigma = 0.7
    expiry = 0.1
    box = 5

    def PV(self, arr):
        # Get Present Value
        return arr * np.exp(-self.rate * self.expiry)

    def copy(self):
        return copy.deepcopy(self)

    def ix(self, strike, opt):
        return self.df.loc[strike, opt]

    def pos(self, iterable):
        strike, opt = iterable
        return self.ix(strike, opt)

    def get_strikes(self, S):
        box = int(self.box)
        atm = int(Price(S, box).round())
        return [atm - 2 * box, atm - box, atm, atm + box, atm + 2 * box]

    def get_rc(self, S):
        K = np.array(self.get_strikes(S))
        return Price(np.mean(K - self.PV(K)))

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
        if S is None:
            S = random.uniform(30, 120)
        self.S = Price(S)
        self.rc = self.get_rc(S)
        self.df = self.infer_board_as_df(S)


class MarketBoard(Board):
    # A board of markets, tied to a Price Board

    def __init__(self, S=None):
        board = PriceBoard(S)
        df = board.df
        for op in opttypes:
            df[op] = df[op].map(Market)
        self.S = Market(board.S)
        self.rc = board.rc
        self.df = df

    def __str__(self):
        # Prettified string representation of options board
        s = chr(27) + "[2J"
        s += self.get_stock_and_rc()
        s += "\n"
        s += spaces(5)
        s += "Delta      Call        "
        s += "|  Strike   |"
        s += "        Put         Buywrite       Put&Stock"
        for strike, row in self.df.iterrows():
            s += "\n"
            s += spaces(7)
            rowarray = ["{:2d}".format(row["calldelta"]),
                        row["call"],
                        "|",
                        "{:3d}".format(strike),
                        "|",
                        row["put"],
                        row["buywrite"],
                        row["put&stock"]]
            rowstrs = map(str, rowarray)
            s += spaces(4).join(rowstrs)
            if strike != self.df.index[-1]:
                s += "\n{}<".format(row["callspread"])
        return s

    def clear(self):
        board = self.copy()
        for op in opttypes:
            board.df[op] = board.df[op].map(lambda mkt: mkt.nullify())
        return board

if __name__ == "__main__":
    print(PriceBoard())
    input("")
    print(MarketBoard())
    input("")
    print(MarketBoard().clear())
