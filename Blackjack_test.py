from Blackjack import *

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


def sim(trials = 30, decks = 2, pen = 0.75):
    n = trials

    deviators = Game(decks,pen,Counter.hilo, Betting.linear, DecisionChart.bja_h17)
    regulars = Game(decks,pen,Counter.hilo, Betting.linear, DecisionChart.basic)
    civillians = Game(decks,pen,Counter.just_gambling, Betting.flat, DecisionChart.basic)

    for i in range(n):
        deviators.play_full_shoe()
        regulars.play_full_shoe()
        civillians.play_full_shoe()
        
    dev_edge = (deviators.table.players[1].br - deviators.table.players[1].initial_br) / n
    reg_edge = (regulars.table.players[1].br - regulars.table.players[1].initial_br) / n
    civ_edge = (civillians.table.players[1].br - civillians.table.players[1].initial_br) / n

    edges = (dev_edge, reg_edge, civ_edge)
    print(edges)