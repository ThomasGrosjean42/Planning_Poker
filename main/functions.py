import sqlite3
import json

# ==============================
# GESTION DE LA BASE DE DONNÉES 
# ==============================
def init_db():
    """
    Initialise la connexion à SQLite et crée le schéma relationnel.
    Utilisation de IF NOT EXISTS pour éviter les erreurs lors des lancements successifs.
    """
    conn = sqlite3.connect("poker.db")
    cur = conn.cursor()
    # Stockage des profils. Le username unique pour éviter les doublons.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, 
            role TEXT
        )
    """)
    # Enregistre les paramètres de la partie (Mode Strict, Moyenne ou Médiane).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            mode TEXT, 
            scrum_master_id INTEGER,
            FOREIGN KEY(scrum_master_id) REFERENCES users(id)
        )
    """)
    # Table de liaison entre sessions et utilisateurs
    # On stocke "value" en text pour accepter les valeurs spéciales : "?", "Café"
    cur.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            session_id INTEGER, 
            user_id INTEGER, 
            value TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    return conn, cur
# =================================================================
# LOGIQUE MÉTIER (USER & SESSION)
# =================================================================
def login_or_create(cur, conn, username, role):
    """
    Gère l'authentification simplifiée. Si l'utilisateur n'existe pas, 
    il est créé avec le rôle spécifié.
    """
    cur.execute("SELECT id, role FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    
    if user:
        return user[0], user[1] # Retourne ID et rôles existants
    
    cur.execute("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
    conn.commit()
    return cur.lastrowid, role
def create_session(cur, conn, name, mode, sm_id):
    """Crée une nouvelle instance de jeu avec le mode de calcul choisi."""
    cur.execute("INSERT INTO sessions (name, mode, scrum_master_id) VALUES (?, ?, ?)", 
                (name, mode, sm_id))
    conn.commit()
    return cur.lastrowid
# =================================================================
# GESTION DES VOTES
# =================================================================
def vote(cur, conn, session_id, user_id, value):
    """
    Enregistre un vote. 
    Logique : On supprime l'ancien vote de l'utilisateur pour cette session 
    avant d'insérer le nouveau (évite les doublons et permet de changer d'avis).
    """
    cur.execute("DELETE FROM votes WHERE session_id=? AND user_id=?", (session_id, user_id))
    cur.execute("INSERT INTO votes (session_id, user_id, value) VALUES (?, ?, ?)", 
                (session_id, user_id, value))
    conn.commit()

def get_votes(cur, session_id):
    """
    Récupère l'ensemble des votes pour une session donnée via une jointure (JOIN).
    Permet d'afficher directement le pseudo du joueur au lieu de son ID.
    """
    cur.execute("""
        SELECT users.username, votes.value 
        FROM votes 
        JOIN users ON users.id = votes.user_id 
        WHERE session_id=?
    """, (session_id,))
    return cur.fetchall()