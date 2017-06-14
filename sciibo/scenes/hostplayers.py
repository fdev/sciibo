from sciibo.core.scene import Scene
from sciibo.graphics import colors
from sciibo.graphics.alert import Alerts
from sciibo.graphics.forms import Form, Button, List
from sciibo.graphics.logo import Logo


class HostPlayers(Scene):
    def enter(self):
        self.set_color(colors.MENU)
        self.erase()

        self.add_child(Logo(3, 18))
        self.draw_rectangle(10, 23, 11, 34)
        self.draw_str(10, 25, ' Host game - Players ', colors.MENU_TEXT)

        # Form
        self.list = List(12, 25, 5, 30, [], on_select=self.on_list_select)
        self.add_child(self.list)
        self.update_players()

        self.leave_button = Button(19, 25, 'Back', on_press=self.on_leave_press)
        self.add_child(self.leave_button)

        self.bot_button = Button(19, 34, 'Add bot', on_press=self.on_bot_press)
        self.add_child(self.bot_button)

        self.start_button = Button(19, 46, 'Start', on_press=self.on_start_press)
        self.add_child(self.start_button)

        self.form = Form()
        self.form.add_row(self.list)
        self.form.add_row(self.leave_button, self.bot_button, self.start_button, default=self.start_button)
        self.form.set_active(self.start_button)

        # Alerts
        self.alerts = Alerts(self)

        # Networking
        self.state.server.on('join', self.on_server_join)
        self.state.server.on('leave', self.on_server_leave)
        self.state.client.on('start', self.on_game_start)

    def update_players(self):
        items = []
        for index, player in enumerate(self.state.server.game.players):
            action = '' if player.type == 'local' else 'Kick'
            items.append((player.id, '%d.%s' % (index + 1, player.name), action))

        self.list.set_items(items)
        if self.list.selected == -1:
            self.list.selected = 0

        self.list.update()

    """
    Network events
    """
    def on_server_join(self, name):
        self.update_players()

    def on_server_leave(self, name):
        self.update_players()

    def on_game_start(self):
        self.state.set_scene("Game")

    """
    Form handling
    """
    def on_list_select(self, key):
        self.state.server.kick_player(key)

    def on_leave_press(self):
        self.alerts.confirm('Are you sure you want to leave?\nAll players will be disconnected.', action='Leave', on_dismiss=self.on_leave_confirm)
        self.form.disable()

    def on_leave_confirm(self, button):
        if button == 'Leave':
            self.state.leave_game()
            self.state.set_scene("Main")
        else:
            self.form.enable()

    def on_start_press(self):
        if len(self.state.server.game.player_ids) < 2:
            self.alerts.error('You need at least two players to start a game.', on_dismiss=self.alert_dismiss)
        else:
            self.state.server.start_game()

    def on_bot_press(self):
        self.state.server.add_bot()

    def alert_dismiss(self, action):
        self.form.enable()

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
