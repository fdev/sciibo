import random

from sciibo.core.helpers import nextcard, fitson


class Pile(object):
    def __init__(self, initial=None):
        self.cards = initial or []

    def add(self, value):
        if not isinstance(value, list):
            value = [value]
        self.cards += value

    def shuffle(self):
        random.shuffle(self.cards)

    def remove(self, n=1):
        if n < 1:
            return []
        cards = self.cards[-n:]
        del self.cards[-n:]
        return cards

    def __len__(self):
        return len(self.cards)

    def __bool__(self):
        return len(self.cards) > 0

    @property
    def top(self):
        if self.cards:
            return self.cards[-1]

    def empty(self):
        return len(self.cards) == 0

    @classmethod
    def fulldeck(cls):
        pile = cls()
        pile.add(list(range(1, 13)) * 12 + ["SB"] * 18)
        pile.shuffle()
        return pile


class Player(object):
    def __init__(self, id, name, conn, type):
        self.id = id
        self.name = name
        self.type = type
        self.conn = conn

        self.stock_pile = None
        self.discard_piles = None
        self.hand = None

    def send(self, data):
        self.conn.send(data)


class Game(object):
    def __init__(self):
        # Game state
        self.started = False
        self.turn = None
        self.ended = False
        self.winner = None

        # Player objects by id
        self.player_data = {}

        # List of active player ids
        self.player_ids = []

        # Auto-incremented player id
        self.player_id = 0

        # Community piles
        self.draw_pile = None
        self.discard_pile = None
        self.build_piles = None

        # Top cards of build piles, with SB cards
        # replaced by representing value
        self.build_cards = None

    def add_player(self, name, conn, type):
        self.player_id += 1
        player = Player(self.player_id, name, conn, type)
        self.player_ids.append(self.player_id)
        self.player_data[self.player_id] = player
        return player

    def remove_player(self, id):
        if id in self.player_ids:
            self.player_ids.remove(id)
            del self.player_data[id]

    def get_player(self, id):
        if id in self.player_ids:
            return self.player_data[id]

    @property
    def players(self):
        return [self.player_data[id] for id in self.player_ids]

    def valid_move(self, value, source, target):
        player = self.get_player(self.turn)

        builds = ['build:0', 'build:1', 'build:2', 'build:3']
        discards = ['discard:0', 'discard:1', 'discard:2', 'discard:3']

        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 'SB']
        sources = ['stock', 'hand'] + discards
        targets = builds + discards

        # Valid sources and targets
        if value not in values:
            return False
        if source not in sources:
            return False
        if target not in targets:
            return False

        # Source is allowed to be moved to target
        if source == 'stock':
            if target in discards:
                return False
        elif source in discards:
            if target in discards:
                return False

        # Source contains value
        if source == 'hand':
            if value not in player.hand:
                return False
        elif source == 'stock':
            if player.stock_pile.empty() or player.stock_pile.top != value:
                return False
        elif source in discards:
            index = discards.index(source)
            if player.discard_piles[index].empty() or player.discard_piles[index].top != value:
                return False

        # Value can be placed on target
        if target in builds:
            index = builds.index(target)
            if not fitson(self.build_cards[index], value):
                return False

        # Card may always be placed on discard pile
        return True

    def draw_cards(self):
        player = self.get_player(self.turn)
        short = 5 - len(player.hand)
        cards = self.draw_pile.remove(short)

        if self.draw_pile.empty():
            # Place shuffled discards into draw pile
            self.discard_pile.shuffle()
            self.draw_pile = self.discard_pile
            self.discard_pile = Pile()

            # We might not have drawn enough cards
            cards += self.draw_pile.remove(short - len(cards))

        player.hand += cards

        return cards

    def next_turn(self):
        # TODO:
        # Check if next player has a move
        # If not, check if any player has a move.
        # If not, end the game without a winner.

        # If current turn is not in front of player id list, then the player
        # at turn has been removed. Don't skip over current player in front.
        if self.turn == self.player_ids[0]:
            # Shift new turn player to front
            self.player_ids = self.player_ids[1:] + self.player_ids[0:1]
        self.turn = self.player_ids[0]

    def play(self, value, source, target):
        player = self.get_player(self.turn)

        # Remove card from source
        if source == 'hand':
            player.hand.remove(value)
        elif source == 'stock':
            player.stock_pile.remove()
        elif source == 'discard:0':
            player.discard_piles[0].remove()
        elif source == 'discard:1':
            player.discard_piles[1].remove()
        elif source == 'discard:2':
            player.discard_piles[2].remove()
        elif source == 'discard:3':
            player.discard_piles[3].remove()

        # Add card to target
        builds = ['build:0', 'build:1', 'build:2', 'build:3']
        discards = ['discard:0', 'discard:1', 'discard:2', 'discard:3']

        if target in builds:
            index = builds.index(target)
            self.build_cards[index] = nextcard(self.build_cards[index])
            self.build_piles[index].add(value)

            # Move cards to discard pile
            if len(self.build_piles[index]) == 12:
                self.discard_pile.add(self.build_piles[index].remove(12))
        else:
            index = discards.index(target)
            player.discard_piles[index].add(value)

    def start(self, stock_size):
        self.started = True

        # Create decks
        self.draw_pile = Pile.fulldeck()
        self.discard_pile = Pile()
        self.build_piles = [
            Pile(),
            Pile(),
            Pile(),
            Pile(),
        ]
        self.build_cards = [12, 12, 12, 12]

        # Choose starting player and player order
        random.shuffle(self.player_ids)
        self.turn = self.player_ids[0]

        # Deal out cards
        for player in self.players:
            player.stock_pile = Pile(self.draw_pile.remove(stock_size))
            player.discard_piles = [
                Pile(),
                Pile(),
                Pile(),
                Pile(),
            ]
            cards = self.draw_pile.remove(5)
            player.hand = cards

    def end(self, winner=None):
        self.ended = True
        self.winner = winner
