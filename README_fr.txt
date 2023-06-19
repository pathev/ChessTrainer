Le programme ChessTrainer a pour but de permettre de s’entraîner sur un livre d’ouverture aux échecs.

Étant donné un fichier PGN, préférentiellement sur un seul arbre (une seule partie, mais avec plein de variations), l’ordinateur choisit pour les coups de l’adversaire des variantes au hasard et demande le meilleur coup (ou un des meilleurs si on en accepte davantage) au joueur, c’est à dire la variante principale de la position (ou une des suivantes selon la limite voulue).

Il est possible d’utiliser un PGN avec plusieurs parties ; on peut imaginer que chaque partie est dans ce cas un modèle d’ouverture différente.

On peut lancer l’entraînement sur : une partie au hasard, la partie en cours ou même la position actuelle.

Le choix au hasard du coup peut être uniforme, mais aussi dépendant de l’ordre, ce qui signifie que les premières variations seront préférentiellement choisies par rapport aux suivantes (à l’aide d’une distribution beta-binomiale).

Les fichiers PGN peuvent être un peu édités, par exemple en ajoutant des commentaires et des flèches de quatre différentes couleurs en utilisant le clic droit et les touches ctrl et/ou alt.

Un autre programme, AutoPGN, non intégré à ChessTrainer, permet de construire des fichiers PGN à l’aide de stockfish, à partir éventuellement d’une position au format fen.

Les deux programmes nécessitent l’ajout du module chess (python-chess) créé par Niklas Fiekas.
Le module peut être téléchargé ici :
https://github.com/niklasf/python-chess
Il suffit d’ajouter le dossier « chess » à la racine du répertoire où se trouvent les programmes.

ChessTrainer nécessite également le module scipy :
https://github.com/scipy/scipy

Il faut également avoir le moteur d’échecs stockfish installé pour pouvoir lancer l’analyse.
Il est possible de modifier l’adresse de l’exécutable, et de modifier également certaines options.
