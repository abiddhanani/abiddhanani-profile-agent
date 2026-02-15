---
title: abiddhanani_profile_agent
app_file: app.py
sdk: gradio
sdk_version: "5.49.1"
---
# abiddhanani Profile Agent

A personal resume agent that chats as you: answers questions about your career, background, skills, and experience using your summary and resume. Built with OpenAI, Gradio, RAG, and persistent chat history.

**Try it:** [Open on Hugging Face Spaces](https://huggingface.co/spaces/YOUR_HF_USERNAME/abiddhanani-profile-agent) *(replace `YOUR_HF_USERNAME` with your Hugging Face username after deploy)*

## Architecture

### Approach

The agent uses two main improvements over the original design:

1. **RAG (Retrieval-Augmented Generation)** – Profile content (summary + resume) is chunked, embedded, and stored in a vector database (Chroma). The model uses a `search_profile` tool to retrieve only relevant passages instead of receiving the full text on every request. This reduces token usage per call.

2. **In-session memory via Gradio** – Chat history is persisted in the browser (`save_history=True`). Users can refresh or return later and continue their conversation. History is truncated to the last 10 turns to control context size.

### Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **System prompt** | Full summary + full resume (~2–5k tokens) on every request | Short instructions (~200–400 tokens); profile fetched on demand |
| **Profile retrieval** | Entire document in every API call | Relevant chunks only via `search_profile` tool (~200–600 tokens when used) |
| **Chat history** | In-memory for active session only | Persisted in browser; survives refresh and return visits |
| **History length** | Unbounded (token growth over long chats) | Last 10 message pairs kept for context |
| **Token usage** | High, especially for long resumes | Lower; retrieval scales with query relevance |

### Current state

- **RAG**: Chroma + OpenAI embeddings; chunks of 600 chars with 100 overlap; top-5 retrieval.
- **Tools**: `search_profile`, `record_user_details`, `record_unknown_question`.
- **Memory**: Gradio `save_history=True` (browser); server-side history truncated to 10 turns.

---

## Setup

1. Clone the repo and enter the project:
   ```bash
   git clone https://github.com/YOUR_USERNAME/abiddhanani-profile-agent.git
   cd abiddhanani-profile-agent
   ```

2. Copy the env template and add your keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your values (see **Required environment variables** below).

3. Add your profile data:
   - Put a short bio in `me/summary.txt`.
   - Put your resume or LinkedIn export as a PDF at `me/AbidDhanani.pdf` (or set `RESUME_PDF` in `.env` to another path).

4. Install dependencies and run (requires [uv](https://docs.astral.sh/uv/)):
   ```bash
   uv sync
   uv run app.py
   ```
   Open the URL shown in the terminal (Gradio default: http://127.0.0.1:7860).

### Deploy to Hugging Face Spaces (Gradio)

If `uv run gradio deploy` warns about uploading a large folder (e.g. due to `.venv` or `uv.lock`), deploy from a minimal bundle so only the app files are uploaded:

```bash
uv run python deploy_bundle.py --deploy
```

Or build the bundle first, then deploy from it:

```bash
uv run python deploy_bundle.py
cd .gradio_deploy_bundle && uv run --project .. gradio deploy
```

---

## Required environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key. Used for chat completions and embeddings. |
| `PUSHOVER_USER` | Pushover user key (starts with `u_`). From your Pushover account dashboard. |
| `PUSHOVER_TOKEN` | Pushover application/API token (starts with `a_`). Create an app at [pushover.net](https://pushover.net) and use its token. |

Notifications: when someone leaves their email (`record_user_details`) or asks something the agent can’t answer (`record_unknown_question`), the app sends a push to your device via Pushover. Both `PUSHOVER_USER` and `PUSHOVER_TOKEN` must be set for notifications to work.

---

## Optional environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PERSON_NAME` | `Abiddhanani` | Display name used in the system prompt. |
| `SUMMARY_PATH` | `me/summary.txt` | Path to your short bio/summary text file. |
| `RESUME_PDF` | `me/AbidDhanani.pdf` | Path to your resume or LinkedIn PDF. |
| `RAG_CHUNK_SIZE` | `600` | RAG chunk size in characters. |
| `RAG_CHUNK_OVERLAP` | `100` | RAG chunk overlap. |
| `RAG_RETRIEVAL_K` | `5` | Number of chunks to retrieve per search. |
| `MAX_HISTORY_TURNS` | `10` | Number of message pairs to keep in context. |

---

## Project layout

```
abiddhanani-profile-agent/
├── .env.example
├── .gitignore
├── .huggingfaceignore
├── LICENSE
├── README.md
├── pyproject.toml
├── requirements.txt    # For Gradio/HF Spaces; full deps in pyproject.toml
├── uv.lock
├── app.py              # Entry point (run: uv run app.py)
├── agent.py            # Chat agent logic
├── main.py             # Alternative entry point
├── rag.py              # RAG pipeline
├── tools.py            # Tools (search_profile, record_user_details, etc.)
├── deploy_bundle.py    # Build minimal folder for gradio deploy
├── .chroma_profile/    # Chroma vector store (created at runtime, gitignored)
└── me/
    ├── summary.txt
    └── AbidDhanani.pdf  # Add your resume here (gitignored)
```

All configuration is read from `.env` via `python-dotenv`.

---


