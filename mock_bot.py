from copy import deepcopy
import pandas as pd
import numpy as np
import math
import random


class Mock(object):
    # Game of mock against a bot

    def __init__(self):
        self.valueBoard = ValueBoard()
        self.publicBoard = PublicBoard(self.valueBoard)
        self.publicBoard.get_user_markets_all()
        self.play()

    def play(self):
        self.botBoard.update()
        print(self.botBoard)


if __name__ == "__main__":
    mock = Mock()


