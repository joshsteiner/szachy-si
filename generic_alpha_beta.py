import math
from random import choice


def minimax(game, game_state, heuristic, depth, alpha, beta, is_maxing_player):
    if depth == 1:
        return heuristic(game_state)

    if is_maxing_player:
        best_move = -math.inf
        for move in game.possible_moves(game_state):
            game.apply_move(move, game_state)
            best_move = max(
                best_move,
                minimax(
                    game, game_state, heuristic,
                    depth - 1, alpha, beta,
                    not is_maxing_player
                )
            )
            game.undo_move(move, game_state)
            alpha = max(alpha, best_move)
            if beta <= alpha:
                return best_move
        return best_move
    else:
        best_move = math.inf
        for move in game.possible_moves(game_state):
            game.apply_move(move, game_state)
            best_move = min(
                best_move,
                minimax(
                    game, game_state, heuristic,
                    depth - 1, alpha, beta,
                    not is_maxing_player
                )
            )
            game.undo_move(move, game_state)
            beta = min(beta, best_move)
            if beta <= alpha:
                return best_move
        return best_move


def choose_best_move_minimax(game, game_state, heuristic, search_depth, is_maxing_player):
    best_moves = []
    if is_maxing_player:
        f = max
        best_score = -math.inf
    else:
        f = min
        best_score = math.inf
    for move in game.possible_moves(game_state):
        game.apply_move(move, game_state)
        child_score = minimax(
            game, game_state, heuristic, search_depth,
            -math.inf, math.inf, is_maxing_player
        )
        game.undo_move(move, game_state)
        if f(child_score, best_score) == child_score:
            if child_score == best_score:
                best_moves.append(move)
            else:
                best_moves = [move]
            best_score = child_score
    return choice(best_moves)
