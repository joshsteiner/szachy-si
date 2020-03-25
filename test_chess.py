import unittest
from chess import position_to_alg_notation, board, possible_moves, WHITE, BLACK


class Test(unittest.TestCase):

    def test_start_position(self):
        """
        test if `possible_moves' returns correct moves from start position
        """
        moves_got = {
            (position_to_alg_notation(frm), position_to_alg_notation(to))
            for (frm, to, _, _)
            in possible_moves(board, WHITE)
        }
        moves_expected = {
            # pawn movements
            ('a2', 'a3'), ('a2', 'a4'),
            ('b2', 'b3'), ('b2', 'b4'),
            ('c2', 'c3'), ('c2', 'c4'),
            ('d2', 'd3'), ('d2', 'd4'),
            ('e2', 'e3'), ('e2', 'e4'),
            ('f2', 'f3'), ('f2', 'f4'),
            ('g2', 'g3'), ('g2', 'g4'),
            ('h2', 'h3'), ('h2', 'h4'),

            # knight movements
            ('b1', 'a3'), ('b1', 'c3'),
            ('g1', 'f3'), ('g1', 'h3'),
        }
        self.assertEqual(moves_expected, moves_got)

        moves_got = {
            (position_to_alg_notation(frm), position_to_alg_notation(to))
            for (frm, to, _, _)
            in possible_moves(board, BLACK)
        }
        moves_expected = {
            # pawn movements
            ('a7', 'a6'), ('a7', 'a5'),
            ('b7', 'b6'), ('b7', 'b5'),
            ('c7', 'c6'), ('c7', 'c5'),
            ('d7', 'd6'), ('d7', 'd5'),
            ('e7', 'e6'), ('e7', 'e5'),
            ('f7', 'f6'), ('f7', 'f5'),
            ('g7', 'g6'), ('g7', 'g5'),
            ('h7', 'h6'), ('h7', 'h5'),

            # knight movements
            ('b8', 'a6'), ('b8', 'c6'),
            ('g8', 'f6'), ('g8', 'h6'),
        }
        self.assertEqual(moves_expected, moves_got)


if __name__ == '__main__':
    unittest.main()
