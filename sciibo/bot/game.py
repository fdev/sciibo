from sciibo.core.helpers import nextcard


class Game(object):
    def __init__(self):
        # Local player id
        self.player_id = None

        # Community piles
        self.build_piles = None

        # Private piles
        self.stock_card = None
        self.discard_piles = None
        self.hand = None

    def on_start(self, order, stock, reveal):
        index = order.index(self.player_id)
        self.stock_card = reveal[index]
        self.build_piles = [12, 12, 12, 12]
        self.discard_piles = [[], [], [], []]
        self.hand = []

    def on_hand(self, cards):
        self.hand += cards

    def on_play(self, id, value, source, target, reveal):
        builds = ['build:0', 'build:1', 'build:2', 'build:3']
        discards = ['discard:0', 'discard:1', 'discard:2', 'discard:3']

        # Bot is only interested in own cards, or build cards
        if id != self.player_id:
            if target in builds:
                index = builds.index(target)
                self.build_piles[index] = nextcard(self.build_piles[index])
            return

        # Remove card from source
        if source == 'hand':
            self.hand.remove(value)
        elif source == 'stock':
            self.stock_card = reveal
        else:
            index = discards.index(source)
            self.discard_piles[index].pop()

        # Add card to target
        if target in builds:
            index = builds.index(target)
            self.build_piles[index] = nextcard(self.build_piles[index])
        else:
            index = discards.index(target)
            self.discard_piles[index].append(value)
