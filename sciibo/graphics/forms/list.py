import curses
import curses.ascii

from sciibo.graphics import colors

from .field import Field


class List(Field):
    def __init__(self, y, x, h, w, items, empty_text='', selected=0, on_select=None):
        super(List, self).__init__(y, x, h, w)
        self.items = items
        self.empty_text = empty_text
        self.selected = min(selected, len(self.items) - 1)
        self.on_select = on_select
        self.offset = max(0, self.selected - self.h + 1)
        self.update()

    def update(self):
        if self.active:
            self.set_color(colors.FORM_LIST_ACTIVE)
        else:
            self.set_color(colors.FORM_LIST)
        self.erase()

        # Display empty text
        if not self.items:
            self.draw_str(0, 0, self.empty_text)
            return

        # Boolean if scrollbar should be displayed
        scrollbar = len(self.items) > self.h

        for index, (key, title, action) in enumerate(self.items):
            y = index - self.offset

            color = None
            if index == self.selected:
                color = colors.FORM_LIST_ACTIVE_SELECTED if self.active else colors.FORM_LIST_SELECTED

            self.draw_fill(y, 0, 1, self.w, color=color)
            self.draw_str(y, 0, title, color=color)

            if action:
                x = self.w - 2 if scrollbar else self.w - 1
                self.draw_str(y, x, ' %s' % action, color=color, rtl=True)

        if scrollbar:
            self.draw_scrollbar(len(self.items), self.offset)

    def select(self, key):
        if self.on_select:
            self.on_select(key)

    def set_items(self, items):
        self.items = items
        self.selected = min(self.selected, len(self.items) - 1)
        self.update()

    def on_key(self, ch):
        if not self.items:
            return False

        if ch == curses.KEY_UP:
            if self.selected == 0:
                return False

            self.selected -= 1

            # Selection is outside view, scroll up
            if self.selected - self.offset < 0:
                self.offset = self.selected

        elif ch == curses.KEY_DOWN:
            if self.selected == len(self.items) - 1:
                return False

            self.selected += 1

            # Selection is outside view, scroll down
            if self.selected - self.offset >= self.h:
                self.offset = self.selected - self.h + 1

        elif ch == curses.KEY_HOME:
            self.selected = 0
            self.offset = 0

        elif ch == curses.KEY_END:
            self.selected = len(self.items) - 1
            self.offset = max(0, self.selected - self.h + 1)

        elif ch == curses.KEY_ENTER:
            key, title, action = self.items[self.selected]
            self.select(key)
            return True  # no update necessary

        else:
            return False

        self.update()
        return True

    def on_mouse(self, chain, y, x):
        if self not in chain:
            return

        index = self.offset + y
        if index < len(self.items):
            if index == self.selected:
                key, title, action = self.items[index]
                self.select(key)
            else:
                self.selected = index
                self.update()
