import os
from chess_ai import Status
from chess_ai import ChessMctsPlayer
from chess_ai import ChessAlphBetaPlayer
from chess_ai import ChessRandomPlayer
from chess_ai import score_board_stockfish, score_board_with_pos_bias
from chess_ai import load_stockfish
from generic_mcts import AiPlayer


def self_play(player1: AiPlayer, player2: AiPlayer, show=False):
    player1 = player1()
    player2 = player2()
    while True:
        if show:
            player1.show()
            print()

        if player1.status() != Status.IN_PROGRESS:
            break
        move1 = player1.choose_move()
        player1.apply_move(move1)
        player2.apply_move(move1)

        if show:
            player1.show()
            print()

        if player2.status() != Status.IN_PROGRESS:
            break
        move2 = player2.choose_move()
        player1.apply_move(move2)
        player2.apply_move(move2)

    return player1.status()


def play(name, white, black, times=1, show=False):
    scores = {'white': 0, 'black': 0, 'draw': 0}
    print(name)
    for _ in range(times):
        try:
            result = self_play(white, black, show=show)
            if result == Status.DRAW:
                scores['draw'] += 1
            elif result == Status.WHITE_WIN:
                scores['white'] += 1
            else:
                scores['black'] += 1
        except Exception as e:
            print(e)
    print(scores)
