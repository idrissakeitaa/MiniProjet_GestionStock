import sqlite3

DB_NAME = "stock.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def creer_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS produits (
        code INTEGER PRIMARY KEY,
        nom TEXT,
        description TEXT,
        quantite INTEGER,
        prix REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS commandes (
        code_cmd INTEGER PRIMARY KEY,
        code_prod INTEGER,
        quantite INTEGER,
        total REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS historique (
        code_cmd INTEGER,
        code_prod INTEGER,
        quantite INTEGER,
        total REAL
    )
    """)

    conn.commit()
    conn.close()
