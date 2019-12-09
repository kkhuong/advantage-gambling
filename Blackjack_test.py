from Blackjack import *

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