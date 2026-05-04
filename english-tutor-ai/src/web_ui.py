"""Streamlit Web UI for the English Tutor AI Agent."""

import asyncio
import json
import logging

import streamlit as st

from src.agents.tutor import chat
from src.database.db import (
    get_all_sessions,
    get_session_messages,
    get_student_stats,
    save_exercise_result,
    delete_session,
)
from src.tools.exercise_tools import (
    generate_fill_in_the_blank,
    generate_multiple_choice,
    generate_sentence_correction,
)
from src.tools.pronunciation_tools import get_pronunciation_guide

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="English Tutor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .tutor-message {
        background-color: #f3e5f5;
        border-left: 4px solid #7b1fa2;
    }
    .exercise-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #fff3e0;
        border-left: 4px solid #f57c00;
        margin: 1rem 0;
    }
    .stats-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e8f5e9;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def run_async(coro):
    """Run an async function from sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def init_session_state():
    """Initialize Streamlit session state."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_exercise" not in st.session_state:
        st.session_state.current_exercise = None
    if "exercise_answered" not in st.session_state:
        st.session_state.exercise_answered = False


def render_sidebar():
    """Render the sidebar with navigation and session management."""
    with st.sidebar:
        st.title("🎓 English Tutor AI")
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigate",
            ["💬 Chat", "📝 Exercises", "🔤 Pronunciation", "📊 Progress", "📚 History"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Session management
        st.subheader("Session")
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()

        if st.session_state.session_id:
            st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

        st.markdown("---")
        st.caption("Powered by Ollama (Phi-3)")

        return page


def render_chat_page():
    """Render the main chat interface."""
    st.header("💬 Chat with Your English Tutor")
    st.markdown("Type in English and I'll help you improve! I'll correct your grammar and teach you new vocabulary.")

    # Display chat history
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            with st.chat_message("user", avatar="📝"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(content)

    # Chat input
    if user_input := st.chat_input("Write something in English..."):
        # Display user message
        with st.chat_message("user", avatar="📝"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get tutor response
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("🤔 Thinking..."):
                try:
                    result = run_async(chat(user_input, st.session_state.session_id))
                    st.session_state.session_id = result["session_id"]
                    response = result["response"]
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}\n\nMake sure Ollama is running: `ollama serve`")


def render_exercises_page():
    """Render the exercises page."""
    st.header("📝 English Exercises")
    st.markdown("Practice your English with interactive exercises!")

    col1, col2 = st.columns(2)

    with col1:
        exercise_type = st.selectbox(
            "Exercise Type",
            ["Fill in the Blank", "Multiple Choice", "Sentence Correction"],
        )

    with col2:
        level = st.selectbox(
            "Difficulty Level",
            ["beginner", "intermediate", "advanced"],
        )

    topic = st.text_input(
        "Topic (optional)",
        placeholder="e.g., past tense, prepositions, articles...",
    )

    if st.button("🎲 Generate Exercise", use_container_width=True):
        with st.spinner("Creating exercise..."):
            try:
                if exercise_type == "Fill in the Blank":
                    result = generate_fill_in_the_blank.invoke(
                        {"topic": topic or "general grammar", "level": level}
                    )
                elif exercise_type == "Multiple Choice":
                    result = generate_multiple_choice.invoke(
                        {"topic": topic or "general grammar", "level": level}
                    )
                else:
                    result = generate_sentence_correction.invoke({"level": level})

                exercise = json.loads(result)
                st.session_state.current_exercise = exercise
                st.session_state.exercise_answered = False
            except Exception as e:
                st.error(f"Error generating exercise: {e}")

    # Display current exercise
    if st.session_state.current_exercise and not st.session_state.exercise_answered:
        exercise = st.session_state.current_exercise

        st.markdown("---")

        if exercise.get("type") == "sentence_correction":
            st.markdown("### ✏️ Correct this sentence:")
            st.markdown(f'> **"{exercise.get("incorrect_sentence", "")}"**')

            answer = st.text_input("Your correction:")
            if st.button("Check Answer"):
                correct = exercise.get("correct_sentence", "")
                st.session_state.exercise_answered = True

                if answer.strip().lower() == correct.strip().lower():
                    st.success(f"✅ Correct! {exercise.get('explanation', '')}")
                    _save_exercise(exercise, answer, True)
                else:
                    st.error(f"❌ Not quite. The correct answer is: **{correct}**")
                    st.info(exercise.get("explanation", ""))
                    _save_exercise(exercise, answer, False)

        else:
            st.markdown(f"### ❓ {exercise.get('question', '')}")
            options = exercise.get("options", [])

            if options:
                answer = st.radio("Choose your answer:", options, index=None)
                if st.button("Check Answer") and answer:
                    correct = exercise.get("correct_answer", "")
                    st.session_state.exercise_answered = True

                    is_correct = answer.strip() == correct.strip() or correct in answer
                    if is_correct:
                        st.success(f"✅ Correct! {exercise.get('explanation', '')}")
                    else:
                        st.error(f"❌ The correct answer is: **{correct}**")
                        st.info(exercise.get("explanation", ""))
                    _save_exercise(exercise, answer, is_correct)

    if st.session_state.exercise_answered:
        if st.button("➡️ Next Exercise"):
            st.session_state.current_exercise = None
            st.session_state.exercise_answered = False
            st.rerun()


def _save_exercise(exercise: dict, answer: str, is_correct: bool):
    """Save exercise result to database."""
    if st.session_state.session_id:
        try:
            save_exercise_result(
                session_id=st.session_state.session_id,
                exercise_type=exercise.get("type", "unknown"),
                question=exercise.get("question", exercise.get("incorrect_sentence", "")),
                correct_answer=exercise.get("correct_answer", exercise.get("correct_sentence", "")),
                student_answer=answer,
                is_correct=is_correct,
            )
        except Exception as e:
            logger.warning("Failed to save exercise result: %s", e)


def render_pronunciation_page():
    """Render the pronunciation practice page."""
    st.header("🔤 Pronunciation Guide")
    st.markdown("Enter any English word to get pronunciation help!")

    word = st.text_input("Enter a word:", placeholder="e.g., pronunciation, comfortable, schedule...")

    if st.button("🔊 Get Pronunciation Guide", use_container_width=True) and word:
        with st.spinner(f"Getting pronunciation guide for '{word}'..."):
            try:
                result = get_pronunciation_guide.invoke(word)
                st.markdown("---")
                st.markdown(result)
            except Exception as e:
                st.error(f"Error: {e}")

    # Common difficult words
    st.markdown("---")
    st.subheader("💡 Common Difficult Words")
    difficult_words = [
        "pronunciation", "comfortable", "schedule", "environment",
        "necessary", "restaurant", "temperature", "Wednesday",
        "February", "library", "colleague", "entrepreneur",
    ]
    cols = st.columns(4)
    for i, w in enumerate(difficult_words):
        with cols[i % 4]:
            if st.button(w, key=f"word_{w}"):
                with st.spinner(f"Loading '{w}'..."):
                    try:
                        result = get_pronunciation_guide.invoke(w)
                        st.session_state[f"pron_{w}"] = result
                    except Exception as e:
                        st.error(str(e))

    # Show results for clicked words
    for w in difficult_words:
        if f"pron_{w}" in st.session_state:
            with st.expander(f"📖 {w}"):
                st.markdown(st.session_state[f"pron_{w}"])


def render_progress_page():
    """Render the student progress page."""
    st.header("📊 Your Progress")

    if not st.session_state.session_id:
        st.info("Start a conversation first to track your progress!")
        return

    try:
        stats = get_student_stats(st.session_state.session_id)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Messages Sent", stats["messages_sent"])
        with col2:
            st.metric("Grammar Corrections", stats["grammar_corrections"])
        with col3:
            st.metric("Exercises Done", stats["exercises_total"])
        with col4:
            st.metric("Accuracy", f"{stats['accuracy']}%")

        st.markdown("---")

        # Tips based on stats
        st.subheader("💡 Tips")
        if stats["messages_sent"] < 5:
            st.info("Keep chatting! The more you practice, the more you'll improve.")
        elif stats["grammar_corrections"] > stats["messages_sent"] * 0.5:
            st.warning("You're making progress! Pay extra attention to grammar rules.")
        else:
            st.success("Great job! Your grammar is improving!")

        if stats["exercises_total"] == 0:
            st.info("Try some exercises to test your knowledge! Go to 📝 Exercises.")
        elif stats["accuracy"] >= 80:
            st.success("Excellent accuracy! Try harder exercises.")
        elif stats["accuracy"] >= 50:
            st.info("Good progress! Keep practicing to improve your accuracy.")

    except Exception as e:
        st.error(f"Error loading stats: {e}")


def render_history_page():
    """Render the conversation history page."""
    st.header("📚 Conversation History")

    try:
        sessions = get_all_sessions()

        if not sessions:
            st.info("No conversations yet. Start chatting to build your history!")
            return

        for session in sessions:
            with st.expander(
                f"📅 {session['created_at'][:16]} — {session['message_count']} messages"
            ):
                messages = get_session_messages(session["id"])
                for msg in messages:
                    role_icon = "📝" if msg["role"] == "human" else "🎓"
                    st.markdown(f"**{role_icon} {msg['role'].title()}:** {msg['content'][:200]}...")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📂 Load Session", key=f"load_{session['id']}"):
                        st.session_state.session_id = session["id"]
                        st.session_state.messages = [
                            {
                                "role": "user" if m["role"] == "human" else "assistant",
                                "content": m["content"],
                            }
                            for m in messages
                        ]
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{session['id']}"):
                        delete_session(session["id"])
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading history: {e}")


def main():
    """Main Streamlit app."""
    init_session_state()
    page = render_sidebar()

    if page == "💬 Chat":
        render_chat_page()
    elif page == "📝 Exercises":
        render_exercises_page()
    elif page == "🔤 Pronunciation":
        render_pronunciation_page()
    elif page == "📊 Progress":
        render_progress_page()
    elif page == "📚 History":
        render_history_page()


if __name__ == "__main__":
    main()
