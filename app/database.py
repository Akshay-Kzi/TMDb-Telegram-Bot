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
        is_admin INTEGER DEFAULT 0,
        is_superuser INTEGER DEFAULT 0,
        query_count INTEGER DEFAULT 0,
        last_used INTEGER
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


def get_or_create_user(user_id: int, username: str = None):
    """Get existing user or create new one"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    
    if not user:
        cur.execute(
            "INSERT INTO users (id, username, query_count, last_used) VALUES (?, ?, 0, ?)",
            (user_id, username, int(time.time()))
        )
        conn.commit()
        user = {"id": user_id, "username": username, "is_superuser": 0, "query_count": 0}
    else:
        user = dict(user)
    
    conn.close()
    return user


def update_user_usage(user_id: int):
    """Increment query count and update last used timestamp"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE users SET query_count = query_count + 1, last_used = ? WHERE id = ?",
        (int(time.time()), user_id)
    )
    
    conn.commit()
    conn.close()


def grant_superuser(user_id: int):
    """Grant superuser privileges to a user"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("UPDATE users SET is_superuser = 1 WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()


def revoke_superuser(user_id: int):
    """Revoke superuser privileges from a user"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("UPDATE users SET is_superuser = 0 WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()


def is_superuser(user_id: int) -> bool:
    """Check if user is a superuser"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT is_superuser FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return bool(row[0])
    return False


def get_all_users():
    """Get all users with their stats"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, username, is_superuser, query_count, last_used FROM users ORDER BY query_count DESC")
    users = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    return users
