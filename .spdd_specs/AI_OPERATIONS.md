# AI Operations — How to Drive the AI Without Being Driven by It

> **Posture.** This is a meta-canvas: it sits beside the
> Constitution (`0_Root_Architecture.trainee.md`) and the weekly
> Task canvases. It coaches you *how* to operate an AI assistant on
> this project; the Task canvases coach you *what* to build. Read
> this on Day 1, then re-read it whenever you find yourself
> fighting the AI.
>
> **Maps to:** Day 0 onboarding. **Depends on:** nothing.
> **Unblocks:** every Task you will ever do.

---

## Why this canvas exists

The single biggest failure mode of AI-assisted curricula is the
trainee who pastes `Task_3_Orchestration.trainee.md` (8 pages)
into the AI chat input, types *"build this"*, and accepts
whatever 200-line truncated mess the AI returns. They will pass a
demo, fail their first PR review, and learn nothing about
architecture in the process.

This document exists to inoculate you against that failure mode.
It coaches the *AI Operations* layer: the deliberate workflow that
keeps the human (you) as the architect and the AI as the typist.

---

## The five rules of operating AI on this project

### Rule 1 — Use plan-then-execute for any Operation longer than three steps

Every Task canvas's *Operations* section is a numbered list. If
the list has four or more steps, we suggest avoiding one-shot
prompts that ask the AI to "do all of this" at once. Two
patterns that tend to work better:

- Let the AI **draft a plan first**, you approve it, then it
  executes step by step, or
- Write the plan yourself, then feed it back as context.

The reason: a one-shot prompt that spans 7 operations + 14
method signatures + 4 acceptance criteria tends to exceed the
model's ability to keep state coherent. The output gets
truncated or contradictory, with step 5 disagreeing with step 2.
Plan-then-execute keeps each step's context window small and
lets you intervene before a wrong direction compounds.

### Rule 2 — Pin the Constitution and the active Task canvas in every session

Every chat session, before you ask anything substantive, attach
two files:

```
.spdd_specs/0_Root_Architecture.trainee.md
.spdd_specs/tasks/Task_<N>_<Topic>.trainee.md
```

We strongly suggest making this a habit. The Constitution names
your data store (Postgres + pgvector — *not* Pinecone, *not*
Chroma, *not* in-memory FAISS), your orchestrator (LangGraph —
*not* LangChain agents, *not* CrewAI), your provider (Ollama
canonical, Opencode Zen/Go first choice). Without these pins, the
AI tends to hallucinate plausible alternatives and you spend an
evening unwiring them.

If you find yourself asking *"why did the AI just import
`langchain.agents.AgentExecutor`?"*, the answer is almost
always "because the Constitution wasn't attached this session".
Re-attach it and re-prompt.

### Rule 3 — Execute Operations sequentially, one or two steps at a time

The Task canvas lists Operations in **strict execution order**.
That order is not aesthetic; it encodes dependencies. Step 6
("write tests") cannot be drafted before step 4 ("implement the
class") because the tests need the class's signature.

Workflow:

1. Read steps N and N+1 of the Operations list.
2. In a fresh chat, ask the AI to do step N (with the Constitution
   and Task canvas attached).
3. Review the diff. Run the verify subset for step N (often
   `pytest tests/test_<that_module>.py`).
4. **Commit step N alone** before moving to step N+1.

Yes, this means more commits per task. That is the point. Each
commit is a checkpoint you can roll back to when step N+2 reveals
that step N's design was wrong. A single mega-commit at the end
of the week is impossible to triage when something breaks.

### Rule 4 — Acceptance Criteria are tests, not vibes

Every Task canvas has *Acceptance criteria (Given/When/Then)*.
Translate them into pytest cases **before** you write the
implementation. Two reasons:

- It forces you to disambiguate the spec's English.
- It gives you a green-bar moment that means something concrete.

When the AI proposes an implementation, the prompt should be
*"here is the failing test (paste it), make it pass"*, not
*"build a class that does X"*. The first prompt is auditable; the
second is hope.

### Rule 5 — Spec reconciliation is a human duty, not an AI one

The SPDD discipline says: *when the spec and the code disagree,
the spec wins, and you fix the spec in the same commit*. The
trap is that trainees get lazy and ask the AI *"update the spec
to match my code"*.

In our experience, AI coding tools will happily delete your
`Safeguards` if you ask them to "update the spec to match the
code". They tend to trim the `Norms` section because *"the code
doesn't seem to need them"*, quietly removing constraints
you depend on.

The pattern we suggest:

- **The AI may draft the spec update**, but ideally as a
  *suggestion in chat*, not as a direct file edit.
- **Read every line of the proposed update** before accepting
  or rejecting it.
- **Treat `Safeguards` and `Norms` as your domain.** If a
  Safeguard needs to change, write the change yourself. The
  AI may help you wordsmith; in our experience it shouldn't
  invent or delete one.

A mentor reviewing your PR will likely check: did the
`Safeguards` section change? If it did, does the change match
a deliberate decision the PR description called out?
Unexplained Safeguard edits tend to be the most common
reconciliation failure mode.

---

## Recommended chat scope

For a single Task, your chat scope should usually be:

```
.spdd_specs/0_Root_Architecture.trainee.md   # the Constitution
.spdd_specs/tasks/Task_<N>_<Topic>.trainee.md # this week's brief
app/                                            # last week's code
tests/                                          # last week's tests
scripts/smoke.starter.sh                        # behaviour probe
```

Avoid attaching `data_pipelines/eval/output/` (large JSONL),
`.venv/`, `data/raw_docs/` (the LLM doesn't need these in
context), or older `Task_<M>_*.md` destination files.

---

## When to start a new chat

Start a new chat:

- Between Operations steps (Rule 3).
- When the conversation transcript exceeds ~50 turns (the model
  will start losing earlier context).
- Whenever you switch tasks (Week N → Week N+1).
- Whenever you are about to ask the AI to do something that
  contradicts a prior decision in the same chat (it will defer to
  the most recent prompt and forget why earlier decisions were
  made).

---

## When to *not* use your AI coding tool

Some tasks are faster done by hand:

- Reading a single error message and grepping the codebase for
  the failing import.
- Writing a one-line `assert` in a test.
- Renaming a variable across one file.
- Reading the Constitution. We strongly suggest reading it
  yourself rather than asking AI to summarise it. The
  summary tends to drop the precise constraints — and the
  precise constraints are the whole point.

---

## A worked example

You are starting Task 3 (orchestration). The Operations list has
10 steps.

**Wrong:**

> *"Read `.spdd_specs/tasks/Task_3_Orchestration.trainee.md` and
> implement the whole thing."*

What happens: the AI produces 600 lines across 8 files in one
shot. Three of the files are empty stubs. The graph has the wrong
edge order. Tests don't run. You have nothing to checkpoint.

**Right (per step):**

Step 1 of the Operations list says *"Apply the schema delta in
`data_pipelines/schema/0001_create_tables.sql`"*.

> *Chat scope: 0_Root_Architecture.trainee.md
> Task_3_Orchestration.trainee.md*
>
> *Step 1 of the Operations list says: "Apply the schema delta in
> `data_pipelines/schema/0001_create_tables.sql`. Make it
> idempotent (`CREATE TABLE IF NOT EXISTS`, `CREATE EXTENSION IF
> NOT EXISTS vector`)."*
>
> *Show me the SQL for the docs and doc_embeddings tables only,
> following the column shape in the Constitution's Schema delta
> section. Do not write the migration application code yet —
> that is step 2.*

You get ~30 lines of SQL. You review it against the Constitution.
You commit. You move on.

---

## What to do when your AI goes off the rails

You will see AI coding tools try to:

- Import LangChain agents instead of LangGraph — *the
  Constitution names LangGraph by name. Reject the suggestion;
  re-attach the Constitution; restart the request.*
- Suggest Pinecone/Chroma/FAISS — *same fix.*
- Write SQL migrations using Alembic — *the Constitution's
  trade-offs section explicitly forbids Alembic for this project.
  Reject and point at the trade-off.*
- Skip the `Safeguards` enforcement (e.g. silent fallback when an
  LLM call fails) — *Norm 7 of the Constitution forbids silent
  downgrade. Reject; demand the explicit raise.*
- Generate fake test data instead of using fixtures from
  `tests/fixtures/` — *reject; re-attach the fixtures dir.*

The fix is always the same shape: **re-pin the Constitution,
restart the request, name the violated rule explicitly.** Over
the 8 weeks you will internalise the Constitution to the point
where you no longer need to re-attach it; that is the goal.

---

## Self-assessment checklist (run weekly)

At the end of every week, before you open the destination canvas
your mentor sends, ask yourself:

- [ ] Did I attach the Constitution + Task canvas to most
      substantive AI coding requests this week? If not, where did
      I forget — and did the omission show up as drift?
- [ ] Did I commit at least once per Operations step?
- [ ] Did I write at least one acceptance-criteria test before
      asking the AI for the implementation?
- [ ] Did the `Safeguards` and `Norms` sections in any spec
      change this week? If yes, can I explain *why* in plain
      English? Did I write the change myself?
- [ ] Are there any imports in `app/` that violate the
      Constitution (LangChain agents, Pinecone, etc.)? Run
      `grep -rE 'langchain\.agents|pinecone|chromadb|faiss' app/`
      to be sure.

If you answered *no* to any of these, you owe yourself a
half-hour of cleanup before you read the destination canvas.
That cleanup is where the senior-engineer instincts grow.
