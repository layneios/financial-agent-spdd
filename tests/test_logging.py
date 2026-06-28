"""Tests for app.core.logging — covers Step 2 acceptance criteria."""

import json
import re
from collections.abc import Generator

import pytest

from app.core.config import Settings
from app.core.logging import bind_request_id, configure_logging, get_request_id

_BASE_SETTINGS = Settings(
    pg_dsn="postgresql+psycopg://app:app@localhost:5432/app",
    log_format="json",
)

_TEXT_SETTINGS = Settings(
    pg_dsn="postgresql+psycopg://app:app@localhost:5432/app",
    log_format="text",
)


@pytest.fixture(autouse=True)
def _reset_request_id() -> Generator[None, None, None]:
    """Ensure the ContextVar is unbound before and after each test."""
    bind_request_id(None)
    yield
    bind_request_id(None)


# ---------------------------------------------------------------------------
# bind_request_id / get_request_id
# ---------------------------------------------------------------------------


def test_bind_request_id_sets_value() -> None:
    """bind_request_id stores the given id; get_request_id retrieves it."""
    rid = "test-request-id-001"
    bind_request_id(rid)
    assert get_request_id() == rid


def test_bind_request_id_none_generates_uuid() -> None:
    """AC: when ContextVar is unset (None passed), a fallback UUIDv4 is generated."""
    returned = bind_request_id(None)
    stored = get_request_id()
    # Both must be a valid UUID4-shaped string (non-null, 36 chars, hex+hyphens)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    assert uuid_pattern.match(returned), f"Returned value is not a UUIDv4: {returned!r}"
    assert uuid_pattern.match(stored), f"Stored value is not a UUIDv4: {stored!r}"
    assert returned == stored


def test_get_request_id_non_null_after_bind() -> None:
    """AC: asserting non-null request_id after bind_request_id (including fallback)."""
    bind_request_id(None)
    assert get_request_id() is not None
    assert get_request_id() != ""


# ---------------------------------------------------------------------------
# configure_logging — JSON format
# ---------------------------------------------------------------------------


def test_json_log_record_contains_required_fields(capsys: pytest.CaptureFixture[str]) -> None:
    """AC: LOG_FORMAT=json → every record contains timestamp, level, request_id, event."""
    from loguru import logger

    configure_logging(_BASE_SETTINGS)
    bind_request_id("req-json-001")

    # Write a test log entry
    logger.info("test_event")

    captured = capsys.readouterr()
    # loguru writes to stderr by default
    output = captured.err.strip()
    assert output, "No log output captured"

    record = json.loads(output.split("\n")[0])
    assert "timestamp" in record or "time" in record, "Missing timestamp/time field"
    assert "level" in record, "Missing level field"
    assert "request_id" in record, "Missing request_id field"
    assert record.get("request_id") == "req-json-001"
    assert "event" in record or "message" in record, "Missing event/message field"


def test_json_log_record_with_duration_ms(capsys: pytest.CaptureFixture[str]) -> None:
    """AC: when duration_ms is included as extra, it appears in JSON output."""
    from loguru import logger

    configure_logging(_BASE_SETTINGS)
    bind_request_id("req-dur-001")

    logger.bind(duration_ms=42.5).info("timed_event")

    captured = capsys.readouterr()
    output = captured.err.strip()
    assert output

    record = json.loads(output.split("\n")[0])
    assert "duration_ms" in record, "duration_ms not propagated to JSON log record"
    assert record["duration_ms"] == 42.5


# ---------------------------------------------------------------------------
# Safeguard 3 — API key redaction
# ---------------------------------------------------------------------------


def test_api_key_redacted_in_log_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Safeguard 3: openrouter_api_key / Authorization header value must not appear in logs."""
    from loguru import logger

    configure_logging(_BASE_SETTINGS)
    bind_request_id("req-redact-001")

    secret = "sk-super-secret-key-xyz"
    # Attempt to log the secret directly (simulates accidental inclusion)
    logger.bind(openrouter_api_key=secret).warning("should_be_redacted")

    captured = capsys.readouterr()
    assert secret not in captured.err, "Raw API key appeared in log output"
