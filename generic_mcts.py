import math
from random import choice


class Status:
    IN_PROGRESS = 0


class Move:
    def __eq__(self, other):
        assert False, "unimplemented"


class GameState:
    def copy(self):
        assert False, "unimplemented"


class Game:
    @staticmethod
    def status(game_state):
        assert False, "unimplemented"

    @staticmethod
    def score(result, game_state):
        assert False, "unimplemented"

    @staticmethod
    def apply_move(move, game_state):
        assert False, "unimplemented"

    @staticmethod
    def undo_move(move, game_state):
        assert False, "unimplemented"

    @staticmethod
    def possible_moves(game_state):
        assert False, "unimplemented"

    @staticmethod
    def initial_state():
        assert False, "unimplemented"

    @staticmethod
    def show(self, game_state):
        assert False, "unimplemented"


class AiPlayer:
    def status(self) -> Status:
        assert False, "unimplemented"

    def choose_move(self) -> Move:
        assert False, "unimplemented"

    def apply_move(self, move: Move):
        assert False, "unimplemented"

    def show(self):
        assert False, "unimplemented"


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


class McTreeNode:

    def __init__(self, game_state, move=None, parent=None):
        self.win_count = 0
        self.playout_count = 0
        self.game_state = game_state
        self.move = move
        self.parent = parent
        self.children = []

    def random_child(self):
        return choice(self.children)

    def add_playout(self, result, score):
        self.playout_count += 1
        self.win_count = score(result, self.game_state)
        if self.parent:
            self.parent.add_playout(result, score)

    def get_weight(self):
        if self.playout_count == 0:
            return 0
        return self.win_count / self.playout_count

    def expand(self, game):
        assert self.children == []
        for move in game.possible_moves(self.game_state):
            game_state = self.game_state.copy()
            game.apply_move(move, game_state)
            node = McTreeNode(game_state, move, parent=self)
            self.children.append(node)

    def get_best_child(self):
        best_weight = max(c.get_weight() for c in self.children)
        return choice([c for c in self.children
                       if c.get_weight() == best_weight])


class McTree:

    def __init__(self, game, select_policy, playout_policy, number_of_playouts):
        self.game = game
        self.select_policy = select_policy
        self.playout_policy = playout_policy
        self.number_of_playouts = number_of_playouts
        self.root = McTreeNode(game.initial_state())

    def apply_move(self, move):
        for child in self.root.children:
            if child.move == move:
                self.root = child
                self.root.parent = None
                return
        game_state = self.root.game_state.copy()
        self.game.apply_move(move, game_state)
        self.root = McTreeNode(game_state, move)

    def choose_best_move(self):
        for i in range(self.number_of_playouts):
            # select
            promising_node = self.select_policy.select(self.root)
            # expand
            if self.game.status(promising_node.game_state) == Status.IN_PROGRESS:
                promising_node.expand(self.game)
            # simulate
            node_to_explore = promising_node
            if node_to_explore.children:
                node_to_explore = node_to_explore.random_child()
            result = self.playout_policy.playout(node_to_explore)
            # update
            node_to_explore.add_playout(result, self.game.score)
        return self.root.get_best_child().move
