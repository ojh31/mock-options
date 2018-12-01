from mock_ccy import Price, Market
from scipy.stats import norm
import numpy as np
import pandas as pd
import random

Phi = norm.cdf
r = 0.01
sigma = 0.7
t = 0.1
interval = 5
opttypes = ["call", "put", "put&stock", "buywrite"]


def PV(arr):
    # Get Present Value
    return arr * np.exp(-r * t)


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
        return Price(np.mean(K - PV(K)))

    @staticmethod
    def infer_board_as_df(S):
        # Infer dataframe of option Prices from stock price using Black-Scholes
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
        df = df.applymap(Price)
        df.calldelta = df.calldelta.map(int)
        df.index = df.index.map(int)
        print(S, rc)
        print(df)
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
            S = random.uniform(50, 80)
        self.S = Price(S)
        self.rc = Board.get_rc()
        self.df = Board.infer_board_as_df(S)


class MarketBoard(Board):
    # A board of markets, tied to a Price Board

    def __init__(self, PriceBoard):
        board = PriceBoard.copy()
        self.PriceBoard = board.copy()
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
                    print("Sorry that market does not contain the fair value!")
                    print("Please try again.")
                    self.get_user_market(row, col)
            else:
                raise IOError(market)
        except (ValueError, IOError):
            print("Sorry, that doesn't look like a valid market")
            self.get_user_market(row, col)

    def get_user_markets_in_col(self, col):
        # getMarket for all missing options in a column
        for strike, row in self.df.iterrows():
            if row[col].hasNull():
                print(self)
                self.get_user_market(strike, col)

    def get_user_markets_all(self):
        # getMarket for all missing calls and puts
        self.get_user_markets_in_col("call")
        self.get_user_markets_in_col("put")

if __name__ == "__main__":
    PriceBoard()
