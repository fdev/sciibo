import curses


def create_color(foreground, background, attrs=0):
    """Create a new color pair."""
    try:
        create_color.index += 1
    except:
        create_color.index = 1
    curses.init_pair(create_color.index, foreground, background)
    return curses.color_pair(create_color.index) | attrs


# Character attributes
BLINK = curses.A_BLINK
BOLD = curses.A_BOLD
DIM = curses.A_DIM
NORMAL = curses.A_NORMAL
REVERSE = curses.A_REVERSE
STANDOUT = curses.A_STANDOUT
UNDERLINE = curses.A_UNDERLINE

# Default colors
BLACK = curses.COLOR_BLACK
BLUE = curses.COLOR_BLUE
CYAN = curses.COLOR_CYAN
GREEN = curses.COLOR_GREEN
MAGENTA = curses.COLOR_MAGENTA
RED = curses.COLOR_RED
WHITE = curses.COLOR_WHITE
YELLOW = curses.COLOR_YELLOW
