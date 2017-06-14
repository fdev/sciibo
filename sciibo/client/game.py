from sciibo.core.helpers import nextcard


class Player(object):
    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type
        self.disconnected = False

        self.stock_card = None
        self.stock_count = None
        self.discard_piles = None
        self.hand = None


class Game(object):
    def __init__(self):
        # Game state
        self.started = False
        self.turn = None
        self.ended = False
        self.winner = None

        # Players
        self.player_data = {}
        self.player_ids = []

        # Local player id
        self.player_id = None

        # Community piles
        self.build_piles = None

    def add_player(self, id, name):
        self.player_ids.append(id)
        player = Player(id, name, type)
        self.player_data[id] = player
        return player

    def remove_player(self, id):
        if id in self.player_ids:
            self.player_ids.remove(id)
            return self.player_data.pop(id)

    def get_player(self, id):
        if id in self.player_ids:
            return self.player_data[id]

    @property
    def players(self):
        return [self.player_data[id] for id in self.player_ids]

    @property
    def opponents(self):
        return [player for player in self.players if player.id != self.player_id]

    @property
    def me(self):
        return self.player_data[self.player_id]

    """
    Events
    """
    def on_start(self, order, stock, reveal):
        for id, reveal in zip(order, reveal):
            player = self.player_data[id]
            player.stock_count = stock
            player.stock_card = reveal
            player.discard_piles = [[], [], [], []]

            # We only know hand count of opponents
            player.hand = 0

        # Rearrange order so opponents come first
        pos = order.index(self.player_id)
        self.player_ids = order[pos + 1:] + order[:pos + 1]

        # We know our hand cards by value
        self.me.hand = []
        self.build_piles = [12, 12, 12, 12]

        self.started = True

    def on_draw(self, id, cards):
        player = self.get_player(id)
        player.hand += cards

    def on_hand(self, cards):
        self.me.hand += cards

    def on_turn(self, id):
        self.turn = id

    def on_play(self, id, value, source, target, reveal):
        player = self.get_player(id)

        # Remove card from source
        if source == 'hand':
            if id == self.player_id:
                player.hand.remove(value)
            else:
                player.hand -= 1
        elif source == 'stock':
            player.stock_count -= 1
            player.stock_card = reveal
        elif source == 'discard:0':
            player.discard_piles[0].pop()
        elif source == 'discard:1':
            player.discard_piles[1].pop()
        elif source == 'discard:2':
            player.discard_piles[2].pop()
        elif source == 'discard:3':
            player.discard_piles[3].pop()

        # Add card to target
        if target == 'build:0':
            self.build_piles[0] = nextcard(self.build_piles[0])
        elif target == 'build:1':
            self.build_piles[1] = nextcard(self.build_piles[1])
        elif target == 'build:2':
            self.build_piles[2] = nextcard(self.build_piles[2])
        elif target == 'build:3':
            self.build_piles[3] = nextcard(self.build_piles[3])
        elif target == 'discard:0':
            player.discard_piles[0].append(value)
        elif target == 'discard:1':
            player.discard_piles[1].append(value)
        elif target == 'discard:2':
            player.discard_piles[2].append(value)
        elif target == 'discard:3':
            player.discard_piles[3].append(value)

    def on_end(self, winner=None):
        self.ended = True
        self.winner = winner
