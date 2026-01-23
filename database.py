import sqlite3

def get_connection():
    return sqlite3.connect("stock.db", check_same_thread=False)

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

    conn.commit()
    conn.close()
