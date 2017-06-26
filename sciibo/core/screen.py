from __future__ import division

import os
import curses
import curses.ascii

from .animation import Animation
from ..core import colors


class Screen:
    def __init__(self, stdscr):
        self.win = stdscr
        self.set_color(colors.create_color(colors.WHITE, colors.BLACK))

    def set_color(self, color):
        self.win.bkgdset(' ', color)

    def animate(self, scene):
        def handle(drawable):
            for child in drawable.children:
                if child.hidden:
                    continue

                if isinstance(child, Animation):
                    if not child.next_frame():
                        # Child might have been removed by Animation's
                        # on_complete callback triggered by next_frame
                        drawable.remove_child(child)
                        continue

                handle(child)

        handle(scene)

    def clip_size(self):
        screen_h, screen_w = self.size()

        clip_h = min(screen_h, 24)
        clip_w = min(screen_w, 80)

        screen_y = (screen_h - clip_h) // 2
        screen_x = (screen_w - clip_w) // 2

        return screen_y, screen_x, clip_h, clip_w

    def draw(self, scene):
        self.win.erase()
        self.win.noutrefresh()

        if not scene:
            return

        screen_y, screen_x, clip_h, clip_w = self.clip_size()

        def refresh(drawable, prow, pcol, cminrow, cmincol, cmaxrow, cmaxcol):
            pminrow = prow + drawable.y
            pmincol = pcol + drawable.x

            pmaxrow = pminrow + drawable.h - 1
            pmaxcol = pmincol + drawable.w - 1

            offset_y = 0
            offset_x = 0

            # Don't draw outside screen clipping bounds
            if pminrow < cminrow:
                offset_y = cminrow - pminrow
                pminrow = cminrow

            if pmincol < cmincol:
                offset_x = cmincol - pmincol
                pmincol = cmincol

            if pmaxrow > cmaxrow:
                pmaxrow = cmaxrow

            if pmaxcol > cmaxcol:
                pmaxcol = cmaxcol

            # No drawable left, nothing to draw
            if pmaxrow < pminrow or pmaxcol < pmincol:
                return

            # Offset to compensate for screen border
            drawable.pad.noutrefresh(
                # upper left point of rectangle in drawable
                offset_y,
                offset_x,
                # upper left point of rectangle in screen
                screen_y + pminrow,
                screen_x + pmincol,
                # lower right point of rectangle in screen
                screen_y + pmaxrow,
                screen_x + pmaxcol,
            )

        def handle(drawable, prow, pcol, cminrow, cmincol, cmaxrow, cmaxcol):
            # Skip hidden drawables
            if drawable.hidden:
                return

            # Update clipping rectangle when drawable is clipped so
            # children don't get drawn outside drawable
            # New rectangle should be contained within old rectangle
            if drawable.clipped:
                cminrow = max(cminrow, prow + drawable.y)
                cmincol = max(cmincol, pcol + drawable.x)

                cmaxrow = min(cmaxrow, prow + drawable.y + drawable.h - 1)
                cmaxcol = min(cmaxcol, pcol + drawable.x + drawable.w - 1)

                # Nothing left to draw
                if cmaxrow < cminrow or cmaxcol < cmincol:
                    return

            refresh(drawable, prow, pcol, cminrow, cmincol, cmaxrow, cmaxcol)

            for child in drawable.children:
                handle(child, prow + drawable.y, pcol + drawable.x, cminrow, cmincol, cmaxrow, cmaxcol)

        # Pass initial parent offset and clipping rectangle (minrow, mincol, maxrow, maxcol)
        handle(scene, 0, 0, 0, 0, clip_h - 1, clip_w - 1)

        curses.doupdate()

    def update(self, scene):
        self.animate(scene)
        self.draw(scene)

    def size(self):
        return self.win.getmaxyx()

    def get_key(self):
        code = self.win.getch()
        if code > 0:
            # Accept newline and carriage return as enter key
            if code == curses.ascii.NL or code == curses.ascii.CR:
                code = curses.KEY_ENTER

            # Accept newline and carriage return as enter key
            if code == curses.ascii.BS:
                code = curses.KEY_BACKSPACE

            return code

    def get_mouse(self, screen):
        try:
            id, x, y, z, bstate = curses.getmouse()
            screen_y, screen_x, clip_h, clip_w = self.clip_size()
            y -= screen_y
            x -= screen_x

            # Ignore clicks outside clipped screen
            if y < clip_h and x < clip_w:
                return self.mouse_target(screen, y, x)
        except curses.error:
            pass

    def mouse_target(self, scene, pos_y, pos_x):
        """
        Returns the chain of drawables that was
        clicked on/through, and the position of
        the mouse inside the top-most drawable.
        """
        def handle(children, y=0, x=0, chain=None):
            if chain is None:
                chain = []
            match = None

            for child in children:
                if child.hidden:
                    continue
                newchain = chain[:]
                if y + child.y <= pos_y < y + child.y + child.h and x + child.x <= pos_x < x + child.x + child.w:
                    newchain += [child]
                    match = (newchain, pos_y - y - child.y, pos_x - x - child.x)
                match = handle(child.children, y + child.y, x + child.x, newchain) or match

            return match

        return handle(scene.children)


def create_screen(fn):
    """
    Initializes curses and passes a Screen to the main loop function `fn`.
    Based on curses.wrapper.
    """
    try:
        # Make escape key more responsive
        os.environ['ESCDELAY'] = '25'

        stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        stdscr.nodelay(1)
        curses.curs_set(0)

        curses.mousemask(curses.BUTTON1_CLICKED)

        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

        screen = Screen(stdscr)
        fn(screen)

    finally:
        # Set everything back to normal
        if 'stdscr' in locals():
            curses.use_default_colors()
            curses.curs_set(1)
            stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
