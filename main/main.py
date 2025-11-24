import sqlite3
from functions import init_db, create_user, login, create_session, list_sessions, join_session, vote, show_votes


#  ****************** #
# INTERACTIVE PROGRAM #
#  ****************** #

def main():
    conn, cur = init_db()
    print("\n=== Bienvenue dans le Planning Poker ===\n")

    username = input("Entrez votre pseudo : ")
    user = login(cur, username)

    if user is None:
        role = input("Voulez-vous être 'user' ou 'scrum_master' ? ").strip().lower()
        if role not in ["user", "scrum_master"]:
            print("Rôle invalide.")
            return
        user_id = create_user(cur, conn, username, role)
        if user_id is None:
            print("Erreur lors de la création du compte.")
            return
        user = (user_id, role)
    else:
        user_id, role = user

    user_id, role = user
    print(f"\nConnecté en tant que {username} ({role})\n")

#****************************** #
# SCRUM MASTER : CREATE SESSION #
#****************************** #
    if role == "scrum_master":
        print("=== Création d'une session ===")
        name = input("Nom de la session : ")
        theme = input("Thème / User Story : ")
        max_users = int(input("Nombre max d'utilisateurs : "))
        pub = input("Session publique ? (o/n) : ").lower()
        is_public = 1 if pub=="o" else 0

        session_id = create_session(cur, conn, name, theme, max_users, is_public, user_id)
        print(f"\n✔ Session créée avec succès ! ID = {session_id}\n")

#  ********************************* #
# USER / SCRUM MASTER : JOIN SESSION #
#  ********************************* #

    print("=== Liste des sessions actives ===")
    sessions = list_sessions(cur)
    if not sessions:
        print("Aucune session disponible.")
        return

    for s in sessions:
        print(f"[ID {s[0]}] {s[1]} — {s[2]} (max {s[3]}) {'[publique]' if s[4] else '[privée]'}")

#  ****************** #
# Selection sécurisée #
#  ****************** #
    while True:
        sid_input = input("Entrez l'ID de la session à rejoindre : ")
        if not sid_input.isdigit():
            print("Merci d'entrer un nombre.")
            continue
        session_id = int(sid_input)
        if not any(s[0]==session_id for s in sessions):
            print("ID inexistant.")
            continue
        if not join_session(cur, session_id, user_id):
            print("La session est pleine.")
            continue
        break

    print(f"\n✔ Vous avez rejoint la session {session_id} !")
#  ***********
    # VOTE
#  ***********

    print("\n=== Vote ===")
    print("Cartes disponibles : 1, 2, 3, 5, 8, 13")
    valid_cards = [1,2,3,5,8,13]

    while True:
        val_input = input("Votre vote : ")
        if not val_input.isdigit() or int(val_input) not in valid_cards:
            print("Carte invalide.")
            continue
        value = int(val_input)
        break

    vote(cur, conn, session_id, user_id, value)
    print("\n✔ Vote enregistré !")

    # Afficher tous les votes
    print("\n=== Résultats actuels ===")
    show_votes(cur, session_id)

if __name__ == "__main__":
    main()
