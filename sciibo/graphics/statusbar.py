from sciibo.core.drawable import Drawable

from ..graphics import colors


class Statusbar(Drawable):
    def __init__(self, y, x):
        super(Statusbar, self).__init__(y, x, 1, 80)
        self.active = False
        self.text = ''
        self.update()

    def update(self):
        self.set_color(colors.STATUSBAR_ACTIVE if self.active else colors.STATUSBAR)
        self.erase()
        self.draw_str(0, 1, self.text)
        self.draw_str(0, 78, 'F1:Help  F10:Leave', rtl=True)
