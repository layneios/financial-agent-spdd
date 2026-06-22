# Week 0 — Day 1 / Setup

Welcome. This is the only week that's *not* trap-and-reveal. Week 0
is plain setup: Docker Compose green, a `/healthz` endpoint that
returns 200, the project skeleton in place. Your `.trainee.md` for
this week is the same as the destination — there's nothing for you
to reverse-engineer this time.

## Suggested first move (~2 minutes)

Initialise this unzipped folder as a git repository. We suggest:

```bash
cd <your-unzipped-folder>
git init
git add .
git commit -m "initial: Day-1 trainee bundle"
```

If you'd like to share your work with your mentor (most cohorts
do), push the repo to your preferred host. **A name we suggest:
`financial-agent-spdd`.** It captures the project (a financial
helpdesk agent) and the discipline (Structured Prompt-Driven
Development). You're welcome to pick anything else — the name
is a hint, not a rule.

If you'd rather not put your work on a hosted git server,
that's also fine. Local commits and weekly zips back to your
mentor work too. Talk to your mentor about what suits you.

## What you might ship by Friday

A working starting point — that's it. Concretely:

- The unzipped folder under git tracking, initial commit made.
- `docker compose up` brings up two containers: `web` (FastAPI)
  and `db` (Postgres + pgvector). Both healthy.
- `curl http://localhost:8000/healthz` → `200 {"status": "ok"}`.
- A skeleton `pyproject.toml` with the constitution-pinned tool
  versions.
- A `README.md` at the project root (copy `.spdd_specs/README.starter.md`
  there and start growing it from Week 1 onwards).
- One test asserting that `/healthz` returns 200.

The list is intentionally small. We suggest holding off on agent
code, retrieval, prompts — those land in later weeks against
specs you don't have yet, and pre-coding tends to waste Friday.
The foundation gets to be boring, working, and reproducible so
that the next eight weeks can compose on top of it.

## What's in this Day-1 bundle

- `.spdd_specs/0_Root_Architecture.trainee.md` — your project
  constitution. We suggest reading it in full once on Day 1,
  then re-attaching it as context to every AI coding session for
  the next eight weeks.
- `.spdd_specs/AI_OPERATIONS.md` — how to drive your AI coding tool
  productively on *this* project. We suggest reading it before
  you open your AI coding tool for the first time. The five rules in
  there will save you hours.
- `.spdd_specs/README.starter.md` — the seed README to copy
  to your project root.
- `.spdd_specs/tasks/Task_0_Environment.md` — your weekly
  brief. *Note:* there's no `.trainee` variant for Week 0
  because the spec and the destination are intentionally the
  same. The `.trainee` variants start in Week 1.
- (`trainee/week_01.md` is also in this bundle — it's
  next week's orientation, included so you can preview if
  you want to. We suggest finishing Week 0 first.)

## Why this week looks so simple

Because everything that comes after it depends on a working
local stack and a repeatable container build. Two failure
patterns we've seen kill cohorts:

1. **Brittle local Python.** A trainee installs deps directly
   into their host Python; things appear to work in Week 0;
   then in Week 5 a colleague's machine cannot reproduce the
   eval and the team blames the eval pipeline. The eval is
   fine — the environment is the bug. Docker tends to be
   the cure.
2. **Skipping pgvector setup.** A trainee saves time by
   running Postgres without pgvector, planning to add the
   extension when retrieval lands. Week 2 then loses two days
   to a `CREATE EXTENSION` that fights with their local
   install. We suggest sorting it now.

## Wednesday self-check

Before you ask your mentor to sign off Week 0, you might want
to confirm:

- [ ] `docker compose up` brings both containers green and
      `/healthz` returns 200.
- [ ] `pyproject.toml` exists with the constitution-pinned
      versions of `fastapi`, `pydantic`, `pydantic-settings`,
      `loguru`, `pytest`, `ruff`, `mypy`.
- [ ] `README.md` exists at repo root and is the
      `.spdd_specs/README.starter.md` content (you'll grow it
      every week).
- [ ] `infra/docker-compose.yml` exists and pins the Postgres
      image with pgvector.
- [ ] One test (`tests/test_healthz.py` or similar) passes.
- [ ] You can re-read the constitution
      (`0_Root_Architecture.trainee.md`) and explain — out
      loud, to a colleague or to yourself — what each REASONS
      section means. If anything's unclear, this is the moment
      to ask. You have eight weeks of REASONS canvases ahead.

## Common Week-0 pitfalls

| Pitfall | What it looks like | A gentler path |
|---|---|---|
| Adding application code "to get ahead" | You start writing `app/services/llm_service.py` before Week 1's spec lands. | We suggest waiting. The Week-1 spec will pin signatures you don't yet know, and pre-coding tends to waste Friday redoing work. |
| Skipping pgvector | The Postgres image is plain `postgres:16`. | The constitution suggests `pgvector/pgvector:pg16` and names the exact tag — easier to use that than to fight a `CREATE EXTENSION` later. |
| Committing `.env` | Real secrets ride into git history. | `.env` is git-ignored by default. `.env.example` ships with placeholder keys; the constitution names every variable. |
| Skipping the README | "I'll write it later." | The README is the spec's `.trainee.md` echo for outsiders. Most weeks' Friday PRs include a small README diff — keeping the habit early makes it cheap to maintain.|

## What Sunday will reveal

For Week 0, *nothing changes*. The destination canvas
(`Task_0_Environment.md`) is the same file you've been working
against. There's no "reveal" this week — Week 0 is shared
between trainee and destination tracks on purpose. The real
`.trainee.md` workflow starts Monday of Week 1.

## Going further (optional reading)

- *The Twelve-Factor App* — the env-var chapter is the
  intellectual ancestor of `pydantic-settings`.
- The Docker Compose docs on `depends_on` with `condition:
  service_healthy` — how `web` waits for `db` to pass
  `/pg_isready` before booting.
- The pgvector README's "Getting Started" page — useful
  even though Week 2 is when you actually use it.
- **FastAPI as the AI Default:** Modern AI applications
  orchestrate embedding generation, vector searches, and LLM
  inference — not single API calls. FastAPI's async-first
  architecture is naturally optimized for the heavy I/O patterns
  of modern AI and RAG systems.
  [How FastAPI Became Python's Fastest-Growing Framework](https://dzone.com/articles/how-fastapi-became-pythons-fastest-growing-framework)
- **High-Performance Vector Scaling (`pgvectorscale`):** While
  `pgvector` enables storing embeddings directly in PostgreSQL,
  production environments often hit performance ceilings.
  `pgvectorscale` builds on top of `pgvector` to add the
  StreamingDiskANN index type for high-recall vector search at
  massive scale with bounded memory usage.
  [pgvector, pgvectorscale, and the Postgres Vector Search Stack](https://www.softwareseni.com/pgvector-pgvectorscale-and-the-postgres-vector-search-stack-explained/)
- **Container Startup Sequencing:** Crucial for ensuring the
  FastAPI backend waits for Postgres to be fully healthy before
  booting.
  [Docker Compose Startup Order Docs](https://docs.docker.com/compose/how-tos/startup-order/)

---

When Week 0 is green, breathe out. The next eight weeks are
where the curriculum actually starts.
