"""Thin httpx wrapper — injectable transport enables MockTransport in tests."""

from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx


class LLMHTTPClient:
    """Minimal async HTTP client wrapping :class:`httpx.AsyncClient`.

    Accepts an optional *transport* so tests can inject
    :class:`httpx.MockTransport` without monkey-patching the network stack.

    Args:
        base_url:  The provider base URL (e.g. ``https://openrouter.ai/api/v1``).
        api_key:   Bearer token sent in ``Authorization`` header, or ``None``.
        transport: Optional :class:`httpx.AsyncBaseTransport` override.
        timeout:   Request timeout in seconds (default 60 s).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 60.0,
    ) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            transport=transport,
            timeout=timeout,
        )

    async def post(self, path: str, *, json: Any) -> httpx.Response:
        """POST *json* to *path* relative to ``base_url``."""
        return await self._client.post(path, json=json)

    async def aclose(self) -> None:
        """Close the underlying :class:`httpx.AsyncClient`."""
        await self._client.aclose()

    async def __aenter__(self) -> LLMHTTPClient:
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc_val, exc_tb)
