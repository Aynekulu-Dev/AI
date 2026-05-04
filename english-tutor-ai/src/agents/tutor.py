"""English Tutor AI Agent built with LangGraph."""

import logging
import uuid
from typing import Annotated

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from src.prompts.tutor_prompts import TUTOR_SYSTEM_PROMPT
from src.schemas.models import GrammarCheckResult
from src.tools.grammar_tools import check_grammar

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the tutor agent graph."""

    messages: Annotated[list, add_messages]
    session_id: str
    user_input: str
    grammar_feedback: str
    tutor_response: str
    message_count: int


def create_llm(temperature: float = 0.7) -> ChatOllama:
    """Create a ChatOllama instance with the phi3 model."""
    return ChatOllama(
        model="phi3",
        temperature=temperature,
        num_predict=1024,
    )


def check_user_grammar(state: AgentState) -> AgentState:
    """Check the user's input for grammar errors."""
    user_input = state["user_input"]

    if not user_input or len(user_input.split()) < 3:
        return {**state, "grammar_feedback": ""}

    try:
        result = check_grammar.invoke(user_input)
        grammar_result = GrammarCheckResult.model_validate_json(result)

        if grammar_result.has_errors and grammar_result.corrections:
            feedback_parts = ["📝 **Grammar Tips:**"]
            for correction in grammar_result.corrections:
                feedback_parts.append(
                    f'  • "{correction.error}" → "{correction.correction}" '
                    f"({correction.explanation})"
                )
            feedback = "\n".join(feedback_parts)
            return {**state, "grammar_feedback": feedback}
    except Exception as e:
        logger.warning("Grammar check skipped: %s", e)

    return {**state, "grammar_feedback": ""}


def generate_response(state: AgentState) -> AgentState:
    """Generate the tutor's response using the LLM (without tool binding)."""
    llm = create_llm()

    messages = list(state["messages"])

    has_system = any(
        isinstance(m, SystemMessage)
        or (isinstance(m, dict) and m.get("role") == "system")
        for m in messages
    )
    if not has_system:
        messages.insert(0, SystemMessage(content=TUTOR_SYSTEM_PROMPT))

    grammar_feedback = state.get("grammar_feedback", "")
    if grammar_feedback:
        context_note = (
            f"\n[Internal note - grammar issues found in user's message, "
            f"address these naturally in your response:\n{grammar_feedback}]"
        )
        messages.append(SystemMessage(content=context_note))

    try:
        response = llm.invoke(messages)

        full_response = response.content
        if grammar_feedback:
            full_response = f"{grammar_feedback}\n\n---\n\n{response.content}"

        return {
            **state,
            "messages": [response],
            "tutor_response": full_response,
            "message_count": state.get("message_count", 0) + 1,
        }
    except Exception as e:
        logger.error("Response generation failed: %s", e)
        error_msg = (
            "I'm having trouble connecting to the language model. "
            "Please make sure Ollama is running with: `ollama serve`"
        )
        return {
            **state,
            "messages": [AIMessage(content=error_msg)],
            "tutor_response": error_msg,
            "message_count": state.get("message_count", 0) + 1,
        }


def build_tutor_graph() -> StateGraph:
    """Build and compile the LangGraph for the English Tutor agent.

    Flow: User Input → [Check Grammar] → [Generate Response] → Output
    Grammar checking is done as a dedicated node (not via LLM tool calling),
    so this works with models like Phi-3 that don't support tool binding.
    """
    graph = StateGraph(AgentState)

    graph.add_node("check_grammar", check_user_grammar)
    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("check_grammar")
    graph.add_edge("check_grammar", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()


# Compile the graph once at module level
tutor_agent = build_tutor_graph()

# In-memory conversation store (also persisted to SQLite)
conversation_store: dict[str, list[dict]] = {}


async def chat(message: str, session_id: str | None = None) -> dict:
    """Process a chat message through the tutor agent.

    Args:
        message: The user's message.
        session_id: Optional session ID for conversation continuity.

    Returns:
        A dict with the tutor's response, session_id, and metadata.
    """
    from src.database.db import create_session, save_message

    if not session_id:
        session_id = create_session()

    # Save user message to database
    save_message(session_id, "human", message)

    previous_messages = conversation_store.get(session_id, [])
    all_messages = previous_messages + [HumanMessage(content=message)]

    initial_state: AgentState = {
        "messages": all_messages,
        "session_id": session_id,
        "user_input": message,
        "grammar_feedback": "",
        "tutor_response": "",
        "message_count": len(previous_messages),
    }

    result = await tutor_agent.ainvoke(initial_state)

    conversation_store[session_id] = list(result["messages"])

    # Save tutor response to database
    save_message(session_id, "ai", result["tutor_response"])

    return {
        "response": result["tutor_response"],
        "session_id": session_id,
        "message_count": result["message_count"],
    }
