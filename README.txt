The aim of ChessTrainer program is to train on opening chess books.

Given a PGN file, preferably on a single tree (one game, but with many variations), the computer chooses a random variation from the opponent's moves and asks the best move (or one of the bests if more are accepted) to the player, in other words the main variation of the position (or one of the following ones, depending on the desired limit).

It is possible to use a PGN with several games ; one can imagine that each game is in this case a different opening model.

One can start the training on: a random game, the current game or even the current position.

The random choice of move from variations can be uniform, but also order dependant, which means the firsts variations will be more likely to be chosen than the nexts ones (using a beta-binomial distribution).

PGN files can be slightly edited, e.g. by adding comments and arrows with four different colors using right-clic with ctrl and/or alt keys.

Another program, AutoPGN, not integrated in ChessTrainer, allows to build PGN files with stockfish, possibly from a position in fen format.

Both programs require the addition of the chess module (python-chess) created by Niklas Fiekas.
The module can be downloaded here:
https://github.com/niklasf/python-chess
You just have to add the folder "chess" to the root of the directory where the programs are located.

ChessTrainer also needs scipy module:
https://github.com/scipy/scipy

You also need to have the stockfish chess engine installed to be able to start the analysis.
It is possible to modify the address of the executable, and also to modify some options.
