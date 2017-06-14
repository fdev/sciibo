from sciibo.core.helpers import Queue
from sciibo.core.emitter import Emitter

from .game import Game


class Client(Emitter):
    def __init__(self, conn):
        super(Client, self).__init__()

        # Create game state
        self.game = Game()

        # Listen for incoming connections
        self.conn = conn
        self.conn.on('receive', self.on_receive)

        # Incoming message queue
        self.queue = Queue()

    def stop(self):
        self.conn.stop()

    def on_receive(self, conn, data):
        self.queue.put(data)

    def process_message(self):
        """
        Network messages don't get processed automatically.
        Instead, the client can request a message to be processed
        so an animation can be started if necessary and prevent
        other animations from starting as well.
        """
        if not self.queue.empty():
            data = self.queue.get()
            self.on_message(data)
            self.queue.task_done()

    def flush_queue(self):
        while not self.queue.empty():
            self.queue.get()
            self.queue.task_done()

    def on_message(self, data):
        type = data['type']

        if type == 'disconnect':
            self.conn.stop()
            self.flush_queue()
            self.trigger('disconnect')

        """
        Lobby events
        """
        if type == 'reject':
            self.conn.stop()
            self.flush_queue()
            self.game.on_end()
            self.trigger('reject', data['reason'])

        if type == 'kick':
            self.conn.stop()
            self.flush_queue()
            self.game.on_end()
            self.trigger('kick')

        if type == 'welcome':
            self.game.player_id = data['id']

            for player in data['players']:
                self.game.add_player(player['id'], player['name'])

            self.trigger('welcome')

        if type == 'leave':
            if not self.game:
                return

            player = self.game.get_player(data['player'])
            if player:
                if self.game.started:
                    player.disconnected = True
                else:
                    self.game.remove_player(player.id)
                self.trigger('leave', player)

        if type == 'join':
            player = self.game.add_player(data['id'], data['name'])
            self.trigger('join', player)

        if type == 'start':
            self.game.on_start(data['order'], data['stock'], data['reveal'])
            self.trigger('start')

        """
        In-game events
        """
        if type == 'draw':
            player = self.game.get_player(data['player'])
            cards = data['cards']
            self.game.on_draw(player.id, cards)
            self.trigger('draw', player, cards)

        if type == 'hand':
            cards = data['cards']
            self.game.on_hand(cards)
            self.trigger('hand', cards)

        if type == 'turn':
            player = self.game.get_player(data['player'])
            self.game.on_turn(player.id)
            self.trigger('turn', player)

        if type == 'invalid':
            self.trigger('invalid')

        if type == 'play':
            player = self.game.get_player(data['player'])
            value = data['value']
            source = data['source']
            target = data['target']
            reveal = data.get('reveal')

            self.game.on_play(player.id, value, source, target, reveal)
            self.trigger('play', player, value, source, target, reveal)

        if type == 'end':
            winner = self.game.get_player(data['winner']) if data.get('winner') else None
            self.game.on_end(winner)
            self.trigger('end', winner)

    """
    Actions
    """
    def join(self, name):
        self.conn.send({
            'type': 'join',
            'name': name,
        })

    def play(self, value, source, target):
        self.conn.send({
            'type': 'play',
            'value': value,
            'source': source,
            'target': target,
        })
