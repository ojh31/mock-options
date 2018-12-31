import enum
import random
from structures import Option
from currencies import OptionPrice


@enum.unique
class Direction(enum.IntEnum):
    BUY = 1
    SELL = -1

    def __str__(self):
        if self.name == 'BUY':
            return 'bid'
        elif self.name == 'SELL':
            return 'offer'
        else:
            raise AttributeError(f'Bad direction name: {self.name}!')

    def __int__(self):
        return self.value


class Order(object):

    def __init__(self, opt, dirn, price, size):
        self.option = opt
        self.direction = dirn
        if isinstance(price, float):
            price = OptionPrice(price).round()
        self.price = price
        self.size = size

    def __str__(self):
        opt = self.option
        dirn = self.direction
        px = self.price
        size = self.size
        if isinstance(px, float):
            px = OptionPrice(px)
        px = px.round()
        if dirn is Direction.BUY:
            return f'{px:.2f} bid for {size} lots of the {opt}'
        elif dirn is Direction.SELL:
            return f'Offer {size} lots of the {opt} @ {px:.2f}'

    def take_str(self):
        dirn = self.direction
        prefix = 'Okay... '
        if dirn is Direction.BUY:
            return prefix + 'mine!'
        elif dirn is Direction.SELL:
            return prefix + 'yours!'

    def __add__(self, other):
        assert self.option == other.option
        opt = self.option
        assert self.direction == other.direction
        dirn = self.direction
        if dirn == Direction.BUY:
            px = max(self.price, other.price)
        elif dirn == Direction.SELL:
            px = min(self.price, other.price)
        size = self.size + other.size
        return Order(opt, dirn, px, size)


class IcebergOrder(object):

    @classmethod
    def rand(cls, board):
        option = Option.rand(board)
        dirn = random.choice([Direction.BUY, Direction.SELL])
        agg = random.choice([0.05, 0.1, 0.2])
        peak = random.choice([50, 100, 200, 500])
        total = random.choice([200, 500, 1000, 2000])
        return cls(option, dirn, agg, peak, total)

    def __init__(self, opt, dirn, agg, peak, total):
        self.option = opt
        self.direction = dirn
        self.aggression = agg
        self.peak = peak
        self.total = total

    def pop(self, size=None):
        opt = self.option
        dirn = self.direction
        peak = self.peak
        price = self.get_price()
        if size is None:
            size = peak
        self.total -= size
        return Order(opt, dirn, price, size)

    def is_empty(self):
        return self.total <= 0

    def get_price(self):
        opt = self.option
        dirn = self.direction
        agg = self.aggression
        return OptionPrice((1 + dirn.value * agg) * opt.get_price())

    def __str__(self):
        opt = self.option
        dirn = self.direction
        agg = self.aggression
        price = 1 + dirn.value * agg
        peak = self.peak
        total = self.total
        ice_str = str(id(self)) + ': '
        if dirn == Direction.BUY:
            ice_str += (f'bid {price:.2f} in {opt} '
                        f'for {peak} lot clips, total {total}')
        elif dirn == Direction.SELL:
            ice_str += (f'offer {peak} lots up to {total} '
                        f'of {opt} @ {price:.2f}')
        return ice_str
