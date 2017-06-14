from threading import Thread
import random
import time

from sciibo.bot import Bot
from sciibo.core.emitter import Emitter
from sciibo.core.helpers import Queue
from sciibo.network.broadcast import BroadcastThread
from sciibo.network.connection import ConnectionThread
from sciibo.network.listen import ListenThread
from sciibo.network.proxy import ProxyConnections

from .game import Game


class Server(Thread, Emitter):
    def __init__(self, name, cards=15, local=False):
        Thread.__init__(self)
        Emitter.__init__(self)

        # Indicates the thread should be stopped
        self.stopped = False

        # Server settings
        self.name = name
        self.local = local
        self.cards = cards

        # Create game state
        self.game = Game()

        if not self.local:
            # Binding the port might fail, exception will bubble up
            # before we start any of these threads
            self.listen = ListenThread()
            self.broadcast = BroadcastThread()

            # Listen for incoming connections
            self.listen.on('connect', self.on_connect)
            self.listen.start()

            # Let clients find this server by broadcasting
            self.broadcast.on('discover', self.on_discover)
            self.broadcast.start()

        # Connections with clients
        self.connections = []

        # Queue of incoming messages to be processed
        self.queue = Queue()

        # Bot clients
        self.bots = []
        self.bot_names = [
            'Anna',
            'Becca',
            'Charlotte',
            'Daphne',
            'Emily',
        ]
        random.shuffle(self.bot_names)

    def stop(self):
        # Thread should be stopped
        self.stopped = True

    def run(self):
        while not self.stopped:
            while not self.queue.empty():
                conn, data = self.queue.get()
                self.on_client_message(conn, data)
                self.queue.task_done()

            time.sleep(0.2)

        # Stop networking
        if not self.local:
            self.listen.stop()
            self.broadcast.stop()

        # Stop connections with clients
        for conn in self.connections:
            conn.stop()

        # Stop bot threads
        for bot in self.bots:
            bot.stop()

    """
    Events
    """
    def on_discover(self, address):
        self.broadcast.send(address, self.name)

    def on_connect(self, sock, address):
        conn = ConnectionThread(sock)
        conn.on('receive', self.on_client_receive)
        self.connections.append(conn)
        conn.start()

    def on_client_receive(self, conn, data):
        self.queue.put((conn, data))

    def on_client_message(self, conn, data):
        type = data['type']

        # Validate message type
        if type not in ('join', 'play', 'disconnect'):
            return

        if type == 'disconnect':
            # Stop connection
            conn.stop()
            self.connections.remove(conn)

            if conn.player:
                player = self.game.get_player(conn.player)

                # Let other players know player left
                self.send_all({
                    'type': 'leave',
                    'player': player.id,
                })

                # Remove player from player list
                self.game.remove_player(player.id)

                # Let interface know (only used in lobby)
                self.trigger('leave', player.name)

                # Active game
                if self.game.started and not self.game.ended:
                    if len(self.game.player_ids) == 1:
                        # Let other players know player left
                        self.send_all({
                            'type': 'end',
                        })
                        self.game.end()
                        return

                    # It was this player's turn
                    if self.game.turn == player.id:
                        self.next_turn()

        if type == 'join':
            # Connection is already joined
            if conn.player:
                return

            name = data['name']
            reason = None

            if self.game.started:
                reason = 'started'
            elif len(self.game.players) == 5:
                reason = 'full'
            elif any(player.name.lower() == name.lower() for player in self.game.players):
                reason = 'name'

            if reason:
                conn.send({
                    'type': 'reject',
                    'reason': reason,
                })
                conn.stop()
                self.connections.remove(conn)
                return

            # Call helper method to add player to game
            self.add_player(name, conn, 'network')

        if type == 'play':
            if not conn.player:
                return

            if not self.game.started:
                return

            if self.game.ended:
                return

            if self.game.turn != conn.player:
                return

            player = self.game.get_player(conn.player)
            value = data['value']
            source = data['source']
            target = data['target']

            # Invalid move, let player try again
            if not self.game.valid_move(value, source, target):
                # Only send turn again to player, other players
                # don't know an invalid move was made
                player.send({
                    'type': 'invalid',
                })
                return

            # Perform move
            self.game.play(value, source, target)
            message = {
                'type': 'play',
                'player': player.id,
                'value': value,
                'source': source,
                'target': target,
            }

            # New stock card revealed
            if source == 'stock':
                message['reveal'] = player.stock_pile.top

            self.send_all(message)

            if player.stock_pile.empty():
                self.send_all({
                    'type': 'end',
                    'winner': player.id,
                })
                self.game.end(player.id)
                return

            # Card was played to build pile
            if target in ('build:0', 'build:1', 'build:2', 'build:3'):
                # Player emptied their hand
                if len(player.hand) == 0:
                    # Give five new cards
                    self.draw_cards()

                # Player gets another turn
                player.send({
                    'type': 'turn',
                    'player': player.id,
                })

            else:
                self.next_turn()

    """
    Actions
    """
    def add_bot(self):
        if len(self.game.player_ids) == 5:
            return

        # Find a bot name that is not in use
        player_names = [player.name.lower() for player in self.game.players]
        name = [name for name in self.bot_names if name.lower() not in player_names][0]
        self.bot_names.remove(name)

        # Add bot
        proxy_server, proxy_client = ProxyConnections()
        bot = Bot(proxy_client)
        bot.start()
        self.bots.append(bot)

        # Call helper method to add player to game
        self.add_player(name, proxy_server, 'bot')
        self.connections.append(proxy_server)

    def kick_player(self, id):
        player = self.game.get_player(id)
        if player:
            # Local player can not be kicked
            if player.type == 'local':
                return

            # Return bot name back to pool
            if player.type == 'bot':
                self.bot_names.append(player.name)

            if player.type == 'network':
                player.send({
                    'type': 'kick'
                })

                # Stop connection
                player.conn.stop()
                self.connections.remove(player.conn)

            # Let other players know player left
            self.send_all({
                'type': 'leave',
                'player': player.id,
            })

            # Remove player from player list
            self.game.remove_player(id)

            # Let interface know
            self.trigger('leave', player.name)

    def start_game(self):
        if len(self.game.player_ids) < 2:
            return

        self.game.start(self.cards)

        # Top stock cards in player order
        reveal_cards = [player.stock_pile.top for player in self.game.players]

        # Start the game
        self.send_all({
            'type': 'start',
            'order': self.game.player_ids,
            'stock': self.cards,
            'reveal': reveal_cards,
        })

        # Send dealt cards to players
        for player in self.game.players:
            # Send hand to player
            player.send({
                'type': 'hand',
                'cards': player.hand,
            })

            # Send hand count to opponents
            self.send_all({
                'type': 'draw',
                'player': player.id,
                'cards': 5,
            }, without=player.id)

        # Let players know whose turn it is
        self.send_all({
            'type': 'turn',
            'player': self.game.turn,
        })

    """
    Helper methods
    """
    def send_all(self, data, without=None):
        for player in self.game.players:
            if player.id == without:
                continue
            player.send(data)

    def add_player(self, name, conn, type):
        # Add player to game
        player = self.game.add_player(name, conn, type)
        # Reset possibly set receive handler by on_connect
        conn.off('receive')
        # Handle messages from client
        conn.on('receive', self.on_client_receive)
        # Bind connection to player
        conn.player = player.id

        # List of players (including player who just joined)
        players = []
        for opponent in self.game.players:
            players.append({
                'id': opponent.id,
                'name': opponent.name,
            })

        # Send welcome message
        player.send({
            'type': 'welcome',
            'name': self.name,
            'id': player.id,
            'players': players,
        })

        # Send join message to other players
        self.send_all({
            'type': 'join',
            'id': player.id,
            'name': player.name,
        }, without=player.id)

        # Let interface know
        self.trigger('join', player.name)

        return player

    def draw_cards(self):
        cards = self.game.draw_cards()
        player = self.game.get_player(self.game.turn)

        # Draw pile might be empty
        if cards:
            # Let player who which cards he drew
            self.send_all({
                'type': 'draw',
                'player': player.id,
                'cards': len(cards),
            }, without=player.id)

            # Let opponents know how many cards the player drew
            player.send({
                'type': 'hand',
                'cards': cards,
            })

    def next_turn(self):
        self.game.next_turn()
        self.draw_cards()

        # Let everybody know whose turn it is
        self.send_all({
            'type': 'turn',
            'player': self.game.turn,
        })
