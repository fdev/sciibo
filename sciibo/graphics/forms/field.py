from sciibo.core.drawable import Drawable


class Field(Drawable):
    def __init__(self, y, x, h, w):
        super(Field, self).__init__(y, x, h, w)
        self.active = False

    def set_active(self, active):
        self.active = active
        self.update()

    def on_key(self, ch):
        # Must return True if event was handled
        pass

    def on_mouse(self, chain, y, x):
        # Must return True if event was handled
        pass
