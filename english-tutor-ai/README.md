# 🎓 English Tutor AI Agent

An AI-powered English language tutor built with **Python**, **LangChain**, **LangGraph**, and **Ollama** (Phi-3 model). It helps students improve their English through interactive conversation with real-time grammar correction and vocabulary building.

## Features

- **Grammar Correction** — Automatically detects grammar errors and explains the rules
- **Vocabulary Building** — Suggests new words and phrases during conversation
- **Writing Improvement** — Provides suggestions to make your English more natural
- **Word Definitions** — Look up any English word with examples
- **Pronunciation Guide** — Get pronunciation tips for any English word
- **Interactive Exercises** — Fill-in-the-blank, multiple choice, sentence correction
- **Progress Tracking** — Track your messages, corrections, and exercise scores
- **Streamlit Web UI** — Beautiful web interface with chat, exercises, and history
- **Interactive CLI** — Chat directly in your terminal
- **REST API** — FastAPI web server for integration with other apps
- **SQLite Database** — Persistent conversation history and exercise results
- **Conversation Memory** — Remembers context within a session

## Architecture

```
english-tutor-ai/
├── src/
│   ├── agents/
│   │   └── tutor.py              # LangGraph agent with grammar check → response flow
│   ├── prompts/
│   │   └── tutor_prompts.py      # System prompts for the tutor
│   ├── schemas/
│   │   └── models.py             # Pydantic data models
│   ├── tools/
│   │   ├── grammar_tools.py      # Grammar checking & vocabulary tools
│   │   ├── pronunciation_tools.py # Pronunciation guide tool
│   │   └── exercise_tools.py     # Exercise generation tools
│   ├── database/
│   │   └── db.py                 # SQLite database for persistence
│   ├── main.py                   # Interactive CLI chat
│   ├── api.py                    # FastAPI web server
│   └── web_ui.py                 # Streamlit web interface
├── tests/
│   └── test_tutor.py             # Unit tests
├── data/                          # SQLite database stored here
├── requirements.txt
├── .env.example
└── README.md
```

### How It Works (LangGraph Flow)

```
User Input → [Check Grammar] → [Generate Response] → Output
                                        ↓
                              [Save to SQLite DB]
```

1. **Check Grammar Node**: Analyzes user's text for grammar errors
2. **Generate Response Node**: Creates a tutor response incorporating grammar feedback
3. **Database**: All messages and corrections are persisted to SQLite

## Prerequisites

- **Python 3.10+**
- **Conda** (Miniconda or Anaconda) — [Install Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- **Ollama** installed and running ([Install Ollama](https://ollama.com/download))
- **Phi-3** model pulled in Ollama

## Setup

### 1. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from: https://ollama.com/download
```

### 2. Pull the Phi-3 Model

```bash
ollama pull phi3
```

### 3. Start Ollama Server

```bash
ollama serve
```

### 4. Clone & Install Dependencies (Conda)

```bash
# Clone the project
git clone https://github.com/Aynekulu-Dev/AI.git
cd AI/english-tutor-ai

# Create a conda environment
conda create -n english-tutor python=3.10 -y

# Activate the environment
conda activate english-tutor

# Install dependencies
pip install -r requirements.txt
```

<details>
<summary>Alternative: Using venv (without Conda)</summary>

```bash
cd english-tutor-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

</details>

### 5. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env if you want to change default settings
```

## Usage

### Option 1: Interactive CLI Chat

```bash
python -m src.main
```

This opens an interactive chat where you can practice English:

```
============================================================
  🎓 English Tutor AI Agent
  Powered by Ollama (Phi-3)
============================================================

  Welcome! I'm your English tutor.
  Type your message in English and I'll help you learn!

  Commands:
    'quit' or 'exit' - End the session
    'new'            - Start a new conversation
    'help'           - Show this help message
============================================================

📝 You: I goes to school yesterday

🤔 Thinking...

🎓 Tutor: 📝 **Grammar Tips:**
  • "I goes" → "I went" (Use past tense for yesterday; 'go' becomes 'went')

---

Great effort! Let me help you with that sentence. The correct way to say it is:
"I **went** to school yesterday."

The verb "go" is irregular — its past tense is "went", not "goes" or "goed".

💡 **Vocabulary tip**: Instead of just "went to school", you could say
"I **attended** school yesterday" for a more formal tone!
```

### Option 2: Streamlit Web UI (Recommended)

```bash
streamlit run src/web_ui.py
```

This opens a beautiful web interface at http://localhost:8501 with:
- **💬 Chat** — Interactive conversation with the tutor
- **📝 Exercises** — Fill-in-the-blank, multiple choice, sentence correction
- **🔤 Pronunciation** — Get pronunciation guides for any word
- **📊 Progress** — Track your learning stats
- **📚 History** — Browse and load past conversations

### Option 3: FastAPI Web Server

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

Then open http://localhost:8000/docs for the interactive API documentation.

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/chat` | Send a message to the tutor |
| `GET` | `/sessions/{id}` | Get conversation history |
| `DELETE` | `/sessions/{id}` | Delete a session |

#### Example API Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I goes to school yesterday"}'
```

## Running Tests

```bash
# Make sure conda environment is active
conda activate english-tutor

pip install pytest
pytest tests/ -v
```

## GPU Setup (NVIDIA)

If Ollama is running on CPU instead of GPU, follow these steps:

### Check GPU Status

```bash
# Check if NVIDIA driver is detected
nvidia-smi

# If it shows your GPU (e.g., NVIDIA T500), the driver is working
# If it fails, install the driver:
sudo ubuntu-drivers autoinstall
sudo reboot
```

### Verify CUDA

```bash
# Check CUDA version
nvcc --version

# If not found, install CUDA toolkit:
sudo apt install nvidia-cuda-toolkit
```

### Force GPU in Ollama

```bash
export OLLAMA_LLM_LIBRARY=cuda
ollama serve
```

### Troubleshooting GPU

If Ollama still shows `total_vram="0 B"`:

1. **Check driver**: `nvidia-smi` must show your GPU
2. **Check CUDA**: Run `nvcc --version`
3. **Reinstall Ollama**: Sometimes a fresh install fixes GPU detection
4. **Memory**: NVIDIA T500 has 4GB VRAM. Phi-3 Mini (Q4_0) uses ~2GB, so it should fit

## Customization

### Change the Model

Edit `src/tools/grammar_tools.py` and `src/agents/tutor.py` — change `model="phi3"` to any Ollama model:

```python
# For example, use Llama 3:
llm = ChatOllama(model="llama3", temperature=0.7)
```

### Modify the Tutor's Personality

Edit `src/prompts/tutor_prompts.py` to customize the system prompt.

### Add New Tools

Create new tools in `src/tools/` using the `@tool` decorator and register them in `src/agents/tutor.py`:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """Description of what the tool does."""
    # Your tool logic here
    return result
```

## Future Improvements

- [ ] Database persistence for conversation history (SQLite/PostgreSQL)
- [ ] Student progress tracking and level assessment
- [ ] Lesson plans and structured exercises
- [ ] Pronunciation practice with audio
- [ ] Multi-language support for explanations
- [ ] Web UI with Streamlit or React

## License

MIT
