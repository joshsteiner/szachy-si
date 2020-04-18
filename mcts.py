""" MCTS data structure """
from random import choice
from pprint import pprint
import chess


NUMBER_OF_PLAYOUTS = 10


# TEMP
def is_final_position(position, color):
    moves = list(chess.possible_moves(position, color))
    return len(moves) == 0


# TEMP
def position_status(position, color):
    oponent_color = chess.switch_color(color)
    possible_moves = chess.possible_moves(position, oponent_color)
    oponent_can_move = len(list(possible_moves)) > 0
    oponent_is_in_check = chess.is_in_check(position, oponent_color)
    if oponent_is_in_check and not oponent_can_move:
        return True   # True = WIN
    else:
        return False  # False = LOSE


class BestChildSelectPolicy:
    def select(self, node, color):
        f = max if color == chess.WHITE else min
        if node.children:
            node = node.get_best_child(f)
        return node


class UniformRandomPlayoutPolicy:
    def playout(self, node, color):
        MAX_PLAYOUT_MOVES = 100
        position = node.position.copy()
        original_color = color
        for _ in range(MAX_PLAYOUT_MOVES):
            if is_final_position(position, color):
                break
            move = choice(list(chess.possible_moves(position, color)))
            chess.apply_move(position, move)
            color = chess.switch_color(color)
        # TODO: score
        return position_status(position, original_color)


class McTreeNode:
    win_count = 0
    playout_count = 0

    def __init__(self, position, color, move, parent=None):
        self.position = position
        self.move = move
        self.parent = parent
        self.color = color
        self.children = []

    def add_playout(self, win):
        """ add playout result and backtrack """
        self.playout_count += 1
        if win:
            self.win_count += 1
        if self.parent:
            self.parent.add_playout(win)

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
        if self.playout_count > 0:
            if self.children:
                for child in self.children:
                    child.expand()
            else:
                self.add_children_from_moves(
                    chess.possible_moves(self.position, self.color)
                )

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
        for i in range(NUMBER_OF_PLAYOUTS):
            print(f"playout {i}...")
            self.root.expand()
            node = self.select_policy.select(self.root, color)
            r = self.playout_policy.playout(node, color)
            node.add_playout(r)

    def choose_best_move(self, color):
        print("starting playouts ...")
        self.do_playouts(color)
        node = self.root.get_best_child(min if color == chess.BLACK else max)
        return node.move

    def apply_move(self, move):
        for child in self.root.children:
            if ((child.move.frm == move.frm).all()
               and (child.move.to == move.to).all()):
                self.root = child
                self.root.parent = None
                return
        position = self.root.position.copy()
        chess.apply_move(position, move)
        self.root = McTreeNode(position, chess.switch_color(self.root.color), move)


if __name__ == '__main__':
    mct = McTree(
        board=chess.board,
        color=chess.WHITE,
        select_policy=BestChildSelectPolicy(),
        playout_policy=UniformRandomPlayoutPolicy()
    )

    while True:
        chess.print_board(mct.root.position)
        move = chess.parse_move(input(": "))
        mct.apply_move(move)
        chess.print_board(mct.root.position)
        ai_move = mct.choose_best_move(chess.BLACK)
        mct.apply_move(ai_move)
