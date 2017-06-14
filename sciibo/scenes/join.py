from sciibo.core.scene import Scene
from sciibo.graphics import colors
from sciibo.graphics.alert import Alerts
from sciibo.graphics.animations.dots import Dots
from sciibo.graphics.forms import Form, List, Button, Input
from sciibo.graphics.logo import Logo
from sciibo.network.search import SearchThread


class Join(Scene):
    def enter(self):
        self.set_color(colors.MENU)
        self.erase()

        self.add_child(Logo(3, 18))
        self.draw_rectangle(10, 23, 12, 34)
        self.draw_str(10, 25, ' Join game ', colors.MENU_TEXT)
        self.draw_str(12, 25, 'Your name:', colors.MENU_TEXT)
        self.draw_str(20, 44, 'Searching', colors.MENU_TEXT)
        self.add_child(Dots(20, 53, colors.MENU_TEXT))

        # Form
        self.name_input = Input(12, 36, 19, 16, self.state.name)
        self.add_child(self.name_input)

        self.list = List(14, 25, 5, 30, [], on_select=self.on_list_select)
        self.add_child(self.list)

        self.back_button = Button(20, 25, 'Back', on_press=self.on_back_press)
        self.add_child(self.back_button)

        self.refresh_button = Button(20, 44, 'Refresh', on_press=self.on_refresh_press)
        self.refresh_button.hide()
        self.add_child(self.refresh_button)

        self.form = Form()
        self.form.add_row(self.name_input)
        self.form.add_row(self.list)
        self.form.add_row(self.back_button, self.refresh_button, default=self.refresh_button)
        self.form.set_active(self.name_input)
        self.form.disable()

        # Alerts
        self.alerts = Alerts(self)

        # Networking
        self.search_thread = None
        self.search_start()

    def leave(self):
        self.search_stop()
        self.state.set_name(self.name_input.value)

        if self.state.client:
            self.state.client.off('welcome', self.on_game_welcome)
            self.state.client.off('reject', self.on_game_reject)
            self.state.client.off('disconnect', self.on_game_disconnect)

    """
    Network events
    """
    def search_start(self):
        self.search_stop()

        self.search_thread = SearchThread()
        self.search_thread.on('result', self.on_search_result)
        self.search_thread.on('complete', self.on_search_complete)
        self.search_thread.on('error', self.on_search_error)
        self.search_thread.start()

    def search_stop(self):
        if self.search_thread:
            self.search_thread.stop()
        self.search_thread = None

    def on_search_result(self, name, address):
        self.list.items.append(((address, name), name, 'Join'))
        if self.list.selected == -1:
            self.list.selected = 0
        self.list.update()

    def on_search_complete(self):
        if not self.list.items:
            self.list.empty_text = 'No servers found.'
            self.list.update()

        self.refresh_button.show()
        self.form.enable()

    def on_search_error(self):
        self.refresh_button.show()
        self.alerts.error('Networking unavailable.', on_dismiss=self.alert_dismiss)

    def on_game_welcome(self):
        self.state.set_scene("JoinPlayers")

    def on_game_reject(self, reason):
        if reason == 'full':
            self.alerts.error('Unable to join, server is full.', on_dismiss=self.alert_dismiss)
        elif reason == 'started':
            self.alerts.error('Unable to join, game has started.', on_dismiss=self.alert_dismiss)
        elif reason == 'name':
            self.alerts.error('Unable to join, your name is in use.', on_dismiss=self.alert_dismiss)
        else:
            self.alerts.error('Unable to connect to server.', on_dismiss=self.alert_dismiss)

    def on_game_disconnect(self):
        self.alerts.error('You were disconnected from the server.', on_dismiss=self.alert_dismiss)

    """
    Form handling
    """
    def on_list_select(self, key):
        # Stop searching
        self.search_stop()
        self.on_search_complete()

        # Validate entered name
        name = self.name_input.value.strip()
        if name == '':
            self.alerts.error('Please enter your name.', on_dismiss=self.alert_dismiss)
            self.form.disable()
            return

        # Save entered name before starting game
        self.state.set_name(name)

        # Server details
        address, name = key

        # Try to connect to server
        if self.state.join_game(address):
            self.state.client.on('welcome', self.on_game_welcome)
            self.state.client.on('reject', self.on_game_reject)
            self.state.client.on('disconnect', self.on_game_disconnect)

            self.alerts.alert('Connecting to server %s...' % name, on_dismiss=self.alert_join_cancel)
            self.form.disable()

        else:
            self.alerts.error('Unable to connect to server.', on_dismiss=self.alert_dismiss)
            self.form.disable()

    def on_back_press(self):
        self.state.set_scene("Main")

    def on_refresh_press(self):
        self.form.disable()
        self.refresh_button.hide()

        self.list.items = []
        self.list.selected = -1
        self.list.empty_text = ''
        self.list.update()

        self.search_start()

    def alert_dismiss(self, action):
        self.form.enable()

    def alert_join_cancel(self, action):
        self.state.leave_game()
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
