import sqlite3
#  *************
# DATABASE INIT
#  *************

def init_db():
    conn = sqlite3.connect("poker.db")
    cur = conn.cursor()

    # Table utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            role TEXT CHECK(role IN ('user', 'scrum_master'))
        )
    """)

    # Table sessions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            theme TEXT,
            max_users INTEGER,
            is_public INTEGER,
            status TEXT CHECK(status IN ('active','finished')),
            scrum_master_id INTEGER
        )
    """)

    # Table votes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            user_id INTEGER,
            value INTEGER
        )
    """)

    conn.commit()
    return conn, cur
#  ***************
# USER MANAGEMENT
#  ***************

def create_user(cur, conn, username, role):
    cur.execute("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
    user_id = cur.lastrowid
    conn.commit()
    return user_id



def login(cur, username):
    cur.execute("SELECT id, role FROM users WHERE username=?", (username,))
    return cur.fetchone()

# SESSION MANAGEMENT
def create_session(cur, conn, name, theme, max_users, is_public, scrum_master_id):
    cur.execute("""
        INSERT INTO sessions(name, theme, max_users, is_public, status, scrum_master_id)
        VALUES (?, ?, ?, ?, 'active', ?)
    """, (name, theme, max_users, is_public, scrum_master_id))
    conn.commit()
    return cur.lastrowid

def list_sessions(cur):
    cur.execute("SELECT id, name, theme, max_users, is_public, status FROM sessions WHERE status='active'")
    return cur.fetchall()

def join_session(cur, session_id, user_id):
    # Nombre d’utilisateurs déjà dans la session
    cur.execute("SELECT COUNT(*) FROM votes WHERE session_id=?", (session_id,))
    count_users = cur.fetchone()[0]

    # Max utilisateurs
    cur.execute("SELECT max_users FROM sessions WHERE id=?", (session_id,))
    max_users = cur.fetchone()[0]

    return count_users < max_users
#  ************
    # VOTE
#  ************

def vote(cur, conn, session_id, user_id, value):
    # Supprime l’ancien vote si existe
    cur.execute("DELETE FROM votes WHERE session_id=? AND user_id=?", (session_id, user_id))
    cur.execute("INSERT INTO votes(session_id, user_id, value) VALUES (?, ?, ?)",
                (session_id, user_id, value))
    conn.commit()

def show_votes(cur, session_id):
    cur.execute("""
        SELECT users.username, votes.value
        FROM votes
        JOIN users ON users.id = votes.user_id
        WHERE votes.session_id=?
    """, (session_id,))
    rows = cur.fetchall()
    for r in rows:
        print(f"{r[0]} → {r[1]}")
#  ************************
    # INTERACTIVE PROGRAM
#  ************************

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

#************************************
    # SCRUM MASTER : CREATE SESSION
#************************************
    if role == "scrum_master":
        print("=== Création d'une session ===")
        name = input("Nom de la session : ")
        theme = input("Thème / User Story : ")
        max_users = int(input("Nombre max d'utilisateurs : "))
        pub = input("Session publique ? (o/n) : ").lower()
        is_public = 1 if pub=="o" else 0

        session_id = create_session(cur, conn, name, theme, max_users, is_public, user_id)
        print(f"\n✔ Session créée avec succès ! ID = {session_id}\n")

#  **********************************
# USER / SCRUM MASTER : JOIN SESSION
#  **********************************

    print("=== Liste des sessions actives ===")
    sessions = list_sessions(cur)
    if not sessions:
        print("Aucune session disponible.")
        return

    for s in sessions:
        print(f"[ID {s[0]}] {s[1]} — {s[2]} (max {s[3]}) {'[publique]' if s[4] else '[privée]'}")

#  ************************
    # Selection sécurisée
#  ************************
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
