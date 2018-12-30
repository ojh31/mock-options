from order_types import Direction


def is_book_crossed(order, mkt):
    assert order.size > 0
    return (((order.direction == Direction.BUY) and (order.price > mkt.ask)) or
            ((order.direction == Direction.SELL) and (order.price < mkt.bid)))
