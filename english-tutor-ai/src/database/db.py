"""SQLite database for conversation history persistence."""

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "tutor.db"


def get_connection() -> sqlite3.Connection:
    """Get a SQLite database connection, creating tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create database tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            student_name TEXT DEFAULT '',
            student_level TEXT DEFAULT 'beginner',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS grammar_corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            original_text TEXT NOT NULL,
            corrected_text TEXT NOT NULL,
            corrections_json TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS exercise_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            exercise_type TEXT NOT NULL,
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_corrections_session ON grammar_corrections(session_id);
        CREATE INDEX IF NOT EXISTS idx_exercises_session ON exercise_results(session_id);
    """)


def create_session(student_name: str = "", level: str = "beginner") -> str:
    """Create a new conversation session. Returns the session ID."""
    session_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO sessions (id, student_name, student_level) VALUES (?, ?, ?)",
            (session_id, student_name, level),
        )
        conn.commit()
    finally:
        conn.close()
    return session_id


def save_message(session_id: str, role: str, content: str) -> None:
    """Save a message to the database."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )
        conn.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )
        conn.commit()
    finally:
        conn.close()


def get_session_messages(session_id: str) -> list[dict]:
    """Get all messages for a session."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_sessions() -> list[dict]:
    """Get all sessions with message counts."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT s.id, s.student_name, s.student_level, s.created_at, s.updated_at,
                   COUNT(m.id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
        """).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def save_grammar_correction(
    session_id: str, original: str, corrected: str, corrections: list[dict]
) -> None:
    """Save a grammar correction record."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO grammar_corrections (session_id, original_text, corrected_text, corrections_json) VALUES (?, ?, ?, ?)",
            (session_id, original, corrected, json.dumps(corrections)),
        )
        conn.commit()
    finally:
        conn.close()


def save_exercise_result(
    session_id: str,
    exercise_type: str,
    question: str,
    correct_answer: str,
    student_answer: str,
    is_correct: bool,
) -> None:
    """Save an exercise result."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO exercise_results (session_id, exercise_type, question, correct_answer, student_answer, is_correct) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, exercise_type, question, correct_answer, student_answer, is_correct),
        )
        conn.commit()
    finally:
        conn.close()


def get_student_stats(session_id: str) -> dict:
    """Get student statistics for a session."""
    conn = get_connection()
    try:
        msg_count = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id = ? AND role = 'human'",
            (session_id,),
        ).fetchone()[0]

        correction_count = conn.execute(
            "SELECT COUNT(*) FROM grammar_corrections WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]

        exercise_rows = conn.execute(
            "SELECT COUNT(*) as total, SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct FROM exercise_results WHERE session_id = ?",
            (session_id,),
        ).fetchone()

        return {
            "messages_sent": msg_count,
            "grammar_corrections": correction_count,
            "exercises_total": exercise_rows["total"] or 0,
            "exercises_correct": exercise_rows["correct"] or 0,
            "accuracy": (
                round((exercise_rows["correct"] or 0) / exercise_rows["total"] * 100, 1)
                if exercise_rows["total"]
                else 0
            ),
        }
    finally:
        conn.close()


def delete_session(session_id: str) -> None:
    """Delete a session and all its data."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM grammar_corrections WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM exercise_results WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()
