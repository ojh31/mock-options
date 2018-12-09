from boards import PublicBoard
from structures import Structure
from user_input import get_user_market


class Mock(object):
    # Game of mock against a bot

    def __init__(self):
        self.publicBoard = PublicBoard()
        self.fairBoard = self.publicBoard.fair
        self.play()

    def play(self):
        asset = Structure.rand(self.fairBoard)
        print(self.publicBoard)
        mkt = get_user_market(asset)
        print(mkt)
        self.play()


if __name__ == "__main__":
    mock = Mock()