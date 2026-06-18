"""SQLite database for job posting deduplication and history tracking."""

import sqlite3
import hashlib
import os
from datetime import datetime, date
from typing import Optional


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "job_digest.db")


def _get_db_path() -> str:
    """Return the database file path, respecting JOB_DIGEST_DB env var."""
    return os.environ.get("JOB_DIGEST_DB", DB_PATH)


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database, creating tables if needed."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create the postings table if it does not exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            posting_id TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            url TEXT,
            score INTEGER DEFAULT 0,
            description TEXT,
            date_found TEXT NOT NULL,
            date_applied TEXT,
            UNIQUE(source, posting_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_postings_score ON postings(score DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_postings_date ON postings(date_found DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_postings_title_company ON postings(title, company)
    """)
    conn.commit()


def _normalize(text: str) -> str:
    """Normalize text for fuzzy matching: lowercase, strip whitespace and common suffixes."""
    text = text.lower().strip()
    # Remove common company suffixes for matching
    for suffix in [", inc.", ", inc", " inc.", " inc", ", llc", " llc",
                   ", ltd", " ltd", " corp", " corporation", " co."]:
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
    return text


def _fuzzy_id(title: str, company: str) -> str:
    """Generate a fuzzy dedup key from title + company."""
    key = f"{_normalize(title)}|{_normalize(company)}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def posting_exists(conn: sqlite3.Connection, source: str, posting_id: str,
                   title: str = "", company: str = "") -> bool:
    """Check if a posting already exists (exact source+id or fuzzy title+company)."""
    # Exact match on source + posting_id
    row = conn.execute(
        "SELECT 1 FROM postings WHERE source = ? AND posting_id = ?",
        (source, posting_id),
    ).fetchone()
    if row:
        return True

    # Fuzzy match on normalized title + company
    if title and company:
        fuzzy = _fuzzy_id(title, company)
        rows = conn.execute(
            "SELECT title, company FROM postings"
        ).fetchall()
        for r in rows:
            if _fuzzy_id(r["title"], r["company"]) == fuzzy:
                return True

    return False


def insert_posting(conn: sqlite3.Connection, posting: dict) -> Optional[int]:
    """Insert a posting if it does not already exist. Returns row id or None if duplicate."""
    source = posting.get("source", "unknown")
    posting_id = posting.get("posting_id", "")
    title = posting.get("title", "")
    company = posting.get("company", "")

    if posting_exists(conn, source, posting_id, title, company):
        return None

    cur = conn.execute(
        """INSERT INTO postings
           (source, posting_id, title, company, location, salary, url, score, description, date_found)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            source,
            posting_id,
            title,
            company,
            posting.get("location", ""),
            posting.get("salary", ""),
            posting.get("url", ""),
            posting.get("score", 0),
            posting.get("description", ""),
            date.today().isoformat(),
        ),
    )
    conn.commit()
    return cur.lastrowid


def insert_postings_batch(conn: sqlite3.Connection, postings: list[dict]) -> list[dict]:
    """Insert a batch of postings, returning only the newly inserted ones."""
    new_postings = []
    for p in postings:
        row_id = insert_posting(conn, p)
        if row_id is not None:
            p["id"] = row_id
            new_postings.append(p)
    return new_postings


def get_todays_postings(conn: sqlite3.Connection, min_score: int = 50) -> list[dict]:
    """Get all postings found today with score >= min_score, sorted by score desc."""
    rows = conn.execute(
        """SELECT * FROM postings
           WHERE date_found = ? AND score >= ?
           ORDER BY score DESC""",
        (date.today().isoformat(), min_score),
    ).fetchall()
    return [dict(r) for r in rows]


def get_all_postings(conn: sqlite3.Connection, limit: int = 100) -> list[dict]:
    """Get all historical postings, newest first."""
    rows = conn.execute(
        "SELECT * FROM postings ORDER BY date_found DESC, score DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def mark_applied(conn: sqlite3.Connection, posting_id: int) -> bool:
    """Mark a posting as applied. Returns True if the posting was found."""
    cur = conn.execute(
        "UPDATE postings SET date_applied = ? WHERE id = ?",
        (datetime.now().isoformat(), posting_id),
    )
    conn.commit()
    return cur.rowcount > 0


def get_application_tracker(conn: sqlite3.Connection) -> list[dict]:
    """Get all postings that have been marked as applied."""
    rows = conn.execute(
        """SELECT * FROM postings
           WHERE date_applied IS NOT NULL
           ORDER BY date_applied DESC""",
    ).fetchall()
    return [dict(r) for r in rows]


def get_stats(conn: sqlite3.Connection) -> dict:
    """Get aggregate stats about the database."""
    total = conn.execute("SELECT COUNT(*) as c FROM postings").fetchone()["c"]
    applied = conn.execute(
        "SELECT COUNT(*) as c FROM postings WHERE date_applied IS NOT NULL"
    ).fetchone()["c"]
    today = conn.execute(
        "SELECT COUNT(*) as c FROM postings WHERE date_found = ?",
        (date.today().isoformat(),),
    ).fetchone()["c"]
    avg_score = conn.execute(
        "SELECT COALESCE(AVG(score), 0) as a FROM postings"
    ).fetchone()["a"]
    return {
        "total_postings": total,
        "applied": applied,
        "found_today": today,
        "average_score": round(avg_score, 1),
    }
