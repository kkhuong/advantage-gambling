import sys
import collections
from functools import reduce
import operator as op

from deuces import Deck




##########################################################################
######################## PROGRAM CONFIGURATION ###########################
##########################################################################
DEBUG = True

# THREE CARD POKER SETTINGS
PAYS_ANTE_BONUS_ON_LOSS = True
STRAIGHT_ANTE_BONUS = 1
TRIPS_ANTE_BONUS = 4
STRAIGHT_FLUSH_ANTE_BONUS = 5







##########################################################################
######################## 3CP SPECIFIC CONSTANTS ##########################
##########################################################################
STRAIGHT_FLUSH = 6
TRIPS = 5
STRAIGHT = 4
FLUSH = 3
PAIR = 2
HIGH_CARD = 1

CALL = True
FOLD = False
DEFAULT_ACTION = FOLD

DEALER_QUALIFYING_HAND = (HIGH_CARD, 1703)





##########################################################################
###################### INTERNAL HELPER FUNCTIONS #########################
##########################################################################
def action_string(a):
    if a == CALL:
        return 'CALL'
    elif a == FOLD:
        return 'FOLD'
    else:
        return 'ERROR...UNKNOWN ACTION'

def rank_2_index(r):
    ranks = '23456789TJQKA'
    return ranks.index(r[0])

def is_trips(hand):
    ranks = {c[0] for c in hand}
    return len(ranks) == 1

def is_straight(hand):
    ranks = [c[0] for c in hand]
    characteristic_array = ['0'] * 13
    
    for r in ranks:
        characteristic_array[rank_2_index(r)] = '1'
    characteristic_array.insert(0, characteristic_array[-1]) # because Aces can make straight for A23 or QKA
    characteristic_string = reduce(op.add, characteristic_array)
    
    return '111' in characteristic_string

def is_flush(hand):
    suits = {c[1] for c in hand}
    return len(suits) == 1

def is_straight_flush(hand):
    return is_straight(hand) and is_flush(hand)

def is_pair(hand):
    ranks = [c[0] for c in hand]
    rank_count = collections.Counter(ranks)
    return 2 in rank_count.values()

def sort_hand(hand):
    if is_pair(hand): # (sort by brute force... because it is most efficient)
        if hand[0][0] == hand[1][0]: # 1st and 2nd card are pair
            return
        elif hand[0][0] == hand[2][0]: # 1st and 3rd card are pair
            tmp = hand[2]
            hand[2] = hand[1]
            hand[1] = tmp
        elif hand[1][0] == hand[2][0]: # 2nd and 3rd card are pair
            tmp = hand[2]
            hand[2] = hand[0]
            hand[0] = tmp
        else:
            sys.exit("Potential error in sort_hand()... possibly due to invalid input")
    else:
        hand.sort(key=rank_2_index, reverse=True)

def score_sorted_hand(hand):
    return (13**2)*rank_2_index(hand[0]) + (13**1)*rank_2_index(hand[1]) \
                    + (13**0)*rank_2_index(hand[2])
        
def eval_hand(hand):
    """Returns (RANK_CATEGORY, STRENGTH_IN_CATEGORY)"""
    
    sort_hand(hand)
    score = score_sorted_hand(hand)
    
    if is_straight_flush(hand):
        return (STRAIGHT_FLUSH, score)
    elif is_trips(hand):
        return (TRIPS, score)
    elif is_straight(hand):
        return (STRAIGHT, score)
    elif is_flush(hand):
        return (FLUSH, score)
    elif is_pair(hand):
        return (PAIR, score)
    else:
        return (HIGH_CARD, score)


def determine_payout(hand, dealer, action, ante_bonus_on_loss=True):
    if action == FOLD:
        return -1
    
    player_eval = eval_hand(hand)
    dealer_eval = eval_hand(dealer)
    
    payout = 0
    if dealer_eval < DEALER_QUALIFYING_HAND:
        payout += 1
    elif player_eval > dealer_eval:
        payout += 2
    elif player_eval < dealer_eval:
        payout += -2
    else: # player_eval == dealer_eval
        payout += 0
    
    # ante bonus
    if player_eval < dealer_eval and not ante_bonus_on_loss:
        return payout
    else:
        (player_hand_category, _) = player_eval
        if player_hand_category == STRAIGHT:
            payout += STRAIGHT_ANTE_BONUS
        elif player_hand_category == TRIPS:
            payout += TRIPS_ANTE_BONUS
        elif player_hand_category == STRAIGHT_FLUSH:
            payout += STRAIGHT_FLUSH_ANTE_BONUS
    
    return payout












##########################################################################
###################### DECISION MAKING FUNCTIONS #########################
##########################################################################
def decision_basic_strategy(hand, dealer, debug_msg=False):
    decision_rule = 'Basic Strategy - '
    action = DEFAULT_ACTION
    
    if eval_hand(hand) >= eval_hand(['Qs', '6h', '4c']):
        decision_rule += 'CALL because we have Q64 or higher'
        action = CALL
    else:
        decision_rule += 'FOLD because we have worse than Q64'
        action = FOLD
    
    
    if debug_msg:
        print(decision_rule)
    
    return action


def decision_holecarding(hand, dealer, debug_msg=False):
    decision_rule = "One Dealer's Hole Card - "
    action = DEFAULT_ACTION

    dealer_holecard = dealer[0]
    player_eval = eval_hand(hand)

    if rank_2_index(dealer_holecard[0]) < rank_2_index('Q'):
        decision_rule += "CALL if the dealer's known card is < Q"
        action = CALL
    elif dealer_holecard[0] == 'Q':
        decision_rule += "dealer has a Queen... only call with Q92+ and fold otherwise"
        if player_eval >= eval_hand(['Qs', '9h', '2c']):
            action = CALL
        else:
            action = FOLD
    elif dealer_holecard[0] == 'K':
        decision_rule += "dealer has a King... only call with K92+ and fold otherwise"
        if player_eval >= eval_hand(['Ks', '9h', '2c']):
            action = CALL
        else:
            action = FOLD
    elif dealer_holecard[0] == 'A':
        decision_rule += "dealer has a Ace... only call with A92+ and fold otherwise"
        if player_eval >= eval_hand(['As', '9h', '2c']):
            action = CALL
        else:
            action = FOLD
    else:
        sys.exit("ERROR: Potential bug in decision_holecarding()")
    
    
    if debug_msg:
        print(decision_rule)
    
    return action











##########################################################################
####################### RUN ONE GAME FUNCTIONS ###########################
##########################################################################
def run_basic_strategy_game(manual=False):
    deck = Deck()
    
    player_hand = deck.draw(3)
    dealer_hand = deck.draw(3)

    action_computer = decision_basic_strategy(player_hand, dealer_hand)
    result_computer = determine_payout(player_hand, dealer_hand, action_computer)
    
    # let the user try to play (if requested). user can play after the computer
    # since we are not holecarding
    if manual:
        print(f"\n\n\n\n===========[New Three Card Poker Hand]===========")
        print(f"Player Hand: {player_hand}")
        action_human = bool(int(input("0-Fold or 1-Call >>> ")))
        result_human = determine_payout(player_hand, dealer_hand, action_human)
        
        sort_hand(player_hand)
        sort_hand(dealer_hand)
        print(f"\n----------- Summary -----------")
        print(f"Player Hand: {player_hand}")
        print(f"Dealer Hand: {dealer_hand}")
        print(f"Computer's Decision: {action_string(action_computer)}")
        print(f"Result: Computer got {result_computer} units and you got {result_human} units")

        return (result_computer, result_human)
        

    return result_computer






def run_holecarding_strategy_game(manual=False):
    deck = Deck()
    
    player_hand = deck.draw(3)
    dealer_hand = deck.draw(3)

    dealer_holecard = dealer_hand[0]

    # now the computer can play out the hand (and possibly sort dealer's hand)
    action_computer = decision_holecarding(player_hand, dealer_hand)
    result_computer = determine_payout(player_hand, dealer_hand, action_computer)
    
    # print hand summary
    if manual:
        print(f"\n\n\n\n===========[New Three Card Poker Hand]===========")
        print(f"Player Hand: {player_hand}")
        print(f"Dealer's Holecard: {dealer_holecard}")
        action_human = bool(int(input("0-Fold or 1-Call >>> ")))
        result_human = determine_payout(player_hand, dealer_hand, action_human)

        sort_hand(player_hand)
        sort_hand(dealer_hand)
        print(f"\n----------- Summary -----------")
        print(f"Player Hand: {player_hand}")
        print(f"Dealer Hand: {dealer_hand}")
        print(f"Computer's Decision: {action_string(action_computer)}")
        print(f"Result: Computer got {result_computer} units and you got {result_human} units")

        return (result_computer, result_human)
        

    return result_computer




##########################################################################
########################### USER FUNCTIONS ###############################
##########################################################################
def play_basic_strategy():
    num_hands = int(input(f"How many hands would you like to play >>> "))

    computer_data = []
    player_data = []
    for i in range(num_hands):
        (c, p) = run_basic_strategy_game(True)
        computer_data.append(c)
        player_data.append(p)


    computer_profit = sum(computer_data)
    player_profit = sum(player_data)
    print(f"\n\n\n\n")
    print(f"You earned: {player_profit} betting units")
    print(f"Your mistakes (if any) had costed you {computer_profit - player_profit} betting units")


def play_holecarding_strategy():
    num_hands = int(input(f"How many hands would you like to play >>> "))

    computer_data = []
    player_data = []
    for i in range(num_hands):
        (c, p) = run_holecarding_strategy_game(True)
        computer_data.append(c)
        player_data.append(p)


    computer_profit = sum(computer_data)
    player_profit = sum(player_data)
    print(f"\n\n")
    print(f"You earned: {player_profit} betting units")
    print(f"Your mistakes (if any) had costed you {computer_profit - player_profit} betting units")






##########################################################################
######################## MONTE CARLO FUNCTIONS ###########################
##########################################################################
def get_basic_strategy_sample_returns(trials = 1000):
    data = []
    for i in range(trials):
        data.append(run_basic_strategy_game())
    return data


def calculate_basic_strategy_ev(trials = 1000000):
    data = get_basic_strategy_sample_returns(trials)
    return sum(data) / trials


def get_holecarding_sample_returns(trials = 1000):
    data = []
    for i in range(trials):
        data.append(run_holecarding_strategy_game())
    return data


def calculate_holecarding_ev(trials = 1000000):
    data = get_holecarding_sample_returns(trials)
    return sum(data) / trials # yes, we can use numpy but we have not set it up yet with pypy




##########################################################################
########################## SIMPLE UNIT TESTS #############################
##########################################################################
assert is_straight(['Jh', '9d', 'Tc']) == True
assert is_straight(['Jh', '9d', 'Qc']) == False

assert is_flush(['Jh', '9h', 'Th']) == True
assert is_flush(['7d', '2c', '9d']) == False

assert is_trips(['4h', '3d', '4c']) == False
assert is_trips(['Ah', 'Ad', 'Ac']) == True

assert is_straight_flush(['3d', '4d', '5d']) == True
assert is_straight_flush(['5d', '4d', '3d']) == True
assert is_straight_flush(['4d', '5d', '3d']) == True
assert is_straight_flush(['Ad', '4d', '3d']) == False

assert is_pair(['2d', '4d', '2c']) == True
assert is_pair(['Ad', '4d', '3d']) == False
assert is_pair(['7d', '7h', '7s']) == False
