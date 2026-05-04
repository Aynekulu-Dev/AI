"""Tests for the database module."""

import os
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

from src.database.db import (
    create_session,
    delete_session,
    get_all_sessions,
    get_session_messages,
    get_student_stats,
    save_exercise_result,
    save_grammar_correction,
    save_message,
)


@pytest.fixture(autouse=True)
def temp_db(tmp_path):
    """Use a temporary database for each test."""
    db_path = tmp_path / "test_tutor.db"
    with patch("src.database.db.DB_PATH", db_path):
        yield db_path


def test_create_session():
    """Test creating a new session."""
    session_id = create_session("Test Student", "beginner")
    assert session_id is not None
    assert len(session_id) == 36  # UUID format


def test_save_and_get_messages():
    """Test saving and retrieving messages."""
    session_id = create_session()
    save_message(session_id, "human", "Hello tutor!")
    save_message(session_id, "ai", "Hello! How can I help?")

    messages = get_session_messages(session_id)
    assert len(messages) == 2
    assert messages[0]["role"] == "human"
    assert messages[0]["content"] == "Hello tutor!"
    assert messages[1]["role"] == "ai"


def test_get_all_sessions():
    """Test getting all sessions."""
    create_session("Student 1")
    create_session("Student 2")

    sessions = get_all_sessions()
    assert len(sessions) >= 2


def test_save_grammar_correction():
    """Test saving grammar corrections."""
    session_id = create_session()
    save_grammar_correction(
        session_id,
        "I goes to school",
        "I go to school",
        [{"error": "goes", "correction": "go", "explanation": "subject-verb agreement"}],
    )
    stats = get_student_stats(session_id)
    assert stats["grammar_corrections"] == 1


def test_save_exercise_result():
    """Test saving exercise results."""
    session_id = create_session()
    save_exercise_result(session_id, "fill_in_the_blank", "Q1", "answer", "answer", True)
    save_exercise_result(session_id, "multiple_choice", "Q2", "B", "A", False)

    stats = get_student_stats(session_id)
    assert stats["exercises_total"] == 2
    assert stats["exercises_correct"] == 1
    assert stats["accuracy"] == 50.0


def test_student_stats_empty():
    """Test stats for a session with no activity."""
    session_id = create_session()
    stats = get_student_stats(session_id)
    assert stats["messages_sent"] == 0
    assert stats["grammar_corrections"] == 0
    assert stats["exercises_total"] == 0
    assert stats["accuracy"] == 0


def test_delete_session():
    """Test deleting a session."""
    session_id = create_session()
    save_message(session_id, "human", "Hello")
    delete_session(session_id)

    messages = get_session_messages(session_id)
    assert len(messages) == 0
