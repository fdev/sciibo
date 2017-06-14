import textwrap

try:
    # Python 3
    from queue import Queue
except ImportError:
    # Python 2
    from Queue import Queue


def valid_string(s):
    """
    Returns if given string contains only ascii printable characters
    """
    return not any(ord(ch) < 32 or ord(ch) > 126 for ch in s)


def wrap_text(text, width):
    """
    Wraps text to a maximum width, keeping newlines intact.
    """
    lines = []
    for line in text.split('\n'):
        if line:
            lines += textwrap.wrap(line, width)
        else:
            # textwrap ignores empty lines, we want to keep them
            lines += ['']
    return lines


def fitson(a, b):
    """
    Returns if card b can be placed on card a.
    """
    return b == 'SB' or 1 + a % 12 == b


def nextcard(a):
    """
    Returns the card that comes after a.
    """
    return 1 + a % 12
