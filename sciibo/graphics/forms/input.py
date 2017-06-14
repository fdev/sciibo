import curses
import curses.ascii

from sciibo.graphics import colors

from .field import Field


class Input(Field):
    def __init__(self, y, x, w, max_length, value=''):
        super(Input, self).__init__(y, x, 1, max(max_length, w))
        self.max_length = max_length
        self.value = value[:max_length]
        self.pos = len(self.value)
        self.update()

    # overrides Field.set_active
    def set_active(self, active):
        self.active = active
        if active:
            self.pos = len(self.value)
        self.update()

    def update(self):
        if self.active:
            self.set_color(colors.FORM_INPUT_ACTIVE)
        else:
            self.set_color(colors.FORM_INPUT)
        self.erase()

        self.draw_str(0, 0, self.value)
        if self.active:
            self.draw_ch(0, self.pos, (self.value + ' ')[self.pos], colors.FORM_INPUT_CURSOR)

    def on_key(self, ch):
        x = self.pos

        # ascii 32-126 (inclusive)
        if curses.ascii.isprint(ch):
            if len(self.value) < self.max_length:
                self.value = self.value[:x] + chr(ch) + self.value[x:]
                self.pos += 1

        elif ch == curses.KEY_LEFT:
            if x > 0:
                self.pos -= 1

        elif ch == curses.KEY_RIGHT:
            if x < len(self.value):
                self.pos += 1

        elif ch == curses.KEY_BACKSPACE:
            if x > 0:
                self.value = self.value[:x - 1] + self.value[x:]
                self.pos -= 1

        elif ch == curses.KEY_DC:
            if x < len(self.value):
                self.value = self.value[:x] + self.value[x + 1:]

        elif ch == curses.KEY_HOME:
            self.pos = 0

        elif ch == curses.KEY_END:
            self.pos = len(self.value)

        else:
            return False

        self.update()
        return True

    def on_mouse(self, chain, y, x):
        if self not in chain:
            return

        self.pos = min(x, len(self.value))
        self.update()
