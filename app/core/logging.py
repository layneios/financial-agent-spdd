"""Structured logging: configure_logging, bind_request_id, get_request_id."""

from __future__ import annotations

import json
import re
import sys
import uuid
from contextvars import ContextVar
from typing import Any

from loguru import logger

from app.core.config import Settings

# ContextVar carrying the request_id for the current async context.
_REQUEST_ID_VAR: ContextVar[str | None] = ContextVar("request_id", default=None)

# Safeguard 3 — patterns that identify sensitive log-extra keys.
_REDACT_KEY_RE = re.compile(r"(?:_api_key|_token)$", re.IGNORECASE)
_REDACT_AUTH_RE = re.compile(r"^authorization$", re.IGNORECASE)


def bind_request_id(request_id: str | None) -> str:
    """Store *request_id* in the ContextVar for the current async context.

    If *request_id* is ``None``, a UUIDv4 fallback is generated and stored.
    Returns the id that was bound.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    _REQUEST_ID_VAR.set(request_id)
    return request_id


def get_request_id() -> str | None:
    """Return the request_id currently bound in the ContextVar, or ``None``."""
    return _REQUEST_ID_VAR.get()


def _patcher(record: Any) -> None:  # type: ignore[misc]
    """Global loguru patcher: inject request_id; redact *_api_key/*_token/Authorization."""
    extra: dict[str, Any] = record["extra"]

    # Inject request_id from ContextVar when the caller hasn't bound one explicitly.
    if "request_id" not in extra:
        rid = _REQUEST_ID_VAR.get()
        extra["request_id"] = rid if rid is not None else "unbound"

    # Redact sensitive fields — Safeguard 3.
    for key in list(extra.keys()):
        if _REDACT_KEY_RE.search(key) or _REDACT_AUTH_RE.match(key):
            extra[key] = "[REDACTED]"


def configure_logging(settings: Settings) -> None:
    """Remove existing loguru handlers and install a fresh handler.

    JSON mode  → flat JSON record with ``timestamp``, ``level``, ``request_id``,
                 ``event``, plus any extra fields bound via ``logger.bind()``.
    Text mode  → human-readable line: ``timestamp | level | request_id | message``.
    """
    logger.remove()
    logger.configure(patcher=_patcher)  # type: ignore[call-arg]

    if settings.log_format == "json":

        def _json_sink(message: Any) -> None:  # type: ignore[misc]
            record = message.record
            # Exclude request_id from the extra spread — it has its own top-level key.
            extra = {k: v for k, v in record["extra"].items() if k != "request_id"}
            log_entry: dict[str, Any] = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "request_id": record["extra"].get("request_id", "unbound"),
                "event": record["message"],
                **extra,
            }
            sys.stderr.write(json.dumps(log_entry) + "\n")
            sys.stderr.flush()

        logger.add(_json_sink, level="DEBUG")  # type: ignore[arg-type]
    else:
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "{extra[request_id]} | "
                "{name}:{line} - <level>{message}</level>"
            ),
            level="DEBUG",
            colorize=False,
        )
