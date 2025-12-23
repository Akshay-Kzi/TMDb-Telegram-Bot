import sqlite3
from pathlib import Path

from app.config import load_config
cfg = load_config()
DB_PATH = Path(cfg.DATABASE_PATH)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)

    # Templates table (per-user override)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS templates (
        user_id INTEGER PRIMARY KEY,
        template TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Global settings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()
