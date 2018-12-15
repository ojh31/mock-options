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


class Order(object):

    def __init__(self, opt, dirn, price, size):
        self.option = opt
        self.direction = dirn
        self.price = price
        self.size = size

    def __str__(self):
        opt = self.option
        dirn = self.direction
        px = self.price
        size = self.size
        if dirn is Direction.BUY:
            return f'{px} bid for {size} of the {opt}'
        elif dirn is Direction.SELL:
            return f'Offer {size} of the {opt} @ {px}'


class IcebergOrder(object):

    @classmethod
    def rand(cls, board=None):
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
        agg = self.aggression
        dirn = self.direction
        price = OptionPrice((1 + dirn.value * agg) * opt.get_price())
        peak = self.peak
        if size is None:
            size = peak
        self.total -= size
        return Order(opt, dirn, price, size)

    def is_empty(self):
        return self.total <= 0


if __name__ == "__main__":
    ice = IcebergOrder.rand()
    while not ice.is_empty():
        print(ice.pop())
