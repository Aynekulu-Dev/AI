"""Tests for the English Tutor AI Agent."""

import pytest

from src.schemas.models import (
    ChatMessage,
    ConversationState,
    GrammarCheckResult,
    GrammarCorrection,
    TutorResponse,
    VocabularyItem,
)


def test_chat_message_creation():
    """Test creating a ChatMessage."""
    msg = ChatMessage(message="Hello, how are you?")
    assert msg.message == "Hello, how are you?"
    assert msg.session_id is None


def test_chat_message_with_session():
    """Test creating a ChatMessage with a session ID."""
    msg = ChatMessage(message="Hello", session_id="test-123")
    assert msg.session_id == "test-123"


def test_grammar_correction():
    """Test GrammarCorrection model."""
    correction = GrammarCorrection(
        error="I goes",
        correction="I go",
        explanation="Use base form of verb with 'I'",
    )
    assert correction.error == "I goes"
    assert correction.correction == "I go"


def test_grammar_check_result_no_errors():
    """Test GrammarCheckResult with no errors."""
    result = GrammarCheckResult(has_errors=False, corrections=[], corrected_text="")
    assert not result.has_errors
    assert len(result.corrections) == 0


def test_grammar_check_result_with_errors():
    """Test GrammarCheckResult with errors."""
    corrections = [
        GrammarCorrection(
            error="I goes",
            correction="I go",
            explanation="Subject-verb agreement",
        )
    ]
    result = GrammarCheckResult(
        has_errors=True,
        corrections=corrections,
        corrected_text="I go to school",
    )
    assert result.has_errors
    assert len(result.corrections) == 1


def test_vocabulary_item():
    """Test VocabularyItem model."""
    vocab = VocabularyItem(
        word="diligent",
        definition="Having or showing care in one's work",
        example="She is a diligent student.",
        tip="Think of 'diligent' as 'doing it gently and carefully'",
    )
    assert vocab.word == "diligent"


def test_conversation_state_defaults():
    """Test ConversationState default values."""
    state = ConversationState()
    assert state.messages == []
    assert state.session_id == ""
    assert state.message_count == 0
    assert state.grammar_feedback is None
