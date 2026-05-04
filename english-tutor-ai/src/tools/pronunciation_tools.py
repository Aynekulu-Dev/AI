"""Pronunciation and phonetics tools for the English Tutor AI Agent."""

import logging

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)


@tool
def get_pronunciation_guide(word: str) -> str:
    """Get pronunciation guidance for an English word.

    Args:
        word: The English word to get pronunciation help for.

    Returns:
        Pronunciation guide with phonetic description and tips.
    """
    llm = ChatOllama(model="phi3", temperature=0.3)
    prompt = f"""Provide a pronunciation guide for the English word "{word}".

Include:
1. Simple phonetic spelling (using common sounds, not IPA)
2. How to break the word into syllables
3. Which syllable is stressed
4. Common pronunciation mistakes to avoid
5. A rhyming word that's easier to pronounce

Keep it simple and practical for non-native speakers.
Format clearly with bullet points."""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error("Pronunciation guide failed: %s", e)
        return f"Sorry, I couldn't generate a pronunciation guide for '{word}'."
