Le programme ChessTrainer a pour but de permettre de s’entraîner sur un livre d’ouverture.
Étant donné un fichier PGN, préférentiellement sur un seul arbre (une seule partie, mais avec plein de variations), l’ordinateur choisit pour les coups de l’adversaire des variantes au hasard et demande le meilleur coup (ou un des meilleurs si on en accepte davantage) au joueur, c’est à dire la variante principale de la position (ou une des suivantes selon la limite voulue).
Il est possible d’utiliser un PGN avec plusieurs parties ; on peut imaginer que chaque partie est dans ce cas un modèle d’ouverture différente.
On peut alors lancer l’entraînement sur une de ces parties au hasard ou sur la partie en cours.

Un autre programme, AutoPGN, non intégré à ChessTrainer, permet de construire des fichiers PGN à l’aide de stockfish, à partir éventuellement d’une position au format fen.

Pour fonctionner, les deux programmes nécessitent l’ajout du module chess (python-chess) créé par Niklas Fiekas.
Le module peut être téléchargé ici :
https://github.com/niklasf/python-chess
Sa documentation est là :
https://python-chess.readthedocs.io/en/latest/
Il suffit d’ajouter le dossier « chess » à la racine du répertoire où se trouve les programmes.

Il faut également avoir le moteur d’échecs stockfish installé pour pouvoir lancer l’analyse.
Il est possible de modifier l’adresse de l’exécutable, et de modifier également certaines options.
