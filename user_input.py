from mock_mkt import Market
from mock_ccy import Price


buywords = set(["buy", "bid", "long", "mine", "buying"])
sellwords = set(["ask", "offer", "sell", "short", "yours", "your's",
                 "selling"])


def get_market(asset_name=None, fair=None):
    """
    Get a Market
    """
    query = "Make me a market"
    if asset_name is not None:
        query += " in the {}".format(asset_name)
    query += ":\n"
    try:
        strmkt = input(query)
        if strmkt:
            market = market_from_string(strmkt)
            if fair is None:
                return market
            else:
                if market.contains(fair):
                    return market
                else:
                    print("Sorry that market does not contain the fair value!")
                    print("Please try again.")
                    return get_market(asset_name)
        else:
            raise IOError(market)
    except (ValueError, IOError) as e:
        print("Sorry, that doesn't look like a valid market")
        print(e)
        return get_market(asset_name)


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
    mkt = get_market()
    print(mkt)
    val = input('Give me a price:\n')
    px = Price(val)
    print("Price = {}".format(px))
    print("Market = {}".format(Market(px)))
