# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

RAG CLI tool: ingest a PDF into PostgreSQL+pgVector as embeddings, then answer questions about it
from the command line. Answers must come **only** from the PDF's content — if the answer isn't in
the retrieved context, the assistant must reply with a fixed refusal string (see `src/chat.py`'s
`PROMPT_TEMPLATE`), never general knowledge.

## Commands

```powershell
# Setup
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # then fill in AI_PROVIDER + the matching API key

# Run (in order)
docker compose up -d          # starts Postgres with pgvector on POSTGRES_PORT (default 5432)
python src/ingest.py          # chunks PDF_PATH and writes embeddings to pgVector
python src/chat.py            # interactive CLI; type 'sair'/'exit'/'quit' to stop

# Ad-hoc retrieval check (no LLM call, just prints similarity hits)
python src/search.py
```

There is no test suite, lint, or build step.

## Architecture

All source lives in `src/`, run as plain scripts (not a package) — hence `ingest.py`/`search.py`/
`chat.py` do bare `import config` rather than relative imports, and must be run with `src/` as the
script path (e.g. `python src/ingest.py`) from the repo root so `.env` resolves correctly.

- **`src/config.py`** — single source of truth for env vars, the Postgres connection string, and
  provider selection. `get_embeddings()` and `get_llm()` branch on `AI_PROVIDER` (`openai` or
  `gemini`) and lazily import the matching LangChain integration package. Any new provider-specific
  code should be added here, not duplicated in the scripts that consume it.
- **`src/ingest.py`** — loads `PDF_PATH` with `PyPDFLoader`, splits with
  `RecursiveCharacterTextSplitter` (`CHUNK_SIZE`/`CHUNK_OVERLAP` from config, default 1000/150), and
  writes to pgVector in batches of `BATCH_SIZE` chunks via `store.add_documents(...)` (with
  `pre_delete_collection=True` on the initial connect) — batching avoids tripping embedding-API rate
  limits on larger PDFs. Re-running ingestion replaces the collection rather than appending to it.
- **`src/search.py`** — opens the same pgVector collection (`PG_COLLECTION_NAME`) for reads and
  exposes `search(query, k)` using `similarity_search_with_score`. `chat.py` imports this directly;
  it is not a network service.
- **`src/chat.py`** — the CLI loop. Builds the prompt from `PROMPT_TEMPLATE` (context + strict
  rules + the fixed "fora de contexto" examples) and calls `config.get_llm()`. Keep the refusal
  string in `PROMPT_TEMPLATE` byte-for-byte if you touch it — it's graded output, not just a
  default.
- **`docker-compose.yml`** — single `pgvector/pgvector:pg16` service; all tunables
  (user/password/db/port) come from the same `.env` used by the Python scripts, so compose and the
  app always point at the same database.

Config/model knobs (provider, chunk size/overlap, `SEARCH_K`, Postgres connection) all flow through
`.env` → `src/config.py`; there are no hardcoded alternates elsewhere in the code.

Required at runtime but not committed: `document.pdf` in the repo root (the file ingestion targets)
and a real API key for whichever `AI_PROVIDER` is selected.
