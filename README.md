# Advantage Play Library
## Introduction
Every casino game has an house edge---that is how the casino makes money in the long run. However, we can overcome the house edge and gain additional edge over the casino if have information on one of the dealer's hole card (e.g. rank, a range of possible rank, or perhaps the exact rank and suit). The most common way to get hole card information is to find an incompetent dealer who flashes her card as she is putting it on the table.

Other form of advantage play is counting card at a Blackjack table and play/bet accordingly to "the count": an indicator of player's advantage and expected return.

With hole card or deck composition information, the advantage player can adjust their strategies and betting amount accordingly to take advantage of the situation.

## Future Work (for this project and in the AP field)
Eliot Jacobson Ph.D. has shown that for Ultimate Texas Hold'em, the optimal edge is 22.3286% (using perfect computer play---not feasible in a casino); James Grosjean's playing decisions in _Beyond Counting_ gives an edge of 20.74%; the decisions in this code base gives an edge of about 18%. I hope that this code base will enable mathematicians and researchers to find improvements on playing decisions (especially for Ultimate Texas Hold'em) to beat my 18% or even beat 20.74% by using only logic that a human can process in real time.


I plan to study these games in the future when I have time:
* Mississippi Stud
* (Card Based) Craps
* High Card Flush
* Blackjack --- other counting systems besides Hi-Lo

## This Library
This repository contains code to simulate casino games that has a possible player's advantage. Example games are
* Three Card Poker (a.k.a. One Card Poker or OCP) by hole carding
* Ultimate Texas Hold'em (UTH) by hole carding [still buggy]
* Blackjack by counting card [comming soon]

Most of the Advantage Play strategies used in this library are from James Grosjean's _Exhibit CAA: Beyond Counting_ book. Out of respect for Grosjean's hard work, I will not repeat the simple description on how to make decisions in OCP and UTH, but you can probably find it in the source code's logic.




# Example Usage
This library is useful for:
* practicing hole carding strategies.... so you won't make a mistake when there is money on the table
* calculating house edge... to check that the program has no bug
* calculating player edge... to see if the games are profitable for you
* mathematicians and researchers hoping to improve the field or their own game.



To play Three Card Poker and/or to practice the Three Card Poker hole carding strategies:
```
>>>> from OCP import *
>>>> play_holecarding_strategy()
How many hands would you like to play >>> 9



===========[New Three Card Poker Hand]===========
Player Hand: ['As', 'Qh', '7c']
Dealer's Holecard: Qs
0-Fold or 1-Call >>>
```

To calculate player's advantage (i.e., average return) for Three Card Poker with perfect play:
```
>>>> from OCP import *
>>>> calculate_holecarding_ev(trials = 100000)
0.03019
>>>> calculate_basic_strategy_ev(trials = 100000)
-0.04123
>>>>
```

[I will write better documentation for the UTH game soon.]




# Data and Statistics
Some of the data used to calculate the player's advantage for Ultimate Texas Hold'em are in the Jupyter Notebook file `UTH_Data.ipynb`.



# Acknowledgements
I have used the [deuces](https://github.com/worldveil/deuces) library from worldveil. This have made my work on the UTH game 100000x easier.

I would also like to thank James Grosjean for everything he wrote in _Beyond Counting_, especially the Ultimate Texas Hold'em chapter.
