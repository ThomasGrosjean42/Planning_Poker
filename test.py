# test_models.py
import pytest
from models import create_tables, add_user, get_user

def test_create_tables():
    """Vérifie que les tables sont créées"""
    conn = create_tables()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert c.fetchone() is not None
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
    assert c.fetchone() is not None

def test_add_and_get_user():
    """Test l'ajout et la récupération d'un utilisateur"""
    conn = create_tables()
    user_id = add_user(conn, "Alice")
    user = get_user(conn, user_id)
    assert user is not None
    assert user[1] == "Alice"  # Le username doit correspondre

def test_multiple_users():
    """Test l'ajout de plusieurs utilisateurs"""
    conn = create_tables()
    id1 = add_user(conn, "Alice")
    id2 = add_user(conn, "Bob")
    user1 = get_user(conn, id1)
    user2 = get_user(conn, id2)
    assert user1[1] == "Alice"
    assert user2[1] == "Bob"
