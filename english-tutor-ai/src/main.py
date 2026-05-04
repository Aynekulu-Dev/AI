"""Main entry point for the English Tutor AI Agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import logging

from src.agents.tutor import chat
from src.schemas.models import ChatMessage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print the welcome banner."""
    print("\n" + "=" * 60)
    print("  🎓 English Tutor AI Agent")
    print("  Powered by Ollama (Phi-3)")
    print("=" * 60)
    print("\n  Welcome! I'm your English tutor.")
    print("  I'll help you improve your English skills.")
    print("  Type your message in English and I'll help you learn!")
    print("\n  Commands:")
    print("    'quit' or 'exit' - End the session")
    print("    'new'            - Start a new conversation")
    print("    'help'           - Show this help message")
    print("=" * 60 + "\n")


async def interactive_chat():
    """Run the interactive chat loop."""
    print_banner()

    session_id = None

    while True:
        try:
            user_input = input("\n📝 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! Keep practicing your English! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("\nGoodbye! Keep practicing your English! 👋")
            break

        if user_input.lower() == "new":
            session_id = None
            print("\n🔄 Started a new conversation!")
            continue

        if user_input.lower() == "help":
            print_banner()
            continue

        print("\n🤔 Thinking...\n")

        try:
            result = await chat(user_input, session_id)
            session_id = result["session_id"]

            print(f"🎓 Tutor: {result['response']}")
            print(f"\n   [Message #{result['message_count']}]")

        except Exception as e:
            logger.error("Error: %s", e)
            print(f"\n❌ Error: {e}")
            print("Make sure Ollama is running: ollama serve")


def main():
    """Main entry point."""
    asyncio.run(interactive_chat())


if __name__ == "__main__":
    main()
