from __future__ import division


class Move(object):
    def __init__(self, drawable, ty, tx, duration=0):
        self.drawable = drawable
        self.ty = ty
        self.tx = tx
        self.duration = duration
        self.frame = 0

    def next_frame(self):
        # Runtime initialization
        if self.frame == 0:
            self.sy = self.drawable.y
            self.sx = self.drawable.x

            self.dy = self.ty - self.sy
            self.dx = self.tx - self.sx

        if self.frame == self.duration:
            self.drawable.y = self.ty
            self.drawable.x = self.tx
            return False

        ratio = self.frame / self.duration

        self.drawable.y = self.sy + int(self.dy * ratio)
        self.drawable.x = self.sx + int(self.dx * ratio)

        self.frame += 1

        return True
