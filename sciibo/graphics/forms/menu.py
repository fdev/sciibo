import curses
import curses.ascii

from sciibo.graphics import colors

from .field import Field


class Menu(Field):
    def __init__(self, y, x, w, items, selected=0, on_select=None):
        self.h = len(items)
        super(Menu, self).__init__(y, x, self.h, w)
        self.set_color(colors.MENU_LIST)
        self.items = items
        self.selectable = [i for i, item in enumerate(items) if item]
        self.selected = min(selected, len(self.selectable))
        self.on_select = on_select
        self.update()

    def update(self):
        self.erase()

        selected = self.selectable[self.selected]
        for index, item in enumerate(self.items):
            if not item:
                continue

            key, title = item

            if index == selected:
                self.draw_fill(index, 0, 1, self.w, color=colors.MENU_LIST_SELECTED)
                self.draw_str(index, 0, title, color=colors.MENU_LIST_SELECTED)
            else:
                self.draw_str(index, 0, title)

    def select(self, key):
        if self.on_select:
            self.on_select(key)

    def on_key(self, ch):
        if not self.items:
            return False

        if ch == curses.KEY_UP:
            self.selected = max(self.selected - 1, 0)

        elif ch == curses.KEY_DOWN:
            self.selected = min(len(self.selectable) - 1, self.selected + 1)

        elif ch == curses.KEY_HOME:
            self.selected = 0

        elif ch == curses.KEY_END:
            self.selected = len(self.selectable) - 1

        elif ch == curses.KEY_ENTER:
            key, title = self.items[self.selectable[self.selected]]
            self.select(key)
            return True  # no update necessary

        else:
            return False

        self.update()
        return True

    def on_mouse(self, chain, y, x):
        if self not in chain:
            return

        item = self.items[y]
        if item:
            if y == self.selectable[self.selected]:
                key, title = item
                self.select(key)
            else:
                self.selected = self.selectable.index(y)
                self.update()
