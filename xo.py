""" tic tac toe using mcts """

import generic_mcts
from random import choice, seed


def opposite_player(p):
    if p == 'x':
        return 'o'
    else:
        return 'x'


class XoStatus(generic_mcts.Status):
    DRAW = 1
    X_WIN = 2
    O_WIN = 3


class XoMove(generic_mcts.Move):
    def __init__(self, r, c, player):
        self.r = r
        self.c = c
        self.player = player

    def __eq__(self, other):
        return (
            self.r == other.r and
            self.c == other.c and
            self.player == other.player
        )


class XoGameState(generic_mcts.GameState):
    def __init__(self, board, player):
        self.board = board
        self.player = player

    def copy(self):
        board = [r[:] for r in self.board]
        return XoGameState(board, self.player)


class XoGame(generic_mcts.Game):
    @staticmethod
    def show(game_state):
        print("  ", end="")
        for c in range(3):
            print(chr(ord('a') + c), end=" ")
        print()
        for row_number, row in enumerate(game_state.board[::-1]):
            print(3 - row_number, end=" ")
            for player in row:
                print(player, end=" ")
            print()

    @staticmethod
    def status(game_state):
        L = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],

            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],

            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]

        for l in L:
            s = ''.join(game_state.board[r][c] for (r, c) in l)
            if s == 'xxx':
                return XoStatus.X_WIN
            elif s == 'ooo':
                return XoStatus.O_WIN

        if len(XoGame.possible_moves(game_state)) == 0:
            return XoStatus.DRAW
        else:
            return XoStatus.IN_PROGRESS

    @staticmethod
    def score(result, game_state):
        assert result != XoStatus.IN_PROGRESS
        if result == XoStatus.DRAW:
            return 0.5
        elif (result == XoStatus.X_WIN and
              game_state.player == 'x'):
            return 1
        elif (result == XoStatus.O_WIN and
              game_state.player == 'o'):
            return 1
        else:
            return 0

    @staticmethod
    def apply_move(move, game_state):
        game_state.board[move.r][move.c] = move.player
        game_state.player = move.player

    @staticmethod
    def undo_move(move, game_state):
        game_state.board[move.r][move.c] = ' '
        game_state.player = opposite_player(move.player)

    @staticmethod
    def possible_moves(game_state):
        moves = [
            XoMove(r, c, opposite_player(game_state.player))
            for r in range(3)
            for c in range(3)
            if game_state.board[r][c] == ' '
        ]
        return moves

    @staticmethod
    def initial_state():
        board = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
        ]
        return XoGameState(board, 'o')

    @staticmethod
    def parse_move(move_str):
        c = ord(move_str[0]) - ord('a')
        r = ord(move_str[1]) - ord('1')
        return XoMove(r, c, None)


class XoUniformRandomPlayoutPolicy:
    def playout(self, node):
        game_state = node.game_state.copy()

        st = XoGame.status(node.game_state)
        if ((st == XoStatus.X_WIN and game_state.player == 'o')
           or (st == XoStatus.O_WIN and game_state.player == 'x')):
            node.win_count = -100
            return

        while XoGame.status(game_state) == XoStatus.IN_PROGRESS:
            move = choice(XoGame.possible_moves(game_state))
            XoGame.apply_move(move, game_state)

        return XoGame.status(game_state)


if __name__ == '__main__':
    seed()

    game = XoGame

    mct = generic_mcts.McTree(
        game,
        select_policy=generic_mcts.UctSelectPolicy(),
        playout_policy=XoUniformRandomPlayoutPolicy(),
        number_of_playouts=1000,
    )

    while True:
        game.show(mct.root.game_state)
        move = game.parse_move(input(": "))
        move.player = opposite_player(mct.root.game_state.player)
        mct.apply_move(move)
        game.show(mct.root.game_state)
        print("thinking...")
        ai_move = mct.choose_best_move()
        mct.apply_move(ai_move)
