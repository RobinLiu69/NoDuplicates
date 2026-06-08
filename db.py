import sqlite3
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "index.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS media (
    guild_id    INTEGER,
    media_type  TEXT,
    media_id    TEXT,
    channel_id  INTEGER,
    message_id  INTEGER,
    author_id   INTEGER,
    author_name TEXT,
    jump_url    TEXT,
    created_at  INTEGER,
    PRIMARY KEY (guild_id, media_type, media_id)
);
CREATE INDEX IF NOT EXISTS idx_media_created ON media(created_at);
"""

_conn: sqlite3.Connection | None = None


def connect() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH)
        _conn.row_factory = sqlite3.Row
        _conn.executescript(SCHEMA)
        _conn.commit()
    return _conn


def record(guild_id, media_type, media_id, channel_id, message_id,
           author_id, author_name, jump_url, created_at=None) -> bool:
    if created_at is None:
        created_at = int(time.time())
    cur = connect().execute(
        "INSERT INTO media "
        "(guild_id, media_type, media_id, channel_id, message_id, "
        "author_id, author_name, jump_url, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(guild_id, media_type, media_id) DO UPDATE SET "
        "channel_id=excluded.channel_id, message_id=excluded.message_id, "
        "author_id=excluded.author_id, author_name=excluded.author_name, "
        "jump_url=excluded.jump_url, created_at=excluded.created_at "
        "WHERE excluded.created_at < media.created_at",
        (guild_id, media_type, media_id, channel_id, message_id,
         author_id, author_name, jump_url, created_at),
    )
    connect().commit()
    return cur.rowcount > 0


def find(guild_id, media_type, media_id) -> sqlite3.Row | None:
    return connect().execute(
        "SELECT * FROM media WHERE guild_id = ? AND media_type = ? AND media_id = ?",
        (guild_id, media_type, media_id),
    ).fetchone()


def remove_message(guild_id, message_id) -> None:
    connect().execute(
        "DELETE FROM media WHERE guild_id = ? AND message_id = ?",
        (guild_id, message_id),
    )
    connect().commit()


def prune(guild_id, ttl_days) -> int:
    cutoff = int(time.time()) - ttl_days * 86400
    cur = connect().execute(
        "DELETE FROM media WHERE guild_id = ? AND created_at < ?",
        (guild_id, cutoff),
    )
    connect().commit()
    return cur.rowcount


def count(guild_id) -> int:
    row = connect().execute(
        "SELECT COUNT(*) AS n FROM media WHERE guild_id = ?",
        (guild_id,),
    ).fetchone()
    return row["n"] if row else 0
