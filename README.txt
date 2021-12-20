The aim of ChessTrainer program is to train on opening books.
Given a PGN file, preferably on a single tree (one game, but with many variations), the computer chooses a random variation from the opponent's moves and asks the best move (or one of the bests if more are accepted) to the player, that is to say the main variation of the position (or one of the following ones, depending on the desired limit).
It is possible to use a PGN with several games ; one can imagine that each game is in this case a different opening model.
One can then launch the training on one a random game from these or on the current game.

Another program, AutoPGN, not integrated in ChessTrainer, allows to build PGN files with stockfish, possibly from a position in fen format.

To work, both programs require the addition of the chess module (python-chess) created by Niklas Fiekas.
The module can be downloaded here:
https://github.com/niklasf/python-chess
You just have to add the folder "chess" to the root of the directory where the programs are located.

You also need to have the stockfish chess engine installed to be able to start the analysis.
It is possible to modify the address of the executable, and also to modify some options.
