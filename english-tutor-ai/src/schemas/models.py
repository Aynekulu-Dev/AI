"""Pydantic models for the English Tutor AI Agent."""

from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message from the user."""

    message: str = Field(..., description="The user's message text")
    session_id: Optional[str] = Field(
        default=None, description="Optional session ID for conversation continuity"
    )


class GrammarCorrection(BaseModel):
    """A single grammar correction."""

    error: str = Field(..., description="The incorrect text")
    correction: str = Field(..., description="The corrected text")
    explanation: str = Field(..., description="Explanation of the grammar rule")


class GrammarCheckResult(BaseModel):
    """Result of a grammar check."""

    has_errors: bool = Field(..., description="Whether errors were found")
    corrections: list[GrammarCorrection] = Field(
        default_factory=list, description="List of corrections"
    )
    corrected_text: str = Field(default="", description="The full corrected text")


class VocabularyItem(BaseModel):
    """A vocabulary suggestion."""

    word: str = Field(..., description="The vocabulary word or phrase")
    definition: str = Field(..., description="Definition of the word")
    example: str = Field(..., description="Example sentence using the word")
    tip: str = Field(default="", description="Memory tip")


class TutorResponse(BaseModel):
    """Response from the English tutor agent."""

    response: str = Field(..., description="The tutor's response message")
    grammar_feedback: Optional[GrammarCheckResult] = Field(
        default=None, description="Grammar corrections if any errors were found"
    )
    vocabulary_tip: Optional[VocabularyItem] = Field(
        default=None, description="Optional vocabulary suggestion"
    )
    session_id: str = Field(..., description="Session ID for conversation continuity")


class ConversationState(BaseModel):
    """State for the LangGraph conversation flow."""

    messages: list[dict] = Field(default_factory=list)
    session_id: str = Field(default="")
    user_input: str = Field(default="")
    grammar_feedback: Optional[GrammarCheckResult] = Field(default=None)
    tutor_response: str = Field(default="")
    message_count: int = Field(default=0)
