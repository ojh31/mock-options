import sys
import random
from boards import PublicBoard
from user_input import get_user_market, get_user_command
from sounds import rand_order
from order_types import IcebergOrder


class Mock(object):
    # Game of mock against a bot

    def __init__(self):
        num_clients = 5
        self.publicBoard = PublicBoard()
        self.fairBoard = self.publicBoard.fair
        self.clients = [IcebergOrder.rand(self.fairBoard)
                        for _ in range(num_clients)]
        self.play()

    def play(self):
        if not self.clients:
            return 'Game over'
        cmd = get_user_command()
        if cmd:
            method_to_call = getattr(self, cmd)
            method_to_call()
            self.play()
        order = self.pop()
        print(self.publicBoard)
        mkt = get_user_market(order)
        print('Player market: {}'.format(mkt))
        rand_order()
        self.play()

    def pop(self):
        clients = self.clients
        client = random.choice(clients)
        popped = client.pop()
        if client.is_empty():
            clients.remove(client)
        return popped

    def show_fair(self):
        print(self.fairBoard)

    def exit(self):
        sys.exit()


if __name__ == "__main__":
    mock = Mock()
