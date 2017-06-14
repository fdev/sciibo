from sciibo.core.scene import Scene
from sciibo.graphics import colors
from sciibo.graphics.alert import Alerts
from sciibo.graphics.forms import Form, Button, Input, Selection
from sciibo.graphics.logo import Logo


class Single(Scene):
    def enter(self):
        self.set_color(colors.MENU)
        self.erase()

        self.add_child(Logo(3, 18))
        self.draw_rectangle(10, 23, 11, 34)
        self.draw_str(10, 25, ' Single player ', colors.MENU_TEXT)
        self.draw_str(12, 25, 'Your name:', colors.MENU_TEXT)
        self.draw_str(14, 25, 'Cards per player:', colors.MENU_TEXT)
        self.draw_str(16, 25, 'Number of bots:', colors.MENU_TEXT)

        # Form
        self.name_input = Input(12, 36, 19, 16, self.state.name)
        self.add_child(self.name_input)

        self.cards_input = Selection(14, 43, [10, 15, 20], selected=1)
        self.add_child(self.cards_input)

        self.bots_input = Selection(16, 43, [1, 2, 3, 4], selected=0)
        self.add_child(self.bots_input)

        self.back_button = Button(19, 25, 'Back', on_press=self.on_back_press)
        self.add_child(self.back_button)

        self.start_button = Button(19, 46, 'Start', on_press=self.on_start_press)
        self.add_child(self.start_button)

        self.form = Form()
        self.form.add_row(self.name_input)
        self.form.add_row(self.cards_input)
        self.form.add_row(self.bots_input)
        self.form.add_row(self.back_button, self.start_button, default=self.start_button)
        self.form.set_active(self.name_input)

        # Alerts
        self.alerts = Alerts(self)

    def leave(self):
        self.state.set_name(self.name_input.value)

    """
    Network events
    """
    def on_game_start(self):
        self.state.set_scene("Game")

    """
    Form handling
    """
    def on_back_press(self):
        self.state.set_scene("Main")

    def on_start_press(self):
        # Validate entered name
        name = self.name_input.value.strip()
        if name == '':
            self.alerts.error('Please enter your name.', on_dismiss=self.alert_dismiss)
            self.form.disable()
            return

        # Save entered name before starting game
        self.state.set_name(name)

        # Create a single player game
        self.state.local_game(self.bots_input.value, self.cards_input.value)
        self.state.client.on('start', self.on_game_start)
        self.state.server.start_game()

    def alert_dismiss(self, action):
        self.form.enable()

    """
    Input handling
    """
    def on_tick(self):
        if self.state.client:
            self.state.client.process_message()

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
