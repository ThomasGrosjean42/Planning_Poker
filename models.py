import sqlite3

def create_tables():
    """Crée une base de données SQLite en mémoire"""
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    max_users INTEGER NOT NULL
                )''')
    conn.commit()
    return conn

def add_user(conn, username):
    """Ajoute un utilisateur à la table users"""
    c = conn.cursor()
    c.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    return c.lastrowid

def get_user(conn, user_id):
    """Récupère un utilisateur par son ID"""
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return c.fetchone()
