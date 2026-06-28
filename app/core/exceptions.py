"""Typed exception hierarchy for the LLM service layer."""

from __future__ import annotations

import json
from typing import Any


class LLMProviderError(Exception):
    """Raised when the LLM provider returns an error or retries are exhausted.

    Attributes:
        provider:    "openrouter" or "ollama".
        status_code: HTTP status code from the upstream response, or -1 for
                     connection-level failures.
        payload:     Raw response body (string, dict, or None).
        request_id:  Correlation id bound at the time of the call.
    """

    def __init__(
        self,
        message: str,
        *,
        provider: str,
        status_code: int,
        payload: Any = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.payload = payload
        self.request_id = request_id

    def __str__(self) -> str:
        try:
            payload_repr = json.dumps(self.payload, default=str)
        except Exception:  # noqa: BLE001
            payload_repr = repr(self.payload)
        return (
            f"LLMProviderError(provider={self.provider!r}, "
            f"status_code={self.status_code}, "
            f"request_id={self.request_id!r}, "
            f"payload={payload_repr}): {super().__str__()}"
        )


class LLMOutputValidationError(Exception):
    """Raised when a structured-output parse fails inside LLMService.

    Defined in Task 1; first used in Task 4.
    """
