import unittest
import sqlite3
from functions import (
    init_db,
    create_user,
    login,
    create_session,
    join_session,
    vote
)


class TestPlanningPoker(unittest.TestCase):

    def setUp(self):
        # Base SQLite en mémoire pour les tests
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()

        # Création des tables
        self.cur.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                role TEXT CHECK(role IN ('user', 'scrum_master'))
            )
        """)
        self.cur.execute("""
            CREATE TABLE sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                theme TEXT,
                max_users INTEGER,
                is_public INTEGER,
                status TEXT CHECK(status IN ('active','finished')),
                scrum_master_id INTEGER
            )
        """)
        self.cur.execute("""
            CREATE TABLE votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                user_id INTEGER,
                value INTEGER
            )
        """)

        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    # ---------------------------------------------------------
    # TEST 1 : Création + connexion utilisateur
    # ---------------------------------------------------------
    def test_create_and_login_user(self):
        user_id = create_user(self.cur, self.conn, "Alice", "user")
        self.assertIsNotNone(user_id)

        user = login(self.cur, "Alice")

        self.assertIsNotNone(user)
        self.assertEqual(user[0], user_id)
        self.assertEqual(user[1], "user")

    # ---------------------------------------------------------
    # TEST 2 : Création de session
    # ---------------------------------------------------------
    def test_create_session(self):
        sm_id = create_user(self.cur, self.conn, "Scrum", "scrum_master")
        session_id = create_session(self.cur, self.conn,
                                   "Sprint 1", "US Login", 5, 1, sm_id)

        self.assertIsNotNone(session_id)

        self.cur.execute("SELECT name, theme FROM sessions WHERE id=?", (session_id,))
        row = self.cur.fetchone()

        self.assertEqual(row[0], "Sprint 1")
        self.assertEqual(row[1], "US Login")

    # ---------------------------------------------------------
    # TEST 3 : Limite d'utilisateurs
    # ---------------------------------------------------------
    def test_join_session_limit(self):
        sm_id = create_user(self.cur, self.conn, "SM", "scrum_master")
        session_id = create_session(self.cur, self.conn,
                                   "Sprint", "Test", 2, 1, sm_id)

        u1 = create_user(self.cur, self.conn, "A", "user")
        u2 = create_user(self.cur, self.conn, "B", "user")
        u3 = create_user(self.cur, self.conn, "C", "user")

        # 1er user → OK
        self.assertTrue(join_session(self.cur, session_id, u1))
        vote(self.cur, self.conn, session_id, u1, 5)

        # 2e user → OK
        self.assertTrue(join_session(self.cur, session_id, u2))
        vote(self.cur, self.conn, session_id, u2, 8)

        # 3e user → REFUSÉ
        self.assertFalse(join_session(self.cur, session_id, u3))

    # ---------------------------------------------------------
    # TEST 4 : Vote + remplacement du vote
    # ---------------------------------------------------------
    def test_vote_system(self):
        sm_id = create_user(self.cur, self.conn, "SM", "scrum_master")
        session_id = create_session(self.cur, self.conn,
                                   "Sprint", "Test", 5, 1, sm_id)

        u = create_user(self.cur, self.conn, "User", "user")

        # Premier vote
        vote(self.cur, self.conn, session_id, u, 8)
        self.cur.execute("SELECT value FROM votes WHERE user_id=?", (u,))
        self.assertEqual(self.cur.fetchone()[0], 8)

        # Vote modifié
        vote(self.cur, self.conn, session_id, u, 3)
        self.cur.execute("SELECT value FROM votes WHERE user_id=?", (u,))
        self.assertEqual(self.cur.fetchone()[0], 3)


if __name__ == "__main__":
    unittest.main()
