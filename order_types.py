import enum
import random


class Direction(enum.Enum):
    buy = 1
    sell = -1


class Order(object):

    def __init__(self, dirn, price, size):
        self.direction = dirn
        self.price = price
        self.size = size


class IcebergOrder(object):

    @classmethod
    def rand(cls):
        dirn = random.choice([Direction.buy, Direction.sell])
        agg = random.choice([0.05, 0.1, 0.2])
        peak = random.choice([50, 100, 200, 500])
        total = random.choice([200, 500, 1000, 2000])
        return cls(dirn, agg, peak, total)

    def __init__(self, dirn, agg, peak, total):
        self.direction = dirn
        self.aggression = agg
        self.peak = peak
        self.total = total

    def pop(self, size=None):
        peak = self.peak
        if size is None:
            size = peak
        self.total -= size
        return size

    def is_empty(self):
        return self.total <= 0

if __name__ == "__main__":
    ice = IcebergOrder.rand()
    while not ice.is_empty():
        print(ice.pop())
