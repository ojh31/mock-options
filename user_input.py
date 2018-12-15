from markets import Market
from currencies import Price
from order_types import IcebergOrder
from boards import PriceBoard
import numpy as np
from sounds import shout


buywords = set(["buy", "bid", "long", "mine", "buying"])
sellwords = set(["ask", "offer", "sell", "short", "yours", "your's",
                 "selling"])


def get_user_market(order=None):
    """
    Get a Market
    """
    if order is None:
        order = IcebergOrder.rand()
    option = order.option
    fair = option.get_price()
    query = (f"Make me a market in "
             f"{order.size} lots of "
             f"the {option}:\n")
    shout(query)
    try:
        strmkt = input(query)
        if strmkt:
            market = market_from_string(strmkt)
            if market.bid > fair:
                shout("Haha, okay... your's!")
            elif market.offer < fair:
                shout("Haha, okay... mine!")
            else:
                return market
        else:
            return Market(np.nan, np.nan)
    except (ValueError, IOError) as e:
        print("Sorry, that doesn't look like a valid market")
        print(e)
        return get_user_market(order)


def market_from_string(strmkt):
    # Infer Market from a string
    if strmkt == '':
        return Market(np.nan, np.nan)
    bid, ask = strmkt.replace(" ", "").replace("-", "@").split("@")
    bid = float(bid)
    ask = float(ask)
    return Market(bid, ask)


"""
def get_user_order():
    order = raw_input("").lower()
    if any(buywords in order):
        return buy_asset(order)
    elif any(sellwords in order):
        return sell_asset(order)
    else:
        print("Sorry I can't understand if you're buying or selling.")
"""

if __name__ == "__main__":
    board = PriceBoard()
    order = IcebergOrder.rand(board)
    print(board)
    mkt = get_user_market(order)
    print('User market: {}'.format(mkt))
    val = input('Give me a price:\n')
    px = Price(val)
    print("Price = {}".format(px))
    print("Market = {}".format(Market.from_price(px)))
