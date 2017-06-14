import random
import curses
import collections

from sciibo.core.scene import Scene
from sciibo.graphics import colors


class About(Scene):
    def enter(self):
        self.set_color(colors.GLYPH_1)
        self.erase()
        self.chars = [' '] * 1920
        self.heat = [0] * 1920
        self.streams = collections.deque(maxlen=24)

    def on_tick(self):
        # Add stream to random position
        self.streams.appendleft(random.randint(0, 79))

        # Cool off the heat map
        for y in range(24):
            for x in range(80):
                index = y * 80 + x
                if self.heat[index] > 0:
                    self.heat[index] -= 1

        # Randomize and heaten heads of streams
        for x, y in zip(self.streams, list(range(24))):
            index = y * 80 + x
            self.heat[index] = 50
            self.chars[index] = chr(random.randint(33, 126))

        # Randomly change some characters (about 2%)
        xs = [random.randint(0, 79) for n in range(40)]
        ys = [random.randint(0, 23) for n in range(40)]
        for y, x in zip(ys, xs):
            index = y * 80 + x
            self.chars[index] = chr(random.randint(33, 126))

        # Update screen
        self.erase()

        for y in range(24):
            for x in range(80):
                index = y * 80 + x
                heat = self.heat[index]
                if not heat:
                    continue

                if heat > 48:
                    color = colors.GLYPH_1
                elif heat > 30:
                    color = colors.GLYPH_2
                else:
                    color = colors.GLYPH_3

                self.draw_ch(y, x, self.chars[index], color=color)

    """
    Input handling
    """
    def on_key(self, ch):
        if ch == curses.KEY_ENTER:
            self.state.set_scene("Main")
