import unittest
import mcts
import chess


def set_up_mctree():
    board = chess.board
    mctree = mcts.McTree(board, None, None)


class TestSelectPolicy(unittest.TestCase):
    ...

