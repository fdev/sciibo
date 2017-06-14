from .drawable import Drawable


class Animation(Drawable):
    # Pause all animations
    paused = False

    def __init__(self, y, x, h, w, on_complete=None):
        super(Animation, self).__init__(y, x, h, w)
        self.on_complete = on_complete
        self.frame = 0

    def update(self):
        raise NotImplementedError

    def next_frame(self):
        if Animation.paused:
            return True

        if self.update():
            self.frame += 1
            return True

        if self.on_complete:
            self.on_complete()

        return False

    @staticmethod
    def pause():
        Animation.paused = True

    @staticmethod
    def resume():
        Animation.paused = False
