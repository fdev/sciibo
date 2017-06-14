from __future__ import division


class ResizeCard(object):
    def __init__(self, card, ty, tx, tsize, duration=0):
        self.card = card
        self.ty = ty
        self.tx = tx
        self.tsize = tsize
        self.duration = duration
        self.frame = 0

    def next_frame(self):
        # Runtime initialization
        if self.frame == 0:
            self.sy = self.card.y
            self.sx = self.card.x
            self.ssize = self.card.size

            self.dy = self.ty - self.sy
            self.dx = self.tx - self.sx

            # Calculate on which frames resize should occur
            sizes = ['tiny', 'small', 'medium', 'large']
            s_index = sizes.index(self.ssize)
            t_index = sizes.index(self.tsize)
            if s_index < t_index:
                self.resize_sizes = sizes[s_index + 1 : t_index + 1]
            else:
                self.resize_sizes = sizes[t_index:s_index][::-1]

            # Longen duration if necessary for resize
            self.duration = max(len(self.resize_sizes), self.duration)

            frames = abs(t_index - s_index)
            self.resize_frames = []
            for n in range(1, frames + 1):
                self.resize_frames.append(int(self.duration * n / (frames + 1)))

        if self.frame in self.resize_frames:
            size = self.resize_sizes.pop(0)
            self.card.resize(size)

        if self.frame == self.duration:
            self.card.y = self.ty
            self.card.x = self.tx
            return False

        ratio = self.frame / self.duration

        self.card.y = self.sy + int(self.dy * ratio)
        self.card.x = self.sx + int(self.dx * ratio)

        self.frame += 1

        return True
