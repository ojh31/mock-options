from boards import PriceBoard
import random


class Structure(object):

    def __init__(self, strikes, name, board):
        if isinstance(strikes, int):
            strikes = [strikes]
        self.strikes = strikes
        self.name = name
        self.board = board

    @classmethod
    def rand(cls, board=None):
        if board is None:
            board = PriceBoard()
        strikes = board.get_strikes()
        strike = random.choice(strikes)
        asset_types = ['Calls', 'Puts', 'Combo']
        asset = random.choice(asset_types)
        return Structure(strike, asset, board)

    def __repr__(self):
        return str(self.strikes) + str(self.name)

    def __str__(self):
        strike_str = '/'.join(str(strike) for strike in self.strikes)
        return strike_str + ' ' + str(self.name)

    def get_price(self):
        board = self.board
        strikes = self.strikes
        df = board.df[board.df.index.isin(strikes)][['call', 'put']].copy()
        name = self.name
        if name == 'Calls':
            return float(df.call)
        elif name == 'Puts':
            return float(df.put)
        elif name == 'Combo':
            return float(df.call - df.put)
        else:
            raise AttributeError('Unknown asset type: ', name)

if __name__ == '__main__':
    struct = Structure.rand()
    print(struct)
    print(struct.get_price())
