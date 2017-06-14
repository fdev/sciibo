import curses
import curses.ascii

from sciibo.core.drawable import Drawable

from .card import Card, DiscardStack
from .timeline import Timeline
from ..graphics import colors


class ClickableTarget(Drawable):
    def __init__(self, y, x):
        super(ClickableTarget, self).__init__(y, x, 5, 7)
        self.set_color(colors.PLAYFIELD)
        self.update()

    def update(self):
        self.draw_box(dashed=True)


class Playfield(Drawable):
    def __init__(self, y, x, game, on_select=None, on_move=None, on_cancel=None):
        super(Playfield, self).__init__(y, x, 14, 80)
        self.game = game

        # Interactive mode
        self.active = False

        # Selectable sources
        self.selectable_sources = []

        # Selectable targets
        self.selectable_targets = []

        # Index of current selectable
        self.selection = None

        # Source or target card child
        self.selection_card = None

        # Source selection
        self.selected = None
        self.selected_source = None
        self.selected_value = None

        # Placement callback
        self.on_select = on_select
        self.on_move = on_move
        self.on_cancel = on_cancel

        self.set_color(colors.PLAYFIELD)
        self.update()

    def update(self):
        self.erase()
        self.remove_children()

        self.draw_rectangle(6, 0, 8, 80, color=colors.PLAYFIELD)
        self.draw_str(13, 2, " %d left " % self.game.me.stock_count, color=colors.PLAYFIELD_TEXT)
        self.draw_str(13, 77, " %s " % self.game.me.name, color=colors.PLAYFIELD_TEXT, rtl=True)

        """
        Slots
        """

        # Build piles
        self.draw_rectangle(0, 13, 5, 7, dashed=True)
        self.draw_rectangle(0, 24, 5, 7, dashed=True)
        self.draw_rectangle(0, 35, 5, 7, dashed=True)
        self.draw_rectangle(0, 46, 5, 7, dashed=True)

        # Draw pile
        self.draw_rectangle(0, 58, 5, 7, dashed=True)

        # Stock pile
        self.draw_rectangle(7, 2, 6, 8, dashed=True)

        # Discard piles
        self.draw_rectangle(7, 19, 5, 4, dashed=True)
        self.draw_rectangle(7, 13, 5, 7, dashed=True)

        self.draw_rectangle(7, 30, 5, 4, dashed=True)
        self.draw_rectangle(7, 24, 5, 7, dashed=True)

        self.draw_rectangle(7, 41, 5, 4, dashed=True)
        self.draw_rectangle(7, 35, 5, 7, dashed=True)

        self.draw_rectangle(7, 52, 5, 4, dashed=True)
        self.draw_rectangle(7, 46, 5, 7, dashed=True)

        # Hand
        self.draw_rectangle(7, 70, 6, 8, dashed=True)
        self.draw_rectangle(7, 67, 6, 8, dashed=True)
        self.draw_rectangle(7, 64, 6, 8, dashed=True)
        self.draw_rectangle(7, 61, 6, 8, dashed=True)
        self.draw_rectangle(7, 58, 6, 8, dashed=True)

        """
        Cards
        """
        self.selectable_sources = []
        self.selectable_targets = []

        # Build piles
        for pos, value in enumerate(self.game.build_piles):
            if value == 12:
                card = ClickableTarget(0, 13 + 11 * pos)
            else:
                card = Card(0, 13 + 11 * pos, value, 'medium')

            self.add_child(card)
            self.selectable_targets.append(('build:%d' % pos, card))

        # Draw pile
        self.add_child(Card(0, 60, 'back', 'medium'))
        self.add_child(Card(0, 59, 'back', 'medium'))
        self.add_child(Card(0, 58, 'back', 'medium'))

        # Stock pile
        if self.game.me.stock_count > 2:
            self.add_child(Card(7, 3, 'back', 'large'))
        if self.game.me.stock_count > 1:
            self.add_child(Card(7, 2, 'back', 'large'))

        if self.game.me.stock_card:
            card = Card(7, 2, self.game.me.stock_card, 'large')
            self.selectable_sources.append(('stock', card))
            self.add_child(card)

        # Discard piles
        for pos, pile in enumerate(self.game.me.discard_piles):
            if not pile:
                card = ClickableTarget(7, 13 + 11 * pos)
                self.add_child(card)

                self.selectable_targets.append(('discard:%d' % pos, card))
                continue

            value, rest = pile[-1], pile[:-1]
            card = Card(7, 13 + 11 * pos, value, 'medium')
            self.add_child(card)

            self.add_child(DiscardStack(7, 20 + 11 * pos, rest))

            self.selectable_sources.append(('discard:%d' % pos, card))
            self.selectable_targets.append(('discard:%d' % pos, card))

        # Hand
        hand_cards = []
        for pos, value in enumerate(self.game.me.hand):
            if value is None:
                continue
            card = Card(7, 70 - pos * 3, value, 'large')
            hand_cards.append(card)
            self.add_child(card)

        # Add hand cards in reverse order so left-most card
        # is displayed on top
        for card in reversed(hand_cards):
            self.selectable_sources.append(('hand', card))

    """
    Animations
    """
    def animate_hand(self, cards, on_complete):
        def animation_complete():
            self.update()
            on_complete()

        draw_y = 0
        draw_x = 58

        timeline = Timeline(on_complete=animation_complete)

        for n, value in zip(list(range(5 - len(cards), 5)), cards):
            # Add new card
            card = Card(draw_y, draw_x, 'back', 'medium')
            card.hide()
            self.add_child(card)

            card_y = 7
            card_x = 70 - n * 3

            timeline.show(card)
            timeline.change_card(card, value)
            timeline.resize_card(card, card_y, card_x, 'large', duration=8)

        timeline.delay(8)
        self.add_child(timeline)

    def animate_play(self, value, source, target, reveal, on_complete):
        def animation_complete():
            self.update()
            on_complete()

        timeline = Timeline(on_complete=animation_complete)

        builds = ['build:0', 'build:1', 'build:2', 'build:3']
        if target in builds:
            build_pile = builds.index(target)
            next_value = self.game.build_piles[build_pile]

            # Move card to slot
            timeline.move(self.selection_card, 0, self.selection_card.x)

            if value == 'SB':
                # Animate the change
                timeline.change_card(self.selection_card, next_value)
                timeline.delay(8)

            # Last card, pile disappears
            if next_value == 12:
                timeline.change_card(self.selection_card, 'slot')
                timeline.delay(8)

        if source == 'stock' and reveal:
            # Add new card
            card = Card(7, 2, 'back', 'large')
            self.add_child(card)

            # Animate the change
            timeline.move(self.selection_card, 0, self.selection_card.x)
            timeline.delay(4)
            timeline.change_card(card, reveal)
            timeline.delay(4)

        self.add_child(timeline)

    """
    Actions
    """
    def activate(self, reset=True):
        # Only reset if asked
        if reset:
            self.reset()
            self.active = True
            self.set_selection(0)
        else:
            self.active = True

    def deactivate(self):
        self.reset()
        self.active = False

    def reset(self):
        if self.selection_card:
            if self.selected:
                self.selected.y = 7
                self.selected.show()
                self.remove_child(self.selection_card)
            else:
                self.selection_card.y = 7

        self.selection = None
        self.selection_card = None

        self.selected = None
        self.selected_source = None
        self.selected_value = None

    def set_selection(self, index):
        if self.selected:
            self.selection = index

            # Move around selected card
            target, card = self.selectable_targets[self.selection]
            self.selection_card.y = card.y + 1
            self.selection_card.x = card.x

        else:
            if self.selection_card:
                # Slide back previous selection
                self.selection_card.y = 7

            self.selection = index
            self.selection_card = self.selectable_sources[self.selection][1]

            # Outjog selected card
            self.selection_card.y = 6

    def cancel_selection(self):
        self.activate()
        self.on_cancel()

    def confirm_selection(self):
        if self.selected:
            target, card = self.selectable_targets[self.selection]
            self.on_move(self.selected_value, self.selected_source, target)
            self.active = False

        else:
            source, card = self.selectable_sources[self.selection]

            self.selected_source = source
            self.selected_value = card.value
            self.selected = card
            self.selected.hide()

            self.on_select(self.selected_value, self.selected_source)

            self.selection_card = Card(0, 0, self.selected_value, 'medium')
            self.add_child(self.selection_card)

            self.set_selection(0)

    """
    Input handling
    """
    def on_key(self, ch):
        if not self.active:
            return

        if self.selected:
            if ch == curses.ascii.ESC:
                self.cancel_selection()

            elif ch == curses.KEY_LEFT:
                if self.selection > 0 and self.selection < 4 or self.selection > 4:
                    self.set_selection(self.selection - 1)

            elif ch == curses.KEY_RIGHT:
                if self.selection < 3 or self.selection > 3 and self.selection < 7:
                    self.set_selection(self.selection + 1)

            elif ch == curses.KEY_UP:
                if self.selection > 3:
                    self.set_selection(self.selection - 4)

            elif ch == curses.KEY_DOWN:
                if self.selection < 4 and self.selected_source == 'hand':
                    self.set_selection(self.selection + 4)

            elif ch == curses.KEY_ENTER:
                self.confirm_selection()

        else:
            if ch == curses.KEY_LEFT:
                if self.selection > 0:
                    self.set_selection(self.selection - 1)

            elif ch == curses.KEY_RIGHT:
                if self.selection + 1 < len(self.selectable_sources):
                    self.set_selection(self.selection + 1)

            elif ch == curses.KEY_ENTER:
                self.confirm_selection()

    def on_mouse(self, chain, y, x):
        if not self.active:
            return

        if self.selected:
            # Selection card blocks click on targets
            if self.selection_card in chain:
                self.confirm_selection()

            else:
                target_cards = [card for target, card in self.selectable_targets]
                for card in target_cards:
                    if card in chain:
                        index = target_cards.index(card)

                        if index == self.selection:
                            self.confirm_selection()

                        else:
                            self.set_selection(index)

        else:
            source_cards = [card for source, card in self.selectable_sources]
            for card in source_cards:
                if card in chain:
                    index = source_cards.index(card)

                    if index == self.selection:
                        self.confirm_selection()

                    else:
                        self.set_selection(index)
