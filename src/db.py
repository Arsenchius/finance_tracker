import sqlite3

conn = sqlite3.connect("transactions.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    type TEXT CHECK(type IN ('income', 'expense')),
    category TEXT,
    amount REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)

conn.commit()


def add_transaction(data):
    cursor.execute(
        "INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, ?, ?, ?, ?)",
        (data["user_id"], data["type"], data["category"], data["amount"], data["date"]),
    )
    conn.commit()


def delete_transaction(user_id: str, category: str, date: str):
    cursor.execute(
        "DELETE FROM transactions WHERE user_id=? AND category=? AND date(date)=date(?)",
        (user_id, category, date),
    )
    conn.commit()


def list_transactions(user_id: str):
    cursor.execute("SELECT * FROM transactions WHERE user_id=?", (user_id,))
    return cursor.fetchall()


def update_transaction(user_id: str, date: str, updates: dict):
    set_clauses = []
    values = []

    for field, value in updates.items():
        set_clauses.append(f"{field} = ?")
        values.append(value)

    set_expr = ", ".join(set_clauses)
    values.extend([user_id, date])  # фильтр по user_id и дате

    cursor.execute(
        f"""
        UPDATE transactions
        SET {set_expr}
        WHERE user_id = ? AND date(date) = date(?)
    """,
        values,
    )
    conn.commit()
