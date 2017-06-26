import curses

from sciibo.core.scene import Scene
from sciibo.core.animation import Animation
from sciibo.graphics import colors
from sciibo.graphics.alert import Alert, Alerts
from sciibo.graphics.playfield import Playfield
from sciibo.graphics.statusbar import Statusbar
from sciibo.graphics.opponent import SmallOpponent, MediumOpponent, LargeOpponent
from sciibo.graphics.animations.timed_alert import TimedAlert


class Game(Scene):
    def enter(self):
        self.set_color(colors.PLAYFIELD)
        self.erase()

        # Helper variable
        self.game = self.state.client.game

        # During animation new events are blocked
        self.animating = False

        # Playfield
        self.playfield = Playfield(
            9, 0, self.game,
            on_select=self.on_playfield_select,
            on_move=self.on_playfield_move,
            on_cancel=self.on_playfield_cancel,
        )
        self.add_child(self.playfield)

        # Opponents
        self.opponents = {}
        if len(self.game.opponents) == 1:
            self.add_opponent(LargeOpponent, 0, 0, self.game.opponents[0])

        elif len(self.game.opponents) == 2:
            self.add_opponent(MediumOpponent, 2, 0, self.game.opponents[0])
            self.add_opponent(MediumOpponent, 2, 40, self.game.opponents[1])

        elif len(self.game.opponents) == 3:
            self.add_opponent(SmallOpponent, 4, 0, self.game.opponents[2])
            self.add_opponent(SmallOpponent, 0, 0, self.game.opponents[0])
            self.add_opponent(SmallOpponent, 0, 40, self.game.opponents[1])

        elif len(self.game.opponents) == 4:
            self.add_opponent(SmallOpponent, 4, 0, self.game.opponents[2])
            self.add_opponent(SmallOpponent, 4, 40, self.game.opponents[3])
            self.add_opponent(SmallOpponent, 0, 0, self.game.opponents[0])
            self.add_opponent(SmallOpponent, 0, 40, self.game.opponents[1])

        # Statusbar
        self.statusbar = Statusbar(23, 0)
        self.add_child(self.statusbar)

        # Alerts
        self.alerts = Alerts(self)

        # Networking
        self.state.client.on('draw', self.on_game_draw)
        self.state.client.on('hand', self.on_game_hand)
        self.state.client.on('turn', self.on_game_turn)
        self.state.client.on('play', self.on_game_play)
        self.state.client.on('invalid', self.on_game_invalid)
        self.state.client.on('end', self.on_game_end)
        self.state.client.on('leave', self.on_game_leave)
        self.state.client.on('disconnect', self.on_game_disconnect)

        # When returning from the help screen, make sure turn is activated
        if self.game.turn:
            self.on_game_turn(self.game.get_player(self.game.turn))

    def leave(self):
        if self.state.client:
            # Unregister networking events to prevent events firing twice
            self.state.client.off('draw', self.on_game_draw)
            self.state.client.off('hand', self.on_game_hand)
            self.state.client.off('turn', self.on_game_turn)
            self.state.client.off('play', self.on_game_play)
            self.state.client.off('invalid', self.on_game_invalid)
            self.state.client.off('end', self.on_game_end)
            self.state.client.off('leave', self.on_game_leave)
            self.state.client.off('disconnect', self.on_game_disconnect)

    def add_opponent(self, graphic, y, x, opponent):
        child = graphic(y, x, opponent)
        self.opponents[opponent.id] = child
        self.add_child(child)

    """
    Network events
    """
    def on_game_draw(self, player, cards):
        """
        Opponent drew cards.
        """
        self.animating = True
        self.child_top(self.opponents[player.id])
        self.opponents[player.id].animate_draw(cards, on_complete=self.animation_complete)

    def on_game_hand(self, cards):
        """
        Player received hand cards.
        """
        self.animating = True
        self.playfield.animate_hand(cards, on_complete=self.animation_complete)

    def on_game_turn(self, player):
        """
        Turn change.
        """
        if player.id == self.game.player_id:
            self.playfield.activate()
        else:
            # Bring opponent playfield to the top
            self.child_top(self.opponents[player.id])
            self.playfield.deactivate()
        self.update_statusbar()

    def on_game_invalid(self):
        """
        Invalid move was made, try again.
        """
        self.playfield.activate(reset=False)
        self.update_statusbar()
        self.alerts.error("That card can not be placed here.")

    def on_game_play(self, player, value, source, target, reveal):
        """
        Player moves around cards.
        """
        if player.id != self.game.player_id:
            # Update playfield as well, since build cards might have been moved there
            def animation_complete():
                self.playfield.update()
                self.animation_complete()

            self.animating = True
            self.opponents[player.id].animate_play(value, source, target, reveal, self.game.build_piles, on_complete=animation_complete)
        else:
            # No longer waiting for response from server
            self.statusbar.text = ''
            self.statusbar.update()

            self.animating = True
            self.playfield.animate_play(value, source, target, reveal, on_complete=self.animation_complete)

    def on_game_end(self, winner):
        """
        Game ends.
        """
        self.update_statusbar()

        if winner:
            if winner.id == self.game.player_id:
                alert_text = "You won the game, congratulations!"
            else:
                alert_text = "%s won the game, better luck next time." % winner.name
        else:
            alert_text = "The game has ended."

        self.alerts.alert(alert_text, buttons=['Leave game'], on_dismiss=self.on_alert_end)

    def on_game_leave(self, player):
        """
        Opponent left.
        """
        self.animating = True
        self.opponents[player.id].update()
        alert = TimedAlert(Alert("%s left the game." % player.name, type='error'), on_complete=self.animation_complete)
        self.add_child(alert)

    def on_game_disconnect(self):
        """
        Disconnected from server.
        """
        self.update_statusbar()
        self.alerts.error('The connection to the server was lost.', on_dismiss=self.on_alert_end)

    """
    Form handling
    """
    def on_playfield_cancel(self):
        self.update_statusbar()

    def on_playfield_select(self, value, source):
        self.update_statusbar()

    def on_playfield_move(self, value, source, target):
        self.update_statusbar()
        self.state.client.play(value, source, target)

    def update_statusbar(self):
        if self.game.ended:
            self.statusbar.active = False
            self.statusbar.text = ''

        elif self.game.turn != self.game.player_id:
            player = self.game.get_player(self.game.turn)
            self.statusbar.active = False
            self.statusbar.text = 'Turn: %s' % player.name

        else:
            self.statusbar.active = True
            if self.playfield.selected:
                self.statusbar.text = 'Place card to play (ESC/BACKSPACE to cancel).'
            else:
                self.statusbar.text = 'Your turn! Select a card to play.'

        self.statusbar.update()

    def animation_complete(self):
        self.animating = False

    def on_alert_leave(self, action):
        if action == 'Leave':
            self.state.leave_game()
            self.state.set_scene("Main")
        Animation.resume()

    def on_alert_end(self, action):
        self.state.leave_game()
        self.state.set_scene("Main")

    """
    Input handling
    """
    def on_tick(self):
        # Wait for animation to finish before
        # processing another network message
        if not self.animating:
            self.state.client.process_message()

    def on_key(self, ch):
        if self.alerts.open:
            self.alerts.on_key(ch)
        elif ch == curses.KEY_F1:
            self.state.set_scene("Help")
        elif ch == curses.KEY_F10:
            Animation.pause()
            self.alerts.confirm('Are you sure you want to leave the game?', action='Leave', on_dismiss=self.on_alert_leave)
        elif not self.animating:
            self.playfield.on_key(ch)

    def on_mouse(self, chain, y, x):
        if self.alerts.open:
            self.alerts.on_mouse(chain, y, x)
        elif not self.animating:
            self.playfield.on_mouse(chain, y, x)
