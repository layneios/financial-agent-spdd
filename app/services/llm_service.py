"""Provider-agnostic LLM service facade — chat completion + batch embeddings."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from loguru import logger
from pydantic import BaseModel

from app.core.config import Settings
from app.core.exceptions import LLMProviderError
from app.core.logging import get_request_id
from app.services.llm_client import LLMHTTPClient

_MAX_RETRIES = 3
_LOG_TRUNCATE = 500


# ---------------------------------------------------------------------------
# Private Pydantic response models — Risk 1: shape-drift caught at parse time
# ---------------------------------------------------------------------------


class _OllamaMsg(BaseModel):
    role: str
    content: str


class _OllamaCompleteResp(BaseModel):
    message: _OllamaMsg


class _ORMsg(BaseModel):
    role: str
    content: str


class _ORChoice(BaseModel):
    message: _ORMsg


class _ORCompleteResp(BaseModel):
    choices: list[_ORChoice]


class _OllamaEmbedResp(BaseModel):
    embedding: list[float]


class _OREmbedItem(BaseModel):
    embedding: list[float]


class _OREmbedResp(BaseModel):
    data: list[_OREmbedItem]


# ---------------------------------------------------------------------------
# LLMService
# ---------------------------------------------------------------------------


class LLMService:
    """Provider-agnostic facade over chat completion and batch embeddings.

    Provider differences (Ollama vs OpenRouter) live inside this class.
    Callers see only :meth:`complete` and :meth:`embed`.
    """

    def __init__(self, settings: Settings, http_client: LLMHTTPClient) -> None:
        self._settings = settings
        self._http = http_client

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        response_format: str | None = None,
        request_id: str | None = None,
    ) -> str:
        rid = request_id or get_request_id() or "unbound"
        provider = self._settings.llm_provider
        log = logger.bind(request_id=rid, provider=provider)
        log.debug(
            "LLM complete",
            messages_head=str(messages)[:_LOG_TRUNCATE],
        )
        if provider == "openrouter":
            return await self._complete_openrouter(
                messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                rid=rid,
            )
        return await self._complete_ollama(
            messages, model=model, temperature=temperature, rid=rid
        )

    async def embed(
        self,
        inputs: list[str],
        *,
        model: str | None = None,
        request_id: str | None = None,
    ) -> list[list[float]]:
        rid = request_id or get_request_id() or "unbound"
        provider = self._settings.llm_provider
        logger.bind(request_id=rid, provider=provider).debug(
            "LLM embed", input_count=len(inputs)
        )
        if provider == "openrouter":
            return await self._embed_openrouter(inputs, model=model, rid=rid)
        return await self._embed_ollama(inputs, model=model, rid=rid)

    # -----------------------------------------------------------------------
    # OpenRouter
    # -----------------------------------------------------------------------

    async def _complete_openrouter(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None,
        temperature: float,
        max_tokens: int | None,
        response_format: str | None,
        rid: str,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self._settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = {"type": response_format}

        resp = await self._retry_post(
            "/chat/completions", json=payload, rid=rid, provider="openrouter"
        )
        parsed = _ORCompleteResp.model_validate(resp.json())
        return parsed.choices[0].message.content

    async def _embed_openrouter(
        self, inputs: list[str], *, model: str | None, rid: str
    ) -> list[list[float]]:
        payload: dict[str, Any] = {
            "model": model or self._settings.embedding_model,
            "input": inputs,
        }
        resp = await self._retry_post(
            "/embeddings", json=payload, rid=rid, provider="openrouter"
        )
        parsed = _OREmbedResp.model_validate(resp.json())
        return [item.embedding for item in parsed.data]

    # -----------------------------------------------------------------------
    # Ollama
    # -----------------------------------------------------------------------

    async def _complete_ollama(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None,
        temperature: float,
        rid: str,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self._settings.ollama_chat_model,
            "messages": messages,
            "stream": False,
        }
        resp = await self._retry_post(
            "/api/chat", json=payload, rid=rid, provider="ollama"
        )
        parsed = _OllamaCompleteResp.model_validate(resp.json())
        return parsed.message.content

    async def _embed_ollama(
        self, inputs: list[str], *, model: str | None, rid: str
    ) -> list[list[float]]:
        embed_model = model or self._settings.embedding_model
        results: list[list[float]] = []
        for text in inputs:
            payload: dict[str, Any] = {"model": embed_model, "prompt": text}
            resp = await self._retry_post(
                "/api/embeddings", json=payload, rid=rid, provider="ollama"
            )
            parsed = _OllamaEmbedResp.model_validate(resp.json())
            results.append(parsed.embedding)
        return results

    # -----------------------------------------------------------------------
    # Shared retry helper
    # -----------------------------------------------------------------------

    async def _retry_post(
        self, path: str, *, json: Any, rid: str, provider: str
    ) -> httpx.Response:
        """POST *path*, retrying up to *_MAX_RETRIES* times on 5xx / connection errors.

        - 5xx and connection-level errors → retry with exponential backoff.
        - 4xx → raise :class:`LLMProviderError` immediately (no retry).
        - Retries exhausted → raise :class:`LLMProviderError`.
        """
        last_exc: Exception | None = None
        last_resp: httpx.Response | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                resp = await self._http.post(path, json=json)
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(2**attempt)
                continue

            if resp.status_code < 400:
                return resp

            if resp.status_code < 500:
                # 4xx — non-retryable
                raise LLMProviderError(
                    f"Provider error: HTTP {resp.status_code}",
                    provider=provider,
                    status_code=resp.status_code,
                    payload=resp.text,
                    request_id=rid,
                )

            # 5xx — retryable
            last_resp = resp
            if attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(2**attempt)

        # All attempts exhausted
        if last_resp is not None:
            raise LLMProviderError(
                f"Provider error after {_MAX_RETRIES} attempts: HTTP {last_resp.status_code}",
                provider=provider,
                status_code=last_resp.status_code,
                payload=last_resp.text,
                request_id=rid,
            )
        if last_exc is not None:
            raise LLMProviderError(
                str(last_exc),
                provider=provider,
                status_code=-1,
                payload=None,
                request_id=rid,
            ) from last_exc

        raise RuntimeError("Unexpected state in _retry_post")  # pragma: no cover
