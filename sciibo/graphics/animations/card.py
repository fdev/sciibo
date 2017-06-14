from __future__ import division

from sciibo.core.animation import Animation


class RevealCard(Animation):
    def __init__(self, y, x, source_card, target_card, on_complete=None):
        super(RevealCard, self).__init__(y, x, source_card.h, source_card.w, on_complete=on_complete)
        self.source_card = source_card
        self.target_card = target_card
        self.update()

    def update(self):
        if self.frame == 12:
            return False

        self.erase()
        self.source_card.pad.overwrite(self.pad, 0, 0, 0, 0, self.h - 1, self.w - 1)

        for y in range(self.h):
            w = min(max(0, self.frame - y), self.w)
            if w > 0:
                self.target_card.pad.overwrite(self.pad, y, 0, y, 0, y, w - 1)

        return True
