from sciibo.core.scene import Scene
from sciibo.core.drawable import Drawable
from sciibo.graphics import colors
from sciibo.graphics.explanation import Explanation
from sciibo.graphics.scrollable import Scrollable
from sciibo.graphics.forms import Button


# Based on http://www.indepthinfo.com/skip-bo/rules.htm
INSTRUCTIONS = """
Objective
Be the first player to play every card in your stock pile, by
playing all of your cards in numerical order (1 to 12) onto the build
piles.

Beginning Play
Each player is dealt 20 cards, which are are dealt face down
and form each player's stock pile. The top card of each stock pile is always
face up. The remaining undealt cards are placed face down on the table to
form the draw pile.

Taking Turns
The turn begins with the active player drawing as many cards
from the draw pile as are needed to bring the hand up to five cards. Next,
the player may play cards - from his hand, the top of one of his own discard
piles, or the top card on the stock pile - onto one or more of the build
piles. A card may be played if it is the next in sequence on a build pile,
or it is a "1" and one of the four build pile positions is empty.
Scii-Bo cards ("SB") play as a wild card in the place of any other card. As
long as there are cards that will legally play, the turn may continue. The
object is to play as many cards from the stock pile as possible.

A player does not have to play any cards at all on the build piles. He may
also have no options to do so. If a player plays out his or her entire hand,
he must draw five more cards from the draw pile. At the end of a player's
turn he is required to place a hand card on one of four of his own discard
piles. If this happens to be the last card in the hand, the player may not
draw five new cards until the player's next turn.

Play proceeds around the table. As the build piles reach "12" the stacks are
removed and shuffled together. When the draw pile becomes completely depleted
the removed cards are shuffled and become a new draw pile. Play proceeds
until one person uses all of his or her cards in the stock pile. At this
point that person may be declared winner.







                          left blank for drawing









Building Piles
Building piles are where players build the 1-12 sequences and
can only be started with a "1" or a "SB" card. Once a pile has completed the
1-12 sequence, remove it from the playing area and start a new build pile.

Draw Pile
Pile with all cards remaining after the stock piles are dealt.

Stock Pile
Pile that must be cleared to win. Only the top card is face up.

Discard Piles
At the end of a turn, a hand card must be placed on one of
four piles. During a turn the top card of any discard pile may be placed onto
a build pile.

Hand Cards
Start your turn by bringing up your hand to five cards.
"""
HEADINGS = (
    (0, 'Objective'),
    (5, 'Beginning Play'),
    (11, 'Taking Turns'),
    (51, 'Building Piles'),
    (56, 'Draw Pile'),
    (59, 'Stock Pile'),
    (62, 'Discard Piles'),
    (67, 'Hand Cards'),
)


class HelpText(Drawable):
    def __init__(self, y, x):
        super(HelpText, self).__init__(y, x, 70, 78)
        self.update()

    def update(self):
        self.set_color(colors.MENU_TEXT)
        self.erase()
        self.draw_text(0, 0, self.w, INSTRUCTIONS.strip())
        for y, heading in HEADINGS:
            self.draw_str(y, 0, heading, color=colors.MENU_TEXT_BOLD)
        self.add_child(Explanation(36, 8))


class Help(Scene):
    def enter(self):
        self.set_color(colors.MENU_TEXT)
        self.erase()
        self.draw_str(1, 1, 'How to play Scii-Bo')

        self.scrollable = Scrollable(3, 1, 21, HelpText(0, 0), color=colors.MENU_TEXT, perpage=8)
        self.add_child(self.scrollable)

        self.back_button = Button(1, 71, 'Back', on_press=self.on_back_press)
        self.back_button.set_active(True)
        self.add_child(self.back_button)

    """
    Form handling
    """
    def on_back_press(self):
        self.state.set_scene("Main")

    """
    Input handling
    """
    def on_key(self, ch):
        if not self.back_button.on_key(ch):
            self.scrollable.on_key(ch)

    def on_mouse(self, chain, y, x):
        if self.back_button in chain:
            self.back_button.on_mouse(chain, y, x)
