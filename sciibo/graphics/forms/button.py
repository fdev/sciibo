import curses

from sciibo.graphics import colors

from .field import Field


class Button(Field):
    def __init__(self, y, x, text, on_press=None):
        super(Button, self).__init__(y, x, 1, len(text) + 4)
        self.text = text
        self.on_press = on_press
        self.update()

    def update(self):
        if self.active:
            self.draw_str(0, 0, '[ %s ]' % self.text, colors.FORM_BUTTON_ACTIVE)
        else:
            self.draw_str(0, 0, '[ %s ]' % self.text, colors.FORM_BUTTON)

    def press(self):
        if self.on_press:
            self.on_press()

    def on_key(self, ch):
        if ch == curses.KEY_ENTER:
            self.press()
            return True
        return False

    def on_mouse(self, chain, y, x):
        if self not in chain:
            return

        self.press()
