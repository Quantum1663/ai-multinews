import os, sqlite3
from contextlib import closing
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "app.db"))

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with closing(get_conn()) as con, con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT UNIQUE,
            source TEXT,
            text TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            misinfo REAL,
            hate REAL,
            cred REAL,
            agree REAL
        )
        """)

def upsert_article(aid: str, title: str, text: str, url: Optional[str], source: Optional[str],
                   misinfo: float, hate: float, cred: float, agree: float):
    with closing(get_conn()) as con, con:
        con.execute("""
        INSERT INTO articles (id, title, text, url, source, misinfo, hate, cred, agree)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title, text=excluded.text, url=excluded.url, source=excluded.source,
            misinfo=excluded.misinfo, hate=excluded.hate, cred=excluded.cred, agree=excluded.agree
        """, (aid, title, text, url, source, misinfo, hate, cred, agree))

def get_by_url(url: str) -> Optional[Dict[str, Any]]:
    with closing(get_conn()) as con:
        cur = con.execute("SELECT * FROM articles WHERE url = ?", (url,))
        row = cur.fetchone()
    return _row_to_dict(row) if row else None

def get_article(aid: str) -> Optional[Dict[str, Any]]:
    with closing(get_conn()) as con:
        cur = con.execute("SELECT * FROM articles WHERE id = ?", (aid,))
        row = cur.fetchone()
    return _row_to_dict(row) if row else None

def list_articles(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    with closing(get_conn()) as con:
        cur = con.execute("""
          SELECT id, title, source, misinfo, hate, cred, agree, created_at
          FROM articles
          ORDER BY datetime(created_at) DESC
          LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = cur.fetchall()
    return [ _row_to_feeditem(r) for r in rows ]

def _row_to_dict(row):
    # row order: id, title, url, source, text, created_at, misinfo, hate, cred, agree
    return {
        "id": row[0], "title": row[1], "url": row[2], "source": row[3],
        "text": row[4], "created_at": row[5],
        "misinfo": row[6], "hate": row[7], "cred": row[8], "agree": row[9],
    }

def _row_to_feeditem(row):
    return {
        "id": row[0], "title": row[1], "source": row[2],
        "m": row[3] or 0.0, "h": row[4] or 0.0, "cred": row[5] or 0.0, "agree": row[6] or 0.0,
        "created_at": row[7],
    }
