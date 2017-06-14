from sciibo.core.scene import Scene
from sciibo.graphics import colors
from sciibo.graphics.logo import Logo
from sciibo.graphics.alert import Alerts
from sciibo.graphics.forms import Form, Button, Input, Selection


class Host(Scene):
    def enter(self):
        self.set_color(colors.MENU)
        self.erase()

        self.add_child(Logo(3, 18))
        self.draw_rectangle(10, 23, 9, 34)
        self.draw_str(10, 25, ' Host game ', colors.MENU_TEXT)
        self.draw_str(12, 25, 'Your name:', colors.MENU_TEXT)
        self.draw_str(14, 25, 'Cards per player:', colors.MENU_TEXT)

        # Form
        self.name_input = Input(12, 36, 19, 16, self.state.name)
        self.add_child(self.name_input)

        self.cards_input = Selection(14, 43, [10, 15, 20])
        self.add_child(self.cards_input)

        self.back_button = Button(17, 25, 'Back', on_press=self.on_back_press)
        self.add_child(self.back_button)

        self.next_button = Button(17, 47, 'Next', on_press=self.on_next_press)
        self.add_child(self.next_button)

        self.form = Form()
        self.form.add_row(self.name_input)
        self.form.add_row(self.cards_input)
        self.form.add_row(self.back_button, self.next_button, default=self.next_button)
        self.form.set_active(self.name_input)

        # Alerts
        self.alerts = Alerts(self)

    def leave(self):
        # Remember fill in name
        self.state.set_name(self.name_input.value)

    """
    Form handling
    """
    def on_back_press(self):
        self.state.set_scene("Main")

    def on_next_press(self):
        # Validate entered name
        name = self.name_input.value.strip()
        if name == '':
            self.alerts.error('Please enter your name.', on_dismiss=self.alert_dismiss)
            self.form.disable()
            return

        # Save entered name before starting game
        self.state.set_name(name)

        # Try starting a server
        if self.state.host_game(self.cards_input.value):
            self.state.set_scene("HostPlayers")
        else:
            self.alerts.error('Could not start server. There might be another server already running.', on_dismiss=self.alert_dismiss)
            self.form.disable()

    def alert_dismiss(self, action):
        self.form.enable()

    """
    Input handling
    """
    def on_key(self, ch):
        if self.alerts.open:
            self.alerts.on_key(ch)
        else:
            self.form.on_key(ch)

    def on_mouse(self, chain, y, x):
        if self.alerts.open:
            self.alerts.on_mouse(chain, y, x)
        else:
            self.form.on_mouse(chain, y, x)
