"""
    Chess game implementation and position generation
"""

import numpy as np
from random import randint
from collections import namedtuple
import math

counter = 0

SEARCH_DEPTH = 4

# piece format:
#  3 bits piece type, 1 bit color
#  piece = 0 is empty square

WHITE = 0
BLACK = 1

PAWN = 1 << 1
KNIGHT = 2 << 1
BISHOP = 3 << 1
ROOK = 4 << 1
QUEEN = 5 << 1
KING = 6 << 1

EMPTY_SQUARE = 0
WHITE_PAWN = WHITE | PAWN
WHITE_KNIGHT = WHITE | KNIGHT
WHITE_BISHOP = WHITE | BISHOP
WHITE_ROOK = WHITE | ROOK
WHITE_QUEEN = WHITE | QUEEN
WHITE_KING = WHITE | KING
BLACK_PAWN = BLACK | PAWN
BLACK_KNIGHT = BLACK | KNIGHT
BLACK_BISHOP = BLACK | BISHOP
BLACK_ROOK = BLACK | ROOK
BLACK_QUEEN = BLACK | QUEEN
BLACK_KING = BLACK | KING

WHITE_PAWN_ROW = 1
BLACK_PAWN_ROW = 6
WHITE_PROMOTION_ROW = 7
BLACK_PROMOTION_ROW = 0

ROOK_DIRECTIONS = np.array([[-1, 0], [+1, 0], [0, -1], [0, +1]])
BISHOP_DIRECTIONS = np.array([[-1, -1], [-1, +1], [+1, -1], [+1, +1]])
QUEEN_DIRECTIONS = np.concatenate((ROOK_DIRECTIONS, BISHOP_DIRECTIONS))
KING_DIRECTIONS = QUEEN_DIRECTIONS  # same as queen but 1 space at a time
KNIGHT_DIRECTIONS = np.array([[-2, -1], [-2, +1], [-1, -2], [-1, +2],
                             [+1, -2], [+1, +2], [+2, -1], [+2, +1]])


board = np.array([
    [WHITE_ROOK, WHITE_KNIGHT, WHITE_BISHOP, WHITE_QUEEN,
     WHITE_KING, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK],
    [WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN,
     WHITE_PAWN, WHITE_PAWN, WHITE_PAWN, WHITE_PAWN],
    [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE,
     EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
    [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE,
     EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
    [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE,
     EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
    [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE,
     EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
    [BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN,
     BLACK_PAWN, BLACK_PAWN, BLACK_PAWN, BLACK_PAWN],
    [BLACK_ROOK, BLACK_KNIGHT, BLACK_BISHOP, BLACK_QUEEN,
     BLACK_KING, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK]
])


Move = namedtuple('Move', 'frm to capture promotion')
PartialMove = namedtuple('PartialMove', 'to capture promotion')


def switch_color(color):
    return color ^ 1


def get_color(piece):
    """ Returns the color of the given piece """
    return piece & 1


def get_piece_type(piece):
    """ Returns the piece type of the given piece """
    return piece & ~1


def is_offboard(position, board):
    """ Returns true if position lies off board """
    n_rows, n_cols = board.shape
    return (
        position[0] < 0
        or position[1] < 0
        or position[0] >= n_rows
        or position[1] >= n_cols
    )


def offset(p, d):
    """ Returns position shifted by d """
    return p + d


def score_board_material(board):
    score_board = np.zeros(board.shape, dtype=np.int64)
    pieces = get_piece_type(board)
    score_board[pieces == KING] = 900
    score_board[pieces == QUEEN] = 90
    score_board[pieces == ROOK] = 50
    score_board[pieces == BISHOP] = 30
    score_board[pieces == KNIGHT] = 30
    score_board[pieces == PAWN] = 10
    score_board[get_color(board) == BLACK] *= -1
    return score_board.sum()


PIECE_REPR = {
    PAWN: 'p', KNIGHT: 'n', BISHOP: 'b',
    ROOK: 'r', QUEEN: 'q', KING: 'k',
}


def print_board(board):
    n_rows, n_cols = board.shape
    print("  ", end="")
    for c in range(n_cols):
        print(chr(ord('a') + c), end=" ")
    print()
    for row_number, row in enumerate(board[::-1]):
        print(n_rows - row_number, end=" ")
        for piece in row:
            if piece == EMPTY_SQUARE:
                print(".", end=" ")
                continue
            piece_str = PIECE_REPR[get_piece_type(piece)]
            if get_color(piece) == BLACK:
                piece_str = piece_str.upper()
            print(piece_str, end=" ")
        print()


def is_in_check_(board, color):
    """ Returns True if color is in check """
    for _, _, capture, _ in possible_moves(board, switch_color(color), True):
        if capture != EMPTY_SQUARE and get_piece_type(capture) == KING:
            return True
    return False


def is_in_check(board, color):
    """ Return True if color is in check """
    r, c = np.where(board == color | KING)
    king_position = np.array([r[0], c[0]])
    for piece in [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]:
        board[king_position[0], king_position[1]] = piece | color
        moves = possible_moves_from_position(board, color, king_position)
        for _, capture, _ in moves:
            if capture != EMPTY_SQUARE and get_piece_type(capture) == piece:
                board[king_position[0], king_position[1]] = KING | color
                return True
    board[king_position[0], king_position[1]] = KING | color
    return False


def apply_move(board, move):
    frm, to, _, promotion_piece = move
    board[to[0], to[1]] = board[frm[0], frm[1]]
    board[frm[0], frm[1]] = EMPTY_SQUARE
    if promotion_piece:
        color = get_color(board[to[0], to[1]])
        board[to[0], to[1]] = color | promotion_piece


def undo_move(board, move):
    frm, to, cpt, promotion_piece = move
    board[frm[0], frm[1]] = board[to[0], to[1]]
    board[to[0], to[1]] = cpt
    if promotion_piece:
        color = get_color(board[to[0], to[1]])
        board[frm[0], frm[1]] = color | PAWN


def possible_moves(board, color, ignore_checks=False):
    """ Generate all possible moves for color at given position """
    n_rows, n_cols = board.shape
    squares = np.array([(r, c)
                       for r in range(n_rows)
                       for c in range(n_cols)])
    for square in squares:
        for move_result in possible_moves_from_position(board, color, square):
            move = Move(square, *move_result)
            if ignore_checks:
                yield move
            else:
                apply_move(board, move)
                if not is_in_check(board, color):
                    undo_move(board, move)
                    yield move
                else:
                    undo_move(board, move)


def possible_moves_from_position(board, color, position):
    """ Generate all possible moves from position """

    def step_move(directions):
        """ Generate moves for step/jump movers (K, N) """
        for direction in directions:
            new_position = offset(position, direction)
            if not is_offboard(new_position, board):
                piece = board[new_position[0], new_position[1]]
                if piece == EMPTY_SQUARE or get_color(piece) != color:
                    yield PartialMove(new_position, piece, None)

    def range_move(directions):
        """ Generate moves for range movers (B, R, Q) """
        for direction in directions:
            i = 1
            while True:
                new_position = offset(
                    position,
                    (i * direction[0], i * direction[1]))
                if is_offboard(new_position, board):
                    break
                else:
                    piece = board[new_position[0], new_position[1]]
                    if piece == EMPTY_SQUARE:
                        yield PartialMove(new_position, EMPTY_SQUARE, None)
                        i += 1
                    elif get_color(piece) == color:
                        break
                    else:
                        yield PartialMove(new_position, piece, None)
                        break

    def pawn_move(direction, first_row=False):
        """ Generate pawn moves """
        # forward
        new_position = offset(position, (direction, 0))
        promotion_row = (WHITE_PROMOTION_ROW
                         if color == WHITE
                         else BLACK_PROMOTION_ROW)
        if (not is_offboard(new_position, board)
           and board[new_position[0], new_position[1]] == EMPTY_SQUARE):
            if new_position[0] == promotion_row:
                for promotion_piece in [PAWN, KNIGHT, BISHOP, ROOK, QUEEN]:
                    yield PartialMove(new_position, EMPTY_SQUARE, promotion_piece)
            else:
                yield PartialMove(new_position, EMPTY_SQUARE, None)

                # double move
                new_position = offset(position, (2 * direction, 0))
                if (first_row
                   and board[new_position[0], new_position[1]] == EMPTY_SQUARE):
                    yield PartialMove(new_position, EMPTY_SQUARE, None)

        # capture
        # TODO: capture promotion
        for column in (-1, 1):
            new_position = offset(position, (direction, column))
            if not is_offboard(new_position, board):
                piece_on_new_position = board[new_position[0], new_position[1]]
                if (piece_on_new_position != EMPTY_SQUARE
                   and get_color(piece_on_new_position) != color):
                    yield PartialMove(new_position, piece_on_new_position, None)

    piece = board[position[0], position[1]]
    if piece == EMPTY_SQUARE or get_color(piece) != color:
        return

    piece_type = get_piece_type(piece)

    if piece_type == PAWN:
        if color == WHITE:
            yield from pawn_move(+1, position[0] == WHITE_PAWN_ROW)
        else:
            yield from pawn_move(-1, position[1] == BLACK_PAWN_ROW)
    elif piece_type == KNIGHT:
        yield from step_move(KNIGHT_DIRECTIONS)
    elif piece_type == BISHOP:
        yield from range_move(BISHOP_DIRECTIONS)
    elif piece_type == ROOK:
        yield from range_move(ROOK_DIRECTIONS)
    elif piece_type == QUEEN:
        yield from range_move(QUEEN_DIRECTIONS)
    elif piece_type == KING:
        yield from step_move(KING_DIRECTIONS)


def algNotatationToPosition(p):
    c = ord(p[0]) - ord('a')
    r = ord(p[1]) - ord('1')
    return np.array([r, c])


def minimax(board, color, depth, alpha, beta):
    global counter
    counter += 1

    if depth == 1:
        return score_board_material(board)

    if color == WHITE:
        best_move = -math.inf
        for move in possible_moves(board, color):
            removed_piece = apply_move(board, move)
            best_move = max(
                best_move,
                minimax(board, switch_color(color), depth - 1, alpha, beta)
            )
            undo_move(board, move)
            alpha = max(alpha, best_move)
            if beta <= alpha:
                return best_move
        return best_move
    else:
        best_move = math.inf
        for move in possible_moves(board, color):
            removed_piece = apply_move(board, move)
            best_move = min(
                best_move,
                minimax(board, switch_color(color), depth - 1, alpha, beta)
            )
            undo_move(board, move)
            beta = min(beta, best_move)
            if beta <= alpha:
                return best_move
        return best_move


def choose_best_move_minimax(board, color):
    global counter
    counter = 0
    best_moves = []
    if color == WHITE:
        f = max
        best_score = -math.inf
    else:
        f = min
        best_score = math.inf
    possible_move_cnt = 0
    for move in possible_moves(board, color):
        possible_move_cnt += 1
        apply_move(board, move)
        child_score = minimax(
            board,
            switch_color(color),
            SEARCH_DEPTH,
            -math.inf,
            math.inf
        )
        undo_move(board, move)
        if f(child_score, best_score) == child_score:
            if child_score == best_score:
                best_moves.append(move)
            else:
                best_moves = [move]
            best_score = child_score
    print(f"possible moves = {possible_move_cnt}")
    return best_moves[randint(0, len(best_moves)) - 1]


if __name__ == '__main__':
    while True:
        print_board(board)
        move = input(": ").split(' ')
        frm = algNotatationToPosition(move[0])
        to = algNotatationToPosition(move[1])
        apply_move(board, (frm, to, None, None))
        ai_move = choose_best_move_minimax(board, BLACK)
        apply_move(board, ai_move)
        print(f"cc {counter}")
        print()
