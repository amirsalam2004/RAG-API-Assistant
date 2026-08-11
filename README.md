# RAG API Assistant — Multi-Agent API Discovery System

An AI-powered API discovery assistant that helps users find the right API endpoints from any OpenAPI/Swagger specification using natural language queries. Built with a multi-agent RAG (Retrieval-Augmented Generation) architecture, it supports multilingual chat and dynamic configuration.

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Agents Pipeline](#agents-pipeline)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How the Pipeline Works](#how-the-pipeline-works)
- [Multilingual Support](#multilingual-support)
- [API Reference](#api-reference)
- [Technologies Used](#technologies-used)

---

## Overview

RAG API Assistant is a multi-agent system that ingests any OpenAPI/Swagger specification into a vector database, then uses a pipeline of LLM-powered agents to understand user requests, retrieve relevant API candidates, rank them by relevance, and return the best match — all through a conversational interface.

### Key Capabilities

- **Dynamic Configuration**: Point to any OpenAPI spec URL — no hardcoded APIs
- **Natural Language Queries**: Ask in plain English (or any language) and get the right API endpoint
- **Multilingual Chat**: Supports chat in any language; translates internally to English for processing
- **Semantic Search**: Uses vector embeddings to find the most relevant APIs
- **LLM-Powered Ranking**: Scores and ranks candidates based on intent, entity, and keyword matching
- **Interactive UI**: Clean Streamlit interface with API cards showing method, path, purpose, and Swagger links

---

## How It Works

```
User sends a message in any language
        ↓
┌─────────────────────────────┐
│  1. Language Detection      │  Detect user's language
│  2. Translation to English  │  Translate input for pipeline
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  3. Intent Detection        │  Is the request clear and complete?
│     → If not: ask clarify   │  Translate question back to user's language
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  4. Query Building          │  Convert natural language to search query
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  5. Vector Retrieval        │  Semantic search in ChromaDB
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  6. LLM Reranking           │  Score candidates by relevance
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  7. Decision                │  Select best API(s) or ask for clarification
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  8. Translation Back        │  Translate response to user's language
└─────────────────────────────┘
        ↓
User sees API card(s) or translated message
```

---

## Architecture

The system follows a **multi-agent pipeline** pattern where each agent performs a specific task and passes its output to the next agent via shared state.

### Core Design Principles

1. **Agent-Based Pipeline**: Each step is an independent agent with a single responsibility
2. **Shared State**: All agents communicate through `AgentState`, which holds conversation history, search queries, candidates, and rankings
3. **Generator Pattern**: The pipeline yields status updates and results, allowing the UI to show real-time progress
4. **Dynamic Configuration**: No hardcoded API sources — everything is configured at runtime
5. **Language Agnostic Processing**: Input is translated to English before the pipeline; output is translated back after

---

## Project Structure

```
RAG API Assistant/
├── app/
│   ├── agents/                    # Pipeline agents
│   │   ├── intent_agent.py        # Detects if user request is complete
│   │   ├── query_builder.py       # Converts natural language to search query
│   │   ├── retrieval_agent.py     # Searches vector DB and parses results
│   │   ├── reranker_agent.py      # Scores and ranks API candidates
│   │   └── decision_agent.py      # Selects best API or asks for clarification
│   │
│   ├── core/                      # Orchestration layer
│   │   ├── state.py               # AgentState class (shared state)
│   │   ├── controller.py          # Pipeline orchestrator (run function)
│   │   └── main.py                # CLI entry point
│   │
│   ├── services/                  # External integrations
│   │   ├── llm_service.py         # LLM calls (OpenRouter/DeepSeek)
│   │   └── vector_db_service.py   # ChromaDB vector database
│   │
│   ├── UI/
│   │   └── streamlit_ui.py        # Streamlit web interface
│   │
│   └── base_prompts.py            # System prompts for all agents
│
├── scripts/
│   └── ingest.py                  # OpenAPI parser and document builder
│
├── chroma_db/                     # Vector database storage (auto-created)
├── .env.example                   # Example environment variables
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Agents Pipeline

### 1. Intent Agent (`intent_agent.py`)

**Purpose**: Determines if the user's request is clear and complete enough to search for an API.

**Input**: Conversation history from `state.messages`
**Output**: `{"complete": true/false, "question": "..."}`

**Logic**:
- A request is COMPLETE if: intent is clear, target entity is clear, action is clear
- A request is NOT COMPLETE if: vague, missing details, or ambiguous
- If incomplete, generates a single clarification question

### 2. Query Builder (`query_builder.py`)

**Purpose**: Converts natural language request into an effective search query for the vector database.

**Input**: Conversation history
**Output**: Updated `state.search_query`

**Logic**:
- Extracts main ACTION (create, update, delete, get)
- Extracts main ENTITY (user, password, post, friend)
- Includes important keywords
- Keeps query short (5-12 words) in API-style wording

### 3. Retrieval Agent (`retrieval_agent.py`)

**Purpose**: Searches the vector database and parses raw results into structured API candidates.

**Input**: `state.search_query` + `vectordb`
**Output**: Updated `state.candidates`

**Logic**:
- Performs semantic search in ChromaDB
- Parses each result into structured format: method, path, purpose, description, category, URL, request body, responses, keywords
- Builds Swagger documentation URL from category and operation ID

### 4. Reranker Agent (`reranker_agent.py`)

**Purpose**: Scores each candidate API based on how well it matches the user request.

**Input**: `state.search_query` + `state.candidates`
**Output**: Updated `state.ranked`

**Scoring Criteria**:
1. **Intent Match** (highest priority): Does the API perform the exact action requested?
2. **Entity Match**: Does it target the correct resource?
3. **Endpoint Semantics**: Path, method, purpose consistency
4. **Keyword Relevance**: Overlap with query terms

**Score Range**: 0.0 (irrelevant) to 1.0 (perfect match)

### 5. Decision Agent (`decision_agent.py`)

**Purpose**: Selects the best API(s) and decides whether to return results or ask for clarification.

**Input**: `state.candidates` + `state.ranked`
**Output**: `{"status": "success"/"clarify", "result": [...]}`

**Logic**:
- If best score < 0.6: asks for clarification
- If best score ≥ 0.6: returns all candidates with score ≥ 0.6
- Each result includes: method, path, purpose, description, category, URL, score

---

## Features

### Dynamic API Source Input

Instead of hardcoded URLs, the system accepts user input at runtime:
- **OpenAPI Spec URL**: URL to the OpenAPI/Swagger JSON specification
- **Swagger Base URL**: Base URL for generating documentation links
- **API Description**: Brief description of the API system (used to generate context)

### Multilingual Chat

- **Automatic Language Detection**: Detects the user's language from each message
- **Input Translation**: Translates user messages to English for internal processing
- **Output Translation**: Translates AI responses (clarification questions, error messages) back to user's language
- **API Card Display**: Technical details (method, path, URL, score) remain in English

### Vector-Based Semantic Search

- Uses `sentence-transformers` for embeddings
- ChromaDB for vector storage and retrieval
- Cosine similarity for finding relevant APIs

### Interactive UI

- Clean Streamlit interface with setup form
- API cards with method badges, purpose, description, category, and match score
- "Best Match" highlighting for top result
- Direct links to Swagger documentation
- Real-time status updates during processing

---

## Prerequisites

- Python 3.9 or higher
- An OpenRouter API key (for LLM access)
- An OpenAPI/Swagger specification URL

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/amirsalam2004/RAG-API-Assistant.git
cd RAG-API-Assistant 
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and set your OpenRouter API key:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Optional configuration (defaults are shown):

```
VECTOR_DB_PATH=./chroma_db
COLLECTION_NAME=api_docs
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | — | Your OpenRouter API key for LLM access |
| `VECTOR_DB_PATH` | No | `./chroma_db` | Path where ChromaDB stores vector data |
| `COLLECTION_NAME` | No | `api_docs` | Name of the ChromaDB collection |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | Sentence transformer model for embeddings |

### Getting an OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key and copy it to your `.env` file

---

## Usage

### Web Interface (Streamlit)

```bash
streamlit run app/UI/streamlit_ui.py
```

1. Open the browser at `http://localhost:8501`
2. Fill in the setup form:
   - **OpenAPI Spec URL**: URL to your OpenAPI JSON file
   - **Swagger Base URL**: Base URL for documentation links
   - **API System Description**: Brief description of what the APIs do
3. Click **Initialize API Assistant**
4. Once initialized, start chatting in the input box
5. Ask natural language questions like:
   - "How do I create a new user?"
   - "I need to update my password"
   - "What APIs are available for payments?"

### Command Line Interface

```bash
python -m app.core.main
```

Note: The CLI requires `OPENAPI_SPEC_URL` to be set in `.env`.

---

## How the Pipeline Works

### Step-by-Step Example

**User Input**: "How do I reset a user's password?" (in any language)

1. **Language Detection**: Detects language (e.g., "english")
2. **Translation**: Translates to English if needed
3. **Intent Detection**:
   - Intent: clear (reset password)
   - Entity: clear (user's password)
   - Action: clear (reset)
   - Result: `{"complete": true}`
4. **Query Building**: Generates search query: "reset user password"
5. **Vector Retrieval**: Searches ChromaDB, finds top 3 candidates
6. **Reranking**: Scores each candidate:
   - `POST /users/reset-password` → 0.95
   - `PUT /users/{id}/password` → 0.82
   - `GET /users/{id}` → 0.31
7. **Decision**: Best score (0.95) ≥ 0.6, returns top candidates
8. **Translation**: Translates response to user's language if needed
9. **UI Display**: Shows API cards with method, path, purpose, and Swagger link

### Clarification Flow

**User Input**: "Update my profile" (ambiguous)

1. **Intent Detection**:
   - Intent: clear (update)
   - Entity: unclear (which field? name, email, avatar?)
   - Result: `{"complete": false, "question": "What field do you want to update?"}`
2. **Translation**: Translates question to user's language
3. **UI Display**: Shows translated clarification question

---

## Multilingual Support

### How It Works

- **Per-Message Detection**: Language is detected on every user message
- **State Tracking**: Detected language is stored in `state.user_language`
- **Internal Processing**: All pipeline agents work in English
- **Output Translation**: AI responses (clarification, errors) are translated back

### What Gets Translated

| Element | Translated? |
|---------|-------------|
| User input messages | Yes → English |
| AI clarification questions | Yes → User's language |
| Error/clarify messages | Yes → User's language |
| API card fields (method, path, URL, score) | No (stays English) |
| Status messages (🔍, 🛠️, etc.) | No (stays English) |

### Supported Languages

Any language supported by the LLM (DeepSeek) can be detected and translated, including:
- English, Spanish, French, German, Italian, Portuguese
- Chinese, Japanese, Korean, Arabic
- Russian, Turkish, Hindi, and many more

---

## API Reference

### AgentState (`app/core/state.py`)

```python
class AgentState:
    messages: list          # Conversation history
    user_info: dict         # User goal and constraints
    openapi_url: str        # OpenAPI specification URL
    swagger_url: str        # Swagger base URL
    SYSTEM_CONTEXT: str     # Generated system context
    user_language: str      # Detected user language
    phase: str              # Current pipeline phase
    search_query: str       # Generated search query
    candidates: list        # Retrieved API candidates
    ranked: list            # Scored and ranked candidates
```

### Controller (`app/core/controller.py`)

```python
def run(state, vectordb, user_input):
    """
    Generator pipeline.
    Yields: {"type": "status", "message": str}
    Yields: {"type": "result", "data": str | list}
    """
```

### VectorDB (`app/services/vector_db_service.py`)

```python
class VectorDB:
    ingest_from_url(url)        # Ingest OpenAPI spec from URL
    reset_and_ingest(url)       # Clear and re-ingest
    search(query, k=3)          # Semantic search
    search_with_parsing(query)  # Search with parsed results
```

### LLM Service (`app/services/llm_service.py`)

```python
def llm_call(state, prompt, temperature=0)    # Main LLM call with SYSTEM_CONTEXT
def detect_language(text)                       # Detect language of text
def translate_text(text, target_lang)           # Translate text to target language
def generate_api_info(description)              # Generate system context from description
def format_messages(messages)                   # Format conversation history
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python** | Core language |
| **Streamlit** | Web UI framework |
| **OpenAI SDK** | LLM API client (via OpenRouter) |
| **DeepSeek V4 Flash** | Large language model |
| **ChromaDB** | Vector database |
| **Sentence Transformers** | Text embeddings |
| **dotenv** | Environment variable management |

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
