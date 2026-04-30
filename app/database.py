import sqlite3
import json
import time
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

    # Cache table for TMDb API responses
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        value TEXT,
        expires_at INTEGER
    )
    """)

    conn.commit()
    conn.close()


def cache_get(key: str):
    """Get cached data if it exists and hasn't expired"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        value, expires_at = row
        if expires_at > time.time():
            return json.loads(value)
        else:
            # Expired, delete it
            cache_delete(key)
    return None


def cache_set(key: str, value, ttl: int = 3600):
    """Set cached data with TTL (default 1 hour)"""
    conn = get_connection()
    cur = conn.cursor()
    
    expires_at = int(time.time()) + ttl
    cur.execute(
        "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
        (key, json.dumps(value), expires_at)
    )
    
    conn.commit()
    conn.close()


def cache_delete(key: str):
    """Delete cached data"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM cache WHERE key = ?", (key,))
    
    conn.commit()
    conn.close()


def cache_clear_expired():
    """Clear all expired cache entries"""
    conn = get_connection()
    cur = conn.cursor()
    
    current_time = int(time.time())
    cur.execute("DELETE FROM cache WHERE expires_at < ?", (current_time,))
    
    conn.commit()
    conn.close()
