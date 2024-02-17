# Musical companion - Mode performance

Ce programme est destiné à permettre aux utilisateurs de jouer leurs performances en étant accompagné par des fourmis artificielles.

Une performance typique est structurée en plusieurs "graphes" contenant chacun des fourmis jouant des notes de musique.

L'utilisateur contrôle une fourmis sur l'un de ces graphes, et influence la colonie en déposant des phéromones lorsqu'il joue des notes.
Un graphe peut être un simple métronome, une mélodie, une mesure de percussions complexes, ou encore une ligne de basse.

# Utilisation

## Dépendences

Ce programme nécessite d'avoir les programmes/bibliothèques suivantes installées sur le système:
- Python 3
- Bibliothèques python:
    - mido
    - pyqt6*
    - pydot*
- Graphviz*

* pour l'interface seulement

## Configuration

Il existe deux types de fichiers nécessaires à la configuration:

Les fichiers dits "de graphes" sont les fichiers contenant une description au format json d'un graphe.

Les fichiers dits "globaux" servent à configurer la performance. Ils contiennent la liste des graphes à ajouter, ainsi que les informations globales telles que le tempo ou le taux d'évaporation des phéromones.
