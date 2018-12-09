from markets import Market
from currencies import Price
from structures import Structure
from boards import PriceBoard


buywords = set(["buy", "bid", "long", "mine", "buying"])
sellwords = set(["ask", "offer", "sell", "short", "yours", "your's",
                 "selling"])


def get_user_market(asset=None):
    """
    Get a Market
    """
    if asset is None:
        asset = Structure.rand()
    fair = asset.get_price()
    query = "Make me a market"
    query += " in the {}".format(asset)
    query += ":\n"
    try:
        strmkt = input(query)
        if strmkt:
            market = market_from_string(strmkt)
            if market.contains(fair):
                return market
            else:
                print("Sorry that market does not contain the fair value!")
                print("Please try again.")
                return get_user_market(asset)
        else:
            raise IOError(market)
    except (ValueError, IOError) as e:
        print("Sorry, that doesn't look like a valid market")
        print(e)
        return get_user_market(asset)


def market_from_string(strmkt):
    # Infer Market from a string
    bid, ask = strmkt.replace(" ", "").replace("-", "@").split("@")
    bid = float(bid)
    ask = float(ask)
    return Market(bid, ask)


def get_user_order():
    order = raw_input("").lower()
    if any(buywords in order):
        return buy_asset(order)
    elif any(sellwords in order):
        return sell_asset(order)
    else:
        print("Sorry I can't understand if you're buying or selling.")

if __name__ == "__main__":
    board = PriceBoard()
    asset = Structure.rand(board)
    print(board)
    mkt = get_user_market(asset)
    print(mkt)
    val = input('Give me a price:\n')
    px = Price(val)
    print("Price = {}".format(px))
    print("Market = {}".format(Market.from_price(px)))
