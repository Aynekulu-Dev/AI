"""FastAPI web server for the English Tutor AI Agent."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.agents.tutor import chat, conversation_store
from src.schemas.models import ChatMessage, TutorResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="English Tutor AI Agent",
    description="An AI-powered English tutor that helps you improve your language skills",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "English Tutor AI Agent",
        "model": "phi3 (via Ollama)",
    }


@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """Send a message to the English tutor and get a response.

    The tutor will:
    - Check your grammar and provide corrections
    - Respond naturally to your message
    - Suggest vocabulary improvements
    """
    try:
        result = await chat(message.message, message.session_id)
        return {
            "response": result["response"],
            "session_id": result["session_id"],
            "message_count": result["message_count"],
        }
    except Exception as e:
        logger.error("Chat error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}. "
            "Make sure Ollama is running with: ollama serve",
        )


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get the conversation history for a session."""
    if session_id not in conversation_store:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = conversation_store[session_id]
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": [
            {"role": m.type if hasattr(m, "type") else "unknown", "content": m.content}
            for m in messages
            if hasattr(m, "content")
        ],
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session."""
    if session_id in conversation_store:
        del conversation_store[session_id]
    return {"status": "deleted", "session_id": session_id}
