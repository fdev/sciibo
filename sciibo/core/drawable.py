from __future__ import division

import curses

from .helpers import wrap_text


class Drawable(object):
    def __init__(self, y, x, h, w):
        self.y = y
        self.x = x
        self.h = h
        self.w = w

        # Prevent rendering
        self.hidden = False

        # Clip children
        self.clipped = False

        # One row higher so last character is writable
        self.pad = curses.newpad(h + 1, w + 1)

        self.children = []

    def resize(self, h, w):
        """Resize the drawable and create a new pad."""
        self.h = h
        self.w = w
        self.pad = curses.newpad(h + 1, w + 1)

    def update(self):
        raise NotImplementedError

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)

    def remove_children(self):
        self.children = []

    def child_top(self, child):
        if child in self.children:
            self.children.remove(child)
            self.children.append(child)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def set_color(self, color):
        """Change default color of drawable."""
        self.pad.bkgdset(' ', color)

    def erase(self):
        """Erase all characters."""
        self.pad.erase()

    def draw_ch(self, y, x, ch, color=None):
        """Single character."""
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return
        self.pad.addch(y, x, ch, color if color else 0)

    def draw_fill(self, y, x, h, w, ch=' ', color=None):
        """Filled rectangle."""
        for dy in range(h):
            for dx in range(w):
                self.draw_ch(y + dy, x + dx, ch, color)

    def draw_str(self, y, x, text, color=None, max_length=None, rtl=False):
        """Single line string."""
        # Cast to string
        text = str(text)

        # Enforce max length
        text = text if max_length is None else text[:max_length]

        if rtl:
            x = x - len(text) + 1

        for dx, ch in enumerate(text):
            self.draw_ch(y, x + dx, ch, color)

    def draw_text(self, y, x, w, text, color=None):
        """Multiple lines, wrapped if necessary."""
        for dy, line in enumerate(wrap_text(text, w)):
            self.draw_str(y + dy, x, line, color=color)

    def draw_hline(self, y, x, w, ch=None, color=None):
        """Horizontal line."""
        ch = ch or curses.ACS_HLINE
        for dx in range(w):
            self.draw_ch(y, x + dx, ch, color)

    def draw_vline(self, y, x, h, ch=None, color=None):
        """Vertical line."""
        ch = ch or curses.ACS_VLINE
        for dy in range(h):
            self.draw_ch(y + dy, x, ch, color)

    def draw_rectangle(self, y, x, h, w, filled=True, dashed=False, color=None):
        """Rectangle with corners."""
        if dashed:
            hch = '-'
            vch = '|'
        else:
            hch = curses.ACS_HLINE
            vch = curses.ACS_VLINE

        # Borders
        self.draw_hline(y,         x + 1,     w - 2, hch, color)  # top
        self.draw_vline(y + 1,     x + w - 1, h - 2, vch, color)  # right
        self.draw_hline(y + h - 1, x + 1,     w - 2, hch, color)  # bottom
        self.draw_vline(y + 1,     x,         h - 2, vch, color)  # left

        # Corners
        self.draw_ch(y,         x,         curses.ACS_ULCORNER, color)
        self.draw_ch(y,         x + w - 1, curses.ACS_URCORNER, color)
        self.draw_ch(y + h - 1, x + w - 1, curses.ACS_LRCORNER, color)
        self.draw_ch(y + h - 1, x,         curses.ACS_LLCORNER, color)

        # Fill
        if filled:
            self.draw_fill(y + 1, x + 1, h - 2, w - 2, color=color)

    def draw_scrollbar(self, lines, offset, color=None):
        """Draws a vertical scrollbar with track and handle."""
        if lines <= self.h:
            return

        if self.h < 2:
            return

        offset_max = lines - self.h

        # Handle height is always > 0 and < self.h
        handle_h = max(1, self.h * self.h // lines)

        # Remainder is track height
        track_h = self.h - handle_h

        if track_h > 1:
            # Handle will only hit top of track if offset is zero, and
            # only hit bottom of track if actual bottom is reached.
            handle_y = 1 + offset * (track_h - 1) // offset_max if offset else 0
        else:
            # Handle will only hit bottom of track if actual bottom
            # is reached, but might linger on top of track.
            handle_y = offset * track_h // offset_max

        self.draw_vline(0, self.w - 1, self.h, ' ')
        self.draw_vline(handle_y, self.w - 1, handle_h, curses.ACS_CKBOARD)

    def draw_box(self, filled=True, dashed=False, color=None):
        """Draw a box on the edges of the drawable."""
        self.draw_rectangle(0, 0, self.h, self.w, filled=filled, dashed=dashed, color=color)

    def draw_child(self, drawable, y=0, x=0):
        """Draw a child drawable directly onto the canvas of this drawable."""
        drawable.pad.overwrite(self.pad, drawable.y + y, drawable.x + y, 0, 0, drawable.h - 1, drawable.w - 1)
        for child in drawable.children:
            self.draw_child(child, drawable.y + y, drawable.x + x)
