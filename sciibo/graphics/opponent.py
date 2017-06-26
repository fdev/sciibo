from sciibo.core.drawable import Drawable

from .timeline import Timeline
from .card import Card, DiscardStack
from ..graphics import colors


class Opponent(Drawable):
    """
    Animations
    """
    def animate_draw(self, cards, on_complete):
        def animation_complete():
            self.update()
            on_complete()

        draw_y = 8 - self.y
        draw_x = 58 - self.x

        timeline = Timeline(on_complete=animation_complete)

        for n in range(5 - cards, 5):
            # Add new card
            card = Card(draw_y, draw_x, 'back', 'medium')
            card.hide()
            self.add_child(card)

            card_y, card_x = self.HAND_POSITIONS[n]

            timeline.show(card)
            timeline.resize_card(card, card_y, card_x, self.HAND_SIZE, duration=8)

        timeline.delay(8)
        self.add_child(timeline)

    def animate_play(self, value, source, target, reveal, build_piles, on_complete):
        """
        Animate card being played.

        hand -> discard

        hand -> build
        stock -> build
        discard -> build
        """
        discards = ['discard:0', 'discard:1', 'discard:2', 'discard:3']
        builds = ['build:0', 'build:1', 'build:2', 'build:3']

        if target in discards:
            self.animate_play_hand_discard(value, discards.index(target), on_complete)
            return

        build_pile = builds.index(target)
        next_value = build_piles[build_pile]

        if source == 'hand':
            self.animate_play_hand_build(value, build_pile, next_value, on_complete)
        elif source == 'stock':
            self.animate_play_stock_build(value, reveal, build_pile, next_value, on_complete)
        else:
            discard_pile = discards.index(source)
            self.animate_play_discard_build(value, discard_pile, build_pile, next_value, on_complete)

    def animate_play_hand_discard(self, value, discard_pile, on_complete):
        """
        Hand card is moved to a discard pile.
        """
        def animation_complete():
            self.update()
            on_complete()

        discard_y, discard_x = self.DISCARD_POSITIONS[discard_pile]

        duration = 6 + (3 - discard_pile) * 4

        # Animate left-most hand card
        card = self.hand_cards[-1]

        timeline = Timeline(on_complete=animation_complete)
        timeline.move(card, card.y + 1, card.x)
        timeline.delay(8)
        timeline.change_card(card, value)
        timeline.delay(8)
        timeline.move(card, discard_y + 1, discard_x, duration=duration)
        timeline.delay(8)
        timeline.move(card, discard_y, discard_x)
        timeline.delay(8)

        self.add_child(timeline)

    def animate_play_hand_build(self, value, build_pile, next_value, on_complete):
        """
        Hand card is moved to a build pile.
        """
        def animation_complete():
            self.update()
            on_complete()

        card = self.hand_cards[-1]

        build_y = 9 - self.y
        build_x = 13 + 11 * build_pile - self.x

        timeline = Timeline(on_complete=animation_complete)
        timeline.move(card, card.y + 1, card.x)
        timeline.delay(8)
        timeline.change_card(card, value)
        timeline.delay(8)
        timeline.resize_card(card, build_y, build_x, 'medium', duration=16)
        timeline.delay(8)

        if value == 'SB':
            timeline.change_card(card, next_value)
            timeline.delay(8)

        # Last card, pile disappears
        if next_value == 12:
            timeline.change_card(card, 'slot')
            timeline.delay(8)

        self.add_child(timeline)

    def animate_play_stock_build(self, value, reveal, build_pile, next_value, on_complete):
        """
        Stock card is moved to a build pile.
        """
        def animation_complete():
            self.update()
            on_complete()

        card = self.stock_card

        if reveal:
            # Add stock card below current stock card
            reveal_card = Card(card.y, card.x, 'back', card.size)
            self.add_child(reveal_card)
            # Move current stock card to top
            self.child_top(card)

        build_y = 9 - self.y
        build_x = 13 + 11 * build_pile - self.x

        timeline = Timeline(on_complete=animation_complete)
        timeline.delay(8)
        timeline.resize_card(card, build_y, build_x, 'medium', duration=16)
        timeline.delay(4)

        if value == 'SB':
            timeline.change_card(card, next_value)
            timeline.delay(8)

        # Last card, pile disappears
        if next_value == 12:
            timeline.change_card(card, 'slot')
            timeline.delay(8)

        if reveal:
            timeline.change_card(reveal_card, reveal)
            timeline.delay(8)

        self.add_child(timeline)

    def animate_play_discard_build(self, value, discard_pile, build_pile, next_value, on_complete):
        """
        Discard is moved to a build pile.
        """
        def animation_complete():
            self.update()
            on_complete()

        card = self.discard_cards[discard_pile]

        build_y = 9 - self.y
        build_x = 13 + 11 * build_pile - self.x

        timeline = Timeline(on_complete=animation_complete)
        timeline.resize_card(card, build_y, build_x, 'medium', duration=16)
        timeline.delay(8)

        if value == 'SB':
            timeline.change_card(card, next_value)
            timeline.delay(8)

        # Last card, pile disappears
        if next_value == 12:
            timeline.change_card(card, 'slot')
            timeline.delay(8)

        self.add_child(timeline)


class LargeOpponent(Opponent):
    HAND_POSITIONS = (
        (1, 70),
        (1, 67),
        (1, 64),
        (1, 61),
        (1, 58),
    )
    HAND_SIZE = 'large'
    DISCARD_POSITIONS = (
        (1, 13),
        (1, 24),
        (1, 35),
        (1, 46),
    )

    def __init__(self, y, x, player):
        super(LargeOpponent, self).__init__(y, x, 8, 80)
        self.player = player
        self.set_color(colors.PLAYFIELD)
        self.update()

    def update(self):
        self.erase()
        self.remove_children()

        self.draw_box()

        if self.player.disconnected:
            self.draw_str(7, 2, " disconnected ", color=colors.PLAYFIELD)
            self.draw_str(7, 77, " %s " % self.player.name, color=colors.PLAYFIELD, rtl=True)
        else:
            self.draw_str(7, 2, " %d left " % self.player.stock_count, color=colors.PLAYFIELD_TEXT)
            self.draw_str(7, 77, " %s " % self.player.name, color=colors.PLAYFIELD_TEXT, rtl=True)

        """
        Slots
        """
        # Stock pile
        self.draw_rectangle(1, 2, 6, 8, dashed=True)

        # Discard piles
        self.draw_rectangle(1, 19, 5, 4, dashed=True)
        self.draw_rectangle(1, 13, 5, 7, dashed=True)

        self.draw_rectangle(1, 30, 5, 4, dashed=True)
        self.draw_rectangle(1, 24, 5, 7, dashed=True)

        self.draw_rectangle(1, 41, 5, 4, dashed=True)
        self.draw_rectangle(1, 35, 5, 7, dashed=True)

        self.draw_rectangle(1, 52, 5, 4, dashed=True)
        self.draw_rectangle(1, 46, 5, 7, dashed=True)

        # Hand
        self.draw_rectangle(1, 70, 6, 8, dashed=True)
        self.draw_rectangle(1, 67, 6, 8, dashed=True)
        self.draw_rectangle(1, 64, 6, 8, dashed=True)
        self.draw_rectangle(1, 61, 6, 8, dashed=True)
        self.draw_rectangle(1, 58, 6, 8, dashed=True)

        """
        Cards
        """
        # Reference cards for animations
        self.stock_card = None
        self.discard_cards = []
        self.hand_cards = []

        # Stock pile
        if self.player.stock_count > 2:
            self.add_child(Card(1, 3, 'back', 'large'))
        if self.player.stock_count > 1:
            self.add_child(Card(1, 2, 'back', 'large'))

        if self.player.stock_card:
            card = Card(1, 2, self.player.stock_card, 'large')
            self.stock_card = card
            self.add_child(card)

        # Discard piles
        for pos, pile in enumerate(self.player.discard_piles):
            if not pile:
                self.discard_cards.append(None)
                continue

            value, rest = pile[-1], pile[:-1]
            card = Card(1, 13 + 11 * pos, value, 'medium')

            self.add_child(DiscardStack(1, 20 + 11 * pos, rest))
            self.add_child(card)
            self.discard_cards.append(card)

        # Hand
        for pos in range(self.player.hand):  # self.player.hand
            card = Card(1, 70 - pos * 3, 'back', 'large')
            self.hand_cards.append(card)
            self.add_child(card)


class MediumOpponent(Opponent):
    HAND_POSITIONS = (
        (1, 33),
        (1, 32),
        (1, 31),
        (1, 30),
        (1, 29),
    )
    HAND_SIZE = 'small'
    DISCARD_POSITIONS = (
        (1, 9),
        (1, 14),
        (1, 19),
        (1, 24),
    )

    def __init__(self, y, x, player):
        super(MediumOpponent, self).__init__(y, x, 6, 40)
        self.player = player
        self.set_color(colors.PLAYFIELD)
        self.update()

    def update(self):
        self.erase()
        self.remove_children()

        self.draw_box()

        if self.player.disconnected:
            self.draw_str(5, 2, " disconnected ", color=colors.PLAYFIELD)
            self.draw_str(5, 37, " %s " % self.player.name, color=colors.PLAYFIELD, rtl=True)
        else:
            self.draw_str(5, 2, " %d left " % self.player.stock_count, color=colors.PLAYFIELD_TEXT)
            self.draw_str(5, 37, " %s " % self.player.name, color=colors.PLAYFIELD_TEXT, rtl=True)

        """
        Slots
        """

        # Stock pile
        self.draw_rectangle(1, 2, 4, 5, dashed=True)

        # Discard piles
        self.draw_rectangle(1, 9, 3, 4, dashed=True)
        self.draw_rectangle(1, 14, 3, 4, dashed=True)
        self.draw_rectangle(1, 19, 3, 4, dashed=True)
        self.draw_rectangle(1, 24, 3, 4, dashed=True)

        # Hand
        self.draw_rectangle(1, 29, 4, 9, dashed=True)

        """
        Cards
        """
        # Reference cards for animations
        self.stock_card = None
        self.discard_cards = []
        self.hand_cards = []

        # Stock pile
        if self.player.stock_count > 1:
            self.add_child(Card(1, 3, 'back', 'small'))
        if self.player.stock_count > 2:
            self.add_child(Card(1, 2, 'back', 'small'))

        if self.player.stock_card:
            card = Card(1, 2, self.player.stock_card, 'small')
            self.stock_card = card
            self.add_child(card)

        # Discard piles
        for pos, pile in enumerate(self.player.discard_piles):
            if not pile:
                self.discard_cards.append(None)
                continue

            value, rest = pile[-1], pile[:-1]
            card = Card(1, 9 + 5 * pos, value, 'tiny')

            if rest:
                # Draw next card below as well for animation
                self.add_child(Card(1, 9 + 5 * pos, rest[-1], 'tiny'))
                self.draw_str(4, 11 + 5 * pos, "+%d" % len(rest), color=colors.PLAYFIELD_TEXT, rtl=True)

            self.discard_cards.append(card)
            self.add_child(card)

        # Hand
        for pos in range(self.player.hand):
            card = Card(1, 33 - pos, 'back', 'small')
            self.hand_cards.append(card)
            self.add_child(card)


class SmallOpponent(Opponent):
    HAND_POSITIONS = (
        (0, 34),
        (0, 33),
        (0, 32),
        (0, 31),
        (0, 30),
    )
    HAND_SIZE = 'tiny'
    DISCARD_POSITIONS = (
        (0, 9),
        (0, 14),
        (0, 19),
        (0, 24),
    )

    def __init__(self, y, x, player):
        super(SmallOpponent, self).__init__(y, x, 4, 40)
        self.player = player
        self.set_color(colors.PLAYFIELD)
        self.update()

    def update(self):
        self.erase()
        self.remove_children()

        self.draw_rectangle(-1, 0, 5, 40)

        if self.player.disconnected:
            self.draw_str(3, 2, " disconnected ", color=colors.PLAYFIELD)
            self.draw_str(3, 37, " %s " % self.player.name, color=colors.PLAYFIELD, rtl=True)
        else:
            self.draw_str(3, 2, " %d left " % self.player.stock_count, color=colors.PLAYFIELD_TEXT)
            self.draw_str(3, 37, " %s " % self.player.name, color=colors.PLAYFIELD_TEXT, rtl=True)

        """
        Slots
        """
        # Reference cards for animations
        self.stock_card = None
        self.discard_cards = []
        self.hand_cards = []

        # Stock pile
        self.draw_rectangle(0, 2, 3, 4, dashed=True)

        # Discard piles
        self.draw_rectangle(0, 9, 3, 4, dashed=True)
        self.draw_rectangle(0, 14, 3, 4, dashed=True)
        self.draw_rectangle(0, 19, 3, 4, dashed=True)
        self.draw_rectangle(0, 24, 3, 4, dashed=True)

        # Hand
        self.draw_rectangle(0, 30, 3, 8, dashed=True)

        """
        Cards
        """

        # Stock pile
        if self.player.stock_count > 1:
            self.add_child(Card(0, 3, 'back', 'tiny'))
        if self.player.stock_count > 2:
            self.add_child(Card(0, 2, 'back', 'tiny'))

        if self.player.stock_card:
            card = Card(0, 2, self.player.stock_card, 'tiny')
            self.stock_card = card
            self.add_child(card)

        # Discard piles
        for pos, pile in enumerate(self.player.discard_piles):
            if not pile:
                self.discard_cards.append(None)
                continue

            value, rest = pile[-1], pile[:-1]
            card = Card(0, 9 + 5 * pos, value, 'tiny')

            if rest:
                # Draw next card below as well for animation
                self.add_child(Card(0, 9 + 5 * pos, rest[-1], 'tiny'))

            self.discard_cards.append(card)
            self.add_child(card)

        # Hand
        for pos in range(self.player.hand):
            card = Card(0, 34 - pos, 'back', 'tiny')
            self.hand_cards.append(card)
            self.add_child(card)
