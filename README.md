# Financial Helpdesk Agent

> **About this README.**
> This is the *seed* version of the project README — the file you copy
> to `/README.md` as part of Task 0. Everything below is intentionally
> minimal: it covers what Task 0 ships (Docker Compose, `/healthz`,
> project skeleton) and nothing further. Each subsequent
> `Task_<N>_<Topic>.trainee.md` includes an *Update README* operation
> that grows this file with one new section per week. By Week 7 your
> README will look quite different from this seed — and that's the
> intended trajectory.
>
> If you're tempted to peek at what the README "should" look like at
> end of Week 8, we'd suggest holding off until you've finished
> Week 7. The trap-and-reveal rhythm of the curriculum works better
> when each week's destination canvas surprises you on Sunday.

A Dockerised, LangGraph-based agent that answers consumer-finance
questions grounded in CFPB public data. Built incrementally over 8
weeks; this README grows one section per week.

The constitutional document is
[`.spdd_specs/0_Root_Architecture.trainee.md`](.spdd_specs/0_Root_Architecture.trainee.md).
Read it once on Day 1; everything below assumes you've at least
skimmed it.

## Quickstart (Week 0 — environment only)

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
curl http://localhost:8000/healthz   # → {"status": "ok"}
```

That is the entire user-visible surface area at the end of Week 0.
The `app` container responds to one health probe; the `db` container
is up but empty. There is no agent yet.

## Project layout

```text
app/                    # FastAPI app (just /healthz at Week 0)
data/                   # Starter corpus (read-only; shipped Week 2)
data_pipelines/         # Empty — populated starting Week 2
infra/                  # Dockerfiles + compose
tests/                  # Pytest suites (one test at Week 0)
.spdd_specs/            # SPDD canvases — your weekly briefs
```

## Local development

```bash
poetry install
poetry run ruff check .
poetry run pytest -q
```

## Where to learn next

The curriculum is delivered through the SPDD spec set. We
suggest reading the constitution first, then each weekly task
as it arrives.

### Already in your Day-1 bundle

| File | When to read |
|---|---|
| [`0_Root_Architecture.trainee.md`](.spdd_specs/0_Root_Architecture.trainee.md) | Day 1 — the constitution. |
| [`AI_OPERATIONS.md`](.spdd_specs/AI_OPERATIONS.md) | Day 1 — how to drive your AI coding tool on this project. We suggest reading it before your first AI coding session. |
| [`tasks/Task_0_Environment.md`](.spdd_specs/tasks/Task_0_Environment.md) | Week 0 — you are here. |
| [`tasks/Task_1_Foundations.trainee.md`](.spdd_specs/tasks/Task_1_Foundations.trainee.md) | Week 1 — preview if you'd like, but Week 0 first. |

### Arrives in subsequent Sunday drops

| File | Week |
|---|---|
| `tasks/Task_2_Ingestion.trainee.md` | Week 2 |
| `tasks/Task_3_Orchestration.trainee.md` | Week 3 |
| `tasks/Task_4_Prompts.trainee.md` | Week 4 |
| `tasks/Task_5_Evaluation.trainee.md` | Week 5 |
| `tasks/Task_6_DataQuality.trainee.md` | Week 6 |
| `tasks/Task_7_Safety.trainee.md` | Week 7 |
| `tasks/Task_8_Extensions.trainee.md` | Week 8 (optional capstone) |

Each weekly task ends with an *Update README* operation that
points at one new section to add to this file. By Week 7 this
README should look quite different from where it started.
