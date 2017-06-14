import curses
from sciibo.core.animation import Animation
from sciibo.graphics import colors


class Logo(Animation):
    def __init__(self, y, x):
        super(Logo, self).__init__(y, x, 5, 44)
        self.set_color(colors.LOGO)
        self.erase()
        self.update()

    def update(self):
        self.erase()

        # Width of logo (44) + width of 'slider' (7) + end delay (16)
        self.frame = self.frame % 67

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
                    if self.frame in (x + y, x + y + 2):
                        self.draw_ch(y, x, curses.ACS_CKBOARD, colors.LOGO_TEXT_SLIDER)
                    elif self.frame == x + y + 1:
                        self.draw_ch(y, x, ' ', colors.LOGO_TEXT_SLIDER)
                    else:
                        self.draw_ch(y, x, ' ', colors.LOGO_TEXT)

        return True
