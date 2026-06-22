# Week 1 — From Environment to Foundations

You shipped Week 0: a green Docker stack, an empty `db` container,
no agent yet. This week, three foundational concepts land that
you'll touch every single week thereafter.

## What you're getting this week

- `.spdd_specs/tasks/Task_1_Foundations.trainee.md` — your
  Monday brief. Incomplete on purpose.
- On Sunday, after your Friday PR is in: the destination canvas
  `Task_1_Foundations.md` (no `.trainee` suffix). That's the
  reconciliation target.

## What this week introduces

Three concepts that recur for the rest of the curriculum:

1. **`Settings`** — a Pydantic-settings model that owns every
   environment variable. After this week, no other module
   reads `os.environ` directly.
2. **`LLMService`** — a provider-agnostic facade with
   `complete()` and `embed()` methods. After this week, no tool
   talks to OpenRouter or Ollama directly.
3. **Structured logging with a `request_id` ContextVar.** After
   this week, every log line carries a `request_id` and an
   `event` keyword.

A fourth concept (`ServicesContainer`) is introduced as a plain
dataclass; it grows into a real container over later weeks.

## Why we did it this way

- **Why Pydantic Settings, not `os.getenv`?** Because Week 5's
  evaluation pipeline runs in a separate process and must
  validate the same env contract. A misspelled env var should
  crash on startup, not on the first `complete()` call.
- **Why one `LLMService` for two providers?** Because in Week 6
  you'll evaluate v0 vs v1 and want the *same* provider on both
  sides. The abstraction is the only honest way to swap it.
- **Why `request_id` via ContextVar instead of arg-passing?**
  Try the alternative for an hour if you'd like. You'll hit
  the propagation pain and understand why we treat
  ContextVar as the strong default for this project.

## Common Week-1 pitfalls

| Pitfall | What it looks like | The fix |
|---|---|---|
| Skipping `LLMProviderError` payload field | `class LLMProviderError(Exception): pass`. | The constructor must take `provider`, `status_code`, `payload`, `request_id`. Without `payload` you cannot debug a malformed response in later weeks. |
| Using `print()` for logs | "I'll add structured logging later." | The constitution sets `loguru.logger` with kwargs as the Day-1 default. Adding it later usually means reworking every call site. |
| Hard-coding the model name | A `"gpt-4.1-mini"` literal sitting in a tool. | Read from `Settings.openrouter_chat_model` or `Settings.ollama_chat_model`. |
| Inline `httpx.AsyncClient()` per call | A new client per `complete()` call leaks file descriptors. | One client per `LLMService` instance, lifecycle owned by `ServicesContainer`. |

## Wednesday self-check

Before you submit your `Task_1_Foundations.trainee.md` for
mentor sign-off:

- [ ] *Risks noticed* lists at least three concrete risks. "The
      LLM might fail" doesn't count — write down what fails,
      where, and how you'd notice. (Hint: rate limits, missing
      `request_id` in error paths, secret leakage in logs.)
- [ ] *Trade-offs accepted* names at least three. ContextVar vs
      explicit-arg propagation. Retry-on-503 vs fail-fast.
      Single `LLMService` vs separate Ollama/OpenRouter
      clients.
- [ ] *Class diagram* drawn (Mermaid `classDiagram`). Even if
      ugly, it must show `Settings → LLMService →
      LLMHTTPClient` ownership, and `LLMProviderError` raised
      by `LLMService`.
- [ ] *Operations* breakdown numbered. Steps marked
      `TODO(trainee)` are filled in. You should be able to walk
      your mentor through them verbally.

If you can't tick all four, fix the canvas before submitting.
The Wednesday gate is the cheapest place to catch a wrong
direction; skipping it is how juniors burn Friday.

## What Sunday will reveal

The destination canvas pins:

- The exact `LLMProviderError` constructor shape and the retry
  budget.
- The structured-log keys every public method emits (`event`,
  `request_id`, plus method-specific kwargs).
- The `ServicesContainer` shape this week, plus the empty
  slots Week 2 will fill.

When the destination drops, diff your spec and your code
against it, then file a *reconciliation PR* in the same week's
branch.

## Going further (optional reading)

- The `contextvars` module's docs on `ContextVar.set` /
  `Token` and the gotchas under `asyncio.gather`.
- `httpx`'s connection-pool documentation.
- *The Twelve-Factor App* — chapter on env-var configuration.
- Look up your favourite war story about a `request_id`
  propagation bug that cost someone a weekend in production.
  This week's discipline prevents that bug.
- **Tool Use & Action Spaces:** Tools define the contract between
  agents and their environment. Effective tools must return
  token-efficient information and encourage efficient agent
  behaviors.
  [Anthropic: Guide to Tool Use](https://docs.anthropic.com/en/docs/tool-use)
- **Context Rot & Strategic Caching:** As token count in a context
  window increases, an LLM's ability to accurately recall
  information decreases — a phenomenon known as context rot.
  Modern platforms use Context Caching to store massive data in
  active memory at a ~90% discount.
  [Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- **Async State Management:** Python's `contextvars` module
  propagates correlation IDs (like `request_id`) across
  asynchronous tasks without explicit argument threading.
  [Python 3 contextvars Documentation](https://docs.python.org/3/library/contextvars.html)
