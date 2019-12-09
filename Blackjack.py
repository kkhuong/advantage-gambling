import random
import math
import copy
from enum import Enum



class BlackjackError(Exception):
    pass

class BJ(Enum):
    HARD = 0
    SOFT = 1
    DOA = 2
    DA2 = 3
    DO911H = 4
    DO911A = 5
    DOT11H = 6
    DOT11A = 7
    DOTH = 8
    DOTA = 9
    DO11H = 10
    DO11A = 11
    BUY_INSURANCE = 12
    NO_INSURANCE = 13
    SURRENDER = 14
    SPLIT = 15
    DOUBLE = 16
    HIT = 17
    STAND = 18
    BUST = 19
    NO_POSSIBLE_DECISION = 20
    WON = 21
    LOSS = 22
    PUSH = 23




class Card:
    CARD_DATA = [('A', 'd', 11, 1), ('A', 'h', 11, 1), ('A', 's', 11, 1), ('A', 'c', 11, 1), ('K', 'd', 10, 10), ('K', 'h', 10, 10), ('K', 's', 10, 10), ('K', 'c', 10, 10), ('Q', 'd', 10, 10), ('Q', 'h', 10, 10), ('Q', 's', 10, 10), ('Q', 'c', 10, 10), ('J', 'd', 10, 10), ('J', 'h', 10, 10), ('J', 's', 10, 10), ('J', 'c', 10, 10), ('T', 'd', 10, 10), ('T', 'h', 10, 10), ('T', 's', 10, 10), ('T', 'c', 10, 10), ('9', 'd', 9, 9), ('9', 'h', 9, 9), ('9', 's', 9, 9), ('9', 'c', 9, 9), ('8', 'd', 8, 8), ('8', 'h', 8, 8), ('8', 's', 8, 8), ('8', 'c', 8, 8), ('7', 'd', 7, 7), ('7', 'h', 7, 7), ('7', 's', 7, 7), ('7', 'c', 7, 7), ('6', 'd', 6, 6), ('6', 'h', 6, 6), ('6', 's', 6, 6), ('6', 'c', 6, 6), ('5', 'd', 5, 5), ('5', 'h', 5, 5), ('5', 's', 5, 5), ('5', 'c', 5, 5), ('4', 'd', 4, 4), ('4', 'h', 4, 4), ('4', 's', 4, 4), ('4', 'c', 4, 4), ('3', 'd', 3, 3), ('3', 'h', 3, 3), ('3', 's', 3, 3), ('3', 'c', 3, 3), ('2', 'd', 2, 2), ('2', 'h', 2, 2), ('2', 's', 2, 2), ('2', 'c', 2, 2)]

    def __init__(self,rank,suit,value_hard,value_soft):
        self.rank = rank
        self.suit = suit
        self.value_hard = value_hard
        self.value_soft = value_soft

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return self.__str__()

    def is_ace(self):
        return self.rank == 'A'

    def is_ten(self):
        return self.value_hard == 10



class Shoe:
    def __init__(self, decks, penetration):
        self.decks = decks
        self.pen = penetration
        self.cards = [Card(rank,suit,hard,soft) for (rank, suit, hard, soft) in Card.CARD_DATA] * decks
        random.shuffle(self.cards)
        self.cutcard = math.floor(self.pen * 52 * self.decks)
        self.burn_cards = []
        self.discard_tray = []
        self.dealer_holecard = None # useful when we need to monte carlo
        self.out_of_cards_error = False

    def __getitem__(self, idx):
        return self.cards[len(self.cards) - idx - 1]

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return str(list(reversed(self.cards)))

    def __repr__(self):
        total_num_cards  = self.decks * 52
        num_played_cards = self.decks * 52 - len(self.cards)
        return f"Decks: {self.decks}\nPEN Proportion: {self.pen}\nShuffle In: {self.cutcard - num_played_cards}\nRemaining Cards: {self.__str__()}"

    def draw(self, is_dealer_hole=False):
        try:
            card = self.cards.pop()
            if is_dealer_hole:
                self.dealer_holecard = card
            return card
        except:
            self.out_of_cards_error = True
            self.cards = self.unseen_cards()
            if is_dealer_hole:
                self.dealer_holecard = card
            return card

    def discard(self, cards_list):
        self.discard_tray.extend(copy.deepcopy(cards_list))

    def depth(self):
        return len(self.discard_tray)

    def burn(self):
        card = self.cards.pop()
        self.burn_cards.append(card)

    def needs_reshuffling(self):
        if self.out_of_cards_error: return True
        total_num_cards  = self.decks * 52
        num_played_cards = self.decks * 52 - len(self.cards)
        return num_played_cards >= self.cutcard

    def remaining_cards(self):
        if self.dealer_holecard is None:
            return copy.deepcopy(self.cards)
        else:
            return copy.deepcopy(self.cards) + [copy.deepcopy(self.cards)]

    def unseen_cards(self):
        return self.remaining_cards() + copy.deepcopy(self.burn_cards)

    def clone_shoe_with_unseen_cards(self):
        shoe = Shoe(self.decks, self.penetration)
        shoe.cards = self.unseen_cards()
        shoe.cutcard = self.cutcard
        shoe.burn_cards = copy.deepcopy(self.burn_cards)
        shoe.discard_tray = copy.deepcopy(self.discard_tray)
        return shoe

    def reshuffle(self):
        random.shuffle(self.cards)

    def reinstate(self):
        self.__init__(self.decks, self.pen)




class Hand:
    def __init__(self, cards_list=None, bet=0):
        if not cards_list:
            self.cards = []
        else:
            self.cards = copy.deepcopy(cards_list)
        self.is_hitted = False
        self.is_doubled = False
        self.is_splitted = False
        self.is_surrendered = False
        self.split_history = None
        self.bet = bet
        self.insurance_bet = 0
        self.bet_result = 0 # going to be win or loss
        self.insurance_result = 0 # going to be win, loss, or NA
        self.monetary_result = 0

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, idx):
        return self.cards[idx]

    def __repr__(self):
        return f'{str(self.cards)}'

    def __str__(self):
        return f'{str(self.cards)}'

    def upcard(self):
        return self.cards[0]

    def contains_ace(self):
        for card in self.cards:
            if card.is_ace():
                return True
        return False

    def is_split_ace(self):
        return self.is_splitted and self.contains_ace()

    def value(self):
        if len(self.cards) < 2:
            raise ValueError

        # calculate value
        total = [0]
        for card in self.cards:
            if not card.is_ace():
                total = [i + card.value_hard for i in total]
            else:
                soft_totals = [i + card.value_soft for i in total]
                hard_totals = [i + card.value_hard for i in total]
                total = soft_totals + hard_totals

        # value
        val = min(total) if (min(total) > 21) else max(filter(lambda x: x<=21,total))
        # hard or soft
        if len(list(filter(lambda x: x<=11,total))) != 0 and self.contains_ace(): hs = BJ.SOFT
        else: hs = BJ.HARD

        return (val, hs)

    def total(self):
        val, _ = self.value()
        return val

    def classify(self):
        val, hs = self.value()
        return (val, hs, self.can_surrender(), self.can_split(), self.can_double(), self.can_hit())

    def is_natural(self):
        return not self.is_splitted and len(self.cards) == 2 and self.total() == 21

    def is_busted(self):
        if len(self.cards) < 2: return False
        val, _ = self.value()
        return val > 21

    def determine_pair(self):
        if len(self.cards) != 2:
            raise BlackjackError("determine_pair")

        if self.cards[0].value_hard == self.cards[1].value_hard:
            return self.cards[0].value_hard
        else:
            raise BlackjackError("determine_pair")

    def can_surrender(self):
        """caution: need to be called from something that knows the dealer upcard"""
        if Config.EARLY_SURRENDER or Config.LATE_SURRENDER:
            if self.is_hitted and not Config.SURRENDER_AFTER_HIT:
                return False
            elif self.is_doubled and not Config.SURRENDER_AFTER_DOUBLE:
                return False
            elif self.is_splitted and not Config.SURRENDER_AFTER_SPLIT:
                return False
            else:
                return True # preliminary
        else:
            return False

    def can_split(self):
        """caution: need to be called from something that knows how many times u already split"""
        if self.is_surrendered or self.is_hitted or self.is_doubled or len(self.cards) != 2:
            return False
        
        if self.cards[0].value_hard == self.cards[1].value_hard:
            if self.is_split_ace() and not Config.RESPLIT_ACE:
                return False
            elif not Config.SPLIT_NONMATCHING_PAINT and (self.cards[0].rank != self.cards[1].rank) and (self.cards[0].value_hard == self.cards[1].value_hard) and (self.cards[0].value_hard == 10):
                return False
            elif self.split_history is None:
                return True
            else:
                return self.split_history[0] < Config.MAX_HAND_FROM_SPLIT
        else:
            return False

    def can_double(self):
        if self.is_surrendered or (self.is_doubled and not Config.REDOUBLE):
            return False
        if self.is_hitted and not Config.DOUBLE_AFTER_HIT:
            return False

        if self.is_splitted:
            if not Config.DOUBLE_AFTER_SPLIT:
                return False
            if self.is_split_ace():
                return Config.HIT_SPLIT_ACE and ((not self.is_hitted) or (Config.DOUBLE_AFTER_HIT))
            else:
                return Config.DOUBLE_AFTER_SPLIT
        
        # rules to reject doubling due to rule restrictions
        tot, hs = self.value()
        if Config.DOUBLING_RULE == BJ.DOA:
            return Config.DOUBLE_AFTER_HIT or not self.is_hitted
        elif Config.DOUBLING_RULE == BJ.DA2:
            return len(self.cards) == 2
        elif Config.DOUBLING_RULE == BJ.DO911H:
            return not (tot < 9 or tot > 11 or hs == BJ.SOFT)
        elif Config.DOUBLING_RULE == BJ.DO911A:
            return not (tot < 9 or tot > 11)
        elif Config.DOUBLING_RULE == BJ.DOT11H:
            return not (tot < 10 or tot > 11 or hs == BJ.SOFT)
        elif Config.DOUBLING_RULE == BJ.DOT11A:
            return not (tot < 10 or tot > 11)
        elif Config.DOUBLING_RULE == BJ.DOTH:
            return not (tot != 10 or hs == BJ.SOFT)
        elif Config.DOUBLING_RULE == BJ.DOTA:
            return tot == 10
        elif Config.DOUBLING_RULE == BJ.DO11H:
            return not (tot != 11 or hs == BJ.SOFT)
        elif Config.DOUBLING_RULE == BJ.DO11A:
            return tot == 11
        else:
            raise BlackjackError('Error in can_double()')

    def can_hit(self):
        if self.is_surrendered or self.is_doubled:
            return False

        if self.is_split_ace():
            return Config.HIT_SPLIT_ACE
        else:
            return not self.is_doubled

    def buy_insurance(self, amount=-1):
        if amount == -1:
            self.insurance_bet = self.bet / 2
        elif -0.01 <= amount <= 1.01*(self.bet / 2):
            self.insurance_bet = amount
        else:
            raise BlackjackError('Can only buy up to half bet for insurance')

    def surrender(self):
        self.is_surrendered = True

    def split(self, new_card):
        c = self.cards.pop()
        self.hit(new_card)
        self.is_splitted = True
        new_hand = Hand([c], self.bet)
        new_hand.is_splitted = True

        if self.split_history is None:
            self.split_history = [2]
        else:
            self.split_history[0] += 1
        new_hand.split_history = self.split_history
        return new_hand

    def double(self, card):
        self.cards.append(card)
        self.is_doubled = True
        self.is_hitted = True
        self.bet *= 2

    def hit(self, card):
        self.cards.append(card)
        if len(self.cards) > 2:
            self.is_hitted = True



class Player:
    def __init__(self, name, initial_br):
        self.name = name
        self.hands = []
        self.initial_br = initial_br
        self.br = initial_br

    def __str__(self):
        return f"{self.name} (${self.initial_br}, ${self.br})"

    def __repr__(self):
        string = ""
        for h in self.hands:
            string += f"\n{str(h)}"
        return f"{self.name} (${self.br}){string}"

    def __getitem__(self, idx):
        return self.hands[idx]

    def start_hand(self, cards_list, bet=0):
        if len(cards_list) != 2:
            raise BlackjackError('Player:start_hand()')
        self.hands.append(Hand(cards_list, bet))

    def collect(self):
        cards = []
        for hand in self.hands:
            for card in hand.cards:
                cards.append(card)
        return cards

    def cleanup(self):
        self.hands = []

    def surrender(self, hand_idx):
        if not self.hands[hand_idx].can_surrender():
            raise BlackjackError('Player:surrender()')
        self.hands[hand_idx].surrender()

    def split(self, hand_idx, new_card):
        if not self.hands[hand_idx].can_split():
            raise BlackjackError('Player:split()')
        new_hand = self.hands[hand_idx].split(new_card)
        self.hands.insert(hand_idx, new_hand)

    def double(self, hand_idx, new_card):
        if not self.hands[hand_idx].can_double():
            raise BlackjackError('Player:double()')
        self.hands[hand_idx].double(new_card)

    def hit(self, hand_idx, new_card):
        if not self.hands[hand_idx].can_hit():
            raise BlackjackError('Player:hit()')
        self.hands[hand_idx].hit(new_card)

    def hand_decision(self, hand_idx, dealer_hand, shoe, play_strategy):
        """resolves insurance on the side. return whaat to do"""
        if len(self.hands[hand_idx]) < 2:
            self.hands[hand_idx].hit(shoe.draw())

        if len(self.hands[hand_idx]) < 2:
            raise BlackjackError('Player:hand_decision()')

        val, hs, surrenderable, splitable, doubleable, hitable = self.hands[hand_idx].classify()
        if not surrenderable and not splitable and not doubleable and not hitable:
            return BJ.STAND
        actions = play_strategy(self.hands[hand_idx], dealer_hand, shoe, extra_seen_cards=None)
        if BJ.BUY_INSURANCE in actions and dealer_hand.upcard().is_ace() and not self.hands[hand_idx].is_splitted and not self.hands[hand_idx].is_doubled:
            self.hands[hand_idx].buy_insurance()

        for action in actions:
            if action == BJ.SURRENDER and surrenderable and (Config.LATE_SURRENDER or Config.EARLY_SURRENDER):
                if Config.EARLY_SURRENDER:
                    if not Config.SURRENDER_VS_ACE and dealer_hand.upcard().is_ace():
                        continue
                    elif not Config.SURRENDER_VS_TEN and dealer_hand.upcard().is_ten():
                        continue
                    else:
                        return BJ.SURRENDER
                elif Config.LATE_SURRENDER:
                    if dealer_hand.is_natural():
                        return BJ.NO_POSSIBLE_DECISION
                    elif not Config.SURRENDER_VS_ACE and dealer_hand.upcard().is_ace():
                        continue
                    elif not Config.SURRENDER_VS_TEN and dealer_hand.upcard().is_ten():
                        continue
                    else:
                        return BJ.SURRENDER
            elif dealer_hand.is_natural():
                return BJ.NO_POSSIBLE_DECISION
            elif action == BJ.SPLIT and splitable:
                return BJ.SPLIT
            elif action == BJ.DOUBLE and doubleable:
                return BJ.DOUBLE
            elif action == BJ.HIT and hitable:
                return BJ.HIT
            elif action == BJ.STAND:
                return BJ.STAND

        raise BlackjackError('play strategy did not give something')


    def resolve_all_hands(self, dealer_hand, shoe, play_strategy):
        potential_showdown = False
        i = 0
        while i < len(self.hands):
            while True:
                if self.hands[i].is_busted():
                    i += 1
                    break

                decision = self.hand_decision(i, dealer_hand, shoe, play_strategy)
                if decision == BJ.NO_POSSIBLE_DECISION: # dealer natural
                    i += 1
                    break
                elif decision == BJ.SURRENDER:
                    self.surrender(i)
                    i += 1
                    break
                elif decision == BJ.SPLIT:
                    self.split(i, shoe.draw())
                elif decision == BJ.DOUBLE:
                    self.double(i, shoe.draw())
                    if not self.hands[i].is_busted(): potential_showdown = True
                    i += 1
                    break
                elif decision == BJ.HIT:
                    self.hit(i, shoe.draw())
                elif decision == BJ.STAND:
                    if not self.hands[i].is_busted(): potential_showdown = True
                    i += 1
                    break
                else:
                    raise BlackjackError('decision cant terminate')
        return potential_showdown

    def settle_payout(self, dealer_hand):
        br_change = 0
        for hand in self.hands:
            if hand.is_surrendered:
                br_change -= hand.bet / 2
                hand.bet_result = BJ.LOSS
                hand.monetary_result = -hand.bet / 2
            elif hand.is_busted() and dealer_hand.is_busted():
                if (Config.CALIFORNIA_STYLE or Config.NO_BUST_STYLE) and hand.total() < dealer_hand.total():
                    br_change -= 0
                    hand.bet_result = BJ.PUSH
                    hand.monetary_result = 0
                else:
                    br_change -= hand.bet
                    hand.bet_result = BJ.LOSS
                    hand.monetary_result = -hand.bet
            elif hand.is_natural() and not dealer_hand.is_natural():
                br_change += Config.BLACKJACK_PAYS * hand.bet
                hand.bet_result = BJ.WON
                hand.monetary_result = Config.BLACKJACK_PAYS * hand.bet
            elif dealer_hand.is_natural():
                if not hand.is_natural(): 
                    br_change -= hand.bet
                    hand.bet_result = BJ.LOSS
                    hand.monetary_result = -hand.bet
                else: # hand.is_natural()
                    br_change -= 0
                    hand.bet_result = BJ.PUSH
                    hand.monetary_result = 0
            elif not hand.is_busted() and dealer_hand.is_busted():
                if dealer_hand.total() == 22:
                    if Config.PUSH22:
                        br_change += 0
                        hand.bet_result = BJ.PUSH
                        hand.monetary_result = 0
                    else:
                        br_change += hand.bet
                        hand.bet_result = BJ.WON
                        hand.monetary_result = hand.bet
                else:
                    br_change += hand.bet
                    hand.bet_result = BJ.WON
                    hand.monetary_result = hand.bet
            elif hand.is_busted() and not dealer_hand.is_busted():
                br_change -= hand.bet
                hand.bet_result = BJ.LOSS
                hand.monetary_result = -hand.bet
            elif not hand.is_busted() and not dealer_hand.is_busted():
                if hand.total() > dealer_hand.total():
                    br_change += hand.bet
                    hand.bet_result = BJ.WON
                    hand.monetary_result = hand.bet
                elif hand.total() < dealer_hand.total():
                    br_change -= hand.bet
                    hand.bet_result = BJ.LOSS
                    hand.monetary_result = -hand.bet
                else:
                    br_change += 0
                    hand.bet_result = BJ.PUSH
                    hand.monetary_result = 0
            else:
                raise BlackjackError('cannot settle payment')

            # insurance/even-money
            if dealer_hand.upcard().is_ace():
                if dealer_hand.is_natural():
                    br_change += 2 * hand.insurance_bet
                    hand.insurance_result = BJ.WON
                    hand.monetary_result += 2 * hand.insurance_bet
                else:
                    br_change -= hand.insurance_bet
                    hand.insurance_result = BJ.LOSS
                    hand.monetary_result -= hand.insurance_bet

        self.br += br_change



class Dealer(Player):
    def __init__(self):
        self.hands = []
        self.name = 'Dealer'

    def __repr__(self):
        if self.hands:
            total, hs = self.hands[0].value()
            return f"{str(self.hands[0])} {'HARD' if hs == BJ.HARD else 'SOFT'} {total}"
        else:
            return f"No Dealer Hand Started"

    def __str__(self):
        return self.__repr__()

    def get_hand(self):
        return self.hands[0]

    def resolve_dealer_hand(self, shoe):
        val, hs = self.hands[0].value()
        while val < 17 or (val == 17 and hs == BJ.SOFT and Config.DEALER_SOFT17 == BJ.HIT):
            self.hands[0].hit(shoe.draw())
            val, hs = self.hands[0].value()

    def value(self):
        val, _ = self.hands[0].value()
        return val

    def is_insurance_offered(self):
        return self.hands[0].cards[0].is_ace()

    def is_natural(self):
        return self.hands[0].is_natural()

    def upcard(self):
        if not self.hands:
            raise BlackjackError('upcard()')
        return self.hands[0].cards[0]

    def settle_payout(self, dealer_hand):
        pass



class Table:
    def __init__(self, *player_constructor_args):
        self.players = [Dealer()]
        for (name, br) in player_constructor_args:
            self.players.append(Player(name, br))

    def __repr__(self):
        num_players = len(self.players) - 1
        players_info = "\n".join(reversed(list(map(str,self.players))))
        return f'{num_players} Players:\n{players_info}'

    def __str__(self):
        return self.__repr__() # just for now

    def __len__(self):
        return len(self.players)


class Game:
    def __init__(self, decks, penetration, count_strategy, bet_strategy, play_strategy):
        self.shoe = Shoe(decks, penetration)
        self.shoe.burn()
        self.table = Table(('AP', Config.INITIAL_BANKROLL)) # just for now
        self.count_strategy = count_strategy
        self.bet_strategy = bet_strategy
        self.play_strategy = play_strategy
        self.data = []
        self.round_num = 0
        self.round_in_progress = False

    def __str__(self):
        if self.data:
            return '\n'.join(map(str, self.data))
        return ''

    def __repr__(self):
        if self.data:
            return '\n'.join(map(str, self.data))
        return ''

    def cleanup(self):
        self.round_in_progress = False
        for p in self.table.players:
            self.shoe.discard(p.collect())
            p.cleanup()

    def init_round(self):
        if self.shoe.needs_reshuffling():
            self.round_num = 0
            self.shoe.reinstate()

        self.round_in_progress = True
        self.round_num += 1

        # pass out cards by alernating (just like in the casino)
        cards_dealt = []
        num_players = len(self.table)
        for i in range(num_players): # first card
            cards_dealt.append([self.shoe.draw()])
        for i in range(num_players): # second card
            cards_dealt[i].append(self.shoe.draw())

        for p_idx in range(num_players):
            bet = self.bet_strategy(self.count_strategy, self.shoe)
            self.table.players[(p_idx-1) % num_players].start_hand(cards_dealt[p_idx], bet)

    def playout_round(self):
        if not self.round_in_progress:
            return

        num_players = len(self.table)
        dealer_hand = self.table.players[0].get_hand()
        potential_showdown = False
        for p_idx in range(1, num_players):
            potential_showdown = potential_showdown or self.table.players[p_idx].resolve_all_hands(dealer_hand, self.shoe, self.play_strategy)

        if potential_showdown:
            self.table.players[0].resolve_dealer_hand(self.shoe)

    def settle_payment(self):
        if not self.round_in_progress:
            return

        dealer_hand = self.table.players[0].get_hand()
        for i in range(1,len(self.table.players)):
            self.table.players[i].settle_payout(dealer_hand)


    def record_data(self):
        if not self.round_in_progress:
            return

        tc = self.count_strategy(self.shoe)
        depth = self.shoe.depth()
        dealer_hand = self.table.players[0].get_hand()
        hand_history = []
        for p in self.table.players:
            if p.name != 'Dealer':
                for i, h in enumerate(p.hands, 1):
                    hand_history.append((tc, depth, p.name, self.round_num, i, h.bet, h, h.total(), dealer_hand, dealer_hand.total(), h.bet_result, h.insurance_result, h.monetary_result, h.is_splitted, h.split_history, h.is_doubled))
                    # hand_history.append((h, h.is_splitted, h.can_split(), dealer_hand))
        self.data.extend(hand_history)


    def play_one_round(self):
        self.init_round()
        self.playout_round()
        self.settle_payment()
        self.record_data()
        self.cleanup() # add this back after debug


    def play_full_shoe(self):
        while not self.shoe.needs_reshuffling():
            self.play_one_round()
        self.shoe.reinstate()
        self.round_num = 0

    def debug(self):
        print(str(self.table))
        print(f"Count: {self.count_strategy(self.shoe)}\nBet: {self.bet_strategy(self.count_strategy, self.shoe)}")
        print(str(self.data))
        return self.shoe

    def d(self):
        for e in self.data:
            if e[-3]:
                print(f"******{str(e)}******")
            else:
                print(str(e))


# class MonteCarlo(Game):
#     def __init__(self, decks, penetration, count_strategy, bet_strategy, play_strategy):
#         super(Game, self).__init__()

#     def load_custom_shoe(self, shoe):
#         self.shoe = copy.deepcopy(shoe)

#     def add_card(self, card):
#         self.shoe.cards.append(card)

#     def remove_card(self, card):
#         idx = self.shoe.cards.index(card)
#         del self.shoe.cards[idx]

#     def record_data(self):
#         """override this"""
#         pass

#     def randomize(self):
#         self.shoe.reshuffle()

#     def clone(self):
#         return copy.deepcopy(self)

#     def clone_and_randomize(self):
#         new_game = copy.deepcopy(self)
#         new_game.randomize()
#         return new_game


# COUNTERS for BETTING
class Counter:
    def just_gambling(shoe, extra_seen_cards=None):
        return 0

    def running_hilo(shoe, extra_seen_cards=None):
        rc = 0
        for card in shoe.discard_tray:
            if card.value_hard == 10 or card.value_hard == 11:
                rc -= 1
            elif 2 <= card.value_hard <= 6:
                rc += 1
        return rc

    def hilo(shoe, extra_seen_cards=None):
        rc = Counter.running_hilo(shoe, extra_seen_cards)
        decks_remaining = len(shoe) / 52
        return math.floor(rc / decks_remaining)

    def wong_halves(shoe, extra_seen_cards=None):
        rc = 0
        for card in shoe.discard_tray:
            if card.value_hard == 10 or card.value_hard == 11:
                rc -= 1
            elif card.value_hard == 2 or card.value_hard == 7:
                rc += 0.5
            elif card.value_hard == 3 or card.value_hard == 4 or card.value_hard == 6:
                rc += 1
            elif card.value_hard == 5:
                rc += 1.5
            elif card.value_hard == 8:
                rc += 0
            elif card.value_hard == 9:
                rc -= 0.5
        decks_remaining = len(shoe.cards)/52
        return math.trunc(rc / decks_remaining)

    def perfect_insurance(shoe, extra_seen_cards=None):
        num_tens = len([card for card in shoe.cards if card.is_ten()])
        num_cards = len(shoe)
        return num_tens / num_cards > 0.33


# COUNTERS for PLAYING
class DeviationCounters:
    def hilo(shoe, extra_seen_cards=None):
        rc = Counter.running_hilo(shoe, extra_seen_cards)
        tc = Counter.hilo(shoe, extra_seen_cards)
        return (tc, rc)


# OPTIMAL BETTING
class Betting:
    def flat(counting_function, shoe, extra_seen_cards=None):
        return Config.BETTING_UNIT_SIZE

    def linear(counting_function, shoe, extra_seen_cards=None):
        tc = counting_function(shoe, extra_seen_cards)
        units = max(tc - 1, 1)
        return Config.BETTING_UNIT_SIZE * units

    def kelly(counting_function, shoe, extra_seen_cards=None):
        edge = counting_function(shoe, extra_seen_cards)
        std = 1.15
        variance = std**2
        return Config.INITIAL_BANKROLL * (edge/variance)



# PLAYING STRATEGIES
class DecisionChart:
    def make_deviation(ref_action_list, action):
        ref_action_list[:0] = [action]

    def basic(hand, dealer_hand, shoe=None, extra_seen_cards=None, insurance_count_function=None):
        d = dealer_hand.upcard().value_hard
        total, hs, sur, spl, dbl, hit = hand.classify()

        action_priorty = []

        # insurance
        if insurance_count_function is not None:
            if insurance_count_function(shoe, extra_seen_cards):
                action_priorty.append(BJ.BUY_INSURANCE)

        # surrender
        if sur:
            if hs == BJ.HARD:
                if total == 16:
                    if 9 <= d <= 11:
                        action_priorty.append(BJ.SURRENDER)
                if total == 15:
                    if d == 10:
                        action_priorty.append(BJ.SURRENDER)

        # if dealer has natural
        if dealer_hand.is_natural():
            action_priorty.append(BJ.NO_POSSIBLE_DECISION)
            return action_priorty

        # split
        if spl:
            paired_rank = hand.determine_pair()
            if paired_rank == 11:
                action_priorty.append(BJ.SPLIT)
            elif paired_rank == 10:
                pass
            elif paired_rank == 9:
                if (2 <= d <= 6) or (8 <= d <= 9):
                    action_priorty.append(BJ.SPLIT)
            elif paired_rank == 8:
                action_priorty.append(BJ.SPLIT)
            elif paired_rank == 7:
                if (2 <= d <= 7):
                    action_priorty.append(BJ.SPLIT)
            elif paired_rank == 6:
                if d == 2:
                    if Config.DOUBLE_AFTER_SPLIT:
                        action_priorty.append(BJ.SPLIT)
                elif (3 <= d <= 6):
                    action_priorty.append(BJ.SPLIT)
            elif paired_rank == 5:
                pass
            elif paired_rank == 4:
                if (5 <= d <= 6):
                    if Config.DOUBLE_AFTER_SPLIT:
                        action_priorty.append(BJ.SPLIT)
            elif paired_rank == 3:
                if (2 <= d <= 3):
                    if Config.DOUBLE_AFTER_SPLIT:
                        action_priorty.append(BJ.SPLIT)
                elif (4 <= d <= 7):
                    action_priorty.append(BJ.SPLIT)
            elif paired_rank == 2:
                if (2 <= d <= 3):
                    if Config.DOUBLE_AFTER_SPLIT:
                        action_priorty.append(BJ.SPLIT)
                elif (4 <= d <= 7):
                    action_priorty.append(BJ.SPLIT)

        # double
        if dbl:
            if hs == BJ.HARD: # hard double
                if total == 11:
                    action_priorty.append(BJ.DOUBLE)
                elif total == 10:
                    if (2 <= d <= 9):
                        action_priorty.append(BJ.DOUBLE)
                elif total == 9:
                    if (3 <= d <= 6):
                        action_priorty.append(BJ.DOUBLE)
            else: # soft double
                if total == 19:
                    if d == 6:
                        action_priorty.append(BJ.DOUBLE)
                elif total == 18:
                    if (2 <= d <= 6):
                        action_priorty.append(BJ.DOUBLE)
                elif total == 17:
                    if (3 <= d <= 6):
                        action_priorty.append(BJ.DOUBLE)
                elif total == 16:
                    if (4 <= d <= 6):
                        action_priorty.append(BJ.DOUBLE)
                elif total == 15:
                    if (4 <= d <= 6):
                        action_priorty.append(BJ.DOUBLE)
                elif total == 14:
                    if (5 <= d <= 6):
                        action_priorty.append(BJ.DOUBLE)
                elif total == 13:
                    if (5 <= d <= 6):
                        action_priorty.append(BJ.DOUBLE)

        # hit
        if hit:
            if hs == BJ.HARD: # hard hit
                if (12 < total <= 16):
                    if (7 <= d <= 11):
                        action_priorty.append(BJ.HIT)
                elif total == 12:
                    if (2 <= d <= 3) or (7 <= d <= 11):
                        action_priorty.append(BJ.HIT)
                elif (total <= 11):
                    action_priorty.append(BJ.HIT)
            else: # soft hit
                if total == 18:
                    if (9 <= d <= 11):
                        action_priorty.append(BJ.HIT)
                elif (total <= 17):
                    action_priorty.append(BJ.HIT)

        # stand
        if hs == BJ.HARD: # hard stand
            if (17 <= total):
                action_priorty.append(BJ.STAND)
            elif (13 <= total <= 16):
                if (2 <= d <= 6):
                    action_priorty.append(BJ.STAND)
            elif total == 12:
                if (4 <= d <= 6):
                    action_priorty.append(BJ.STAND)
        else: # soft stand
            if (19 <= total <= 21):
                action_priorty.append(BJ.STAND)
            elif total == 18:
                if (2 <= d <= 8):
                    action_priorty.append(BJ.STAND)

        if not action_priorty:
            print(hand)
            print(dealer_hand)
            print(hand.classify())
            print(hand.is_surrendered, hand.is_splitted, hand.is_doubled, hand.is_hitted)
            raise BlackjackError('Basic strategy')

        return action_priorty


    def bja_h17(hand, dealer_hand, shoe, extra_seen_cards=None, insurance_count_function=None):
        d = dealer_hand.upcard().value_hard
        total, hs, sur, spl, dbl, hit = hand.classify()
        tc, rc = DeviationCounters.hilo(shoe, extra_seen_cards)
        actions = DecisionChart.basic(hand, dealer_hand, shoe, extra_seen_cards, insurance_count_function)

        if sur:
            if (total == 17 and hs == BJ.HARD) and d == 11: # hard 17 vs Ace
                DecisionChart.make_deviation(actions, BJ.SURRENDER)
                return actions
            elif (total == 16 and hs == BJ.HARD) and d == 9:
                if tc <= -1:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 16 and hs == BJ.HARD) and d == 8:
                if tc >= 4:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 15 and hs == BJ.HARD) and d == 11:
                if tc >= -1:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 15 and hs == BJ.HARD) and d == 10:
                if rc < 0:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 15 and hs == BJ.HARD) and d == 9:
                if tc >= 2:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 15 and hs == BJ.HARD) and d == 8:
                if tc >= 7:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 14 and hs == BJ.HARD) and d == 11:
                if tc >= 4:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 14 and hs == BJ.HARD) and d == 10:
                if tc >= 4:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 14 and hs == BJ.HARD) and d == 9:
                if tc >= 6:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
        
        if spl: # deviate to split
            paired_rank = hand.determine_pair()
            if paired_rank == 10 and d == 4:
                if tc >= 6:
                    DecisionChart.make_deviation(actions, BJ.SPLIT)
                    return actions
            elif paired_rank == 10 and d == 5:
                if tc >= 5:
                    DecisionChart.make_deviation(actions, BJ.SPLIT)
                    return actions
            if paired_rank == 10 and d == 6:
                if tc >= 4:
                    DecisionChart.make_deviation(actions, BJ.SPLIT)
                    return actions

        if dbl: # deviate from double
            if (total == 19 and hs == BJ.SOFT) and d == 6:
                if rc < 0:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 19 and hs == BJ.SOFT) and d == 5:
                if tc >= 1:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions
            elif (total == 19 and hs == BJ.SOFT) and d == 4:
                if tc >= 3:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions
            elif (total == 17 and hs == BJ.SOFT) and d == 2:
                if tc >= 1:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions

        if hit: # deviate from hit
            if (total == 16 and hs == BJ.HARD) and d == 11:
                if tc >= 3:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 16 and hs == BJ.HARD) and d == 10:
                if rc > 0:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 16 and hs == BJ.HARD) and d == 9:
                if tc >= 4:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 15 and hs == BJ.HARD) and d == 11:
                if tc >= 5:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 15 and hs == BJ.HARD) and d == 10:
                if tc >= 4:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 13 and hs == BJ.HARD) and d == 2:
                if tc <= -1:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 12 and hs == BJ.HARD) and d == 4:
                if rc < 0:
                    DecisionChart.make_deviation(actions, BJ.HIT)
                    return actions
            elif (total == 12 and hs == BJ.HARD) and d == 3:
                if tc >= 2:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 12 and hs == BJ.HARD) and d == 2:
                if tc >= 3:
                    DecisionChart.make_deviation(actions, BJ.STAND)
                    return actions
            elif (total == 10 and hs == BJ.HARD) and d == 11:
                if tc >= 3:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions
            elif (total == 10 and hs == BJ.HARD) and d == 10:
                if tc >= 4:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions
            elif (total == 9 and hs == BJ.HARD) and d == 7:
                if tc >= 3:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions
            elif (total == 9 and hs == BJ.HARD) and d == 2:
                if tc >= 1:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions
            elif (total == 8 and hs == BJ.HARD) and d == 6:
                if tc >= 2:
                    DecisionChart.make_deviation(actions, BJ.DOUBLE)
                    return actions



        return actions

    def bja_h17_exp(hand, dealer_hand, shoe, extra_seen_cards=None, deviation_count_function=None, insurance_count=None):
        pass

    def bja_s17(hand, dealer_hand, shoe, extra_seen_cards=None, deviation_count_function=None, insurance_count=None):
        pass

    def bja_s17_exp(hand, dealer_hand, shoe, extra_seen_cards=None, deviation_count_function=None, insurance_count=None):
        pass



# CONFIG
class Config:
    DEALER_SOFT17 = BJ.HIT
    MAX_HAND_FROM_SPLIT = 4
    RESPLIT_ACE = False
    HIT_SPLIT_ACE = False
    DOUBLE_AFTER_SPLIT = True
    DOUBLE_AFTER_HIT = False
    DOUBLING_RULE = BJ.DA2
    REDOUBLE = False
    SPLIT_NONMATCHING_PAINT = True
    LATE_SURRENDER = True
    EARLY_SURRENDER = False
    SURRENDER_AFTER_HIT = False
    SURRENDER_AFTER_DOUBLE = False
    SURRENDER_AFTER_SPLIT = False
    SURRENDER_VS_ACE = True
    SURRENDER_VS_TEN = True
    PLAYING_STRATEGY = DecisionChart.bja_h17
    BETTING_STRATEGY = Betting.linear
    COUNTING_STRATEGY = Counter.hilo
    BLACKJACK_PAYS = 1.5
    PUSH22 = False
    NO_BUST_STYLE = False
    CALIFORNIA_STYLE = False
    BETTING_UNIT_SIZE = 1
    INITIAL_BANKROLL = 500
