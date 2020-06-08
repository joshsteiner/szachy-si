import chess
import platform
import chess.engine
import generic_mcts
from generic_mcts import Move
import generic_alpha_beta
from colorama import Fore
from colorama import Style
from random import choice


stockfish = None


def load_stockfish():
    system = platform.system()
    if system == 'Linux':
        fn = './stockfish/stockfish_linux'
    elif system == 'Windows':
        fn = './stockfish/stockfish_windows.exe'
    elif system == 'Darwin':
        fn = './stockfish/stockfish_mac'
    stockfish = chess.engine.SimpleEngine.popen_uci(fn)


class Status:
    IN_PROGRESS = 0
    DRAW = 1
    WHITE_WIN = 2
    BLACK_WIN = 3


class Game(generic_mcts.Game):
    @staticmethod
    def status(game_state):
        r = game_state.result()
        if r == '*':
            return Status.IN_PROGRESS
        elif r == '1-0':
            return Status.WHITE_WIN
        elif r == '0-1':
            return Status.BLACK_WIN
        else:
            return Status.DRAW

    @staticmethod
    def score(result, game_state):
        if ((result == Status.WHITE_WIN and game_state.turn == chess.WHITE)
           or (result == Status.BLACK_WIN and game_state.turn == chess.BLACK)):
            return 1
        elif result == Status.DRAW:
            return 0.25
        # w normalnych warunkach MCTS powinien rozgrywać grę do końca,
        # jednak przy ograniczonej liczbie ruchów rzadko dochodzi do
        # rozstrzygnięcia
        elif result == Status.IN_PROGRESS:
            score = score_board_with_pos_bias(game_state)
            if ((score > 0 and game_state.turn == chess.WHITE)
               or (score < 0 and game_state.turn == chess.BLACK)):
                return 0.5
            else:
                return 0
        else:
            return 0

    @staticmethod
    def apply_move(move, game_state):
        game_state.push(move)

    @staticmethod
    def undo_move(move, game_state):
        game_state.pop()

    @staticmethod
    def possible_moves(game_state):
        return list(game_state.legal_moves)

    @staticmethod
    def initial_state():
        return chess.Board()

    @staticmethod
    def parse_move(move_str):
        return chess.Move.from_uci(move_str)

    @staticmethod
    def show(game_state, colors=True):
        PIECE_REPR = {
            chess.PAWN: 'P',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.ROOK: 'R',
            chess.QUEEN: 'Q',
            chess.KING: 'K',
        }
        n_rows, n_cols = 8, 8
        print("  ", end="")
        for c in range(n_cols):
            print(chr(ord('a') + c), end=" ")
        print()
        for row_number in reversed(range(8)):
            print(row_number + 1, end=" ")
            for column_number in range(8):
                piece = game_state.piece_at(row_number * 8 + column_number)
                if piece is None:
                    print(".", end=" ")
                    continue
                piece_str = PIECE_REPR[piece.piece_type]
                if colors:
                    if piece.color == chess.BLACK:
                        print(Fore.GREEN + piece_str + Style.RESET_ALL, end=" ")
                    else:
                        print(Fore.BLUE + piece_str + Style.RESET_ALL, end=" ")
                else:
                    if piece.color == chess.BLACK:
                        print(piece_str.lower(), end=" ")
                    else:
                        print(piece_str.upper(), end=" ")
            print()


class ChessMctsPlayer(generic_mcts.AiPlayer):
    def __init__(self, max_playout_len=100, number_of_playouts=200, colors=False):
        self.game = Game
        self.colors = colors
        self.mct = generic_mcts.McTree(
            self.game,
            select_policy=generic_mcts.UctSelectPolicy(),
            playout_policy=UniformRandomPlayoutPolicy(max_playout_len),
            number_of_playouts=number_of_playouts,
        )

    def status(self) -> Status:
        return self.game.status(self.mct.root.game_state)

    def choose_move(self) -> Move:
        return self.mct.choose_best_move()

    def apply_move(self, move: Move):
        self.mct.apply_move(move)

    def show(self):
        self.game.show(self.mct.root.game_state, colors=self.colors)


class ChessAlphBetaPlayer(generic_mcts.AiPlayer):
    def __init__(self, search_depth=5, colors=False):
        self.game = Game
        self.colors = colors
        self.board = self.game.initial_state()
        self.search_depth = search_depth

    def status(self) -> Status:
        return self.game.status(self.board)

    def choose_move(self) -> Move:
        return generic_alpha_beta.choose_best_move_minimax(
            self.game, self.board,
            score_board_with_pos_bias,
            self.search_depth,
            self.board.turn == chess.WHITE)

    def apply_move(self, move: Move):
        self.game.apply_move(move, self.board)

    def show(self):
        self.game.show(self.board, colors=self.colors)


class ChessRandomPlayer(generic_mcts.AiPlayer):
    def __init__(self, colors=False):
        self.game = Game
        self.colors = colors
        self.board = self.game.initial_state()

    def status(self) -> Status:
        return self.game.status(self.board)

    def choose_move(self) -> Move:
        return choice(self.game.possible_moves(self.board))

    def apply_move(self, move: Move):
        self.game.apply_move(move, self.board)

    def show(self):
        self.game.show(self.board, colors=self.colors)


class UniformRandomPlayoutPolicy:
    def __init__(self, max_playout_len=100):
        self.max_playout_len = max_playout_len

    def playout(self, node):
        state = node.game_state.copy()
        for _ in range(self.max_playout_len):
            if state.result() != '*':
                return
            move = choice(list(state.legal_moves))
            state.push(move)

        return Game.status(state)


POSITION_BIAS = {
    chess.PAWN: [
        [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        [ 0.5,  1.0,  1.0, -2.0, -2.0,  1.0,  1.0,  0.5],
        [ 0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
        [ 0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
        [ 0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
        [ 1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
        [ 5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
        [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    ],

    chess.KNIGHT: [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
        [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
        [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
        [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
        [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
        [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    ],

    chess.BISHOP: [
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [-1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
        [-1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
        [-1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
        [-1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
        [-1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
        [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    ],

    chess.ROOK: [
        [ 0.0,  0.0,  0.0,  0.5,  0.5,  0.0,  0.0,  0.0],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [ 0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
        [ 0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    ],

    chess.QUEEN: [
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [-1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [ 0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [-0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [-1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    ],

    chess.KING: [
        [ 2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0],
        [ 2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0],
        [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    ],
}


def score_board_with_pos_bias(board):
    PIECE_VAL = {
        chess.PAWN: 10,
        chess.KNIGHT: 30,
        chess.BISHOP: 30,
        chess.ROOK: 50,
        chess.QUEEN: 90,
        chess.KING: 900,
    }

    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -20000
        else:
            return 20000

    def mirror(r, c):
        return (7 - r, 7 - c)
    s = 0
    for r in range(8):
        for c in range(8):
            piece = board.piece_at(8 * r + c)
            if piece is None:
                continue
            piece_score = PIECE_VAL[piece.piece_type]
            mr, mc = r, c
            if piece.color == chess.BLACK:
                mr, mc = mirror(r, c)
            piece_score += POSITION_BIAS[piece.piece_type][mr][mc]
            if piece.color == chess.WHITE:
                s += piece_score
            else:
                s -= piece_score
    return s


def score_board_stockfish(board):
    info = stockfish.analyse(board, chess.engine.Limit(depth=1), info=chess.engine.INFO_SCORE)
    score = info['score'].white().score(mate_score=10000)
    if info['score'].is_mate():
        return 0
    return score

def play_against_computer(method, **kwargs):
    load_stockfish()

    if method == 'mcts':
        game = Game

        mct = generic_mcts.McTree(
            game,
            select_policy=kwargs['select_policy'],
            playout_policy=kwargs['playout_policy'],
            number_of_playouts=kwargs['number_of_playouts'],
        )

        while True:
            game.show(mct.root.game_state)
            move = game.parse_move(input(": "))
            mct.apply_move(move)
            game.show(mct.root.game_state)
            print("thinking...")
            ai_move = mct.choose_best_move()
            mct.apply_move(ai_move)
            print()
    elif method == 'alpha beta':
        try:
            load_stockfish()

            game = Game
            board = game.initial_state()

            while True:
                game.show(board)
                move = game.parse_move(input(": "))
                game.apply_move(move, board)
                game.show(board)
                print("thinking...")
                ai_move = generic_alpha_beta.choose_best_move_minimax(
                    game, board,
                    kwargs['heuristics'],
                    kwargs['depth'],
                    False
                )
                game.apply_move(ai_move, board)
                print()
        finally:
            stockfish.quit()


if __name__ == '__main__':
    play_against_computer('mcts', select_policy=generic_mcts.UctSelectPolicy(),
                          playout_policy=UniformRandomPlayoutPolicy(),
                          number_of_playouts=200)

    play_against_computer('alpha beta', heuristics=score_board_stockfish, depth=3)
