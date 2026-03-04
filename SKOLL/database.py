
import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            session_count INTEGER DEFAULT 0,
            drift_score REAL DEFAULT 0.0,
            trust_score REAL DEFAULT 100.0,
            location TEXT,
            registration_time TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS edit_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            request_time TEXT,
            location TEXT,
            token TEXT,
            token_expiry TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cols = [row[1] for row in c.execute("PRAGMA table_info(edit_requests)").fetchall()]
    if 'status' not in cols:
        c.execute("ALTER TABLE edit_requests ADD COLUMN status TEXT DEFAULT 'Pending'")

    c.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            process_name TEXT,
            cpu_usage REAL,
            window_title TEXT,
            ts TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS vulnerability_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signature TEXT,
            pattern TEXT,
            severity REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS behavior_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            user_id INTEGER,
            drift_score REAL,
            trust_score REAL,
            action_taken TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
