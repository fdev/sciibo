from __future__ import division

import textwrap

from sciibo.core.drawable import Drawable
from .forms import Button, Form
from ..graphics import colors


class Alert(Drawable):
    def __init__(self, text='', type='info', buttons=None, default=None, on_dismiss=None):
        self.lines = sum([textwrap.wrap(line, 38) for line in str(text).split('\n')], [])
        self.h = len(self.lines) + (4 if buttons else 2)
        self.y = (24 - self.h) // 2
        super(Alert, self).__init__(self.y, 20, self.h, 40)

        self.on_dismiss = on_dismiss
        self.type = type
        self.buttons = buttons or []
        self.default = buttons.index(default) if default else -1

        self.update()

    def on_press(self, label):
        def call():
            if self.on_dismiss:
                self.on_dismiss(label)
        return call

    def form_buttons(self):
        x = 39
        buttons = []
        for label in reversed(self.buttons):
            x -= len(label) + 4 + 1
            buttons.append(Button(self.h - 2, x, label, on_press=self.on_press(label)))
        buttons.reverse()
        return buttons

    def update(self):
        if self.type == 'error':
            self.set_color(colors.ALERT_ERROR)
        else:
            self.set_color(colors.ALERT_INFO)
        self.erase()
        self.draw_box()

        # Text, wrapped over multiple lines
        for y, line in enumerate(self.lines):
            self.draw_str(y + 1, 1, line)

        # Form
        self.form = Form()
        if self.buttons:
            buttons = self.form_buttons()
            for button in buttons:
                self.add_child(button)
            self.form.add_row(*buttons)
            self.form.set_active(buttons[self.default])

    def on_key(self, ch):
        self.form.on_key(ch)

    def on_mouse(self, chain, y, x):
        self.form.on_mouse(chain, y, x)


class Alerts(object):
    def __init__(self, parent):
        self.parent = parent
        self.open = None

    def alert(self, text, type='info', buttons=None, default=None, on_dismiss=None):
        """Create an alert and replace any existing alert."""
        self.close()

        def dismiss(button):
            if on_dismiss:
                on_dismiss(button)
            self.close()

        self.open = Alert(text, type=type, buttons=buttons, default=default, on_dismiss=dismiss)
        self.parent.add_child(self.open)

    def close(self):
        if self.open:
            self.parent.remove_child(self.open)
        self.open = None

    """
    Helper methods for common alert types
    """
    def error(self, text, on_dismiss=None):
        self.alert(text, type='error', buttons=['Dismiss'], on_dismiss=on_dismiss)

    def confirm(self, text, action, on_dismiss=None):
        self.alert(text, buttons=['Cancel', action], default='Cancel', on_dismiss=on_dismiss)

    """
    Input handling
    """
    def on_key(self, ch):
        if self.open:
            self.open.on_key(ch)

    def on_mouse(self, chain, y, x):
        if self.open:
            self.open.on_mouse(chain, y, x)
