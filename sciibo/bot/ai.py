from __future__ import division

import collections
import random
import time

from sciibo.core.helpers import nextcard, fitson


class CalculationTimeout(Exception):
    pass


def enumerate_unique(cards):
    """
    Enumerate but eliminate duplicates.
    """
    seen = set()
    for n, card in enumerate(cards):
        if card in seen:
            continue
        seen.add(card)
        yield n, card
    # for card in set(cards):
    #     yield cards.index(card), card


def top_cards(piles):
    """
    Returns the pile number and top card of each non-empty pile.

    Example:
    > top_cards([[1,2,3], [], [4,5,6], [7,8,9]])
    [(0, 3), (2, 6), (3, 9)]
    """
    for n, pile in enumerate(piles):
        if not pile:
            continue
        yield n, pile[-1]


def pull(cards, card):
    """
    Pulls the a card from a hand and returns the new hand.

    Example:
    > pull([4,5,6,7,8], 6)
    [4,5,7,8]
    """
    rest = cards[:]
    rest.remove(card)
    return rest


def pull_top(piles, pos):
    """
    Pulls the top card of pile number `pos`,
    and returns the new set of piles.

    Example:
    > pull_top([[1,2,3], [], [4,5,6], [7,8,9]], 2)
    [[1,2,3], [], [4,5], [7,8,9]]
    """
    rest = piles[:]
    rest[pos] = piles[pos][:-1]
    return rest


def place(cards, pos, card):
    """
    Replaces the card at a given position in a list.

    Example:
    > place([1,4,7,10,12], 2, 9)
    [1,4,9,10,12]
    """
    result = cards[:]
    result[pos] = card
    return result


def best_moves(result):
    """
    For each list of moves, count the number of hand cards and the
    number of SB cards that are played, and return the set of
    moves with minimum SB cards and maximum hand cards.
    """
    result = [
        (
            sum(1 for value, source, target in moves if source == 'hand'),
            sum(1 for value, source, target in moves if value == 'SB'),
            moves
        ) for moves in result
    ]

    # Get the least number of SB cards for moves that play the maximum number of hand cards
    minsb = min(sb for hands, sb, moves in result)

    # Get the maximum number of hand cards that can be played
    maxhands = max(hands for hands, sb, moves in result if sb == minsb)

    # Return first set of moves with maximum hand cards and minimum SB cards
    for hands, sb, moves in result:
        if hands == maxhands and sb == minsb:
            return moves


def stock_moves(stock, discards, hand, builds, timeout=None):
    """
    Returns the shortest list of cards to move
    to get rid of the stock card.

    Note: Five SB cards will be considered 'better'
    than six non-SB cards, because it uses fewer cards.
    """

    if not stock:
        return

    # Stock card is SB, can be placed on any pile
    if stock == 'SB':
        # Calculate number of possible subsequent moves per build pile.
        result = []
        builds_unique = list(enumerate_unique(builds))
        for pos, card in builds_unique:
            new_builds = place(builds, pos, nextcard(card))
            limit = timeout / len(builds_unique) if timeout else None
            try:
                moves = most_moves(discards, hand, new_builds, timeout=limit)
                result.append((pos, len(moves) if moves else 0))
            except CalculationTimeout:
                pass

        # Get build pile number that gives us the most
        # subsequent moves (might be zero)
        maxmoves = max(moves for pos, moves in result)
        result = [pos for pos, moves in result if moves == maxmoves]

        # Choose random build pile when multiple equal most subsequent moves
        pos = random.choice(result)
        return [(stock, 'stock', 'build:%d' % pos)]

    # Keep time to enforce calculation time limit
    start_time = time.time()

    # Keep moves of same length to calculate best move later
    result = []

    # Start with no moves
    queue = collections.deque()
    queue.append((stock, discards, hand, builds, []))

    # Let queue empty out before moving on to results with one card more
    # Prevent duplicate moves because of SB cards
    queueable = collections.deque()

    while queue:
        # Enforce calculation time limit
        if timeout and time.time() - start_time > timeout:
            # Return with no results
            raise CalculationTimeout

        stock, discards, hand, builds, moves = queue.popleft()
        unique_builds = list(enumerate_unique(builds))

        # Build pile numbers the stock card can be placed upon
        finalmoves = [pos for pos, card in unique_builds if fitson(card, stock)]

        # Stock card can be played, store results and wait for queue to empty
        if finalmoves:
            for pos in finalmoves:
                result.append(moves + [(stock, 'stock', 'build:%d' % pos)])

        # Don't look for result with more cards if stock can be played
        else:
            # Hand cards take precedence over discard cards
            for hand_card in set(hand):
                for pos, card in unique_builds:
                    if fitson(card, hand_card):
                        new_hand = pull(hand, hand_card)
                        new_builds = place(builds, pos, nextcard(card))
                        new_moves = moves + [(hand_card, 'hand', 'build:%d' % pos)]
                        queueable.append((stock, discards, new_hand, new_builds, new_moves))

            for discard_pos, discard_card in top_cards(discards):
                for pos, card in unique_builds:
                    if fitson(card, discard_card):
                        new_discards = pull_top(discards, discard_pos)
                        new_builds = place(builds, pos, nextcard(card))
                        new_moves = moves + [(discard_card, 'discard:%d' % discard_pos, 'build:%d' % pos)]
                        queueable.append((stock, new_discards, hand, new_builds, new_moves))

        # Queue has been emptied
        if not queue:
            # There are results (of equal length)
            if result:
                # Select result with most hand cards and least SB cards
                return best_moves(result)

            # No results, continue with next queue (one extra card played)
            queue = queueable
            queueable = collections.deque()


def most_moves(discards, hand, builds, timeout=None):
    """
    Returns the list of cards to move
    to get rid of as many cards as possible.

    Note: Six SB cards will be considered 'better'
    than five non-SB cards, because it plays more cards.
    """

    # Keep time to enforce calculation time limit
    start_time = time.time()

    # Start with no moves
    queue = collections.deque()
    queue.append((discards, hand, builds, [], [None, None, None, None]))

    # Keep moves of same length to calculate best move later
    result = []
    length = 0

    while queue:
        # Enforce calculation time limit
        if timeout and time.time() - start_time > timeout:
            # Return with no results
            raise CalculationTimeout

        discards, hand, builds, moves, top = queue.popleft()
        unique_builds = list(enumerate_unique(builds))

        # Store result if SB card was not placed on top of build pile [1]
        if moves and 'SB' not in top:
            # More moves than previously found, discard other results
            if len(moves) > length:
                result = []
                length = len(moves)
            result.append(moves)

        # Hand cards take precedence over discard cards
        for hand_card in set(hand):
            for pos, card in unique_builds:
                if fitson(card, hand_card):
                    new_hand = pull(hand, hand_card)
                    new_builds = place(builds, pos, nextcard(card))
                    new_moves = moves + [(hand_card, 'hand', 'build:%d' % pos)]

                    # Last hand card is an SB, allow it to pass through check 1 above
                    # Does not work is last *two* hand cards are SB
                    if not new_hand and hand_card == 'SB' and top[pos] != 'SB':
                        new_top = place(top, pos, nextcard(card))
                    else:
                        new_top = place(top, pos, hand_card)

                    queue.append((discards, new_hand, new_builds, new_moves, new_top))

        for discard_pos, discard_card in top_cards(discards):
            for pos, card in unique_builds:
                if fitson(card, discard_card):
                    new_discards = pull_top(discards, discard_pos)
                    new_builds = place(builds, pos, nextcard(card))
                    new_moves = moves + [(discard_card, 'discard:%d' % discard_pos, 'build:%d' % pos)]
                    new_top = place(top, pos, discard_card)
                    queue.append((new_discards, hand, new_builds, new_moves, new_top))

    # Select result with most hand cards and least SB cards
    if result:
        return best_moves(result)


def lucky_move(stock, discards, hand, builds):
    """
    Returns if any non-SB card can be played to a build pile.
    """
    unique_builds = list(enumerate_unique(builds))

    # Stock card
    for pos, card in unique_builds:
        if fitson(card, stock):
            return [(stock, 'stock', 'build:%d' % pos)]

    # Non-SB hand cards
    for hand_card in set(hand):
        if hand_card == 'SB':
            continue
        for pos, card in unique_builds:
            if fitson(card, hand_card):
                return [(hand_card, 'hand', 'build:%d' % pos)]

    # Non-SB discards
    for discard_pos, discard_card in top_cards(discards):
        if discard_card == 'SB':
            continue
        for pos, card in unique_builds:
            if fitson(card, discard_card):
                return [(discard_card, 'discard:%d' % discard_pos, 'build:%d' % pos)]

    # SB hand cards
    for hand_card in set(hand):
        if hand_card != 'SB':
            continue
        for pos, card in unique_builds:
            if fitson(card, hand_card):
                return [(hand_card, 'hand', 'build:%d' % pos)]

    # SB discards
    for discard_pos, discard_card in top_cards(discards):
        if discard_card != 'SB':
            continue
        for pos, card in unique_builds:
            if fitson(card, discard_card):
                return [(discard_card, 'discard:%d' % discard_pos, 'build:%d' % pos)]


def any_move(stock, discards, hand, builds):
    """
    Returns if any card can be played to a build pile.
    """
    for pile in builds:
        if fitson(pile, stock):
            return True

        if any(fitson(pile, card) for card in hand):
            return True

        if any(fitson(pile, card) for pos, card in top_cards(discards)):
            return True

    return False


def discard_move(discards, hand):
    """
    Determines which card to discard to which pile.
    """
    # Same card already in discards
    for discard_pos, discard_card in top_cards(discards):
        for card in set(hand):
            if card == discard_card:
                return [(card, 'hand', 'discard:%d' % discard_pos)]

    # Look for empty discard pile
    for discard_pos, discard_pile in enumerate(discards):
        if not discard_pile:
            # Choose random non-SB card
            normal_cards = [card for card in hand if card != 'SB']
            if normal_cards:
                card = random.choice(normal_cards)
                return [(card, 'hand', 'discard:%d' % discard_pos)]

    # Look for next card to 'count down'
    for discard_pos, discard_card in top_cards(discards):
        # Don't count down SB cards
        if discard_card == 'SB':
            continue

        for card in set(hand):
            if card == 'SB':
                continue
            if card + 1 == discard_card:
                return [(card, 'hand', 'discard:%d' % discard_pos)]

    # Choose random hand card and random discard pile
    card = random.choice(hand)
    discard_pos = random.randrange(4)
    return [(card, 'hand', 'discard:%d' % discard_pos)]


def calculate_move(stock, discards, hand, builds, timeout=None):
    """
    Calculates the next moves to make.

    May take up to a fixed number of seconds, otherwise
    player waits too long.
    """
    if timeout:
        start_time = time.time()

        # Find moves that get rid of the stock card
        try:
            moves = stock_moves(stock, discards, hand, builds, timeout=timeout)
            if moves:
                return moves
        except CalculationTimeout:
            # There might be subsequent moves we didn't have time to calculate.
            # Perform any move possible or discard
            return lucky_move(stock, discards, hand, builds) or discard_move(discards, hand)

        # Find moves that play the most number of cards
        remaining = start_time + timeout - time.time()
        try:
            moves = most_moves(discards, hand, builds, timeout=remaining)
            if moves:
                return moves

        except CalculationTimeout:
            # There might be subsequent moves we didn't have time to calculate.
            # Perform any move possible or discard
            return lucky_move(stock, discards, hand, builds) or discard_move(discards, hand)

        # Don't perform lucky_move as it will play SB cards that most_moves deemed bad to play
        return discard_move(discards, hand)

    return (
        stock_moves(stock, discards, hand, builds) or
        most_moves(discards, hand, builds) or
        discard_move(discards, hand)
    )
