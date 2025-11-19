import sqlite3
from typing import List, Tuple

DB_NAME = "post_machine.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        code TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        data TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_program(name: str, code: str):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR REPLACE INTO programs (name, code) VALUES (?, ?)", (name, code))
    conn.commit()
    conn.close()

def save_input(name: str, data: str):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR REPLACE INTO inputs (name, data) VALUES (?, ?)", (name, data))
    conn.commit()
    conn.close()

def list_programs() -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT id, name FROM programs").fetchall()
    conn.close()
    return rows

def list_inputs() -> List[Tuple[int, str]]:
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT id, name FROM inputs").fetchall()
    conn.close()
    return rows

def load_program(name: str) -> str:
    conn = sqlite3.connect(DB_NAME)
    row = conn.execute("SELECT code FROM programs WHERE name = ?", (name,)).fetchone()
    conn.close()
    if not row:
        raise ValueError("Программа не найдена")
    return row[0]

def load_input(name: str) -> str:
    conn = sqlite3.connect(DB_NAME)
    row = conn.execute("SELECT data FROM inputs WHERE name = ?", (name,)).fetchone()
    conn.close()
    if not row:
        raise ValueError("Входные данные не найдены")
    return row[0]
