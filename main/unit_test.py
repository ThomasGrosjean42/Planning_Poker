import unittest
import sqlite3
from functions import init_db, login_or_create, create_session, vote, get_votes

class TestPlanningPoker(unittest.TestCase):

    def setUp(self):
        """Initialisation d'une base de données vierge en mémoire pour chaque test"""
        # On utilise une base en mémoire pour ne pas polluer poker.db
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        
        # On recrée la structure de la DB
        self.cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, role TEXT)")
        self.cur.execute("CREATE TABLE sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mode TEXT, scrum_master_id INTEGER)")
        self.cur.execute("CREATE TABLE votes (session_id INTEGER, user_id INTEGER, value TEXT)")
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_login_or_create(self):
        """Teste la création et la récupération d'un utilisateur"""
        uid, role = login_or_create(self.cur, self.conn, "Rémi", "scrum_master")
        self.assertIsNotNone(uid)
        self.assertEqual(role, "scrum_master")

    def test_voting_logic(self):
        """Vérifie l'enregistrement et la mise à jour d'un vote"""
        # 1. Créer les données nécessaires
        uid, _ = login_or_create(self.cur, self.conn, "Thomas", "user")
        sid = create_session(self.cur, self.conn, "Test Session", "Strict", uid)

        # 2. Effectuer un premier vote
        vote(self.cur, self.conn, sid, uid, "5")
        
        # 3. Vérifier que le vote existe
        votes = get_votes(self.cur, sid)
        self.assertEqual(len(votes), 1, "Le vote devrait être enregistré")
        self.assertEqual(votes[0][0], "Thomas")
        self.assertEqual(votes[0][1], "5")

        # 4. Modifier le vote (Mise à jour)
        vote(self.cur, self.conn, sid, uid, "13")
        votes_updated = get_votes(self.cur, sid)
        
        self.assertEqual(len(votes_updated), 1, "Il ne devrait y avoir qu'un seul vote après mise à jour")
        self.assertEqual(votes_updated[0][1], "13", "La valeur du vote devrait être 13")
    def test_math_logic(self):
        """Vérifie les calculs de moyenne et médiane"""
        import statistics
        
        # Simulation de votes reçus par get_votes
        mock_votes = [('Rémi', '5'), ('Thomas', '13'), ('Alice', '8')]
        
        # Extraction des nombres
        values = [int(v[1]) for v in mock_votes] 
        
        # Test Moyenne
        moyenne = sum(values) / len(values)
        self.assertAlmostEqual(moyenne, 8.67, places=2)
        
        # Test Médiane
        mediane = statistics.median(values)
        self.assertEqual(mediane, 8)

if __name__ == "__main__":
    unittest.main()