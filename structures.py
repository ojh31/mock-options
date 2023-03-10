from currencies import Price
import random
import enum
import numpy as np


@enum.unique
class Structure(enum.Enum):
    CALL = 'calls'
    PUT = 'puts'
    COMBO = 'combo'
    STRADDLE = 'straddle'
    CALLSPREAD = 'call spread'
    PUTSPREAD = 'put spread'
    RISKY = 'risk reversal'

    def __str__(self):
        return self.value

    def num_strikes(self):
        if self.name in ['CALL', 'PUT', 'COMBO', 'STRADDLE']:
            return 1
        elif self.name in ['CALLSPREAD', 'PUTSPREAD', 'RISKY', 'STRANGLE']:
            return 2
        elif self.name == 'FLY':
            return 3
        else:
            raise AttributeError('Unrecognised structure name: {}'
                                 .format(self.name))


class Option(object):

    def __init__(self, strikes, structure, board):
        if isinstance(strikes, int) or isinstance(strikes, np.int64):
            self.strikes = [strikes]
        else:
            self.strikes = strikes
        self.structure = structure
        self.board = board

    @classmethod
    def rand(cls, board=None):
        struct = random.choice(list(Structure))
        strikes = np.random.choice(board.get_strikes(),
                                   size=struct.num_strikes(),
                                   replace=False)
        strikes = np.sort(strikes).tolist()
        return Option(strikes, struct, board)

    def __repr__(self):
        return str(self.strikes) + str(self.structure)

    def __str__(self):
        strike_str = '/'.join(str(strike) for strike in self.strikes)
        return strike_str + ' ' + str(self.structure)

    def get_price(self):
        board = self.board
        strikes = self.strikes
        structure = self.structure
        df = board.df[board.df.index.isin(strikes)][['call', 'put']].copy()
        df = df.reset_index(drop=True)
        if structure is Structure.CALL:
            px = float(df.call)
        elif structure is Structure.PUT:
            px = float(df.put)
        elif structure is Structure.COMBO:
            px = float(df.call - df.put)
        elif structure is Structure.STRADDLE:
            px = float(df.call + df.put)
        elif structure is Structure.CALLSPREAD:
            px = float(df.call[0] - df.call[1])
        elif structure is Structure.PUTSPREAD:
            px = float(df.put[1] - df.put[0])
        elif structure is Structure.RISKY:
            px = abs(float((df.put[1] - df.call[0])))
        elif structure is Structure.STRANGLE:
            px = float(df.call[1] + df.put[0])
        else:
            raise AttributeError('Unknown struct type: ', structure)
        return Price(px)


if __name__ == '__main__':
    struct = Option.rand()
    print(struct)
    print(struct.get_price())
