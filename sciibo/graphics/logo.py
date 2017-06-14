import curses

from sciibo.core.drawable import Drawable

from ..graphics import colors


class Logo(Drawable):
    def __init__(self, y, x):
        super(Logo, self).__init__(y, x, 5, 44)
        self.set_color(colors.LOGO)
        self.erase()
        self.update()

    def update(self):
        self.erase()

        lines = [
            ' :88888 :88888:8888:8888    :88888   :88888 ',
            ':88    :88     :88  :88     :88 :88 :88  :88',
            ':888888:88     :88  :88 :88 :8888888:88  :88',
            '    :88:88     :88  :88     :88  :88:88  :88',
            ':88888  :88888:8888:8888    :888888  :88888 ',
        ]

        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                if ch == ' ':
                    continue
                elif ch == ':':
                    self.draw_ch(y, x, curses.ACS_CKBOARD, colors.LOGO_SHADOW)
                else:
                    self.draw_ch(y, x, ' ', colors.LOGO_TEXT)
