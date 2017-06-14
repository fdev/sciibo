from sciibo.core.animation import Animation


class Dots(Animation):
    def __init__(self, y, x, color):
        super(Dots, self).__init__(y, x, 1, 2)
        self.set_color(color)

    def update(self):
        self.erase()

        frame = self.frame % 9
        if frame < 3:
            self.draw_str(0, 0, '  ')
        elif frame < 6:
            self.draw_str(0, 0, '. ')
        else:
            self.draw_str(0, 0, '..')

        return True
