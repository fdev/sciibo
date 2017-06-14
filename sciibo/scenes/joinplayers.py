from sciibo.core.scene import Scene
from sciibo.graphics import colors
from sciibo.graphics.alert import Alerts
from sciibo.graphics.animations.dots import Dots
from sciibo.graphics.forms import Form, Button, List
from sciibo.graphics.logo import Logo


class JoinPlayers(Scene):
    def enter(self):
        self.set_color(colors.MENU)
        self.erase()

        self.add_child(Logo(3, 18))
        self.draw_rectangle(10, 23, 11, 34)
        self.draw_str(10, 25, ' Join game - Players ', colors.MENU_TEXT)

        self.draw_str(19, 42, 'Please wait', colors.MENU_TEXT)
        self.add_child(Dots(19, 53, colors.MENU_TEXT))

        # Form
        self.list = List(12, 25, 5, 30, [], selected=-1)
        self.add_child(self.list)
        self.update_players()

        self.leave_button = Button(19, 25, 'Leave', on_press=self.on_leave_press)
        self.add_child(self.leave_button)

        self.form = Form()
        self.form.add_row(self.leave_button)
        self.form.set_active(self.leave_button)

        # Alerts
        self.alerts = Alerts(self)

        # Networking
        self.state.client.on('kick', self.on_game_kick)
        self.state.client.on('disconnect', self.on_game_disconnect)
        self.state.client.on('join', self.on_game_join)
        self.state.client.on('leave', self.on_game_leave)
        self.state.client.on('start', self.on_game_start)

    def leave(self):
        if self.state.client:
            self.state.client.off('kick', self.on_game_kick)
            self.state.client.off('disconnect', self.on_game_disconnect)
            self.state.client.off('join', self.on_game_join)
            self.state.client.off('leave', self.on_game_leave)
            self.state.client.off('start', self.on_game_start)

    def update_players(self):
        items = []
        for index, player in enumerate(self.state.client.game.players):
            items.append((player.id, '%d. %s' % (index + 1, player.name), None))

        self.list.set_items(items)

    """
    Network events
    """
    def on_game_kick(self):
        self.alerts.error('You were kicked from the game.', on_dismiss=self.alert_dismiss)
        self.form.disable()

    def on_game_disconnect(self):
        self.alerts.error('The connection to the server was lost.', on_dismiss=self.alert_dismiss)
        self.form.disable()

    def on_game_join(self, player):
        self.update_players()

    def on_game_leave(self, player):
        self.update_players()

    def on_game_start(self):
        self.state.set_scene("Game")

    """
    Form handling
    """
    def on_leave_press(self):
        self.state.leave_game()
        self.state.set_scene("Join")

    def alert_dismiss(self, action):
        self.state.set_scene("Join")

    """
    Input handling
    """
    def on_tick(self):
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
