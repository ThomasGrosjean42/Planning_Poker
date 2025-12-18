# Projet Planning Poker - M1 Informatique Rémi Galant et Thomas Grosjean

# Présentation
Ce projet est une application de Planning Poker développée en Python (et Tkinter pour interface graphique) dans un cadre de gestion de projet Agile (Scrum). 
L'application permet d'enregistrer des participants, de charger un backlog au format JSON, et de réaliser des sessions de vote tour par tour avec plusieurs modes de calcul pour les résultats finaux.

# Fonctionnalités
- Gestion des utilisateurs : Inscription avec rôles (user ou scrum_master).
- Gestion des données : Utilisation de SQLite3 pour stocker les joueurs, les sessions et les votes en cours.
- Backlog externe : Importation des UserStories via un fichier "backlog.json".
- Modes de calcul : 
    - Strict : Unanimité requise.
    - Moyenne: Calcul de la moyenne.
    - Médiane : Calcul de la valeur médiane des votes.
    - Export des résultats : Sauvegarde automatique de chaque estimation dans un fichier "resultats_session.json".

# Structure du Projet
- "gui.py" : Point d'entrée de l'application (Interface Tkinter).
- "functions.py" : Logique métier et requêtes SQL.
- "unit_test.py" : Tests unitaires (Database, Logique métier, Statistiques).
- "backlog.json" : Fichier d'exemple contenant les tâches à estimer.
- "cartes/" : Dossier contenant les visuels des cartes de vote.

