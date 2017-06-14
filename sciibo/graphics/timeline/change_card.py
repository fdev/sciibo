class ChangeCard(object):
    def __init__(self, card, value):
        self.card = card
        self.value = value
        self.frame = 0

    def next_frame(self):
        # Runtime initialization
        if self.frame == 0:
            self.new_card = self.card.__class__(0, 0, self.value, self.card.size)

        if self.frame == self.card.w + self.card.h - 1:
            self.card.value = self.new_card.value
            return False

        for y in range(self.card.h):
            x = self.frame - y
            if self.card.w > x >= 0:
                self.new_card.pad.overwrite(self.card.pad, y, x, y, x, y, x)

        self.frame += 1
        return True
