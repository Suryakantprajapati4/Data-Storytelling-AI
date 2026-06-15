"""
Database module for Data Storytelling AI.
Manages SQLite storage for file history, reports, insights, and user activity.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "data_storytelling.db")


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize all required tables."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS file_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_size INTEGER,
            row_count INTEGER,
            col_count INTEGER,
            upload_timestamp TEXT NOT NULL,
            metadata TEXT
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT NOT NULL,
            title TEXT,
            content TEXT,
            created_timestamp TEXT NOT NULL,
            file_id INTEGER,
            FOREIGN KEY (file_id) REFERENCES file_history(id)
        );

        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            insight_type TEXT NOT NULL,
            insight_text TEXT NOT NULL,
            severity TEXT DEFAULT 'info',
            created_timestamp TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES file_history(id)
        );

        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            detail TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            user_query TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES file_history(id)
        );
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# File History
# ---------------------------------------------------------------------------

def save_file_record(filename: str, file_size: int, row_count: int,
                     col_count: int, metadata: Optional[Dict] = None) -> int:
    """Insert a new file record and return its id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO file_history
           (filename, file_size, row_count, col_count, upload_timestamp, metadata)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (filename, file_size, row_count, col_count,
         datetime.now().isoformat(), json.dumps(metadata or {}))
    )
    file_id = cur.lastrowid
    conn.commit()
    conn.close()
    log_activity("file_upload", f"Uploaded {filename}")
    return file_id


def get_file_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Return recent file upload records."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM file_history ORDER BY upload_timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_file_record(file_id: int) -> Optional[Dict[str, Any]]:
    """Return a single file record by id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM file_history WHERE id = ?", (file_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def save_report(report_type: str, title: str, content: str,
                file_id: Optional[int] = None) -> int:
    """Save a generated report and return its id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reports
           (report_type, title, content, created_timestamp, file_id)
           VALUES (?, ?, ?, ?, ?)""",
        (report_type, title, content, datetime.now().isoformat(), file_id)
    )
    report_id = cur.lastrowid
    conn.commit()
    conn.close()
    log_activity("report_generated", f"{report_type}: {title}")
    return report_id


def get_reports(limit: int = 20) -> List[Dict[str, Any]]:
    """Return recent reports."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM reports ORDER BY created_timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

def save_insight(file_id: Optional[int], insight_type: str,
                 insight_text: str, severity: str = "info") -> int:
    """Persist an insight record."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO insights
           (file_id, insight_type, insight_text, severity, created_timestamp)
           VALUES (?, ?, ?, ?, ?)""",
        (file_id, insight_type, insight_text, severity,
         datetime.now().isoformat())
    )
    insight_id = cur.lastrowid
    conn.commit()
    conn.close()
    return insight_id


def save_insights_batch(file_id: Optional[int],
                        insights_list: List[Dict[str, str]]) -> None:
    """Save multiple insights at once."""
    conn = get_connection()
    cur = conn.cursor()
    ts = datetime.now().isoformat()
    for ins in insights_list:
        cur.execute(
            """INSERT INTO insights
               (file_id, insight_type, insight_text, severity, created_timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (file_id, ins.get("type", "general"),
             ins.get("text", ""), ins.get("severity", "info"), ts)
        )
    conn.commit()
    conn.close()


def get_insights(file_id: Optional[int] = None,
                 limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve insights, optionally filtered by file_id."""
    conn = get_connection()
    if file_id:
        rows = conn.execute(
            "SELECT * FROM insights WHERE file_id = ? "
            "ORDER BY created_timestamp DESC LIMIT ?",
            (file_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM insights ORDER BY created_timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Chat History
# ---------------------------------------------------------------------------

def save_chat_message(file_id: Optional[int], user_query: str,
                      ai_response: str) -> int:
    """Save a chat exchange."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO chat_history
           (file_id, user_query, ai_response, timestamp)
           VALUES (?, ?, ?, ?)""",
        (file_id, user_query, ai_response, datetime.now().isoformat())
    )
    msg_id = cur.lastrowid
    conn.commit()
    conn.close()
    return msg_id


def get_chat_history(file_id: Optional[int] = None,
                     limit: int = 50) -> List[Dict[str, Any]]:
    """Return chat history."""
    conn = get_connection()
    if file_id:
        rows = conn.execute(
            "SELECT * FROM chat_history WHERE file_id = ? "
            "ORDER BY timestamp DESC LIMIT ?",
            (file_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM chat_history "
            "ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# User Activity
# ---------------------------------------------------------------------------

def log_activity(action: str, detail: str = "") -> None:
    """Record a user activity event."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO user_activity (action, detail, timestamp)
           VALUES (?, ?, ?)""",
        (action, detail, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_activity(limit: int = 30) -> List[Dict[str, Any]]:
    """Return recent user activity."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM user_activity ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Stats / Overview
# ---------------------------------------------------------------------------

def get_dashboard_stats() -> Dict[str, int]:
    """Return aggregate counts for the overview dashboard."""
    conn = get_connection()
    stats = {
        "total_files": conn.execute(
            "SELECT COUNT(*) FROM file_history").fetchone()[0],
        "total_reports": conn.execute(
            "SELECT COUNT(*) FROM reports").fetchone()[0],
        "total_insights": conn.execute(
            "SELECT COUNT(*) FROM insights").fetchone()[0],
        "total_chats": conn.execute(
            "SELECT COUNT(*) FROM chat_history").fetchone()[0],
    }
    conn.close()
    return stats
