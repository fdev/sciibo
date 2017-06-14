import curses
import curses.ascii


class Form(object):
    def __init__(self):
        self.rows = []
        self.defaults = []
        self.active = None
        self.disabled = None

    def add_row(self, *fields, **kwargs):
        default = kwargs.get('default')
        if default is not None and default not in fields:
            raise Exception("Form row does not contain default field.")

        self.rows.append(fields)
        self.defaults.append(fields.index(default) if default else 0)

    def fields(self):
        for fields in self.rows:
            for field in fields:
                yield field

    def position(self, field):
        for row, fields in enumerate(self.rows):
            if field in fields:
                return row, fields.index(field)

    def on_key(self, ch):
        if not self.active or self.disabled:
            return

        if not self.active.on_key(ch):
            y, x = self.position(self.active)

            if ch == curses.KEY_UP:
                if y > 0:
                    self.set_active(self.rows[y - 1][self.defaults[y - 1]])

            elif ch in (curses.KEY_DOWN, curses.KEY_ENTER):
                if y < len(self.rows) - 1:
                    self.set_active(self.rows[y + 1][self.defaults[y + 1]])

            elif ch == curses.KEY_LEFT:
                if x > 0:
                    self.set_active(self.rows[y][x - 1])

            elif ch == curses.KEY_RIGHT:
                if x < len(self.rows[y]) - 1:
                    self.set_active(self.rows[y][x + 1])

            elif ch == curses.ascii.TAB:
                # Right
                if x < len(self.rows[y]) - 1:
                    self.set_active(self.rows[y][x + 1])
                # Down, ignoring defaults
                elif y < len(self.rows) - 1:
                    self.set_active(self.rows[y + 1][0])
                else:
                    self.set_active(self.rows[0][0])

            elif ch == curses.KEY_BTAB:
                # Left
                if x > 0:
                    self.set_active(self.rows[y][x - 1])
                # Up
                elif y > 0:
                    col = len(self.rows[y - 1]) - 1
                    self.set_active(self.rows[y - 1][col])
                else:
                    row = len(self.rows) - 1
                    col = len(self.rows[row]) - 1
                    self.set_active(self.rows[row][col])

    def on_mouse(self, chain, y, x):
        # Form is not active
        if not self.active or self.disabled:
            return

        for field in self.fields():
            if field in chain:
                if self.active == field:
                    field.on_mouse(chain, y, x)
                else:
                    self.set_active(field)
                return

    def set_active(self, field):
        if self.active:
            self.active.set_active(False)
        if field:
            field.set_active(True)
        self.active = field

    def disable(self):
        if self.disabled:
            return
        if self.active:
            self.active.set_active(False)
        self.disabled = True

    def enable(self):
        if not self.disabled:
            return
        if self.active:
            self.active.set_active(True)
        self.disabled = False
