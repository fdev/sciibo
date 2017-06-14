import curses
import curses.ascii

from sciibo.graphics import colors

from .field import Field


class Selection(Field):
    def __init__(self, y, x, items, selected=0, on_select=None):
        super(Selection, self).__init__(y, x, 1, self.item_width(items))
        self.items = items
        self.selected = selected
        self.on_select = on_select
        self.value = items[selected]
        self.update()

    def item_width(self, items):
        return sum(map(len, list(map(str, items)))) + len(items) * 2

    def update(self):
        if self.active:
            self.set_color(colors.FORM_SELECTION_ACTIVE)
        else:
            self.set_color(colors.FORM_SELECTION)
        self.erase()

        self.draw_str(0, 1, "  ".join(map(str, self.items)))

        x = self.item_width(self.items[:self.selected])
        color = colors.FORM_SELECTION_ACTIVE_SELECTED if self.active else colors.FORM_SELECTION_SELECTED
        self.draw_str(0, x, ' %s ' % self.items[self.selected], color)

    def on_key(self, ch):
        if ch == curses.KEY_LEFT:
            if self.selected > 0:
                self.selected -= 1

        elif ch == curses.KEY_RIGHT:
            if self.selected + 1 < len(self.items):
                self.selected += 1

        else:
            return False

        self.value = self.items[self.selected]
        self.update()
        return True

    def on_mouse(self, chain, y, x):
        if self not in chain:
            return

        width = 0
        for index, item in enumerate(map(str, self.items)):
            width += len(item) + 2
            if x < width:
                self.selected = index
                self.value = self.items[self.selected]
                self.update()
                return
