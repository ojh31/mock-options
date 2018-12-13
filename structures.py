from boards import PriceBoard
import random
import enum


@enum.unique
class Structure(enum.Enum):
    CALL = 'calls'
    PUT = 'puts'
    COMBO = 'combo'

    def __str__(self):
        return self.value


class Option(object):

    def __init__(self, strikes, structure, board):
        if isinstance(strikes, int):
            strikes = [strikes]
        self.strikes = strikes
        self.structure = structure
        self.board = board

    @classmethod
    def rand(cls, board=None):
        if board is None:
            board = PriceBoard()
        strikes = board.get_strikes()
        strike = random.choice(strikes)
        struct = random.choice(list(Structure))
        return Option(strike, struct, board)

    def __repr__(self):
        return str(self.strikes) + str(self.structure)

    def __str__(self):
        strike_str = '/'.join(str(strike) for strike in self.strikes)
        return strike_str + ' ' + str(self.structure)

    def get_price(self):
        board = self.board
        strikes = self.strikes
        df = board.df[board.df.index.isin(strikes)][['call', 'put']].copy()
        structure = self.structure
        if structure is Structure.CALL:
            return float(df.call)
        elif structure is Structure.PUT:
            return float(df.put)
        elif structure is Structure.COMBO:
            return float(df.call - df.put)
        else:
            raise AttributeError('Unknown struct type: ', structure)

if __name__ == '__main__':
    struct = Option.rand()
    print(struct)
    print(struct.get_price())
