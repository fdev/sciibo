class Delay(object):
    def __init__(self, duration):
        self.duration = duration
        self.frame = 0

    def next_frame(self):
        if self.frame == self.duration:
            return False

        self.frame += 1
        return True
