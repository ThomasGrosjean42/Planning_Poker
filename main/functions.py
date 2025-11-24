import sqlite3

#  ************* #
# DATABASE INIT  #
#  ************* #

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



#  *************** #
# USER MANAGEMENT  #
#  *************** #

def create_user(cur, conn, username, role):
    cur.execute("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
    user_id = cur.lastrowid
    conn.commit()
    return user_id

def login(cur, username):
    cur.execute("SELECT id, role FROM users WHERE username=?", (username,))
    return cur.fetchone()



# ****************** #
# SESSION MANAGEMENT #
# ****************** #

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



#  **** #
#  VOTE #
#  **** #

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


        