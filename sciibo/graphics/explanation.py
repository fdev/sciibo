import curses

from sciibo.core.drawable import Drawable

from .card import Card
from ..graphics import colors


class Explanation(Drawable):
    def __init__(self, y, x):
        super(Explanation, self).__init__(y, x, 14, 58)
        self.set_color(colors.PLAYFIELD)
        self.update()

    def update(self):
        self.erase()

        # Build piles
        self.draw_ch(0, 16, curses.ACS_ULCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_hline(1, 12, 20, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(1, 11, curses.ACS_ULCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(1, 18, curses.ACS_TTEE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(1, 25, curses.ACS_TTEE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(1, 32, curses.ACS_URCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(1, 16, curses.ACS_BTEE, color=colors.PLAYFIELD_TEXT)
        self.draw_str(0, 18, "Build piles", color=colors.PLAYFIELD_TEXT)

        self.add_child(Card(2,  9,  3, 'small'))
        self.add_child(Card(2, 16, 10, 'small'))
        self.draw_rectangle(2, 23,  4, 5, dashed=True)
        self.add_child(Card(2, 30,  7, 'small'))

        # Draw pile
        self.draw_ch(0, 41, curses.ACS_ULCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(1, 41, curses.ACS_VLINE, color=colors.PLAYFIELD_TEXT)
        self.draw_str(0, 43, "Draw pile", color=colors.PLAYFIELD_TEXT)

        self.add_child(Card(2, 41, 'back', 'small'))
        self.add_child(Card(2, 40, 'back', 'small'))
        self.add_child(Card(2, 39, 'back', 'small'))

        # Playfield
        self.draw_rectangle(6, 0, 6, 58)

        # Stock pile
        self.add_child(Card(7, 4, 'back', 'small'))
        self.add_child(Card(7, 3, 'back', 'small'))
        self.add_child(Card(7, 2, 10, 'small'))

        self.draw_ch(11, 4, curses.ACS_VLINE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(12, 4, curses.ACS_LLCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_str(12, 6, "Stock pile", color=colors.PLAYFIELD_TEXT)

        # Discard piles
        self.draw_rectangle(7, 13, 3, 4, dashed=True)
        self.draw_rectangle(7, 10, 3, 4, dashed=True)

        self.draw_rectangle(7, 21, 3, 4, dashed=True)
        self.draw_rectangle(7, 18, 3, 4, dashed=True)

        self.draw_rectangle(7, 29, 3, 4, dashed=True)
        self.draw_rectangle(7, 26, 3, 4, dashed=True)

        self.draw_rectangle(7, 37, 3, 4, dashed=True)
        self.draw_rectangle(7, 34, 3, 4, dashed=True)

        self.add_child(Card(7, 13,  12, 'tiny'))
        self.add_child(Card(7, 10,  6, 'tiny'))
        self.add_child(Card(7, 26, 1, 'tiny'))

        self.draw_hline(10, 12, 24, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(10, 11, curses.ACS_LLCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(10, 19, curses.ACS_BTEE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(10, 28, curses.ACS_BTEE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(10, 36, curses.ACS_LRCORNER, color=colors.PLAYFIELD_TEXT)

        self.draw_ch(10, 22, curses.ACS_TTEE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(11, 22, curses.ACS_VLINE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(12, 22, curses.ACS_LLCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_str(12, 24, "Discard piles", color=colors.PLAYFIELD_TEXT)

        # Hand
        self.add_child(Card(7, 51, 11, 'small'))
        self.add_child(Card(7, 49, 2, 'small'))
        self.add_child(Card(7, 47, 8, 'small'))
        self.add_child(Card(7, 45, 'SB', 'small'))
        self.add_child(Card(7, 43, 4, 'small'))

        self.draw_ch(11, 54, curses.ACS_VLINE, color=colors.PLAYFIELD_TEXT)
        self.draw_ch(12, 54, curses.ACS_LRCORNER, color=colors.PLAYFIELD_TEXT)
        self.draw_str(12, 43, "Hand cards", color=colors.PLAYFIELD_TEXT)
