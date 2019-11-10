import sys
import collections
import copy
from functools import reduce
import operator as op

from deuces import Deck, Evaluator



##########################################################################
######################## PROGRAM CONFIGURATION ###########################
##########################################################################
DEBUG = False




##########################################################################
######################## 3CP SPECIFIC CONSTANTS ##########################
##########################################################################
ALL_CARDS = ['2c', '2s', '2h', '2d', '3c', '3s', '3h', '3d', \
             '4c', '4s', '4h', '4d', '5c', '5s', '5h', '5d', \
             '6c', '6s', '6h', '6d', '7c', '7s', '7h', '7d', \
             '8c', '8s', '8h', '8d', '9c', '9s', '9h', '9d', \
             'Tc', 'Ts', 'Th', 'Td', 'Jc', 'Js', 'Jh', 'Jd', \
             'Qc', 'Qs', 'Qh', 'Qd', 'Kc', 'Ks', 'Kh', 'Kd', \
             'Ac', 'As', 'Ah', 'Ad']

ROYAL_FLUSH = 0
STRAIGHT_FLUSH = 1
QUADS = 2
FULL_HOUSE = 3
FLUSH = 4
STRAIGHT = 5
TRIPS = 6
TWO_PAIRS = 7
PAIR = 8
HIGH_CARD = 9

DIAMOND = 'd'
CLUB = 'c'
SPADE = 's'
HEART = 'h'

RAISE = True
BET = True
CALL = True
CHECK = False
FOLD = False





##########################################################################
##################### "INTERNAL" HELPER FUNCTIONS ########################
##########################################################################
def argmin(lst, f):
    """Returns the element e in lst for which f(e) is the minimum.
    Runtime:
        O(|lst|)

    Args:
        lst: List of elements
        f: Function in which we apply to each element in lst
    
    Example:
        >>> argmin([9,2,3], lambda x: x**2)
        2
    
    Returns:
        The element e for which f(e) is minimum
    """
    if len(lst) > 0:
        mapped = [f(e) for e in lst]
        idx = mapped.index(min(mapped))
        return lst[idx]
    raise ValueError("argmin() lst is an Empty Sequence")


def argmax(lst, f):
    """Returns the element e in lst for which f(e) is the minimum. 
    Runtime:
        O(|lst|)
    
    Args:
        lst: List of elements
        f: Function in which we apply to each element in lst
    
    Example:
        >>> argmax([9,2,3], lambda x: x**2)
        9
        
    Returns:
        The element e for which f(e) is maximum
    """
    if len(lst) > 0:
        mapped = [f(e) for e in lst]
        idx = mapped.index(max(mapped))
        return lst[idx]
    raise ValueError("argmax() lst is an Empty Sequence")


def rank_2_index(r):
    """Returns the nth highest of the rank.
    Runtime:
        O(1)
    
    Args:
        r: Either the rank of the card (i.e., '2', '3', ..., 'A') or the
        actual card (e.g. 'Ks')
    
    Example:
        >>> rank_2_index('2')
        0
        
        >>> rank_2_index('A')
        12
        
        Because Deuce is the lowest rank card and Ace is the highest rank card
    
    Returns:
        The number of ranks below r.
    """
    ranks = '23456789TJQKA'
    return ranks.index(r[0]) # just in case they have a suit


def index_2_rank(i):
    """Returns the rank in which exactly i other ranks are below it.
    Runtime:
        O(1)
    
    Args:
        i: An integer in the range 0 <= i < 13
    
    Example:
        >>> index_2_rank(0)
        '2'
        
        >>> rank_2_index(12)
        'A'
        
        Because Deuce is the lowest rank card and Ace is the highest rank card
    
    Returns:
        A rank (in the form of a string).
    """
    ranks = '23456789TJQKA'
    return ranks[i]


def rank_better_than(r1, r2):
    """In one card poker, does the first card beat the second?
    Runtime:
        O(1)
    
    Args:
        r1: Either a rank or a card (as string)
        r2: Either a rank or a card (as string)
    
    Example:
        >>> rank_better_than('A', 'K')
        True
        
        >>> rank_better_than('2', 'J')
        False
        
    Returns:
        A boolean indicating whether or not r1 beats r2.
    """
    return rank_2_index(r1) > rank_2_index(r2)


def rank_at_least(r1, r2):
    """Is the rank of first at least as good as the second?
    Runtime:
        O(1)
    
    Args:
        r1: Either a rank or a card (as string)
        r2: Either a rank or a card (as string)
    
    Example:
        >>> rank_at_least('A', 'A')
        True
        
        >>> rank_at_least('2', 'J')
        False
        
    Returns:
        A boolean indicating whether or not r1 is as good as r2.
    """
    return rank_2_index(r1) >= rank_2_index(r2)


def eval_int(hand, board):
    """Evaluate hand given list of two hero's card and list of card on board.
    [IDEALLY YOU NEVER CALL THIS FUNCTION. CALL eval_int() INSTEAD]
    Runtime:
        O(|board|^2)
    
    Args:
        hand: A list containing 2 cards (in integer representation)
        board: A list containing 5 cards (in integer representation)
    
    Returns:
        Three-tuple (n, category_number, category_name)
        where
            n: the number of how many other hand beats it
            category_number:
                9 => High Card
                8 => Pair
                7 => Two Pairs
                6 => Trips
                5 => Straight
                4 => Flush
                3 => Boat
                2 => Quads
                1 => Straight Flush
                0 => Royal Flush
            category_name: simply the name of the hand strength
    """
    evaluator = Evaluator()
    
    nth_best = evaluator.evaluate(hand, board)
    nth_class = evaluator.get_rank_class(nth_best)
    hand_class = evaluator.class_to_string(nth_class)
    
    if (nth_best == 1):
        return (nth_best, 0, 'Royal Flush')
    else:
        return (nth_best, nth_class, hand_class)


def eval_pretty(hand, board):
    """Evaluate hand given list of two hero's card and list of card on board.
    This function takes list of cards in 2 character string representation
    instead of integer representation.
    
    Runtime:
        O(|board|^2)
    
    Args:
        hand: A list containing 2 cards (2 character strings)
        board: A list containing 5 cards (again, card is a 2 character string)
    
    Returns:
        Three-tuple (n, category_number, category_name)
        where
            n: the number of how many other hand beats it
            category_number:
                9 => High Card
                8 => Pair
                7 => Two Pairs
                6 => Trips
                5 => Straight
                4 => Flush
                3 => Boat
                2 => Quads
                1 => Straight Flush
                0 => Royal Flush
            category_name: simply the name of the hand strength
    """
    # map pretty card to integer representing the card. h = hand, b = board
    from deuces import Card
    h = [Card.new(c) for c in hand]
    b = [Card.new(c) for c in board]
    
    return eval_int(h, b)


def settle_pretty_payout(hand, dealer, board, bet):
    """Return units won/loss.
    Assumption:
        We have bet unit of 1 on Ante and 1 on Blinds.
        bet is an integer 1, 2, or 4.
        This function is called only if the hero did not fold.
    
    Args:
        hand: A list containing 2 cards (string representation)
        dealer: A list containing 2 cards (string representation)
        board: A list containing (up to 5) cards (string representation)
        bet: An integer 0, 1, 2, or 4 where the meaning are
            4 => Hero Raised Pre-Flop
            2 => Hero Checked Pre-Flop, but Bets on the Flop
            1 => Hero Checked Pre-Flop and Flop, but Calls on the River
            0 => Hero Check, Check, Fold
    
    Examples:
        >>> settle_pretty_payout(['Qh', '9s'], ['8h', '2c'], ['Jh', 'Th', '3h', 'Ah', '2h'], 0)
        -2
        
        >>> settle_pretty_payout(['Qh', '9s'], ['8h', '2c'], ['Jh', 'Th', '3h', 'Ah', '2h'], 2)
        4.5
    
    Returns:
        An float indicating how much we won or loss.
    """
    # We Folded
    if bet == 0:
        return -2
    
    # Evaluate Dealer and Hero's Hands
    (d_score, d_rank, _) = eval_pretty(dealer, board)
    (h_score, h_rank, _) = eval_pretty(hand, board)
    
    if d_score == h_score: # push
        return 0
    elif d_score < h_score: # we lost
        if d_rank > 8:
            return -bet - 1
        else:
            return -bet - 2
    else: # we won
        payout = bet
        
        # ante payout
        if d_rank <= 8:
            payout += 1
        
        # blind payout
        if h_rank == 5: # straight
            payout += 1
        elif h_rank == 4: # flush
            payout += 1.5
        elif h_rank == 3: # full house
            payout += 3
        elif h_rank == 2: # quads
            payout += 10
        elif h_rank == 1: # straight flush
            payout += 50
        elif h_rank == 0: # royal flush
            payout += 500
        
        return payout


def is_pocket_pair(hand):
    """Given a hand, is it a pocket pair?
    Assumption:
        hand is a list of valid string card representation.
    
    Args:
        hand: A list containing 2 cards (string representation)
        
    Examples:
        >>> is_pocket_pair(['Qd', 'Qh'])
        True
        
        >>> is_pocket_pair(['As', 'Ks'])
        False
    
    Returns:
        A boolean
    """
    card1 = hand[0]
    card2 = hand[1]
    return card1[0] == card2[0]


def dominates(card1, card2):
    """In one card poker, does the first card beat the second?
    Runtime:
        O(1)
    
    Args:
        card1: Either a rank (as char) or a card (as string)
        card2: Either a rank (as char) or a card (as string)
    
    Example:
        >>> dominates('As', 'Ks')
        True
        
        >>> dominates('2', 'J')
        False
        
    Returns:
        A boolean indicating whether or not card1 beats card2 in One Card Poker.
    """
    return rank_better_than(card1[0], card2[0])


def is_suited(*args):
    """Given as arguments, a bunch of cards, are they suited?
    
    Args:
        *args: cards (string representation)
    
    Examples:
        >>> is_suited('Qd', 'Ah')
        False
        
        >>> hand_notation('Ah', 'Qh', '3h')
        True
    
    Returns:
        A boolean.
    """
    suits = {card[1] for card in args}
    return len(suits) == 1


def hand_notation(hand):
    """Given a hand, return its starting range notation.
    
    Args:
        hand: A list containing 2 cards (string representation)
    
    Examples:
        >>> hand_notation(['Qd', 'Ah'])
        'AQo'
        
        >>> hand_notation(['Ad', 'Qh'])
        'AQs'
    
    Returns:
        Return a 3 character string.
    """
    card1 = hand[0]
    card2 = hand[1]
    r_i1 = rank_2_index(card1[0])
    r_i2 = rank_2_index(card2[0])
    
    string = index_2_rank(max(r_i1, r_i2)) + index_2_rank(min(r_i1, r_i2))
    if is_suited(card1, card2):
        string += 's'
    else:
        string += 'o'
    
    return string


def sorted_hand_string(hand):
    """Gives string representing hand with bigger rank first.
    
    Args:
        hand: A list containing 2 cards (string representation)
    
    Examples:
        >>> sorted_hand_string(['Qd', 'Ah'])
        'Ah,Qd'
    
    Returns:
        A 5 characters string.
    """
    card1 = hand[0]
    card2 = hand[1]
    if dominates(card1, card2):
        return f"['{card1}', '{card2}']"
    else:
        return f"['{card2}', '{card1}']"


def is_dominated(hand, dealer, one_card_only = True):
    """Are we behind in 'Two Card Poker' with no board?
    Assumption:
        We don't care about suitedness.
    
    Args:
        hand: A list containing 2 cards (string representation)
        dealer: A list containing 2 cards (string representation)
        one_card_only: True => consider only dealer[0]. False => both dealer's
    
    Examples:
        >>> is_dominated(['Qd', 'Ah'], ['Ks', 'Qs'])
        False
    
    Returns:
        A boolean.
    """
    if one_card_only:
        return rank_2_index(hand[0]) < rank_2_index(dealer[0]) and rank_2_index(hand[1]) < rank_2_index(dealer[0])
    else:
        if is_pocket_pair(dealer) and not is_pocket_pair(hand):
            # dealer has made hand, we are on high card
            return True
        elif is_pocket_pair(hand) and not is_pocket_pair(dealer):
            # we have made hand, dealer on high card
            return False
        elif rank_2_index(hand[0]) < rank_2_index(dealer[0]) and rank_2_index(hand[1]) < rank_2_index(dealer[0]):
            # both hole smaller than dealer's first card
            return True
        elif rank_2_index(hand[0]) < rank_2_index(dealer[1]) and rank_2_index(hand[1]) < rank_2_index(dealer[1]):
            # both hole smaller than dealer's second card
            return True
        else:
            # should not reach here
            print("Potential error in is_dominated()")
            sys.exit()


def is_probably_dominated(hand, d):
    """Follows the definition of Probably Dominated in James Grosjean's
    Beyond Counting. 
    
    Args:
        hand: A list containing 2 cards (string representation)
        d: A 2 character string representing a card
    
    Examples:
        >>> is_probably_dominated(['9h', '3s'], '9d')
    
    Returns:
        True if one of your card matches the dealer's known card and your
        second card is inferrior (rank 6 or less). False otherwise.
    """
    card1 = hand[0]
    card2 = hand[1]
    
    if card1[0] == d[0] and not rank_at_least(card2[0], '7'):
        return True
    elif card2[0] == d[0] and not rank_at_least(card1[0], '7'):
        return True
    else:
        return False

def flush_draw(hand, board):
    """Indicate whether the hand has a flush draw. That is, if one more card
    of the modal suit were to come onto the board, the hand would become a flush.
    
    Args:
        hand: A list containing (up to 2) cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Examples:
        >>> flush_draw(['Ks', '9s'], ['Js', '4s', '2h'])
        (True, 's')
    
    Returns:
        Returns a two-tuple (b, s) where
            b is a boolean indicating the existence of 4-flush
            s is a character indicating the modal suit
    """
    cards = copy.deepcopy(hand) + copy.deepcopy(board)
    suits = [c[1] for c in cards]
    
    suit_counts = collections.Counter(suits)
    for suit, count in suit_counts.items():
        if count == 4 and has_suit_in_hand(suit, hand):
            return (True, suit)
    return (False, None)


def runner_runner_flush_draw(hand, board):
    """Indicate whether the hand has a runner-runner flush draw. That is, if two
    more card of the modal suit were to come onto the board, the hand would
    become a flush.

    [Does the same thing as flush_draw() but with one line changed]

    Assumptions:
        Though it does not make sense to use this function on a board of 5 cards,
        we use this function as a helper for live_3_flush(hand, )
    
    Args:
        hand: A list containing (up to 2) cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Examples:
        >>> runner_runner_flush_draw(['Th'], ['Js', '4h', '2h'])
        True
    
    Returns:
        Returns a two-tuple (b, s) where
            b is a boolean indicating the existence of 4-flush
            s is a character indicating the modal suit
    """
    cards = copy.deepcopy(hand) + copy.deepcopy(board)
    suits = [c[1] for c in cards]
    
    suit_counts = collections.Counter(suits)
    for suit, count in suit_counts.items():
        if count >= 3 and has_suit_in_hand(suit, hand):
            return (True, suit)
    return (False, None)


# has_three_flush(hand, board)
# indicates if there are 3 of same suit
def has_3_flush(hand, board):
    (result, _) = runner_runner_flush_draw(hand, board)
    return result


def live_4_flush(hand, d, board):
    """To determine if our flush draw is good. Or is our flush draw inferrior.
    Perhaps we don't even have a flush draw since we mis-read the suits. Use
    this function to find out if your draw is worth it!

    Remarks:
        To determine if the dealer has a live_4_flush instead of the hero,
        use this logic:
            flush_draw([d], board) and not live_4_flush(hand, d, board)
        where d is the known dealer hole card. Alternatively, you can replace
        [d] with dealer (for the entire dealer's hand if you have that info).
    
    Args:
        hand: A list containing (up to 2) cards (string representation)
        d: A 2 character string representing one of the dealer's known card
        board: A list containing (up to 5) cards (string representation)
    
    Examples:
        >>> live_4_flush(['Kh', '2h'], 'Qh' ,['8h', '7h', '2c'])
        True

        >>> live_4_flush(['Kh', 'Tc'], 'Ah' ,['8h', '7h', '2h'])
        False        
    
    Returns:
        Returns a boolean.
    """
    (hero_draw, hero_draw_suit) = flush_draw(hand, board)
    (dealer_draw, dealer_draw_suit) = flush_draw([d], board)
    if hero_draw and not dealer_draw:
        return True
    elif (not hero_draw) and dealer_draw:
        return False
    elif (not hero_draw) and (not dealer_draw):
        return False
    else: # does hero have stronger flush draw
        hero_cards = copy.deepcopy(hand) + copy.deepcopy(board)
        hero_ranks_for_draw = [c[0] for c in hero_cards if c[1] == hero_draw_suit]
        hero_ranks_for_draw.sort(key=rank_2_index, reverse=True)
        
        dealer_cards = [d] + copy.deepcopy(board)
        dealer_ranks_for_draw = [c[0] for c in dealer_cards if c[1] == dealer_draw_suit]
        dealer_ranks_for_draw.sort(key=rank_2_index, reverse=True)
        
        return rank_2_index(hero_ranks_for_draw[0]) > rank_2_index(dealer_ranks_for_draw[0])


def num_ranks_can_fill_straight(hand, board):
    """How many card ranks can complete a straight?
    
    Args:
        hand: A list containing (up to 2) cards (string representation)
        board: A list containing 3 cards (string representation)
    
    Returns:
        An integer in the range 0 <= i <= 13
    """
    cards = copy.deepcopy(hand) + copy.deepcopy(board)
    num_ranks = 0
    
    # characteristic is a binary array denoting absense/presense of a rank
    characteristic = ['0'] * 13
    for c in cards:
        characteristic[rank_2_index(c)] = '1'
    characteristic = [characteristic[-1]] + characteristic[:]
    
    # see if 2-K make a straight
    for i in range(1,13):
        characteristic_copy = copy.deepcopy(characteristic)
        characteristic_copy[i] = '1'
        characteristic_string = reduce(op.add, characteristic_copy)
        if '11111' in characteristic_string:
            num_ranks += 1
    
    # see if Ace make a straight
    characteristic_copy = copy.deepcopy(characteristic)
    characteristic_copy[0] = '1'
    characteristic_copy[13] = '1'
    characteristic_string = reduce(op.add, characteristic_copy)
    if '11111' in characteristic_string:
        num_ranks += 1
    
    return num_ranks
    

def is_open_ended_straight_draw(hand, board):
    """Is there 2 different rank that will complete a straight?
    Args:
        hand: A list containing (up to 2) cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        A boolean. A double gutter is also considered a OESD.
    """
    return num_ranks_can_fill_straight(hand, board) >= 2


def possible_straight_draw(hand, board):
    """Is there at least one rank that will complete a straight?
    Args:
        hand: A list containing (up to 2) cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        A boolean.
    """
    return num_ranks_can_fill_straight(hand, board) >= 1


def is_behind(hand, dealer, board):
    """Will we win/lose if showdown is right now?
    
    Assumptions:
        Assumes we know both dealer's hole card.
    
    Args:
        hand: A list containing 2 cards (string representation)
        dealer: A list containing 2 cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        True means hero is losing. False means hero is winning.
    """
    (d_score, _, _) = eval_pretty(dealer, board)
    (h_score, _, _) = eval_pretty(hand, board)
    
    return d_score <= h_score


def is_ahead(hand, dealer, board):
    """Will we win/lose if showdown is right now?
    
    Assumptions:
        Assumes we know both dealer's hole card.
    
    Args:
        hand: A list containing 2 cards (string representation)
        dealer: A list containing 2 cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        True means hero is winning. False means hero is losing.
    """
    return not is_behind(hand, dealer, board)


def worst_possible_made_hand(d, board, dead=None):
    """Returns the best nth hand ranking possible as well as its category.
    Args:
        d: Dealer's known card
        board: A list containing (up to 5) cards (string representation)
        dead: A list of cards we know cannot be dealer's second card.
    
    Examples:
        >>> best_possible_hand_rating(d = '5d', board = ['3d', 'Jd', '2d'], dead = ['Ah', 'Kh'])
        (689, 4, 'Flush')
    
    Returns:
        Three-tuple (n, category_number, category_name)
        where
            n: the number of how many other hand beats it
                Royal flush (best hand possible)          => 1
                7-5-4-3-2 unsuited (worst hand possible)  => 7462
            category_number:
                9 => High Card
                8 => Pair
                7 => Two Pairs
                6 => Trips
                5 => Straight
                4 => Flush
                3 => Boat
                2 => Quads
                1 => Straight Flush
                0 => Royal Flush
            category_name: simply the name of the hand strength
    """
    remaining_cards = copy.deepcopy(ALL_CARDS)
    
    if dead is None:
        dead = []
    
    # remove dead cards from remaining_cards... remaining_card are possible second dealer card
    for c in dead:
        remaining_cards.remove(c)
    for c in board:
        remaining_cards.remove(c)
    remaining_cards.remove(d)
    
    # enumerate all hands, while keeping track of the worst one yet
    d_score = -1
    d_rank = -1
    d_category = ''
    for c in remaining_cards:
        (d_score_new, d_rank_new, d_category_new) = eval_pretty([d, c], board)
        if d_score_new > d_score:
            d_score = d_score_new
            d_rank = d_rank_new
            d_category = d_category_new
    
    return (d_score, d_rank, d_category)


def best_possible_made_hand(d, board, dead=None):
    """Returns the best nth hand ranking possible as well as its category.
    Args:
        d: Dealer's known card
        board: A list containing (up to 5) cards (string representation)
        dead: A list of cards we know cannot be dealer's second card.
    
    Examples:
        >>> best_possible_hand_rating(d = '5d', board = ['3d', 'Jd', '2d'], dead = ['Ah', 'Kh'])
        (689, 4, 'Flush')
    
    Returns:
        Three-tuple (n, category_number, category_name)
        where
            n: the number of how many other hand beats it
                Royal flush (best hand possible)          => 1
                7-5-4-3-2 unsuited (worst hand possible)  => 7462
            category_number:
                9 => High Card
                8 => Pair
                7 => Two Pairs
                6 => Trips
                5 => Straight
                4 => Flush
                3 => Boat
                2 => Quads
                1 => Straight Flush
                0 => Royal Flush
            category_name: simply the name of the hand strength
    """
    remaining_cards = copy.deepcopy(ALL_CARDS)
    
    if dead is None:
        dead = []
    
    # remove dead cards from remaining_cards... remaining_card are possible second dealer card
    for c in dead:
        remaining_cards.remove(c)
    for c in board:
        remaining_cards.remove(c)
    remaining_cards.remove(d)
    
    # enumerate all hands, while keeping track of the worst one yet
    d_score = 99999999999
    d_rank = 99999999999
    d_category = ''
    for c in remaining_cards:
        (d_score_new, d_rank_new, d_category_new) = eval_pretty([d, c], board)
        if d_score_new < d_score:
            d_score = d_score_new
            d_rank = d_rank_new
            d_category = d_category_new
    
    return (d_score, d_rank, d_category)


def is_behind_given_one_dealer_card(hand, d, board):
    """We assume that the dealer's second card is the worst possible for her.
    Are we still behind?
    
    Args:
        hand: A list containing 2 cards (string representation)
        d: Dealer's known card
        board: A list containing (up to 5) cards (string representation)
        
    Returns:
        A boolean. True if we should not put money into pot. False if we should
        put money into pot.
    """
    (d_score, _, _) = worst_possible_made_hand(d, board, dead = hand)
    (h_score, _, _) = eval_pretty(hand, board)
    
    return d_score < h_score


def is_paired_board(board):
    """Is board paired?
    Assumption:
        Input is valid: formatting, no duplicate card.
    
    Args:
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        A boolean.
    """
    ranks = [c[0] for c in board]
    rank_collection = set(ranks)
    return len(rank_collection) < len(board)


def is_trips_on_board(board):
    """Does board have trips?
    Assumption:
        Input is valid: formatting, no duplicate card.
    
    Args:
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        A boolean.
    """
    rank_count = collections.Counter()
    for c in board:
        rank_count[c[0]] += 1

    return 3 in rank_count.values()


def get_kicker_for_trips_using_one_hole(hand, board):
    """Kicker
    Assumption:
        There is at least a pair on board. You have trips (or even 'two trips').
        We are only using one of two hole to build the trips.
    
    Args:
        hand: A list containing 2 cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        A character representing a rank.
    """
    # find the pair(s) on board
    rank_count = collections.Counter()
    for c in board:
        rank_count[c[0]] += 1
        
    possible_pairs = []
    for rnk, occurrence in rank_count.items():
        if occurrence >= 2:
            possible_pairs.append(rnk)
    
    # remove that from hand, remaining is the kicker
    possible_kickers = []
    hand_copy = copy.deepcopy(hand)
    for r in possible_pairs:
        if r == hand[0][0]:
            possible_kickers.append(hand[1][0])
        elif r == hand[1][0]:
            possible_kickers.append(hand[0][0])
    
    if len(possible_kickers) > 0:
        return argmin(possible_kickers, rank_2_index)
    else:
        return '2'


def get_kicker_for_two_pairs(hand, board):
    """Kicker
    Assumption:
        There is at least a pair on board. You have trips (or even 'two trips').
        We are only using one of two hole to build the trips.
    
    Args:
        hand: A list containing 2 cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        A character representing a rank.
    """
    two_pairs_ranks = sorted(get_pairs(hand, board[:3]), key=rank_2_index, reverse=True)
    lst = hand + board
    lst_pairs_removed = [c[0] for c in lst if c[0] not in two_pairs_ranks]
    return sorted(lst_pairs_removed, key=rank_2_index, reverse=True)[0]



def get_pairs(hand, board):
    """List of ranks that occur twice in hand+board.
    Assumption:
        No duplicate cards. Board has at least 3 cards.
    
    Args:
        hand: A list containing (up to 2) cards (string representation)
        board: A list containing (up to 5) cards (string representation)
    
    Returns:
        List of ranks that occur twice. May not be sorted.
    """
    # count rank occurrence
    rank_count = collections.Counter()
    lst = hand + board
    for c in lst:
        rank_count[c[0]] += 1
    
    # pairs
    possible_pairs = []
    for rnk, occurrence in rank_count.items():
        if occurrence == 2:
            possible_pairs.append(rnk)
    return possible_pairs


def card_rank_is_in_hand(r, hand):
    """Does your hand have a card of rank r?
    Args:
        r: A rank or card (string representation)
        hand: A list containing (up to 2) cards (string representation)
    
    Examples:
        >>> card_rank_is_in_hand('A', ['Ks', 'Kd'])
        False
    
    Returns:
        Boolean.
    """
    rank1 = hand[0][0]
    rank2 = hand[1][0]
    return r[0] == rank1 or r[0] == rank2


def has_rank_or_better_in_hand(r, hand):
    """Does your hand have a card of rank r or better?
    Args:
        r: A rank or card (string representation)
        hand: A list containing (up to 2) cards (string representation)
    
    Examples:
        >>> has_rank_or_better_in_hand('A', ['Ks', 'Kd'])
        False
    
    Returns:
        Boolean.
    """
    r_i = rank_2_index(r)
    r_i1 = rank_2_index(hand[0][0])
    r_i2 = rank_2_index(hand[1][0])
    return r_i1 >= r_i or r_i2 >= r_i


def has_suit_in_hand(s, hand):
    """Do you have a card of suit s? This might be useful if we are designing
    a bluff catcher.

    Args:
        s: A character indicating suit (i.e., 'd', 'h', 's', or 'c')
        hand: A list containing (up to 2) cards (string representation)

    Examples:
        >>> has_suit_in_hand('h', ['Ah'])
        True

        >>> has_suit_in_hand('h', ['As', 'Kd'])
        False

    Returns:
        A boolean.
    """
    suits = { c[1] for c in hand }
    return s in suits



def dealer_outs(hand, d, board, other_dead_cards = None):
    """Gives a list of what we do not want to see as the dealer's second hole
    card. Usually, this function is called during a river decision.

    Args:
        hand: A list containing 2 cards (in string representation)
        d: A 2-character string denoting a card
        board: A list containing (up to 5) cards (in string representation)

    Examples:
        >>> 

    Returns:
        Returns a 2-tuple (outs, probability) where
            outs is a list of cards
            probability is the probability dealer will get one of these outs
        In otherwords, probability is probability that hero will lose.
        (Remember to take the complement if calculating probability of winning)
    """
    if other_dead_cards is None:
        other_dead_cards = []

    # remaining_cards is a list of all possible second hole card
    remaining_cards = copy.deepcopy(ALL_CARDS)
    for c in other_dead_cards:
        remaining_cards.remove(c)
    for c in board:
        remaining_cards.remove(c)
    for c in hand:
        remaining_cards.remove(c)
    remaining_cards.remove(d)

    # hero's hand status
    (hero_nth_rank, hero_hand_category_number, _) = eval_pretty(hand, board)

    # enumerate all of these possibilities and collect the "bads"
    outs = []
    for c in remaining_cards:
        (dealer_nth_rank, dealer_hand_category_number, _) = eval_pretty([d, c], board)
        if dealer_nth_rank < hero_nth_rank:
            outs.append(c)

    return (outs, len(outs) / len(remaining_cards))



    # enumerate all hands, while keeping track of the worst one yet
    # d_score = -1
    # d_rank = -1
    # d_category = ''
    # for c in remaining_cards:
    #     (d_score_new, d_rank_new, d_category_new) = eval_pretty([d, c], board)
    #     if d_score_new > d_score:
    #         d_score = d_score_new
    #         d_rank = d_rank_new
    #         d_category = d_category_new
    
    # return (d_score, d_rank, d_category)







##########################################################################
###################### DECISION MAKING FUNCTIONS #########################
##########################################################################
def ono_preflop(hand, dealer, board):
    """This function returns True if the AP should Raise preflop and False if the AP should check.
       Even though this function takes in the entire board, it only consider one of the card: the first flop card.
       
       Similarly, it only looks at the first dealer's hole card even though she has two.
    """
    RAISE = True
    BET = True
    CALL = True
    CHECK = False
    FOLD = False
    hole_dealer = dealer[0]
    hole_flop = board[0]
    
    rule = ''
    pre_flop_action_computer = CHECK
    card_ranks = '23456789TJQKA'
    
    # PREFLOP ONO... may need to consider the dealer's hole card
    if hand[0][0] == hand[1][0] == hole_flop[0]: # you have trips
        rule = "Rule One 'n' One (Pre-Flop) (1): You got Trips"
        pre_flop_action_computer = RAISE
    elif (is_pocket_pair(hand) and hole_dealer[0] != hole_flop[0]): # you have pocket pair and dealer doesnt have a pair
        rule = "Rule One 'n' One (Pre-Flop) (2): You have a pocket pair and dealer doesn't have a pair"
        pre_flop_action_computer = RAISE
    elif is_pocket_pair(hand) and (hole_dealer[0] == hole_flop[0]) and dominates(hand[0], hole_dealer): # you have pocket pair and dealer has a pair but your pair beats hers
        rule = "Rule One 'n' One (Pre-Flop) (3): You have a pocket pair and flop card does give dealer a pair... BUT your pair beats hers"
        pre_flop_action_computer = RAISE
    elif hand[0][0] == hole_flop[0] and card_ranks.index(hand[1][0]) >= card_ranks.index('T') and (hole_dealer[0] == hole_flop[0]): # both you and dealer has pair but you have 10 kicker or better
        rule = "Rule One 'n' One (Pre-Flop) (4): You and dealer has pair, but your kicket is T or higher"
        pre_flop_action_computer = RAISE
    elif hand[1][0] == hole_flop[0] and card_ranks.index(hand[0][0]) >= card_ranks.index('T') and (hole_dealer[0] == hole_flop[0]): # both you and dealer has pair but you have 10 kicker or better
        rule = "Rule One 'n' One (Pre-Flop) (5): You and dealer has pair, but your kicket is T or higher"
        pre_flop_action_computer = RAISE
    elif (hand[0][0] == hole_flop[0] or hand[1][0] == hole_flop[0]) and (hole_dealer[0] != hole_flop[0]): # you have pair and dealer doesnt
        rule = "Rule One 'n' One (Pre-Flop) (6): You have pair and dealer doesn't"
        pre_flop_action_computer = RAISE
    elif is_pocket_pair([hole_dealer, hole_flop]) and (hand[0][0] != hole_flop[0] and hand[1][0] != hole_flop[0]) and not is_pocket_pair(hand): # dealer has pair and you dont
        rule = "Rule One 'n' One (Pre-Flop) (7): Dealer has pair and you dont"
        pre_flop_action_computer = CHECK
    else:
        rule = "Rule One 'n' One (Pre-Flop) (999999999999): RESORT TO OCR PRE-FLOP RULES"
        pre_flop_action_computer = None

    # EXTRAS
    if DEBUG:
        print(rule)

    return pre_flop_action_computer


def ocr_preflop(hand, dealer, board):
    """This function returns True if the AP should Raise preflop and False if the AP should check.
       Even though this function takes in the entire board, it does not consider any card there.
       
       Similarly, it only looks at the first dealer's hole card even though she has two.
       
       [When playing an ONO game, please run ono_preflop() first before running this function]
    """
    RAISE = True
    BET = True
    CALL = True
    CHECK = False
    FOLD = False
    hole_dealer = dealer[0]
    hole_flop = board[0]
    
    rule = ''
    pre_flop_action_computer = CHECK
    card_ranks = '23456789TJQKA'
    
    
    # PREFLOP OCR... completely ignore the dealer's hole card even though we may have that information
    if is_pocket_pair(hand) and card_ranks.index(hand[0][0]) >= card_ranks.index('7'): # pocket pair 77+
        rule = "Rule One Card Reloaded (Pre-Flop) (1): Pocket 77+ or higher"
        pre_flop_action_computer = RAISE
    elif is_pocket_pair(hand) and card_ranks.index(hand[0][0]) >= card_ranks.index(hole_dealer[0]): # pocket pair 66- and dealer has no overcard
        rule = "Rule One Card Reloaded (Pre-Flop) (2): Pocker 66- and dealer has no over card"
        pre_flop_action_computer = RAISE
    elif card_ranks.index(hand_notation(hand)[0]) >= card_ranks.index('T') and card_ranks.index(hand_notation(hand)[1]) >= card_ranks.index(hole_dealer[0]):
        rule = "Rule One Card Reloaded (Pre-Flop) (3): Raise Tx, Jx, Qx, Kx, and Ax if D <= x (Page 364 of Beyond Counting)"
        pre_flop_action_computer = RAISE
    elif card_ranks.index(hand_notation(hand)[0]) <= card_ranks.index('9'):
        rule = "Rule One Card Reloaded (Pre-Flop) (4): Check 9x or worse"
        pre_flop_action_computer = CHECK
    else:
        rule = "Rule One Card Reloaded (Pre-Flop) (5): You have Hx and dealer has D. Check Beyond Counting page 364 for the table of decision."
        H = hand_notation(hand)[0]
        x = hand_notation(hand)[1]
        D = hole_dealer[0]
        if dominates(D, H):
            rule = "Rule One Card Reloaded (Pre-Flop) (5-1): You are definitely dominated by the dealer's high card"
            pre_flop_action_computer = CHECK
        elif H == 'Q': # starting here until the end of the one-card-reloaded section, we assume H >= D
            if is_suited(hand[0], hand[1], hole_flop):
                if card_ranks.index(x) < card_ranks.index(D) < card_ranks.index(H) and card_ranks.index(x) >= card_ranks.index('8'):
                    pre_flop_action_computer = RAISE
                elif D == H and card_ranks.index(x) >= card_ranks.index('9'):
                    pre_flop_action_computer = RAISE
                else:
                    pre_flop_action_computer = CHECK
            else:
                if card_ranks.index(x) < card_ranks.index(D) < card_ranks.index(H) and card_ranks.index(x) >= card_ranks.index('T'):
                    pre_flop_action_computer = RAISE
                elif D == H and card_ranks.index(x) >= card_ranks.index('T'):
                    pre_flop_action_computer = RAISE
                else:
                    pre_flop_action_computer = CHECK
        elif H == 'K':
            if is_suited(hand[0], hand[1], hole_flop):
                if card_ranks.index(x) < card_ranks.index(D) < card_ranks.index(H) and card_ranks.index(x) >= card_ranks.index('6'):
                    pre_flop_action_computer = RAISE
                elif D == H and card_ranks.index(x) >= card_ranks.index('9'):
                    pre_flop_action_computer = RAISE
                else:
                    pre_flop_action_computer = CHECK
            else:
                if card_ranks.index(x) < card_ranks.index(D) < card_ranks.index(H) and card_ranks.index(x) >= card_ranks.index('T'):
                    pre_flop_action_computer = RAISE
                elif D == H and card_ranks.index(x) >= card_ranks.index('T'):
                    pre_flop_action_computer = RAISE
                else:
                    pre_flop_action_computer = CHECK
        elif H == 'A':
            if is_suited(hand[0], hand[1], hole_flop):
                if card_ranks.index(x) < card_ranks.index(D) < card_ranks.index(H) and card_ranks.index(x) >= card_ranks.index('2'):
                    pre_flop_action_computer = RAISE
                elif D == H and card_ranks.index(x) >= card_ranks.index('9'):
                    pre_flop_action_computer = RAISE
                else:
                    pre_flop_action_computer = CHECK
            else:
                if card_ranks.index(x) < card_ranks.index(D) < card_ranks.index(H) and card_ranks.index(x) >= card_ranks.index('7'):
                    pre_flop_action_computer = RAISE
                elif D == H and card_ranks.index(x) >= card_ranks.index('T'):
                    pre_flop_action_computer = RAISE
                else:
                    pre_flop_action_computer = CHECK
        else:
            pre_flop_action_computer = CHECK
            # print("Cannot find a preflop action")
            # print(f"Hand {hand}")
            # print(f"Board {board}")
            # print(f"Dealer {dealer}")
    
    # EXTRAS
    if DEBUG:
        print(rule)

    return pre_flop_action_computer


def ocr_flop(hand, dealer, board):
    """This function returns True if the AP should Bet on the flop and False if the AP should check.
       Even though this function takes in the entire board, it only consider the flop: the first three card.
       
       Though it takes the dealer's hand, it does not consider it at all!
       
       [This should be called after you have called the preflop functions with the same parameters!]
    """
    RAISE = True
    BET = True
    CALL = True
    CHECK = False
    FOLD = False
    
    hole_dealer = dealer[0]
    D = hole_dealer[0]
    H = hand_notation(hand)[0]
    x = hand_notation(hand)[1]
    
    rule = ''
    flop_action_computer = CHECK
    card_ranks = '23456789TJQKA'
    
    # from now on, we assume that we have not determined that we are behind yet!
    (h_score, h_rank, _) = eval_pretty(hand, board[:3])
    (worst_d_score, worst_d_rank, _) = worst_possible_made_hand(dealer[0], board[:3], dead = hand)
    (best_d_score, best_d_rank, _) = best_possible_made_hand(dealer[0], board[:3], dead = hand)

    # FLOP
    if is_behind_given_one_dealer_card(hand, dealer[0], board[:3]):
        rule = "Rule One Card Reloaded (Flop) (1): Dealer's single known card tells us that we are behind!"
        flop_action_computer = CHECK
    
    elif h_rank <= 5: # straight or better
        rule = "Rule One Card Reloaded (Flop) (2): Bet with any straight or higher!"
        flop_action_computer = BET
    elif h_rank == 6: # three of a kind
        rule = "Rule One Card Reloaded (Flop) (3): If you have trips..."
        if worst_d_rank > 6: # dealer does not have trips
            rule += "(3-1) bet if dealer has less than trips"
            flop_action_computer = BET
        elif is_trips_on_board(board[:3]) and ((card_ranks.index(hand[0][0]) >= card_ranks.index('Q')) or (card_ranks.index(hand[1][0]) >= card_ranks.index('Q'))):
            rule += "(3-2) the trips is on the board and you have a Q kicker or better!"
            flop_action_computer = BET
        elif worst_d_rank == 6 and h_rank == 6 and is_paired_board(board[:3]):
            kicker = get_kicker_for_trips_using_one_hole(hand, board[:3])
            if rank_2_index(kicker) >= rank_2_index('T'):
                rule += "(3-3.1) and the dealer has trips BUT your kicker is T or better"
                flop_action_computer = BET
            else:
                rule += "(3-3.2) and the dealer has trips BUT you are probably dominated (low kicker)"
                flop_action_computer = CHECK
    elif h_rank == 7: # two pairs
        rule = "Rule One Card Reloaded (Flop) (4): If you have two pairs..."
        if worst_d_rank > 7: # dealer less than two pairs
            board_pairs = get_pairs([], board[:3])
            if not is_pocket_pair(hand) and not is_paired_board(board[:3]):
                rule += "(4-1.1) using both card and dealer has less than two pairs"
                flop_action_computer = BET
            elif is_pocket_pair(hand) and (len(board_pairs) == 1 and rank_2_index(hand[0]) < rank_2_index(board_pairs[0])) and (rank_2_index(hand[0]) < rank_2_index(D)):
                rule += "(4-1.3) UNLESS you hold pocket pair pp that is under pair to the board (and also lower than dealer's hole)"
                flop_action_computer = CHECK
            else:
                rule += "(4-1.2) with a over pocket pair pp or p >= D"
                flop_action_computer = BET
        elif worst_d_rank == 7: # dealer has two pair
            dealer_two_pairs = list(sorted(get_pairs([hole_dealer], board[:3]), key=rank_2_index, reverse=True))
            hero_two_pairs = list(sorted(get_pairs(hand, board[:3]), key=rank_2_index, reverse=True))
            kicker = get_kicker_for_two_pairs(hand, board[:3])
            kicker_is_on_board = not card_rank_is_in_hand(kicker, hand)

            if dealer_two_pairs == hero_two_pairs: # we both have same two pair
                rule += "(4-2.1) and dealer has same two pair"
                if rank_2_index(kicker) > rank_2_index('T') and not kicker_is_on_board: # kicker is not shared
                    rule += "(4-2.1.1) and YOUR kicker is >= T"
                    flop_action_computer = BET
                elif rank_2_index(kicker) > rank_2_index('T') and kicker_is_on_board: # kicker is shared
                    rule += "(4-2.1.2) and BOARD's kicker is >= T"
                    flop_action_computer = BET
                else:
                    rule += "(4-2.1.3) but probably dominated"
                    flop_action_computer = CHECK
            else: # we both have two pairs but different
                if dominates(hero_two_pairs[0], dealer_two_pairs[0]) or (hero_two_pairs[0] == dealer_two_pairs[0] and dominates(hero_two_pairs[1], dealer_two_pairs[1])):
                    print("[WARNING]: Computer/player possibly made mistake by checking pre-flop")
                    rule += "(4-2.2.1) but our two pairs is better. Better bet late than never!"
                    flop_action_computer = BET
                else:
                    print("[WARNING]: We are behind and should not reach here. Rule (1) should have taken care of it.")
                    rule += "(4-2.2.2) but our two pairs is inferrior. :'("
                    flop_action_computer = CHECK
    elif h_rank == 8: # pair
        rule = "Rule One Card Reloaded (Flop) (5): If you have a pair..."
        (dealer_is_drawing_flush, _) = flush_draw([hole_dealer], board[:3])
        if dealer_is_drawing_flush and (not live_4_flush(hand, hole_dealer, board[:3])):
            rule += "(5-0) BUT dealer has live-4-flush"
            flop_action_computer = CHECK
        elif is_open_ended_straight_draw([hole_dealer], board[:3]):
            rule += "(5-1) BUT dealer has open ended straight draw OESD"
            flop_action_computer = CHECK
        elif is_paired_board(board[:3]) and live_4_flush(hand, hole_dealer, board[:3]):
            rule += "(5-2) pair on board and hero has live-4-flush"
            flop_action_computer = BET
        elif is_paired_board(board[:3]) and (card_rank_is_in_hand('A', hand) or card_rank_is_in_hand('K', hand)) and not possible_straight_draw([hole_dealer], board[:3]):
            rule += "(5-3) pair on board and hero has Ace or King"
            flop_action_computer = BET
        elif is_paired_board(board[:3]) and is_open_ended_straight_draw(hand, board[:3]) and has_rank_or_better_in_hand('T', hand) and (not possible_straight_draw([hole_dealer], board[:3])) and (not is_probably_dominated(hand, hole_dealer)):
            rule += "(5-4) pair on board, BET an OESD when you have T or better in the hole and dealer has no straight potential"
            flop_action_computer = BET
        elif not is_paired_board(board[:3]) and not is_pocket_pair(hand):
            hero_pair_list = list(sorted(get_pairs(hand, board[:3]), key=rank_2_index, reverse=True))
            dealer_pair_list = list(sorted(get_pairs([hole_dealer], board[:3]), key=rank_2_index, reverse=True))
            kicker = [c[0] for c in hand if c[0] not in hero_pair_list][0]
            if len(dealer_pair_list) > 0 and dealer_pair_list[0] == hero_pair_list[0] and not rank_better_than(kicker, '9'):
                rule += "(5-5.2) UNLESS dealer has same pair and your kicker <= 9"
                flop_action_computer = CHECK
            elif num_ranks_can_fill_straight([hole_dealer], board[:3]) > num_ranks_can_fill_straight(hand, board[:3]) and dominates(D, hero_pair_list[0]):
                rule += "(5-5.3) UNLESS dealer has more straight draws than you and hole-card overcard to your pair."
                flop_action_computer = CHECK
            else:
                rule += "(5-5.1) bet pair that uses single hole card"
                flop_action_computer = BET
    elif h_rank == 9: # nothing (or high card)
        rule = "Rule One Card Reloaded (Flop) (6): If you have nothing..."
        (dealer_is_drawing_flush, _) = flush_draw([hole_dealer], board[:3])
        if is_probably_dominated(hand, hole_dealer):
            rule += "(6-0) but you are probably dominated... just check"
            flop_action_computer = CHECK
        elif live_4_flush(hand, hole_dealer, board[:3]) and has_rank_or_better_in_hand('8', hand):
            rule += "(6-1) you have live-4-flush and 8+ in the hole"
            flop_action_computer = BET
        elif is_open_ended_straight_draw(hand, board[:3]) and has_rank_or_better_in_hand('T', hand) and (not dealer_is_drawing_flush) and (not possible_straight_draw([hole_dealer], board[:3])):
            rule += "(6-2) you have OESD with T+ in the hole AND dealer has no possible draws"
            flop_action_computer = BET
        elif card_rank_is_in_hand('A', hand) and rank_better_than('A', D) and (not dealer_is_drawing_flush) and (not possible_straight_draw([hole_dealer], board[:3])) and (not has_3_flush([hole_dealer], board[:3])):
            rule += "(6-3) you have Ace and D < Ace. Dealer has no draws."
            flop_action_computer = BET
        else:
            rule += "(6-999999999) you should just check"
            flop_action_computer = CHECK
    else:
        print("POSSIBLE ERROR IN ocr_flop()")
        sys.exit()

    # EXTRAS
    if DEBUG:
        print(rule)

    return flop_action_computer


def ocr_river(hand, dealer, board, other_dead_cards = None):
    """This function returns True if the AP should Call on the river and False if the AP should FOLD.
       
       Though it takes the dealer's hand, it does not consider it at all!
       
       [This should be called after you have called the flop functions with the same parameters!]
    """
    if other_dead_cards is None:
        other_dead_cards = []

    RAISE = True
    BET = True
    CALL = True
    CHECK = False
    FOLD = False

    hole_dealer = dealer[0]
    D = hole_dealer[0]
    H = hand_notation(hand)[0]
    x = hand_notation(hand)[1]
    
    rule = ''
    river_action_computer = FOLD
    card_ranks = '23456789TJQKA'


    # from now on, we assume that we have not determined that we are behind yet!
    (h_score, h_rank, _) = eval_pretty(hand, board)
    (worst_d_score, worst_d_rank, _) = worst_possible_made_hand(dealer[0], board, dead=(hand + other_dead_cards))
    (best_d_score, best_d_rank, _) = best_possible_made_hand(dealer[0], board, dead=(hand + other_dead_cards))

    if is_behind_given_one_dealer_card(hand, dealer[0], board):
        rule = "Rule One Card Reloaded (River) (1): Dealer's single known card tells us that we are behind!"
        river_action_computer = FOLD

    elif h_rank <= STRAIGHT:
        rule = "Rule One Card Reloaded (River) (2): Call if you have straight or better."
        river_action_computer = CALL

    else:
        (outs, p_bad) = dealer_outs(hand, hole_dealer, board, other_dead_cards)
        p_good = 1 - p_bad
        if DEBUG:
            print(f"Dealer's Outs: {outs}")
            print(f"Probability of Not Losing if we call: {p_good}  ({len(outs)} outs)")
        
        if p_good >= 0.2:
            rule = "Rule One Card Reloaded (River) (3-1): You are ahead and dealer has < 35 outs."
            river_action_computer = CALL
        else:
            rule = "Rule One Card Reloaded (River) (3-2): Dealer has >= 35 outs."
            river_action_computer = FOLD

    # EXTRAS
    if DEBUG:
        print(rule)

    return river_action_computer





##########################################################################
####################### RUN ONE GAME FUNCTIONS ###########################
##########################################################################
def ono_game(manual=False):
    # setup for one round of UTH
    deck = Deck()
    hand = deck.draw(2)
    dealer = deck.draw(2)
    board = deck.draw(5)
    result_computer = 0
    result_human = 0

    if manual:
        print(f"\n==========================================================")
        print(f"==========================================================\n")

    if DEBUG:
        print(f"[DEBUG MESSAGE]")
    
    # PRE-FLOP: try ONO rule first, if none found, try OCR
    pre_flop_action_computer = ono_preflop(hand, dealer, board)
    if pre_flop_action_computer is None:
        pre_flop_action_computer = ocr_preflop(hand, dealer, board)
    
    # FLOP: if we already raise preflop, just settle payment. otherwise decide what to do
    if pre_flop_action_computer: # we raised pre-flop... just compute result and be done with this round
        result_computer = settle_pretty_payout(hand, dealer, board, 4)
    else: # we checked pre-flop... onto the flop
        flop_action_computer = ocr_flop(hand, dealer, board)
        if flop_action_computer: # we bet on flop
            result_computer = settle_pretty_payout(hand, dealer, board, 2)
        else: # RIVER: we check on flop... onto the river
            river_action_computer = ocr_river(hand, dealer, board)
            if river_action_computer: # we call on river
                result_computer = settle_pretty_payout(hand, dealer, board, 1)
            else: # we fold on river
                result_computer = settle_pretty_payout(hand, dealer, board, 0)

    if DEBUG:
        print(f"[/END DEBUG MESSAGE]")

    # Practice Mode
    if manual:
        print()
        print(f"\n[STARTING HAND]")
        player_made_mistake = False

        # PRE-FLOP
        print(f"----------------------- Pre-flop -----------------------")
        hole_dealer = dealer[0]
        hole_flop = board[0]
        print(f"Hero Hand: {sorted_hand_string(hand)}")
        print(f"Dealer Hole: {hole_dealer}")
        print(f"Board: {board[:1]}")
        pre_flop_action_human = bool(int(input("0-Check or 1-Raise >>> ")))
        if pre_flop_action_human != pre_flop_action_computer:
            print("!!!!!!!!!!!!!!!!!YOU MADE A PREFLOP ERROR!!!!!!!!!!!!!!!!!")
            player_made_mistake = True
        if pre_flop_action_human:
            result_human = settle_pretty_payout(hand, dealer, board, 4)
            
        # FLOP
        if not pre_flop_action_human and not player_made_mistake:
            print(f"\n----------------------- Flop -----------------------")
            flop = board[0:3]
            print(f"Hero Hand: {sorted_hand_string(hand)}")
            print(f"Dealer Hole: {hole_dealer}")
            print(f"Board: {flop}")
            flop_action_human = bool(int(input("0-Check or 1-Bet >>> ")))
            if flop_action_human != flop_action_computer:
                print("!!!!!!!!!!!!!!!!!YOU MADE A FLOP ERROR!!!!!!!!!!!!!!!!!")
                player_made_mistake = True
            if flop_action_human:
                result_human = settle_pretty_payout(hand, dealer, board, 2)
        elif not pre_flop_action_human and player_made_mistake:
            print(f"\n----------------------- Flop -----------------------")
            print("!!!!!!!!SUPRESSING WARNING FOR THE REMAINDER OF THIS HAND!!!!!!!!")
            flop = board[0:3]
            print(f"Hero Hand: {sorted_hand_string(hand)}")
            print(f"Dealer Hole: {hole_dealer}")
            print(f"Board: {flop}")
            flop_action_human = bool(int(input("0-Check or 1-Bet >>> ")))
            if flop_action_human:
                result_human = settle_pretty_payout(hand, dealer, board, 2)
        
        # RIVER
        if not pre_flop_action_human and not flop_action_human and not player_made_mistake:
            print(f"\n----------------------- River -----------------------")
            print(f"Hero Hand: {sorted_hand_string(hand)}")
            print(f"Dealer Hole: {hole_dealer}")
            print(f"Board: {board}")
            river_action_human = bool(int(input("0-Fold or 1-Call >>> ")))
            if river_action_human != river_action_computer:
                print("!!!!!!!!!!!!!!!!!YOU MADE A RIVER ERROR!!!!!!!!!!!!!!!!!")
                player_made_mistake = True
            if river_action_human:
                result_human = settle_pretty_payout(hand, dealer, board, 1)
            else:
                result_human = settle_pretty_payout(hand, dealer, board, 0)
        elif not pre_flop_action_human and not flop_action_human and player_made_mistake:
            print(f"\n----------------------- River -----------------------")
            print(f"Hero Hand: {sorted_hand_string(hand)}")
            print(f"Dealer Hole: {hole_dealer}")
            print(f"Board: {board}")
            river_action_human = bool(int(input("0-Fold or 1-Call >>> ")))
            if river_action_human:
                result_human = settle_pretty_payout(hand, dealer, board, 1)
            else:
                result_human = settle_pretty_payout(hand, dealer, board, 0)

        # result
        (hero_nth, _, hero_hand_category) = eval_pretty(hand, board)
        (dealer_nth, _, dealer_hand_category) = eval_pretty(dealer, board)
        print(f"\n----------------------- SUMMARY -----------------------")
        print(f"Hero Hand:   {sorted_hand_string(hand)}\t\t\t\t({hero_hand_category}-{hero_nth})")
        print(f"Dealer Hand: {dealer}\t\t\t\t({dealer_hand_category}-{dealer_nth})")
        print(f"Board:       {board}")
        print(f"Computer play result: {result_computer} units")
        print(f"Your action result:   {result_human} units")

        print(f"[/ENDING HAND]")
    
    return (result_computer, result_human)

def ono_2p_game(manual=False):
    # setup for one round of UTH
    deck = Deck()
    hand = deck.draw(2)
    dealer = deck.draw(2)
    board = deck.draw(5)

    teammate = deck.draw(2)

    ## DO MAIN PLAYER
    
    # PRE-FLOP: try ONO rule first, if none found, try OCR
    pre_flop_action_computer = ono_preflop(hand, dealer, board)
    if pre_flop_action_computer is None:
        pre_flop_action_computer = ocr_preflop(hand, dealer, board)
    
    # FLOP: if we already raise preflop, just settle payment. otherwise decide what to do
    if pre_flop_action_computer: # we raised pre-flop... just compute result and be done with this round
        result_computer = settle_pretty_payout(hand, dealer, board, 4)
    else: # we checked pre-flop... onto the flop
        flop_action_computer = ocr_flop(hand, dealer, board)
        if flop_action_computer: # we bet on flop
            result_computer = settle_pretty_payout(hand, dealer, board, 2)
        else: # RIVER: we check on flop... onto the river
            river_action_computer = ocr_river(hand, dealer, board, teammate)
            if river_action_computer: # we call on river
                result_computer = settle_pretty_payout(hand, dealer, board, 1)
            else: # we fold on river
                result_computer = settle_pretty_payout(hand, dealer, board, 0)

    player_1_result = result_computer
    

    ## DO TEAMMATE

    # PRE-FLOP: try ONO rule first, if none found, try OCR
    pre_flop_action_computer = ono_preflop(teammate, dealer, board)
    if pre_flop_action_computer is None:
        pre_flop_action_computer = ocr_preflop(teammate, dealer, board)
    
    # FLOP: if we already raise preflop, just settle payment. otherwise decide what to do
    if pre_flop_action_computer: # we raised pre-flop... just compute result and be done with this round
        result_computer = settle_pretty_payout(teammate, dealer, board, 4)
    else: # we checked pre-flop... onto the flop
        flop_action_computer = ocr_flop(teammate, dealer, board)
        if flop_action_computer: # we bet on flop
            result_computer = settle_pretty_payout(teammate, dealer, board, 2)
        else: # RIVER: we check on flop... onto the river
            river_action_computer = ocr_river(teammate, dealer, board, hand)
            if river_action_computer: # we call on river
                result_computer = settle_pretty_payout(teammate, dealer, board, 1)
            else: # we fold on river
                result_computer = settle_pretty_payout(teammate, dealer, board, 0)

    player_2_result = result_computer

    return (player_1_result, player_2_result)










##########################################################################
######################## MONTE CARLO FUNCTIONS ###########################
##########################################################################
def risk_of_ruin_solo(bankroll, bet_size, num_trials = 30):
    num_people_went_broke = 0
    starting_units = bankroll // bet_size

    for i in range(num_trials):
        current_units = starting_units
        while True:
            (result, _) = ono_game()
            current_units += result
            if current_units >= 2*starting_units:
                break

            if current_units <= 0:
                num_people_went_broke += 1
                break

    return num_people_went_broke / num_trials

def risk_of_ruin_team(bankroll, bet_size, num_trials = 30):
    num_people_went_broke = 0
    starting_units = bankroll // bet_size

    for i in range(num_trials):
        current_units = starting_units
        while True:
            result = sum(ono_2p_game())
            current_units += result
            if current_units >= 2*starting_units:
                break

            if current_units <= 0:
                num_people_went_broke += 1
                break

    return num_people_went_broke / num_trials

def calculate_solo_ROR(units):
    uth_solo_risk_of_ruins = {5: 0.48, 10: 0.47, 15: 0.38, 20: 0.31, 30: 0.43, 35: 0.3, 40: 0.34, 60: 0.19, 80: 0.08}
    if units in uth_solo_risk_of_ruins.keys():
        return uth_solo_risk_of_ruins[units]
    else:
        ror = risk_of_ruin_solo(units, 1, num_trials = 30)
        print(f"Please save this ROR into the dictionary. ror = {ror}")
