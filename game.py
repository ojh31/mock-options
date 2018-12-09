from mock_board import PriceBoard, MarketBoard
from mock_mkt import Market


class Mock(object):
    # Game of mock against a bot

    def __init__(self):
        self.PriceBoard = PriceBoard()
        self.publicBoard = PublicBoard(self.PriceBoard)
        self.publicBoard.get_user_markets_all()
        self.play()

    def play(self):
        self.botBoard.update()
        print(self.botBoard)


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
        self = self.clear()
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
    mock = Mock()
