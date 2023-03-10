import sys
import random
from boards import PublicBoard
from user_input import get_user_market, get_user_command
from sounds import shout, rand_countdown
from order_types import IcebergOrder
from matching import is_book_crossed
from game_logging import Logger


class Mock(object):
    # Game of mock against a bot

    def __init__(self):
        self.logger = Logger()
        num_clients = 5
        self.publicBoard = PublicBoard()
        self.fairBoard = self.publicBoard.fair
        self.clients = [IcebergOrder.rand(self.fairBoard)
                        for _ in range(num_clients)]
        for client in self.clients:
            self.logger.add(client)
        self.logger.add(self.fairBoard)
        self.play()

    def play(self):
        if not self.clients:
            return shout('Game over')
        print(self.publicBoard)
        self.get_user_command()
        order = self.pop()
        mkt = get_user_market(order)
        if mkt:
            self.logger.show('Player market: {}'.format(mkt))
            rand_countdown()
            if is_book_crossed(order, mkt):
                self.logger.shout(order.take_str())
            else:
                self.logger.shout('Nothing there...')
        else:
            self.publicBoard.append(order)
            self.logger.shout(str(order))
        self.get_user_command()
        self.play()

    def get_user_command(self):
        cmd = get_user_command()
        if cmd:
            method_to_call = getattr(self, cmd)
            method_to_call()
            self.play()

    def pop(self):
        clients = self.clients
        client = random.choice(clients)
        popped = client.pop()
        if client.is_empty():
            clients.remove(client)
        return popped

    def show_fair(self):
        self.logger.confirm(self.fairBoard)

    def show_log(self):
        self.logger.view()

    def exit(self):
        sys.exit()


if __name__ == "__main__":
    mock = Mock()
