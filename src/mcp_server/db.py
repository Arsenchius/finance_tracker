import sqlite3

def init_db():
    with sqlite3.connect("transactions.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            type TEXT CHECK(type IN ('income', 'expense')),
            category TEXT,
            amount REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
