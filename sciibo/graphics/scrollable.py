import curses

from sciibo.core.drawable import Drawable


class Scrollable(Drawable):
    def __init__(self, y, x, h, drawable, color=None, perpage=5):
        super(Scrollable, self).__init__(y, x, h, drawable.w + 1)
        self.perpage = perpage
        self.scroll = 0
        self.maxscroll = max(0, drawable.h - h)

        self.clipped = True
        self.drawable = drawable
        self.add_child(self.drawable)

        self.set_color(color)
        self.update()

    def update(self):
        self.erase()
        self.drawable.y = -self.scroll
        if self.maxscroll:
            self.draw_scrollbar(self.h + self.maxscroll, self.scroll)

    def on_key(self, ch):
        if ch not in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_PPAGE, curses.KEY_NPAGE):
            return

        if ch == curses.KEY_UP:
            self.scroll = max(self.scroll - 1, 0)

        if ch == curses.KEY_DOWN:
            self.scroll = min(self.scroll + 1, self.maxscroll)

        if ch == curses.KEY_PPAGE:
            self.scroll = max(self.scroll - self.perpage, 0)

        if ch == curses.KEY_NPAGE:
            self.scroll = min(self.scroll + self.perpage, self.maxscroll)

        self.update()
