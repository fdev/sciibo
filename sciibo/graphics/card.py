import curses

from sciibo.core.drawable import Drawable

from ..graphics import colors


class Card(Drawable):
    def __init__(self, y, x, value, size):
        h, w = self.hw_for_size(size)
        super(Card, self).__init__(y, x, h, w)
        self.value = value
        self.size = size
        self.update()

    def hw_for_size(self, size):
        if size == 'tiny':
            return 3, 4
        elif size == 'small':
            return 4, 5
        elif size == 'medium':
            return 5, 7
        else:
            return 6, 8

    def resize(self, size):
        if self.size == size:
            return
        self.size = size
        h, w = self.hw_for_size(size)
        super(Card, self).resize(h, w)
        self.update()

    def update(self):
        if self.value in (1, 2, 3, 4):
            self.set_color(colors.CARD_1234)
        elif self.value in (5, 6, 7, 8):
            self.set_color(colors.CARD_5678)
        elif self.value in (9, 10, 11, 12):
            self.set_color(colors.CARD_9012)
        elif self.value == 'SB':
            self.set_color(colors.CARD_SB)
        elif self.value == 'back':
            self.set_color(colors.CARD_BACK)
        elif self.value == 'slot':
            self.set_color(colors.PLAYFIELD)

        self.erase()

        # Don't draw all values
        if self.value in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 'SB'):
            # Borders
            self.draw_box()

            # Top right value
            self.draw_str(1, self.w - 2, self.value, rtl=True)

            # Only draw if card has 2 text lines
            if self.h > 3:
                # Bottom left value
                self.draw_str(self.h - 2, 1, self.value)

        elif self.value == 'back':
            self.draw_box()
            self.draw_fill(1, 1, self.h - 2, self.w - 2, '/')

        elif self.value == 'slot':
            self.draw_box(dashed=True)


class DiscardStack(Drawable):
    def __init__(self, y, x, values=None):
        h = min(len(values), 6)
        super(DiscardStack, self).__init__(y, x, h, 3)
        self.set_color(colors.PLAYFIELD_TEXT)
        self.values = list(reversed(values)) or []
        self.update()

    def update(self):
        self.erase()
        if self.values:
            for y, value in enumerate(self.values[:5]):
                # Shadow of top card
                if value in (1, 2, 3, 4):
                    color = colors.DISCARD_1234
                elif value in (5, 6, 7, 8):
                    color = colors.DISCARD_5678
                elif value in (9, 10, 11, 12):
                    color = colors.DISCARD_9012
                elif value == 'SB':
                    color = colors.DISCARD_SB
                self.draw_ch(y, 0, curses.ACS_CKBOARD, color=color)

                # Value of card
                if value in (1, 2, 3, 4):
                    color = colors.CARD_1234
                elif value in (5, 6, 7, 8):
                    color = colors.CARD_5678
                elif value in (9, 10, 11, 12):
                    color = colors.CARD_9012
                elif value == 'SB':
                    color = colors.CARD_SB
                self.draw_str(y, 2, '%2s' % value, color=color, rtl=True)

        if len(self.values) > 5:
            more = len(self.values) - 5
            self.draw_str(5, 2, "+%d" % more, rtl=True)
