import curses

from sciibo.core.animation import Animation


class Spinner(Animation):
    def __init__(self, y, x, color):
        super(Spinner, self).__init__(y, x, 1, 1)
        self.set_color(color)

    def update(self):
        self.erase()

        self.frame = self.frame % 4
        if self.frame < 1:
            self.draw_ch(0, 0, curses.ACS_HLINE)
        elif self.frame < 2:
            self.draw_ch(0, 0, '\\')
        elif self.frame < 3:
            self.draw_ch(0, 0, '|')
        else:
            self.draw_ch(0, 0, '/')

        return True
