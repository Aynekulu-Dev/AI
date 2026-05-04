"""Grammar checking tools for the English Tutor AI Agent."""

import json
import logging
import re

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from src.prompts.tutor_prompts import GRAMMAR_CHECK_PROMPT
from src.schemas.models import GrammarCheckResult, GrammarCorrection

logger = logging.getLogger(__name__)


def _parse_grammar_response(response_text: str) -> GrammarCheckResult:
    """Parse the LLM response into a GrammarCheckResult."""
    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            corrections = [
                GrammarCorrection(**c) for c in data.get("corrections", [])
            ]
            return GrammarCheckResult(
                has_errors=data.get("has_errors", len(corrections) > 0),
                corrections=corrections,
                corrected_text=data.get("corrected_text", ""),
            )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Failed to parse grammar check response: %s", e)

    return GrammarCheckResult(has_errors=False, corrections=[], corrected_text="")


@tool
def check_grammar(text: str) -> str:
    """Check the grammar of the given English text and return corrections.

    Args:
        text: The English text to check for grammar errors.

    Returns:
        A JSON string with grammar corrections and explanations.
    """
    llm = ChatOllama(model="phi3", temperature=0.1)
    prompt = GRAMMAR_CHECK_PROMPT.format(text=text)

    try:
        response = llm.invoke(prompt)
        result = _parse_grammar_response(response.content)
        return result.model_dump_json()
    except Exception as e:
        logger.error("Grammar check failed: %s", e)
        return GrammarCheckResult(
            has_errors=False, corrections=[], corrected_text=text
        ).model_dump_json()


@tool
def get_word_definition(word: str) -> str:
    """Get the definition and usage examples of an English word.

    Args:
        word: The English word to define.

    Returns:
        A definition with usage examples.
    """
    llm = ChatOllama(model="phi3", temperature=0.3)
    prompt = f"""Provide a clear definition of the English word "{word}".
Include:
1. Part of speech (noun, verb, adjective, etc.)
2. Definition in simple English
3. Two example sentences
4. Any common synonyms

Keep it concise and student-friendly."""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error("Word definition failed: %s", e)
        return f"Sorry, I couldn't look up the word '{word}' right now."


@tool
def suggest_improvement(text: str) -> str:
    """Suggest improvements to make the English text more natural and fluent.

    Args:
        text: The English text to improve.

    Returns:
        Suggestions for improving the text.
    """
    llm = ChatOllama(model="phi3", temperature=0.3)
    prompt = f"""As an English tutor, suggest improvements for this text to make it more natural:

"{text}"

Provide:
1. An improved version
2. Brief explanation of what you changed and why
3. A vocabulary tip related to the topic

Keep explanations simple and encouraging."""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error("Improvement suggestion failed: %s", e)
        return "Sorry, I couldn't generate suggestions right now."
