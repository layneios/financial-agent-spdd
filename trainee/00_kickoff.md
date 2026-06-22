# Trainee Kickoff — Financial Helpdesk Agent (8-Week Curriculum)

Welcome. You're holding the Day-1 packet for an eight-week
curriculum on building a production-grade GenAI agent. The
materials are yours to read, copy, fork, ignore, or remix — we'll
suggest a rhythm, but you're an adult engineer and the choices are
yours.

This kickoff has three jobs: tell you **what you're walking into**,
tell you **what you'll have when you walk out**, and tell you
**what to do today**. We've kept it free of week-by-week spoilers
on purpose. Most weeks of this curriculum have a deliberate shape
that rewards experiencing it, not previewing it.

---

## 1. What this curriculum actually is

Two playgrounds, on top of each other:

| Layer | Visible deliverable | Invisible deliverable |
|---|---|---|
| **Agent Development** | A real Financial Helpdesk Agent: retrieval-augmented generation over a public CFPB complaints dataset and a small set of policy documents, structured outputs, evaluation, safety guardrails, a feedback flywheel. | The full GenAI lifecycle: ingestion, retrieval, orchestration, prompts, evaluation, data quality, safety, extensions. |
| **A discipline** | A weekly canvas you fill in, gate, ship code against, and reconcile. | A way of working with AI that holds up at production scale — the part of the job your manager actually pays you to do for the rest of your career. |

If you only retain the first layer, you leave as a competent Agent
Developer. That's a real outcome, and a valuable one. If you stay
present for the second layer too — and there's a moment in Week 8
designed to make it click — you leave as something rarer. We'll
talk more about that on Week 8 morning. For now, just know there
are *two* skills being stacked, on purpose.

---

## 2. The design pattern of this curriculum

You won't be reading lecture notes. You'll be receiving a series of
**REASONS canvases** — short documents structured as Requirements,
Entities, Approach, Structure, Operations, Norms, Safeguards.

Each Monday you receive a canvas that is *intentionally
incomplete*. The blanks (`TODO(trainee)`) are the work. You fill
them in: Risks noticed, Trade-offs accepted, Class diagram, the
remaining Operations steps. Your filled-in canvas is your
architectural thinking, made visible. By Wednesday, your trainer
sees it. By Friday, the code you ship is meant to honour it. By
Sunday, you reconcile your version against a *destination* canvas
the trainer releases — the version a senior engineer would have
written from scratch.

This shape is called **Structured Prompt-Driven Development
(SPDD)**, formalised by Thoughtworks in their 2026-04 article. The
core idea is that the spec is no longer documentation; it is the
*compiler input* the AI receives every time it generates code. A
drifting spec literally breaks the build. That makes drift visible
immediately, not six weeks later.

### Where SPDD comes from (a one-screen industry-evolution map)

The table below puts SPDD in context — Agile and TDD didn't fail;
they answered a different question. As the "compiler" became an
LLM, the bottleneck moved from human typing speed to machine
non-determinism, and a new generation of methodology grew on top
of the old one. Skim it; the alphabet soup in the bottom row is
just naming neighbours, you don't need to know them yet.

| Layer (tree metaphor) | SE 2.0 — *Data-Augmented & Iterative* | SE 3.0 — *AI-Native & Agentic* |
|---|---|---|
| **The problem solved** | Managing human unpredictability, typing speed, and cross-team communication constraints. | Managing machine non-determinism, orchestrating cognitive load, and guaranteeing translation fidelity. |
| **1. The root** *(core methodology)* | **Agile & DevOps** — respond to change over following a plan; unify development with operations. | **IDD & SDD** — define human outcomes (Intent-Driven) and lock them into machine-readable contracts (Spec-Driven). |
| **2. The branches** *(operating pillars / frameworks)* | **Scrum, Lean Kanban, SAFe, LeSS, SoS** — structural systems designed to align human pods and scale their efforts. | **Spec=Code, EDD, Abstraction First** — the governing laws: spec is the single source of truth; LLM-as-a-Judge gates (EDD); and locking boundaries before generating code. |
| **3. The leaves** *(daily practices / practice groups)* | **TDD, DDD, CI/CD, Pair Programming, XP** — granular, human-centric engineering habits that ensure code quality and safety. | **SPDD, BMAD, OpenSpec, SpecKit, Superpowers, MUSUBI, GSD** — the competing frameworks and daily habits teams use to execute intent and reconcile specs. |

> **One thing worth noticing about row 3.** The SE 2.0 branches
> (Scrum, Kanban, SAFe…) earned their canonical status through
> a decade-plus of community shakeout. The SE 3.0 leaves above
> are all young — most under two years old at time of writing —
> and the industry has not yet picked winners. SPDD might
> become the "Scrum of SE 3.0"; or a sibling might; or a name
> none of us has heard yet might. Hold the alphabet soup
> lightly: it's the contender list, not the verdict.

The key takeaway for you: the discipline you'll build through
this curriculum (REASONS canvas, Wednesday gate, Sunday
reconciliation) is one specific leaf — SPDD — but it sits on a
root and branches that are also worth knowing. If you join a
team later that uses a sibling like BMAD or SpecKit, the
underlying habit transfers; only the file format changes. And
if the eventual SE 3.0 winner turns out to be something else
entirely, the discipline still transfers — that's the whole
reason we're investing in this shape rather than this
particular file extension.

Two consequences of this shape worth keeping in mind:

- **Architectural thinking is graded ahead of code.** Most weeks,
  the trainer's review on Wednesday is about your `.trainee.md`,
  not about whether your code runs. Code that passes tests but
  contradicts the canvas is the canonical bug pattern this
  curriculum is designed to surface.
- **The destination canvas arrives Sunday, not Monday.** This
  isn't to make life hard. It's because trying first, then
  diffing against the senior version, is how the senior instinct
  is built. Reading the destination ahead of time short-circuits
  the most valuable mechanism in the whole eight-week loop.

You will run into the second consequence almost immediately. We
encourage you to trust the timing for at least the first three
weeks before judging it. The pedagogical loop accumulates faster
than it reveals itself.

---

## 3. The goal — what you walk away with

After eight weeks, you will have:

1. **A working Financial Helpdesk Agent** — code, tests, evaluation
   harness, a Streamlit UI, a populated database, the works. It
   answers questions about consumer-finance complaints with
   citations, it refuses prohibited topics, it logs every decision
   for audit, and it has thresholds gating its evals.
2. **Eight filled-in REASONS canvases plus eight reconciliation
   PRs** — your architectural thinking, made visible. This is the
   portfolio you can show a future hiring manager. The eight Friday
   PRs are the artifact; the eight reconciliation PRs are the
   *evidence of growth*.
3. **A working mental model of the GenAI lifecycle.** You will be
   able to walk into a new GenAI project and say, with confidence,
   "this is the ingestion layer, this is the orchestration layer,
   this is where the eval lives, this is where safety lands". That
   mental model is the most portable thing this curriculum
   produces.
4. **(For trainees who lean in)** *the SPDD discipline as
   muscle memory.* By the end of Week 8, the canvas-first habit
   should feel like the natural way to start any non-trivial
   feature, not just AI features. If that lands, you leave as a
   Context Engineer — the role title we expect to outgrow "GenAI
   Engineer" within a few cohort cycles.

We do not grade you against any of these outcomes. The cohort is
not a competition. The Friday review is for spec-to-code
consistency; the Sunday reconciliation is for honest self-review.
That is the whole grading rubric.

---

## 4. What's in this Day-1 zip

This first zip ships only what you need to get started. It contains:

```text
trainee/
├── 00_kickoff.md        # this file — start here
├── week_00.md           # Day 1 / setup
└── week_01.md           # Week 1 — Foundations

.spdd_specs/
├── 0_Root_Architecture.trainee.md   # the project constitution
├── AI_OPERATIONS.md             # how to drive your AI coding tool productively
└── README.starter.md                # the skeleton README to copy to /README.md
```

That's six files, and that's deliberate. Future weeks arrive as
small follow-up bundles each Sunday, so you're never reading
ahead of where the cohort is. If you finish a week early and want
the next one sooner, ask your trainer — many will happily hand you
Week N+1 ahead of schedule.

### What you'll do with these files (in 60 seconds)

1. Unzip the bundle into a directory of your choice.
2. (Suggested, not required.) Initialise it as a git repo so you
   can track your work and, if you'd like, share it with your
   trainer for review. We suggest a name like
   **`financial-agent-spdd`** — it captures the project (a
   financial helpdesk agent) and the discipline (Structured
   Prompt-Driven Development). You're welcome to pick anything
   else; the name is a hint, not a rule.
3. Read this file end-to-end (~15 minutes; you're nearly there).
4. Open `week_00.md` and follow it on Day 1. It's mostly setup —
   Docker, Postgres + pgvector, the agent skeleton. By the end of
   Day 1 you should have a healthy `/healthz` endpoint and your
   first commit.
5. On Monday of Week 1, open `week_01.md` and the Week 1 Task
   canvas at `.spdd_specs/tasks/Task_1_Foundations.trainee.md`.

---

## 5. The two-track filing rule

This is the single most useful thing to keep straight in your head.
Each week you'll be juggling two kinds of file, and they have
different jobs.

```text
You read on Monday morning            You build against
─────────────────────────             ─────────────────
trainee/week_<N>.md                   .spdd_specs/tasks/Task_<N>_<Topic>.trainee.md
(orientation, why this week is        (the actual SPDD canvas you
 shaped this way, common pitfalls)     fill in — REASONS structure)
```

The `trainee/week_<N>.md` files are *orientation*. They tell you
why a week looks the way it does, what trapped previous trainees,
and what your Wednesday self-check might cover. They are not the
spec.

The spec is the `.spdd_specs/tasks/Task_<N>...trainee.md` canvas.
Keeping the two distinct in your head saves a lot of confusion
later. When in doubt: the canvas is what you fill in and ship; the
weekly brief is the framing.

---

## 6. The weekly rhythm

Every week of the curriculum has the same shape. We've found this
rhythm gives the best learning yield, but it's a suggested default
— your trainer may flex it for your cohort.

```text
   Monday      Wednesday          Friday              Sunday
      │             │                 │                   │
      ▼             ▼                 ▼                   ▼
   Open          Spec Gate          Code PR           The Reveal
   week_<N>.md   share your         submit code +     trainer releases
   + Task_<N>.   .trainee.md        reconciled        Task_<N>.md
   trainee.md    for review         .trainee.md       (destination)
```

| Day | What we suggest | Why this gate exists |
|---|---|---|
| **Monday** | Read `trainee/week_<N>.md` end-to-end. Then open `.spdd_specs/tasks/Task_<N>_<Topic>.trainee.md`. Start filling in the `TODO(trainee)` blocks (Risks noticed, Trade-offs accepted, Class diagram). | Architectural thinking before code is the cheapest place to fix a wrong direction. Most senior engineers learned this the hard way; the curriculum tries to shortcut you past that pain. |
| **Wednesday** | Share your filled-in `.trainee.md` canvas with your trainer for review. We strongly suggest waiting for that review before generating code with AI. | The AI multiplies misunderstanding fast. Catching a wrong direction Wednesday tends to cost ~30 minutes; catching it Friday tends to cost a weekend. |
| **Friday** | Submit a PR with your code, your tests, and your *reconciled* `.trainee.md` (the version you actually built). Grow the README. Keep the smoke harness covering what it covered last week. | Spec ↔ code parity is the canonical SPDD invariant. If they drift, the curriculum's lesson is in the discipline, not the typing. |
| **Sunday** | Your trainer releases `Task_<N>_<Topic>.md` (no `.trainee` suffix) — the destination canvas. Diff your work against it, file a *reconciliation PR* on the same week's branch, ship it, and Monday brings Week N+1. | The destination is the cohort's anchor for the next week's start. The earlier you reconcile, the firmer your foundation when Week N+1 begins. |

### Reading order each Monday

1. **`trainee/week_<N>.md`** (this bundle) — orientation, why the
   week is shaped this way, common pitfalls.
2. **`.spdd_specs/tasks/Task_<N>_<Topic>.trainee.md`** — the
   REASONS canvas you fill in.
3. **`.spdd_specs/0_Root_Architecture.trainee.md`** — a refresher
   on the constitution. Re-attaching it as context for the week's
   AI coding sessions tends to keep the model honest.

### Reading order each Sunday

1. The destination canvas your trainer drops:
   `.spdd_specs/tasks/Task_<N>_<Topic>.md` (no `.trainee` suffix).
2. Your own `.trainee.md` from Friday.
3. The diff. Open a *reconciliation PR* listing every gap you
   noticed and what you'd change about your Wednesday thinking
   to catch it next time. The diff itself is the lesson; the PR
   makes the lesson public to the cohort.

---

## 7. The one habit we'd most like you to keep

**Wait for the Wednesday review before generating code.**

We suggest this as a strong default rather than a rule. Here's the
reasoning, so you can decide for yourself:

- The Wednesday review is the cheapest place in the week to catch
  a wrong direction.
- AI coding tools will happily produce 600 lines of code against a
  half-formed spec. Reverting 600 lines on Friday is harder than
  rewriting half a `.trainee.md` on Wednesday.
- We've watched cohorts that skip the gate burn Friday into
  Saturday into Sunday. We've watched cohorts that respect it
  ship by Friday afternoon and rest.

If you're confident in your design and want to skip the Wednesday
gate occasionally, that's your call. We'd ask you to flag it to
your trainer so they can adjust their support expectations for
that week.

---

## 8. What arrives later (and when)

| Week | What you receive on Sunday               | Source                         |
|------|------------------------------------------|--------------------------------|
| 1    | (already in this zip)                    | this zip                       |
| 2    | `trainee/week_02.md` + Task 2 trainee spec | next Sunday's drop           |
| 3-8  | one trainee-spec + one weekly handoff each | one Sunday drop per week    |
| any  | the *destination* canvas of last week    | every Sunday after your Friday PR |

You're never reading more than one week ahead. That's intentional:
most weeks have a "trap" the curriculum sets up deliberately, and
reading ahead defuses the trap before it can coach you something.
We've found trainees who read ahead are the ones who say *"I
learned the technical skills but I didn't get the deeper point."*
The deeper point is what we're hoping you'll keep.

---

## 9. Where to ask for help

- **Spec confusion.** Ask before Wednesday's spec gate if you can.
  Late asks tend to cost you architectural time, but
  better-late-than-stuck.
- **AI tool going off the rails.**
  `.spdd_specs/AI_OPERATIONS.md` has a section titled "what to
  do when your AI goes off the rails". Read it first; ask your
  trainer second.
- **Compute is too slow.** Cursor is no longer available for this
  curriculum. Below are several paths ordered by cost-effectiveness;
  pick what fits your setup. There is no "right" path and this
  list does not negate whatever you already have — use what works
  for you.

  1. **Apply for a company Copilot seat (default).** If your
     company provides GitHub Copilot or a similar coding-plan
     subscription, that is the recommended starting point. It
     requires no personal billing and keeps everything in your
     existing workflow.

  2. **Opencode Go($5 1st Month, $10 following).** Low-cost
     subscription. Models available: DeepSeek V4, Mimo v2.5,
     Minimax 3. The first month is $5; subsequent months are $10.

  3. **Opencode Zen(Do not enable Billing).** Free, no billing
     setup needed. Built-in models provide good performance for
     curriculum work at zero cost.

  4. **DeepSeek official top-up.** Directly recharge a DeepSeek
     account and use their API. Pay-as-you-go, no subscription
     lock-in.

  5. **Local Ollama / mlx-community-optiq.** Free and fully
     offline after pulling the models, but noticeably slower on
     consumer hardware. Viable if you have patience and a capable
     machine.

  6. **Your existing Coding Plan subscription.** If you are
     already subscribed to another coding plan (Cline, Continue,
     Windsurf, etc.), that works too. The curriculum does not
     mandate a specific provider.

  Mention which path you picked in your weekly reconcile note.
  Full provider posture lives in `README.md` and
  `.spdd_specs/tasks/Task_0_Environment.md`.
- **Falling behind.** It happens. The curriculum is paced for a
  full-time engineer with light other commitments; if your week
  has been chaotic, tell your trainer Wednesday morning and
  re-baseline. Catching up by accumulating debt is the failure
  mode we most often watch trainees walk into.

---

## 10. The one-line theory of this curriculum

> *We are not just coaching you to build an LLM agent. We are
> coaching you the **discipline** that turns LLMs from a magic
> trick into engineering. The agent is the artifact; the
> discipline is the deliverable.*

If that line lands for you on Day 1, save it. We'd like to know on
Week 8 whether it's still the same line, or whether you've updated
it for yourself.

---

## 11. Further reading

References for experienced developers who want the deeper industry
context behind this curriculum's architectural choices.

* **Context Engineering (Google Cloud):** The focus is no longer on
  manual word choice; it is on building automated data pipelines
  and managing the environment state. Context engineering ensures
  the AI operates within a stable, data-driven reality rather than
  guessing what you want.
  [Google Cloud: What Is AI Context Engineering?](https://cloud.google.com/discover/ai-context-engineering)

* **The 2026 Agentic Coding Reality (Anthropic):** In 2026, the
  value of an engineer shifts from writing raw code to system
  architecture design, agent coordination, and quality evaluation.
  Single-agent workflows are being replaced by multi-agent
  architectures that process tasks using parallel reasoning.
  [Anthropic: 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)

* **Structured Prompt-Driven Development (SPDD):** The methodology
  your curriculum relies on to enforce architectural boundaries and
  treat prompts as version-controlled artifacts.
  [Martin Fowler: Structured Prompt-Driven Development](https://martinfowler.com/articles/structured-prompt-driven/)

---

## 12. Start here

When you're ready, open `week_00.md` and follow it on Day 1. We
suggest reading in order, since later weeks compose on earlier
ones — but if you already know what you're doing, the materials
won't stop you skipping around. Each week's spec is self-contained
enough that a senior engineer could enter at Week 4 if they
wanted to.

Welcome to the cohort. We're glad you're here.
