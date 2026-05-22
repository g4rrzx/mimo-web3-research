"""SQLite storage layer for research agent."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional


SCHEMA = """
-- Whale transactions tracked
CREATE TABLE IF NOT EXISTS whale_txs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain TEXT NOT NULL,
    tx_hash TEXT UNIQUE NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    value_eth REAL,
    value_usd REAL,
    token_symbol TEXT,
    block_number INTEGER,
    timestamp INTEGER NOT NULL,
    label TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_whale_chain_ts ON whale_txs(chain, timestamp);
CREATE INDEX IF NOT EXISTS idx_whale_from ON whale_txs(from_address);

-- Social posts collected
CREATE TABLE IF NOT EXISTS social_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    post_id TEXT NOT NULL,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT,
    engagement_score REAL,
    sentiment REAL,
    timestamp INTEGER NOT NULL,
    keywords TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    UNIQUE(platform, post_id)
);

CREATE INDEX IF NOT EXISTS idx_social_platform_ts ON social_posts(platform, timestamp);

-- News articles
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    summary TEXT,
    published_at INTEGER,
    relevance_score REAL,
    tags TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_news_source_ts ON news_articles(source, published_at);

-- Daily briefings generated
CREATE TABLE IF NOT EXISTS briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    sections TEXT,
    metrics TEXT,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Alert log (rate limiting)
CREATE TABLE IF NOT EXISTS alerts_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    target TEXT NOT NULL,
    payload TEXT,
    sent_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_alerts_type_ts ON alerts_log(alert_type, sent_at);

-- MiMo API call cache (avoid duplicate analysis)
CREATE TABLE IF NOT EXISTS mimo_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT UNIQUE NOT NULL,
    prompt_hash TEXT NOT NULL,
    response TEXT NOT NULL,
    tokens_used INTEGER,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_mimo_key ON mimo_cache(cache_key);
"""


class Database:
    """SQLite wrapper with simple ORM-like helpers."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Initialize tables."""
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        """Context manager for DB connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def insert_whale_tx(self, **kwargs) -> Optional[int]:
        """Insert whale transaction. Returns row ID or None if duplicate."""
        try:
            with self.connect() as conn:
                cur = conn.execute(
                    """INSERT INTO whale_txs
                    (chain, tx_hash, from_address, to_address, value_eth,
                     value_usd, token_symbol, block_number, timestamp, label)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (kwargs.get("chain"), kwargs.get("tx_hash"),
                     kwargs.get("from_address"), kwargs.get("to_address"),
                     kwargs.get("value_eth"), kwargs.get("value_usd"),
                     kwargs.get("token_symbol"), kwargs.get("block_number"),
                     kwargs.get("timestamp"), kwargs.get("label")),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def insert_social_post(self, **kwargs) -> Optional[int]:
        """Insert social post. Returns row ID or None if duplicate."""
        try:
            with self.connect() as conn:
                cur = conn.execute(
                    """INSERT INTO social_posts
                    (platform, post_id, author, content, url,
                     engagement_score, sentiment, timestamp, keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (kwargs.get("platform"), kwargs.get("post_id"),
                     kwargs.get("author"), kwargs.get("content"),
                     kwargs.get("url"), kwargs.get("engagement_score"),
                     kwargs.get("sentiment"), kwargs.get("timestamp"),
                     kwargs.get("keywords")),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def insert_news(self, **kwargs) -> Optional[int]:
        """Insert news article. Returns row ID or None if duplicate."""
        try:
            with self.connect() as conn:
                cur = conn.execute(
                    """INSERT INTO news_articles
                    (source, title, url, summary, published_at, relevance_score, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (kwargs.get("source"), kwargs.get("title"),
                     kwargs.get("url"), kwargs.get("summary"),
                     kwargs.get("published_at"), kwargs.get("relevance_score"),
                     kwargs.get("tags")),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def save_briefing(self, date: str, content: str,
                      sections: str = None, metrics: str = None):
        """Save daily briefing."""
        with self.connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO briefings
                (date, content, sections, metrics) VALUES (?, ?, ?, ?)""",
                (date, content, sections, metrics),
            )

    def get_recent_whales(self, hours: int = 24, limit: int = 50) -> list:
        """Get recent whale transactions."""
        cutoff = int(__import__("time").time()) - (hours * 3600)
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM whale_txs WHERE timestamp >= ?
                ORDER BY value_usd DESC LIMIT ?""",
                (cutoff, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_recent_social(self, hours: int = 24, limit: int = 100) -> list:
        """Get recent social posts."""
        cutoff = int(__import__("time").time()) - (hours * 3600)
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM social_posts WHERE timestamp >= ?
                ORDER BY engagement_score DESC LIMIT ?""",
                (cutoff, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_recent_news(self, hours: int = 24, limit: int = 50) -> list:
        """Get recent news articles."""
        cutoff = int(__import__("time").time()) - (hours * 3600)
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM news_articles WHERE published_at >= ?
                ORDER BY relevance_score DESC, published_at DESC LIMIT ?""",
                (cutoff, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def can_alert(self, alert_type: str, target: str,
                  cooldown_seconds: int) -> bool:
        """Check if we can send alert (rate limiting)."""
        cutoff = int(__import__("time").time()) - cooldown_seconds
        with self.connect() as conn:
            row = conn.execute(
                """SELECT COUNT(*) as cnt FROM alerts_log
                WHERE alert_type = ? AND target = ? AND sent_at >= ?""",
                (alert_type, target, cutoff),
            ).fetchone()
            return row["cnt"] == 0

    def log_alert(self, alert_type: str, target: str, payload: str = None):
        """Log sent alert."""
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO alerts_log (alert_type, target, payload)
                VALUES (?, ?, ?)""",
                (alert_type, target, payload),
            )

    def get_mimo_cache(self, cache_key: str) -> Optional[str]:
        """Get cached MiMo response."""
        with self.connect() as conn:
            row = conn.execute(
                "SELECT response FROM mimo_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
            return row["response"] if row else None

    def set_mimo_cache(self, cache_key: str, prompt_hash: str,
                       response: str, tokens: int = 0):
        """Store MiMo response in cache."""
        with self.connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO mimo_cache
                (cache_key, prompt_hash, response, tokens_used)
                VALUES (?, ?, ?, ?)""",
                (cache_key, prompt_hash, response, tokens),
            )
