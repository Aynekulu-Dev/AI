"""English exercise generation tools for the English Tutor AI Agent."""

import json
import logging
import re
from typing import Optional

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)


@tool
def generate_fill_in_the_blank(topic: str, level: str = "beginner") -> str:
    """Generate a fill-in-the-blank exercise.

    Args:
        topic: The topic for the exercise (e.g., "past tense", "prepositions").
        level: Difficulty level (beginner, intermediate, advanced).

    Returns:
        A JSON string with the exercise question, options, and correct answer.
    """
    llm = ChatOllama(model="phi3", temperature=0.5)
    prompt = f"""Create a fill-in-the-blank English exercise about "{topic}" for a {level} student.

Respond in this exact JSON format:
{{
    "type": "fill_in_the_blank",
    "question": "The sentence with _____ for the blank",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": "the correct option",
    "explanation": "Brief explanation of why this is correct"
}}

Only output the JSON, nothing else."""

    try:
        response = llm.invoke(prompt)
        json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if json_match:
            return json_match.group()
        return json.dumps({
            "type": "fill_in_the_blank",
            "question": f"Practice exercise about {topic} coming soon!",
            "options": [],
            "correct_answer": "",
            "explanation": "Could not generate exercise.",
        })
    except Exception as e:
        logger.error("Exercise generation failed: %s", e)
        return json.dumps({"error": str(e)})


@tool
def generate_multiple_choice(topic: str, level: str = "beginner") -> str:
    """Generate a multiple choice grammar exercise.

    Args:
        topic: The grammar topic (e.g., "articles", "verb tenses").
        level: Difficulty level (beginner, intermediate, advanced).

    Returns:
        A JSON string with the question, choices, and correct answer.
    """
    llm = ChatOllama(model="phi3", temperature=0.5)
    prompt = f"""Create a multiple choice English grammar question about "{topic}" for a {level} student.

Respond in this exact JSON format:
{{
    "type": "multiple_choice",
    "question": "Which sentence is grammatically correct?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "A",
    "explanation": "Brief explanation of why this is correct"
}}

Only output the JSON, nothing else."""

    try:
        response = llm.invoke(prompt)
        json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if json_match:
            return json_match.group()
        return json.dumps({
            "type": "multiple_choice",
            "question": f"Grammar question about {topic} coming soon!",
            "options": [],
            "correct_answer": "",
            "explanation": "Could not generate exercise.",
        })
    except Exception as e:
        logger.error("Exercise generation failed: %s", e)
        return json.dumps({"error": str(e)})


@tool
def generate_sentence_correction(level: str = "beginner") -> str:
    """Generate a sentence correction exercise.

    Args:
        level: Difficulty level (beginner, intermediate, advanced).

    Returns:
        A JSON string with an incorrect sentence and the correction.
    """
    llm = ChatOllama(model="phi3", temperature=0.5)
    prompt = f"""Create a sentence correction exercise for a {level} English student.

Provide a sentence with a common grammar mistake and the corrected version.

Respond in this exact JSON format:
{{
    "type": "sentence_correction",
    "incorrect_sentence": "The sentence with a mistake",
    "correct_sentence": "The corrected sentence",
    "error_type": "Type of error (e.g., subject-verb agreement, tense)",
    "explanation": "Brief explanation of the error and correction"
}}

Only output the JSON, nothing else."""

    try:
        response = llm.invoke(prompt)
        json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if json_match:
            return json_match.group()
        return json.dumps({
            "type": "sentence_correction",
            "incorrect_sentence": "Exercise coming soon!",
            "correct_sentence": "",
            "error_type": "",
            "explanation": "Could not generate exercise.",
        })
    except Exception as e:
        logger.error("Exercise generation failed: %s", e)
        return json.dumps({"error": str(e)})
