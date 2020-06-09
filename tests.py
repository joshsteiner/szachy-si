import os
from self_play import play
from chess_ai import ChessMctsPlayer
from chess_ai import ChessAlphBetaPlayer
from chess_ai import ChessRandomPlayer
from chess_ai import score_board_stockfish, score_board_with_pos_bias
from chess_ai import load_stockfish
from chess_ai import UniformRandomPlayoutPolicy


try:
    global stockfish
    load_stockfish()

    play(
        "alpha beta (white), 1, score_board_with_pos_bias",
        white=lambda: ChessAlphBetaPlayer(
            search_depth=1,
            heuristic=score_board_with_pos_bias,
        ),
        black=lambda: ChessRandomPlayer(),
        times=5,
        show=False,
    )

    play(
        "alpha beta (black), 1, score_board_with_pos_bias",
        white=lambda: ChessRandomPlayer(),
        black=lambda: ChessAlphBetaPlayer(
            search_depth=1,
            heuristic=score_board_with_pos_bias,
        ),
        times=5,
        show=False,
    )

    play(
        "alpha beta (white), 2, score_board_with_pos_bias",
        white=lambda: ChessAlphBetaPlayer(
            search_depth=2,
            heuristic=score_board_with_pos_bias,
        ),
        black=lambda: ChessRandomPlayer(),
        times=5,
        show=False,
    )

    play(
        "alpha beta (black), 2, score_board_with_pos_bias",
        white=lambda: ChessRandomPlayer(),
        black=lambda: ChessAlphBetaPlayer(
            search_depth=2,
            heuristic=score_board_with_pos_bias,
        ),
        times=5,
        show=False,
    )

    play(
        "alpha beta (white), 3, score_board_with_pos_bias",
        white=lambda: ChessAlphBetaPlayer(
            search_depth=3,
            heuristic=score_board_with_pos_bias,
        ),
        black=lambda: ChessRandomPlayer(),
        times=5,
        show=False,
    )

    play(
        "alpha beta (black), 3, score_board_with_pos_bias",
        white=lambda: ChessRandomPlayer(),
        black=lambda: ChessAlphBetaPlayer(
            search_depth=3,
            heuristic=score_board_with_pos_bias,
        ),
        times=5,
        show=False,
    )

    play(
        "alpha beta (white), 1, score_board_stockfish",
        white=lambda: ChessAlphBetaPlayer(
            search_depth=1,
            heuristic=score_board_stockfish,
        ),
        black=lambda: ChessRandomPlayer(),
        times=5,
        show=False,
    )

    play(
        "alpha beta (black), 1, score_board_stockfish",
        white=lambda: ChessRandomPlayer(),
        black=lambda: ChessAlphBetaPlayer(
            search_depth=1,
            heuristic=score_board_stockfish,
        ),
        times=5,
        show=False,
    )

    play(
        "alpha beta (white), 2, score_board_stockfish",
        white=lambda: ChessAlphBetaPlayer(
            search_depth=2,
            heuristic=score_board_stockfish,
        ),
        black=lambda: ChessRandomPlayer(),
        times=5,
        show=False,
    )

    play(
        "alpha beta (black), 2, score_board_stockfish",
        white=lambda: ChessRandomPlayer(),
        black=lambda: ChessAlphBetaPlayer(
            search_depth=2,
            heuristic=score_board_stockfish,
        ),
        times=5,
        show=False,
    )

    play(
        "MCTS (white), 200",
        white=lambda: ChessMctsPlayer(
            colors=True,
            playout_policy=UniformRandomPlayoutPolicy(max_playout_len=100),
            number_of_playouts=200,
        ),
        black=lambda: ChessRandomPlayer(),
        times=5,
        show=False,
    )

    play(
        "MCTS (black), 200",
        white=lambda: ChessRandomPlayer(),
        black=lambda: ChessMctsPlayer(
            playout_policy=UniformRandomPlayoutPolicy(max_playout_len=100),
            number_of_playouts=200,
        ),
        times=5,
        show=False,
    )

finally:
    os._exit(0)
