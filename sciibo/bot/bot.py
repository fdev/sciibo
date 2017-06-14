import time
from threading import Thread

from sciibo.core.helpers import Queue
from sciibo.core.emitter import Emitter

from .game import Game
from .ai import calculate_move


class Bot(Thread, Emitter):
    def __init__(self, conn):
        Thread.__init__(self)
        Emitter.__init__(self)

        # Indicates the thread should be stopped
        self.stopped = False

        # Create game state
        self.game = Game()

        # Listen for incoming connections
        self.conn = conn
        self.conn.on('receive', self.on_receive)

        # List of calculated next moves
        self.moves = None

        # Queue of incoming messages to be processed
        self.queue = Queue()

    def run(self):
        while not self.stopped:
            while not self.queue.empty():
                data = self.queue.get()
                self.on_message(data)
                self.queue.task_done()

            time.sleep(0.2)

        self.conn.stop()

    def stop(self):
        self.stopped = True

    """
    Events
    """
    def on_receive(self, conn, data):
        self.queue.put(data)

    def on_message(self, data):
        type = data['type']

        if type == 'welcome':
            self.game.player_id = data['id']

        if type == 'start':
            self.game.on_start(data['order'], data['stock'], data['reveal'])

        if type == 'hand':
            self.game.on_hand(data['cards'])

        if type == 'turn':
            # Our turn, calculate next move
            if data['player'] == self.game.player_id:
                # Calculated next moves left
                if not self.moves:
                    start_time = time.time()
                    self.moves = calculate_move(
                        self.game.stock_card,
                        self.game.discard_piles,
                        self.game.hand,
                        self.game.build_piles,
                        # Limit calculation time to 5 seconds
                        timeout=5.0,
                    )
                    duration = time.time() - start_time

                    # Emulate thinking time
                    if duration < 1.5:
                        time.sleep(1.5 - duration)
                else:
                    time.sleep(1.5)

                value, source, target = self.moves.pop(0)
                self.conn.send({
                    'type': 'play',
                    'value': value,
                    'source': source,
                    'target': target,
                })

        if type == 'play':
            player = data['player']
            value = data['value']
            source = data['source']
            target = data['target']
            reveal = data.get('reveal')

            self.game.on_play(player, value, source, target, reveal)

        if type == 'invalid':
            raise Exception("Bot sent invalid move, should not be possible")
