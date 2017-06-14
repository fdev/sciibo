from .drawable import Drawable


class Scene(Drawable):
    def __init__(self, state):
        super(Scene, self).__init__(0, 0, 24, 80)
        self.state = state
        self.clipped = True

    def enter(self):
        raise NotImplementedError

    def leave(self):
        pass

    def on_tick(self):
        pass

    def on_key(self, ch):
        pass

    def on_mouse(self, chain, y, x):
        pass
