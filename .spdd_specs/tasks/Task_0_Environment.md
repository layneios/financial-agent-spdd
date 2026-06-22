# Task 0 — Environment (REASONS Canvas)

> **Maps to:** Learning Plan Week 0 — *Environment & Project Skeleton*.
> **Depends on:** `0_Root_Architecture.md` only.
> **Unblocks:** `Task_1_Foundations.md`.

---

## Requirements

### Analysis context

**Domain keywords scanned:** docker compose, FastAPI, postgres,
pgvector, healthz/readyz, env file. **Existing artifacts:**
`data/samples/complaints_sample.csv`, `data/raw_docs/*.txt`,
`.env.example`. **Prior tasks read:** none — Task 0 is the bootstrap.

**Strategic direction:** keep the Day-1 surface area microscopic.
One Dockerfile, one compose file, one `/healthz`, no business
logic. Anything that can defer to Task 1 (LLM service, settings
class) defers.

**Risks noticed:** (1) pgvector image variant matters — the
ARM-on-Mac story is fragile if the image is not multi-arch; (2)
`.env.example` must list every env key any later Task touches, even
if Task 0 itself does not use them, so we don't keep editing the
example file every week.

### Why this task exists

A junior developer must be able to run `docker compose up` from a clean
clone and see a healthy stack within minutes. The agent's correctness
in later tasks depends on a reproducible runtime where every later
piece (Postgres, embeddings, LangGraph, evaluation) plugs into the same
container topology. Without this scaffold, every Task downstream
spends time fighting infrastructure instead of building features.

### Acceptance criteria (Given/When/Then)

- **Given** a clean clone of the repository, a populated `.env`
  containing `PG_DSN` and Ollama-pointing model fields, and a running
  local `ollama` daemon (or `OPENROUTER_API_KEY` if the developer is
  using the OpenRouter escape hatch),
  **when** the developer runs `docker compose -f infra/docker-compose.yml up --build`,
  **then** both the `app` and `db` services reach healthy state and
  `curl http://localhost:8000/healthz` returns `{"status": "ok"}`
  with HTTP 200.
- **Given** the `db` service is running,
  **when** a connection is opened with the project's `PG_DSN`,
  **then** the `pgvector` extension is installed (`CREATE EXTENSION IF
  NOT EXISTS vector` succeeds without error).
- **Given** the test suite is invoked with `pytest tests/test_health.py`,
  **when** it runs without any external services,
  **then** all tests pass without hitting the network.
- **Given** the developer runs `python -m data_pipelines.ingest_tables.build_starter_sample`
  *and* `python -m data_pipelines.ingest_docs.fetch_starter_docs`,
  **when** the existing scripts complete,
  **then** the resulting CSV and `.txt` files are unchanged in shape
  from what they produced at the end of data-prep (1,000 rows, 4
  products × 250, three text files in `data/raw_docs/`).

### Explicit non-goals for this task

- No LLM client implementation (Task 1).
- No retrieval logic, no LangGraph nodes, no prompts.
- No production secret management. Local `.env` is sufficient.

---

## Entities

| Entity | Notes for Task 0 |
|---|---|
| `Settings` | Stub class only — declares the env keys, no business logic yet. Concretised in Task 1. |
| `pgvector` | Postgres extension. Must be available in the chosen image; the `pgvector/pgvector:pg16` image is preferred for zero install steps. |
| `request_id` | Reserved keyword. The `/healthz` handler does not need to emit one yet, but the FastAPI app must already attach a placeholder middleware so Task 1 can extend it. |
| Existing data artifacts | `data/samples/complaints_sample.csv`, `data/raw_docs/*.txt`. **Task 0 must not touch these files.** It only confirms the layout exists. |

### Deployment topology overview

Task 0 is the only Task that owns runtime *topology* rather than data
shapes, so the diagram is a class-level view of the bring-up: which
container talks to which, and which env keys cross which boundary.

```mermaid
classDiagram
direction LR

class App {
  +FastAPI app
  +healthz() 200
  +Settings settings
}

class Db {
  +postgres pg16
  +pgvector extension
  +PG_DSN endpoint
}

class Ollama {
  +host daemon (not in compose)
  +OLLAMA_BASE_URL
}

class StarterCorpus {
  <<read-only>>
  +complaints_sample.csv
  +raw_docs/*.txt
}

class Settings {
  +str PG_DSN
  +str LLM_PROVIDER
  +str OLLAMA_BASE_URL
  +str EMBEDDING_MODEL
  +int EMBEDDING_DIM
}

App "1" --> "1" Db          : PG_DSN
App "1" ..> "1" Ollama      : OLLAMA_BASE_URL (Task 1+)
App "1" ..> "1" StarterCorpus : reads (Task 2+)
App "1" *-- "1" Settings    : owns
```

---

## Approach

### Design decisions

1. **Single-stage `Dockerfile.app`**, not multi-stage, in this Task.
   Keep the image dumb until there is real Python code to optimise the
   build cache around. Multi-stage tightening lives in Task 6 alongside
   the rest of the production hardening.
2. **`pgvector/pgvector:pg16` image** for the `db` service. Avoid the
   "install extension at startup" dance by picking an image that already
   has the binary in place.
3. **No `langgraph` dependency yet.** Pinning it now risks the version
   churn breaking Task 3. Add it in Task 3.
4. **Healthcheck is a flat handler.** `GET /healthz` does *not* check
   the database. A separate `GET /readyz` handler will be added in
   Task 1 for that, so the deployment knows the difference between "the
   process is alive" and "downstream dependencies are reachable".
5. **`.env.example` lives in repo, `.env` does not.** Developers copy
   the example. CI uses environment variables directly.

### Trade-offs accepted

- The Dockerfile installs the full project venv inside the runtime
  image. That is wasteful but simple; Task 6's multi-stage build will
  shrink it.
- The repository structure is created upfront in this Task even though
  most folders will be empty until later Tasks touch them. This is
  intentional: keeping the layout stable from day one prevents AI
  from "discovering" alternative locations during code generation.

---

## Structure

### Files this task creates or amends

```text
financial-agent/
├── pyproject.toml                       # AMEND (extend existing)
├── poetry.lock                          # CREATE
├── .env.example                         # CREATE
├── README.md                            # CREATE (skeleton)
├── infra/
│   ├── docker/
│   │   └── Dockerfile.app               # CREATE
│   └── docker-compose.yml               # CREATE
├── app/
│   ├── __init__.py                      # CREATE
│   ├── api/
│   │   ├── __init__.py                  # CREATE
│   │   └── main.py                      # CREATE (healthz only)
│   ├── core/
│   │   ├── __init__.py                  # CREATE
│   │   └── config.py                    # CREATE (skeleton)
│   ├── services/
│   │   └── __init__.py                  # CREATE
│   └── tools/
│       └── __init__.py                  # CREATE
└── tests/
    ├── __init__.py                      # CREATE
    └── test_health.py                   # CREATE
```

### Existing files this task must respect

- `pyproject.toml` already declares `httpx>=0.27,<1.0`. Extend in
  place; do not rewrite from scratch.
- `data_pipelines/__init__.py`, `data_pipelines/ingest_tables/__init__.py`,
  `data_pipelines/ingest_docs/__init__.py` already exist. Leave alone.
- `.gitignore` already exists. Append entries only if needed.
- `.venv/` is created by the developer; do not commit it.

### Configuration shape

`.env.example`:

```dotenv
# Provider posture: Ollama primary, OpenRouter optional escape hatch.
LLM_PROVIDER=ollama

# Postgres connection. Host loopback for ingest / eval scripts that run
# outside compose; override to db:5432 inside the compose network.
PG_DSN=postgresql+psycopg://app:app@localhost:5432/app

# Logging mode: 'json' for production, 'text' for local dev.
LOG_FORMAT=text

# Ollama (local) — set OLLAMA_CHAT_MODEL to whatever `ollama list` shows.
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=gemma3:27b
OLLAMA_OPS_MODEL=qwen3.5:4b

# Embeddings. nomic-embed-text -> 768 dim. If you change the model,
# update EMBEDDING_DIM and re-apply the schema (immutable column type).
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768

# OpenRouter (optional). Required only when LLM_PROVIDER=openrouter.
# OPENROUTER_API_KEY=
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# OPENROUTER_MODEL=gpt-4.1-mini
```

#### Compute paths — pick whichever fits your machine

The curriculum is provider-agnostic. There is no "right" path; pick
the one that keeps your laptop fans honest and your tab open.

> **Note:** Cursor is no longer available for this curriculum. The
> paths below are ordered by cost-effectiveness; your existing
> setup is not negated.

1. **Company Copilot (default).** Apply for a GitHub Copilot or
   similar company coding-plan seat if available. No personal
   billing, fits your existing workflow.

2. **Opencode Go($5 1st Month, $10 following).** Low-cost
   subscription. Models: DeepSeek V4, Mimo v2.5, Minimax 3.
   The first month is $5; subsequent months are $10.

3. **Opencode Zen(Do not enable Billing).** Free, no billing
   setup needed. Built-in models provide good performance for
   curriculum work at zero cost.

4. **DeepSeek official top-up.** Directly recharge a DeepSeek
   account and use their API. Pay-as-you-go, no lock-in.

5. **Local Ollama / mlx-community-optiq.** Free and fully offline
   after pulling models, but slower on consumer hardware. On a
   16 GB Mac where `gemma3:27b` swaps badly, switching
   `OLLAMA_CHAT_MODEL=qwen3.5:4b` is a fully accepted fallback.
   Synthesis loses some flair; the curriculum still lands.

6. **Your existing Coding Plan subscription.** If you already
   use Cline, Continue, Windsurf, or another plan, it works fine.
   The curriculum does not mandate a specific provider.

### `infra/docker-compose.yml` skeleton (target shape)

```yaml
version: "3.9"

services:
  app:
    build:
      context: ..
      dockerfile: infra/docker/Dockerfile.app
    env_file: ../.env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy

  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  db_data:
```

---

## Operations (strict execution order)

Your AI coding tool must perform these steps top-to-bottom and stop on the first
failure.

1. **Extend `pyproject.toml`.** Add the runtime deps for Task 0/1:

   ```toml
   [project]
   dependencies = [
       "httpx>=0.27,<1.0",
       "fastapi>=0.115,<0.120",
       "uvicorn[standard]>=0.30,<1.0",
       "pydantic>=2.7,<3.0",
       "pydantic-settings>=2.4,<3.0",
       "loguru>=0.7,<1.0",          # OR structlog; pick exactly one
   ]

   [project.optional-dependencies]
   dev = [
       "pytest>=8.0,<9.0",
       "pytest-asyncio>=0.23,<1.0",
       "httpx[http2]>=0.27",        # for ASGI test client
       "mypy>=1.10,<2.0",
       "ruff>=0.5,<1.0",
   ]
   ```

   Generate `poetry.lock` if Poetry is in use; otherwise document the
   `uv` equivalent in `README.md`.

2. **Scaffold packages.** Create empty `__init__.py` files for `app/`,
   `app/api/`, `app/core/`, `app/services/`, `app/tools/`, and
   `tests/`. Do not create the `app/core/prompts/` folder yet (Task 4).

3. **Write `app/core/config.py` skeleton.**

   ```python
   from typing import Literal
   from pydantic import model_validator
   from pydantic_settings import BaseSettings, SettingsConfigDict

   class Settings(BaseSettings):
       model_config = SettingsConfigDict(env_file=".env", extra="ignore")

       pg_dsn: str
       llm_provider: Literal["ollama", "openrouter"] = "ollama"
       ollama_base_url: str = "http://localhost:11434"
       ollama_chat_model: str = "gemma3:27b"
       ollama_ops_model: str = "qwen3.5:4b"
       embedding_model: str = "nomic-embed-text"
       embedding_dim: int = 768
       openrouter_api_key: str | None = None
       openrouter_model: str = "gpt-4.1-mini"
       log_format: Literal["json", "text"] = "text"

       @model_validator(mode="after")
       def _require_openrouter_key(self) -> "Settings":
           if self.llm_provider == "openrouter" and not self.openrouter_api_key:
               raise ValueError("OPENROUTER_API_KEY required when LLM_PROVIDER=openrouter")
           return self

   def get_settings() -> Settings:
       return Settings()  # Task 1 will replace with @lru_cache
   ```

   No business logic; this exists so the FastAPI app can import it.

4. **Write `app/api/main.py` with one route.**

   ```python
   from fastapi import FastAPI

   app = FastAPI(title="Financial Helpdesk Agent", version="0.0.0")

   @app.get("/healthz")
   def healthz() -> dict[str, str]:
       return {"status": "ok"}
   ```

5. **Write `infra/docker/Dockerfile.app`.** Single-stage Python 3.11
   slim base. Install Poetry (or `uv`), copy `pyproject.toml` and
   `poetry.lock` first, install deps, then copy `app/`. Run as a
   non-root user. Final command:

   ```dockerfile
   CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

6. **Write `infra/docker-compose.yml`** matching the skeleton above.

7. **Write `.env.example`** matching the configuration shape above.

8. **Write `README.md` skeleton.** Sections: *Quickstart*, *Project
   Layout*, *Data Prep*, *Health Endpoints*. Quickstart commands:

   ```bash
   cp .env.example .env
   # If using Ollama (default): pull models once
   #   ollama pull gemma3:27b
   #   ollama pull qwen3.5:4b
   #   ollama pull nomic-embed-text
   # If using OpenRouter: set OPENROUTER_API_KEY and LLM_PROVIDER=openrouter
   docker compose -f infra/docker-compose.yml up --build
   curl http://localhost:8000/healthz
   ```

9. **Write `tests/test_health.py`.** Use FastAPI's `TestClient` to hit
   `/healthz` and assert the JSON body. Must not import `Settings`
   directly so it runs without environment variables set.

10. **Verify locally.** Run `pytest tests/test_health.py` *and*
    `docker compose -f infra/docker-compose.yml up --build` (in the
    background; the developer can `Ctrl-C`). Confirm both succeed.

11. **Print a final summary** listing files created, files amended, and
    the verification commands the user can rerun.

---

## Norms

- Folder packaging: every directory under `app/` and `tests/` has an
  `__init__.py` even if empty. This avoids implicit namespace packages
  and makes `mypy` happy.
- Python files start with a one-line module docstring describing intent.
- Configuration access is always through `get_settings()`; never read
  `os.environ` directly outside `config.py`.
- Imports order: standard library, third-party, local. One blank line
  between groups.
- Line length: 100 characters; enforced by `ruff` defaults.
- Docker layer order is dependency-files-first, code-second. Bust the
  cache only on dependency changes.

---

## Safeguards

### What this task must NOT do

1. **Do not create or modify any file under `data/`.** The starter
   corpus is read-only from this point onward.
2. **Do not pull `langgraph` or `langchain-core` into `pyproject.toml`.**
   Those are Task 3 dependencies.
3. **Do not implement `LLMService` or `RetrievalService` stubs.** Task 1
   owns the LLM abstraction; Task 2 owns retrieval.
4. **Do not add a vector-store service to `docker-compose.yml`.**
   `pgvector` runs inside the `db` Postgres container.
5. **Do not add `chroma`, `qdrant`, `weaviate`, or `faiss` to deps.**
6. **Do not add Streamlit yet.** UI is Task 5.
7. **Do not add a database migration tool yet** (no Alembic, no Atlas).
   Schema creation belongs to Task 2's ingestion script for the first
   time. A migration tool can be introduced in Task 6 if the AI can
   justify it in the canvas.
8. **Do not bake secrets into images.** All secrets come from `.env`
   via `env_file` in compose.
9. **Do not run network-dependent tests in CI by default.** Mark them
   `@pytest.mark.network` and skip unless an env flag is set.

### Error handling specifics

- If `docker compose up` fails because `pgvector/pgvector:pg16` is
  unavailable, fall back to `postgres:16` with an explicit `init.sql`
  that runs `CREATE EXTENSION vector;`. Document the fallback in
  `README.md`. Do not silently change the image without updating the
  README.
- If `pyproject.toml` already contains a dependency at a different
  version than this canvas requires, raise the conflict in the run
  log and stop; do not "auto-resolve" by upgrading or downgrading.

### Verification command (printed to the user at the end)

```bash
cp .env.example .env  # then either start `ollama serve` (default), or
                       # set OPENROUTER_API_KEY + LLM_PROVIDER=openrouter
pytest tests/test_health.py
docker compose -f infra/docker-compose.yml up --build
curl -fsS http://localhost:8000/healthz   # expect {"status":"ok"}
```
