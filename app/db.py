"""
Simple SQLite helper for logs table.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'logs.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            ip TEXT,
            input_text TEXT,
            result TEXT,
            reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_log(ts, ip, input_text, result, reason=''):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO logs (ts, ip, input_text, result, reason) VALUES (?, ?, ?, ?, ?)',
              (ts, ip, input_text, result, reason))
    conn.commit()
    conn.close()

def get_latest_logs(limit=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT ts, ip, input_text, result, reason FROM logs ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows