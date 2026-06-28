"""Tests for LLMService — covers Step 5 acceptance criteria.

Uses httpx.MockTransport for full network isolation.
asyncio.sleep is monkeypatched to near-zero to keep retry tests fast.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import httpx
import pytest

from app.core.config import Settings
from app.core.exceptions import LLMProviderError
from app.services.llm_client import LLMHTTPClient
from app.services.llm_service import LLMService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_OLLAMA_BASE = "http://localhost:11434"
_OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def _make_mock_transport(
    responses: list[httpx.Response],
) -> httpx.MockTransport:
    """Return a MockTransport that replays *responses* in order."""
    calls: list[httpx.Request] = []
    idx = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal idx
        calls.append(request)
        resp = responses[idx % len(responses)]
        idx += 1
        return resp

    transport = httpx.MockTransport(handler)
    transport.calls = calls  # type: ignore[attr-defined]
    return transport


def _ollama_complete_response(content: str = "hello") -> httpx.Response:
    body = json.dumps({"message": {"role": "assistant", "content": content}})
    return httpx.Response(200, content=body.encode())


def _openrouter_complete_response(content: str = "hello") -> httpx.Response:
    body = json.dumps(
        {"choices": [{"message": {"role": "assistant", "content": content}}]}
    )
    return httpx.Response(200, content=body.encode())


def _error_response(status: int) -> httpx.Response:
    body = json.dumps({"error": f"status {status}"})
    return httpx.Response(status, content=body.encode())


def _make_ollama_service(transport: httpx.MockTransport) -> LLMService:
    settings = Settings(
        pg_dsn="postgresql+psycopg://app:app@localhost:5432/app",
        llm_provider="ollama",
    )
    client = LLMHTTPClient(base_url=_OLLAMA_BASE, transport=transport)
    return LLMService(settings=settings, http_client=client)


def _make_openrouter_service(transport: httpx.MockTransport) -> LLMService:
    settings = Settings(
        pg_dsn="postgresql+psycopg://app:app@localhost:5432/app",
        llm_provider="openrouter",
        openrouter_api_key="sk-test-key",
    )
    client = LLMHTTPClient(
        base_url=_OPENROUTER_BASE, api_key="sk-test-key", transport=transport
    )
    return LLMService(settings=settings, http_client=client)


# ---------------------------------------------------------------------------
# AC: correct POST endpoint per provider
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openrouter_complete_posts_to_correct_endpoint() -> None:
    """AC: OpenRouter complete → POST https://openrouter.ai/api/v1/chat/completions."""
    transport = _make_mock_transport([_openrouter_complete_response()])
    svc = _make_openrouter_service(transport)

    await svc.complete(messages=[{"role": "user", "content": "hi"}])

    assert len(transport.calls) == 1  # type: ignore[attr-defined]
    req: httpx.Request = transport.calls[0]  # type: ignore[attr-defined]
    assert str(req.url) == f"{_OPENROUTER_BASE}/chat/completions"
    assert req.method == "POST"


@pytest.mark.asyncio
async def test_ollama_complete_posts_to_correct_endpoint() -> None:
    """AC: Ollama complete → POST http://localhost:11434/api/chat."""
    transport = _make_mock_transport([_ollama_complete_response()])
    svc = _make_ollama_service(transport)

    await svc.complete(messages=[{"role": "user", "content": "hi"}])

    assert len(transport.calls) == 1  # type: ignore[attr-defined]
    req: httpx.Request = transport.calls[0]  # type: ignore[attr-defined]
    assert str(req.url) == f"{_OLLAMA_BASE}/api/chat"
    assert req.method == "POST"


@pytest.mark.asyncio
async def test_ollama_complete_unwraps_message_content() -> None:
    """AC: Ollama response shape — unwrap message.content correctly."""
    transport = _make_mock_transport([_ollama_complete_response("pong")])
    svc = _make_ollama_service(transport)

    result = await svc.complete(messages=[{"role": "user", "content": "ping"}])

    assert result == "pong"


@pytest.mark.asyncio
async def test_openrouter_complete_unwraps_choices_content() -> None:
    """OpenRouter response shape — unwrap choices[0].message.content."""
    transport = _make_mock_transport([_openrouter_complete_response("world")])
    svc = _make_openrouter_service(transport)

    result = await svc.complete(messages=[{"role": "user", "content": "hello"}])

    assert result == "world"


# ---------------------------------------------------------------------------
# AC: retry logic
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_5xx_retries_three_times_then_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC: transient 5xx → retries with exponential backoff up to 3 attempts → LLMProviderError."""
    sleep_calls: list[float] = []

    async def _fast_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("app.services.llm_service.asyncio.sleep", _fast_sleep)

    transport = _make_mock_transport(
        [_error_response(503), _error_response(503), _error_response(503)]
    )
    svc = _make_ollama_service(transport)

    with pytest.raises(LLMProviderError) as exc_info:
        await svc.complete(messages=[{"role": "user", "content": "hi"}])

    assert exc_info.value.provider == "ollama"
    assert exc_info.value.status_code == 503
    # 3 attempts total → 2 sleeps between retries
    assert len(sleep_calls) == 2
    assert len(transport.calls) == 3  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_4xx_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC: 4xx → no retry, raises LLMProviderError immediately."""
    sleep_calls: list[float] = []

    async def _fast_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("app.services.llm_service.asyncio.sleep", _fast_sleep)

    transport = _make_mock_transport([_error_response(422)])
    svc = _make_ollama_service(transport)

    with pytest.raises(LLMProviderError) as exc_info:
        await svc.complete(messages=[{"role": "user", "content": "hi"}])

    assert exc_info.value.status_code == 422
    assert len(sleep_calls) == 0  # no retries
    assert len(transport.calls) == 1  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_5xx_recovers_on_second_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    """5xx on attempt 1, success on attempt 2 — result is returned without raising."""
    monkeypatch.setattr(
        "app.services.llm_service.asyncio.sleep", AsyncMock(return_value=None)
    )

    transport = _make_mock_transport(
        [_error_response(500), _ollama_complete_response("recovered")]
    )
    svc = _make_ollama_service(transport)

    result = await svc.complete(messages=[{"role": "user", "content": "hi"}])

    assert result == "recovered"
    assert len(transport.calls) == 2  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# AC: embed routing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openrouter_embed_posts_to_embeddings_endpoint() -> None:
    """OpenRouter embed → POST /embeddings."""
    body = json.dumps({"data": [{"embedding": [0.1, 0.2, 0.3]}]})
    transport = _make_mock_transport(
        [httpx.Response(200, content=body.encode())]
    )
    svc = _make_openrouter_service(transport)

    result = await svc.embed(inputs=["hello"])

    req: httpx.Request = transport.calls[0]  # type: ignore[attr-defined]
    assert str(req.url) == f"{_OPENROUTER_BASE}/embeddings"
    assert result == [[0.1, 0.2, 0.3]]


@pytest.mark.asyncio
async def test_ollama_embed_loops_over_api_embeddings() -> None:
    """Ollama embed → one POST /api/embeddings per input (client-side loop)."""
    vec_a = [0.1, 0.2]
    vec_b = [0.3, 0.4]
    responses = [
        httpx.Response(200, content=json.dumps({"embedding": vec_a}).encode()),
        httpx.Response(200, content=json.dumps({"embedding": vec_b}).encode()),
    ]
    transport = _make_mock_transport(responses)
    svc = _make_ollama_service(transport)

    result = await svc.embed(inputs=["first", "second"])

    assert len(transport.calls) == 2  # type: ignore[attr-defined]
    for req in transport.calls:  # type: ignore[attr-defined]
        assert str(req.url) == f"{_OLLAMA_BASE}/api/embeddings"
    assert result == [vec_a, vec_b]
