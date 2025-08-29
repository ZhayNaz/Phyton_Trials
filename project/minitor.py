import sqlite3
from datetime import datetime

DB_FILE = "lab_logs.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS logs(
              id INTEGER PRIMARY KEY AUTOINCREMENT
              laboratory TEXT,
              action TEXT,
              time TEXT,
              date TEXT
            )
    ''')
    conn.commit()
    conn.close()

def log_entry(laboratory, action):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (laboratory, actions, time, date) VALUE (laboratory, action, time, date)"),
    (laboratory, action, time_str, date_str)
    conn.commit()
    conn.close()