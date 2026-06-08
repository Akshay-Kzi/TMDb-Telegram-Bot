import aiosqlite
import json
import time
from pathlib import Path

from app.config import load_config
cfg = load_config()
DB_PATH = Path(cfg.DATABASE_PATH)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        # Users table
        await conn.execute("""
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
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            user_id INTEGER PRIMARY KEY,
            template TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        # Global settings table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        # Cache table for TMDb API responses
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            expires_at INTEGER
        )
        """)

        await conn.commit()


async def cache_get(key: str):
    """Get cached data if it exists and hasn't expired"""
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,)) as cur:
            row = await cur.fetchone()
    
    if row:
        value, expires_at = row[0], row[1]
        if expires_at > time.time():
            return json.loads(value)
        else:
            # Expired, delete it
            await cache_delete(key)
    return None


async def cache_set(key: str, value, ttl: int = 3600):
    """Set cached data with TTL (default 1 hour)"""
    expires_at = int(time.time()) + ttl
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), expires_at)
        )
        await conn.commit()


async def cache_delete(key: str):
    """Delete cached data"""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        await conn.commit()


async def cache_clear_expired():
    """Clear all expired cache entries"""
    current_time = int(time.time())
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM cache WHERE expires_at < ?", (current_time,))
        await conn.commit()


async def get_or_create_user(user_id: int, username: str = None):
    """Get existing user or create new one, updating username if changed"""
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        
        if not row:
            await conn.execute(
                "INSERT INTO users (id, username, query_count, last_used) VALUES (?, ?, 0, ?)",
                (user_id, username, int(time.time()))
            )
            await conn.commit()
            user = {"id": user_id, "username": username, "is_superuser": 0, "query_count": 0}
        else:
            user = dict(row)
            if user["username"] != username:
                await conn.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
                await conn.commit()
                user["username"] = username
        
        return user


async def update_user_usage(user_id: int):
    """Increment query count and update last used timestamp"""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET query_count = query_count + 1, last_used = ? WHERE id = ?",
            (int(time.time()), user_id)
        )
        await conn.commit()


async def grant_superuser(user_id: int):
    """Grant superuser privileges to a user"""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("UPDATE users SET is_superuser = 1 WHERE id = ?", (user_id,))
        await conn.commit()


async def revoke_superuser(user_id: int):
    """Revoke superuser privileges from a user"""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("UPDATE users SET is_superuser = 0 WHERE id = ?", (user_id,))
        await conn.commit()


async def is_superuser(user_id: int) -> bool:
    """Check if user is a superuser (or matches OWNER_ID)"""
    if user_id == cfg.OWNER_ID:
        return True
        
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute("SELECT is_superuser FROM users WHERE id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
    
    if row:
        return bool(row[0])
    return False


async def get_all_users():
    """Get all users with their stats"""
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT id, username, is_superuser, query_count, last_used FROM users ORDER BY query_count DESC"
        ) as cur:
            rows = await cur.fetchall()
            
    return [dict(row) for row in rows]

