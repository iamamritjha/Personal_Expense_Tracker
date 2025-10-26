# setup_db.py
import sqlite3, os

os.makedirs("database", exist_ok=True)
DB_PATH = os.path.join("database", "expenses.db")

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            category TEXT,
            amount REAL,
            date TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()

print("✅ Database and tables created successfully at", DB_PATH)