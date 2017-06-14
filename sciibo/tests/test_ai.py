import unittest

from sciibo.bot import ai
from sciibo.core.helpers import nextcard, fitson


def print_layout(stock=None, discards=None, hand=None, builds=None):
    layout = "" \
        "    __   __   __   __                      \n" \
        "   |xx| |xx| |xx| |xx|                     \n" \
        "   |__| |__| |__| |__|                     \n" \
        " __    __   __   __   __    __ __ __ __ __ \n" \
        "|xx|  |xx| |xx| |xx| |xx|  |xx|xx|xx|xx|xx|\n" \
        "|__|  |__| |__| |__| |__|  |__|__|__|__|__|"

    layout = layout.replace('xx', '%2s')
    values = []

    for n in range(4):
        try:
            values.append(builds[n])
        except:
            values.append('')

    values.append(stock or '')

    for n in range(4):
        try:
            values.append(discards[n][0])
        except:
            values.append('')

    for n in range(5):
        try:
            values.append(hand[n])
        except:
            values.append('')

    print(layout % tuple(values))

    for y in range(1, max(len(cards) for cards in discards)):
        line1 = " " * 5
        line2 = line1

        for n in range(4):
            try:
                line1 += " |%2s|" % discards[n][y]
                line2 += " |__|"
            except:
                line1 += "         "
                line2 += "         "

        print(line1)
        print(line2)


def print_moves(moves):
    if not moves:
        print("No moves possible")
        return

    for value, source, target in moves:
        print("Move card with value %s from %s to %s" % (value, source, target))


class TestAI(unittest.TestCase):
    """
    Helper methods
    """
    def test_next_card(self):
        self.assertEqual(nextcard(1), 2)
        self.assertEqual(nextcard(2), 3)
        self.assertEqual(nextcard(3), 4)
        self.assertEqual(nextcard(4), 5)
        self.assertEqual(nextcard(5), 6)
        self.assertEqual(nextcard(6), 7)
        self.assertEqual(nextcard(7), 8)
        self.assertEqual(nextcard(8), 9)
        self.assertEqual(nextcard(9), 10)
        self.assertEqual(nextcard(10), 11)
        self.assertEqual(nextcard(11), 12)
        self.assertEqual(nextcard(12), 1)

    def test_fitson(self):
        self.assertTrue(fitson(1, 2))
        self.assertTrue(fitson(6, 7))
        self.assertTrue(fitson(12, 1))
        self.assertTrue(fitson(1, 'SB'))
        self.assertTrue(fitson(6, 'SB'))
        self.assertTrue(fitson(12, 'SB'))

        self.assertFalse(fitson(1, 1))
        self.assertFalse(fitson(1, 3))
        self.assertFalse(fitson(1, 12))
        self.assertFalse(fitson(6, 6))
        self.assertFalse(fitson(7, 6))
        self.assertFalse(fitson(12, 12))

    def test_enumerate_unique(self):
        result = list(ai.enumerate_unique([1, 2, 2, 3, 4, 4]))
        expected = [
            (0, 1),
            (1, 2),
            (3, 3),
            (4, 4),
        ]
        self.assertEqual(result, expected)

    def test_top_cards(self):
        result = list(ai.top_cards([[1, 2, 3], [], [4, 5, 6], [7, 8, 9]]))
        expected = [(0, 3), (2, 6), (3, 9)]
        self.assertEqual(result, expected)

    def test_pull(self):
        result = ai.pull([4, 5, 6, 7, 8], 6)
        expected = [4, 5, 7, 8]
        self.assertEqual(result, expected)

    def test_pull_top(self):
        result = ai.pull_top([[1, 2, 3], [], [4, 5, 6], [7, 8, 9]], 2)
        expected = [[1, 2, 3], [], [4, 5], [7, 8, 9]]
        self.assertEqual(result, expected)

    def test_place(self):
        result = ai.place([1, 4, 7, 10, 12], 2, 9)
        expected = [1, 4, 9, 10, 12]
        self.assertEqual(result, expected)

    """
    Best moves
    """
    def test_best_moves(self):
        # Play the hand with least SB and most hand cards
        moves = [
            # 1 SB, 1 hand cards
            [
                ('SB', 'discard:0', 'build:0'),
                (8, 'discard:0', 'build:0'),
                (9, 'hand', 'build:0'),
                (10, 'discard:1', 'build:0'),
            ],
            # 1 SB, 2 hand cards
            [
                ('SB', 'hand', 'build:0'),
                (8, 'discard:0', 'build:0'),
                (9, 'hand', 'build:0'),
                (10, 'discard:1', 'build:0'),
            ],
            # 2 SB, 2 hand cards
            [
                ('SB', 'hand', 'build:0'),
                ('SB', 'discard:0', 'build:0'),
                (9, 'hand', 'build:0'),
                (10, 'discard:1', 'build:0'),
            ],
            # 1 SB, 0 hand cards
            [
                ('SB', 'discard:0', 'build:0'),
                (8, 'discard:0', 'build:0'),
                (9, 'discard:2', 'build:0'),
                (10, 'discard:1', 'build:0'),
            ],
        ]
        expected = moves[1]
        result = ai.best_moves(moves)
        self.assertEqual(result, expected)

    """
    Lucky move
    """
    def test_lucky_move(self):
        # Stock before hand and discard
        values = {
            'stock': 5,
            'discards': [[8], ['SB', 2, 5], [], []],
            'hand': [9, 7, 12, 5, 'SB'],
            'builds': [2, 3, 1, 4],
        }
        self.assertEqual(ai.lucky_move(**values), [(5, 'stock', 'build:3')])

        # Hand number before hand SB and discard
        values = {
            'stock': 1,
            'discards': [[8], ['SB', 2, 5], [], []],
            'hand': [9, 7, 12, 5, 'SB'],
            'builds': [2, 3, 1, 4],
        }
        self.assertEqual(ai.lucky_move(**values), [(5, 'hand', 'build:3')])

        # Discard number before hand SB
        values = {
            'stock': 1,
            'discards': [[8], ['SB', 2, 5], [], []],
            'hand': [9, 7, 12, 'SB'],
            'builds': [2, 3, 1, 4],
        }
        self.assertEqual(ai.lucky_move(**values), [(5, 'discard:1', 'build:3')])

        # Hand SB before discard SB
        values = {
            'stock': 1,
            'discards': [[8], [9, 'SB'], [], []],
            'hand': [9, 7, 12, 'SB'],
            'builds': [2, 3, 1, 4],
        }
        self.assertEqual(ai.lucky_move(**values), [('SB', 'hand', 'build:0')])

        # Discard SB
        values = {
            'stock': 1,
            'discards': [[8], [9, 'SB'], [], []],
            'hand': [9, 7, 12],
            'builds': [2, 3, 1, 4],
        }
        self.assertEqual(ai.lucky_move(**values), [('SB', 'discard:1', 'build:0')])

        # No moves
        values = {
            'stock': 1,
            'discards': [[8], [2, 9], [], []],
            'hand': [9, 7, 12],
            'builds': [2, 3, 1, 4],
        }
        self.assertEqual(ai.lucky_move(**values), None)

    """
    Discard move
    """
    def test_discard_move(self):
        # Same number value
        values = {
            'discards': [[8], [5], [9], [12]],
            'hand': [11, 9, 7, 4, 'SB'],
        }
        self.assertEqual(ai.discard_move(**values), [(9, 'hand', 'discard:2')])

        # Empty discard pile
        values = {
            'discards': [[8], [5], [], [12]],
            'hand': [11, 7, 4, 'SB'],
        }
        result = ai.discard_move(**values)
        value, source, target = result[0]  # First move
        self.assertIn(value, values['hand'])
        self.assertEqual(source, 'hand')
        self.assertEqual(target, 'discard:2')

        # Count down
        values = {
            'discards': [[8], [5], [9], [12]],
            'hand': [11, 7, 4, 'SB'],
        }
        self.assertEqual(ai.discard_move(**values), [(7, 'hand', 'discard:0')])

        # Same SB value
        values = {
            'discards': [[8], [5], ['SB'], []],
            'hand': [12, 7, 4, 'SB'],
        }
        self.assertEqual(ai.discard_move(**values), [('SB', 'hand', 'discard:2')])

        # Falls back to random choice, kind of difficult to test

    """
    Any move
    """
    def test_any_move(self):
        # No moves
        values = {
            'stock': 1,
            'discards': [[8], [2, 9], [], []],
            'hand': [9, 7, 12],
            'builds': [2, 3, 1, 4],
        }
        self.assertFalse(ai.any_move(**values))

        # Number
        values = {
            'stock': 5,
            'discards': [[8], [2, 9], [], []],
            'hand': [9, 7, 12],
            'builds': [2, 3, 1, 4],
        }
        self.assertTrue(ai.any_move(**values))

        values = {
            'stock': 1,
            'discards': [[8], [2, 4], [], []],
            'hand': [9, 7, 12],
            'builds': [2, 3, 1, 4],
        }
        self.assertTrue(ai.any_move(**values))

        values = {
            'stock': 1,
            'discards': [[8], [2, 9], [], []],
            'hand': [9, 7, 12, 3],
            'builds': [2, 3, 1, 4],
        }
        self.assertTrue(ai.any_move(**values))

        # SB
        values = {
            'stock': 'SB',
            'discards': [[8], [2, 9], [], []],
            'hand': [9, 7, 12],
            'builds': [2, 3, 1, 4],
        }
        self.assertTrue(ai.any_move(**values))

        values = {
            'stock': 1,
            'discards': [[8], [2, 'SB'], [], []],
            'hand': [9, 7, 12],
            'builds': [2, 3, 1, 4],
        }
        self.assertTrue(ai.any_move(**values))

        values = {
            'stock': 1,
            'discards': [[8], [2, 9], [], []],
            'hand': [9, 7, 12, 'SB'],
            'builds': [2, 3, 1, 4],
        }
        self.assertTrue(ai.any_move(**values))

    """
    Stock moves
    """
    def test_stock_non_greedy_hand(self):
        # 3 must be played from discard instead of hand to release 12
        values = {
            'stock': 1,
            'discards': [[12, 3], [7], [2], []],
            'hand': [3, 9, 7, 10],
            'builds': [11, 1, 6, 9],
        }
        expected = [
            (2, 'discard:2', 'build:1'),
            (3, 'discard:0', 'build:1'),
            (12, 'discard:0', 'build:0'),
            (1, 'stock', 'build:0'),
        ]
        result = ai.stock_moves(**values)
        self.assertEqual(result, expected)

    """
    Most moves
    """
    def test_most_number_over_sb(self):
        # SB must not be played, does not help us
        values = {
            'discards': [['SB'], [6], [7], [8]],
            'hand': [6, 8],
            'builds': [1, 5, 12, 12],
        }
        expected = [
            (6, 'hand', 'build:1'),
            (7, 'discard:2', 'build:1'),
            (8, 'hand', 'build:1'),
        ]
        result = ai.most_moves(**values)
        self.assertEqual(result, expected)

    def test_most_clear(self):
        # Clear hand
        values = {
            'discards': [[], [], [], []],
            'hand': [6, 7, 8, 'SB', 2],
            'builds': [5, 12, 12, 12],
        }
        expected = [
            ('SB', 'hand', 'build:1'),
            (2, 'hand', 'build:1'),
            (6, 'hand', 'build:0'),
            (7, 'hand', 'build:0'),
            (8, 'hand', 'build:0'),
        ]
        result = ai.most_moves(**values)
        self.assertEqual(result, expected)

    def test_most_keep_sb(self):
        # Don't play SB card
        values = {
            'discards': [[], [], [], []],
            'hand': [6, 7, 8, 'SB', 3],
            'builds': [5, 12, 12, 12],
        }
        expected = [
            (6, 'hand', 'build:0'),
            (7, 'hand', 'build:0'),
            (8, 'hand', 'build:0'),
        ]
        result = ai.most_moves(**values)
        self.assertEqual(result, expected)

    def test_most_sb_to_clear_hand(self):
        # Play SB to clear hand
        values = {
            'discards': [[], [], [], []],
            'hand': [6, 7, 8, 'SB'],
            'builds': [5, 12, 12, 12],
        }
        expected = [
            (6, 'hand', 'build:0'),
            (7, 'hand', 'build:0'),
            (8, 'hand', 'build:0'),
            ('SB', 'hand', 'build:0'),
        ]
        result = ai.most_moves(**values)
        self.assertEqual(result, expected)

    def test_most_play_hand_sb_keep_discard_sb(self):
        # Play SB to clear hand, but don't play SB in discards
        values = {
            'discards': [['SB'], [], [], []],
            'hand': [6, 7, 8, 'SB'],
            'builds': [5, 1, 12, 12],
        }
        expected = [
            (6, 'hand', 'build:0'),
            (7, 'hand', 'build:0'),
            (8, 'hand', 'build:0'),
            ('SB', 'hand', 'build:0'),
        ]
        result = ai.most_moves(**values)
        self.assertEqual(result, expected)

    def test_most_dont_waste_sb(self):
        # Don't waste SB cards to clear hand
        values = {
            'discards': [[], [], [], []],
            'hand': [2, 'SB', 'SB'],
            'builds': [1, 2, 3, 4],
        }
        expected = [
            (2, 'hand', 'build:0'),
        ]
        result = ai.most_moves(**values)
        self.assertEqual(result, expected)

    """
    Calculate moves
    """
    def test_calculate_terminates(self):
        # Large calculations must terminate
        values = {
            'stock': 26,
            'discards': [[7, 6, 5, 4, 2], [11, 11, 9, 8, 6], [11], [10]],
            'hand': ['SB', 'SB', 'SB', 'SB', 'SB'],
            'builds': [1, 2, 3, 4],
        }
        expected = [
            (2, 'discard:0', 'build:0'),
        ]
        result = ai.calculate_move(timeout=1, **values)
        self.assertEqual(result, expected)

    """
    Specific bugs
    """
    def test_bug(self):
        values = {
            'stock': 1,
            'discards': [[], [], [], []],
            'hand': [3, 7, 2, 11, 12],
            'builds': [12, 12, 12, 12],
        }
        expected = [
            (1, 'stock', 'build:0'),
        ]
        result = ai.calculate_move(**values)
        self.assertEqual(result, expected)

    def test_bug_1(self):
        # Unexpected behavior:
        # result: [('SB', 'hand', 'build:0')]
        values = {
            'stock': 6,
            'discards': [[6], [7], [], []],
            'hand': [8, 7, 12, 9, 'SB'],
            'builds': [3, 12, 12, 12],
        }
        expected = [
            (7, 'hand', 'discard:1'),
        ]
        result = ai.calculate_move(**values)
        self.assertEqual(result, expected)

    def test_bug_2(self):
        # Unexpected behavior:
        # result: [('SB', 'hand', 'build:0')]
        values = {
            'stock': 7,
            'discards': [[9], [], [], []],
            'hand': [10, 'SB', 6],
            'builds': [10, 2, 2, 1],
        }
        expected = [
            [(6, 'hand', 'discard:1')],
            [(10, 'hand', 'discard:1')],
        ]
        result = ai.calculate_move(**values)
        self.assertIn(result, expected)

    def test_bug_3(self):
        values = {
            'stock': 12,
            'discards': [[], [], [], []],
            'hand': ['SB', 'SB', 9],
            'builds': [4, 12, 12, 12],
        }
        expected = [
            (9, 'hand', 'discard:0'),
        ]
        result = ai.calculate_move(**values)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
