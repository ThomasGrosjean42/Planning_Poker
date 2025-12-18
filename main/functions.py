import sqlite3
import json

def init_db():
    conn = sqlite3.connect("poker.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, role TEXT)")
    cur.execute("""CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mode TEXT, scrum_master_id INTEGER)""")
    cur.execute("CREATE TABLE IF NOT EXISTS votes (session_id INTEGER, user_id INTEGER, value TEXT)")
    conn.commit()
    return conn, cur

def login_or_create(cur, conn, username, role):
    cur.execute("SELECT id, role FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    if user: return user[0], user[1]
    cur.execute("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
    conn.commit()
    return cur.lastrowid, role

def create_session(cur, conn, name, mode, sm_id):
    cur.execute("INSERT INTO sessions (name, mode, scrum_master_id) VALUES (?, ?, ?)", (name, mode, sm_id))
    conn.commit()
    return cur.lastrowid

def vote(cur, conn, session_id, user_id, value):
    cur.execute("DELETE FROM votes WHERE session_id=? AND user_id=?", (session_id, user_id))
    cur.execute("INSERT INTO votes (session_id, user_id, value) VALUES (?, ?, ?)", (session_id, user_id, value))
    conn.commit()

def get_votes(cur, session_id):
    cur.execute("SELECT users.username, votes.value FROM votes JOIN users ON users.id = votes.user_id WHERE session_id=?", (session_id,))
    return cur.fetchall()