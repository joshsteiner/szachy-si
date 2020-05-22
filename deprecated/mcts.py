""" chess using mcts """

import mcts
import chess
import math
import numpy as np
from random import choice
from pprint import pprint


NUMBER_OF_PLAYOUTS = 100
MAX_PLAYOUT_LEN = 50


class UctSelectPolicy:
    @staticmethod
    def uct(node):
        if node.playout_count == 0:
            return 10000  # return high value
        w = node.win_count
        n = node.playout_count
        t = node.parent.playout_count
        return w / n + math.sqrt(2 * math.log(t) / n)

    def select(self, node):
        while node.children:
            node = max(node.children, key=lambda n: UctSelectPolicy.uct(n))
        return node


class UniformRandomPlayoutPolicy:
    def playout(self, node):
        position = node.position.copy()
        original_color = node.color
        color = original_color

        for _ in range(MAX_PLAYOUT_LEN):
            if chess.status(position) != chess.IN_PROGRESS:
                return
            color = chess.switch_color(color)
            move = choice(list(chess.possible_moves(position, color)))
            chess.apply_move(position, move)

        return chess.status(position)


class McTreeNode:
    win_count = 0
    playout_count = 0

    def __init__(self, position, color, move, parent=None):
        assert color in [chess.WHITE, chess.BLACK]
        self.position = position
        self.move = move
        self.parent = parent
        self.color = color
        self.children = []

    def random_child(self):
        return choice(self.children)

    def add_playout(self, result):
        """ add playout result and backtrack """
        self.playout_count += 1
        if self.color == result:
            self.win_count += 1
        elif result == chess.IN_PROGRESS:
            pass
        elif result == chess.DRAW:
            self.win_count += 0.25
        if self.parent:
            self.parent.add_playout(result)

    def add_children_from_moves(self, moves):
        for move in moves:
            position = self.position.copy()
            chess.apply_move(position, move)
            node = McTreeNode(position, chess.switch_color(self.color), move, parent=self)
            self.children.append(node)

    def serialize(self):
        return {
            "ratio": f"{self.win_count}/{self.playout_count}",
            "move": f"{chess.position_to_alg_notation(self.move.frm)}-{chess.position_to_alg_notation(self.move.to)}" if self.move else "None",
            "children": [
                child.serialize() for child in self.children
            ],
        }

    def get_weight(self):
        if self.playout_count == 0:
            return 0
        return self.win_count / self.playout_count

    def expand(self):
        assert self.children == []
        moving_color = chess.switch_color(self.color)
        for move in chess.possible_moves(self.position, moving_color):
            position = self.position.copy()
            chess.apply_move(position, move)
            node = McTreeNode(position, moving_color,
                              move, parent=self)
            self.children.append(node)

    def get_best_child(self, f):
        best_weight = f(c.get_weight() for c in self.children)
        return choice([c for c in self.children
                       if c.get_weight() == best_weight])


class McTree:
    def __init__(self, board, color, select_policy, playout_policy):
        self.select_policy = select_policy
        self.playout_policy = playout_policy
        self.root = McTreeNode(board, color, None)

    def do_playouts(self, color):
        global NUMBER_OF_PLAYOUTS
        for i in range(NUMBER_OF_PLAYOUTS):
            if i % 100 == 0:
                print(f"playout {i}...")
            node = self.select_policy.select(self.root, color)
            node.expand()
            if node.children:
                for child in node.children:
                    self.playout_policy.playout(child)
            else:
                self.playout_policy.playout(node)

    def apply_move(self, move):
        for child in self.root.children:
            if chess.move_eq(child.move, move):
                self.root = child
                self.root.parent = None
                return
        position = self.root.position.copy()
        chess.apply_move(position, move)
        self.root = McTreeNode(position, chess.switch_color(self.root.color), move)

    def choose_best_move(self):
        for i in range(NUMBER_OF_PLAYOUTS):
            # select
            promising_node = self.select_policy.select(self.root)
            # expand
            if chess.status(promising_node.position) == chess.IN_PROGRESS:
                promising_node.expand()
            # simulate
            node_to_explore = promising_node
            if node_to_explore.children:
                node_to_explore = node_to_explore.random_child()
            result = self.playout_policy.playout(node_to_explore)
            # update
            node_to_explore.add_playout(result)
        return self.root.get_best_child(max).move


if __name__ == '__main__':
    mct = McTree(
        board=chess.board,
        color=chess.BLACK,  # oposite of starting color
        select_policy=UctSelectPolicy(),
        playout_policy=UniformRandomPlayoutPolicy()
    )

    while True:
        chess.print_board(mct.root.position)
        move = chess.parse_move(input(": "))
        mct.apply_move(move)
        chess.print_board(mct.root.position)
        print("thinking...")
        ai_move = mct.choose_best_move()
        mct.apply_move(ai_move)
