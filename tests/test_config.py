"""Tests for app.core.config — covers all Step 1 acceptance criteria."""

from collections.abc import Generator

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Generator[None, None, None]:
    """Purge lru_cache before/after every test so env changes take effect."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Settings field validation
# ---------------------------------------------------------------------------


def test_settings_valid_env_returns_model_name() -> None:
    """AC: given valid env, Settings resolves openrouter_model without raising."""
    s = Settings(pg_dsn="postgresql+psycopg://app:app@localhost:5432/app")
    assert s.openrouter_model == "gpt-4.1-mini"


def test_openrouter_missing_api_key_raises_validation_error() -> None:
    """AC: LLM_PROVIDER=openrouter + missing key → ValidationError naming OPENROUTER_API_KEY."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            pg_dsn="postgresql+psycopg://app:app@localhost:5432/app",
            llm_provider="openrouter",
            openrouter_api_key=None,
        )
    assert "OPENROUTER_API_KEY" in str(exc_info.value)


def test_ollama_provider_no_key_required() -> None:
    """AC: LLM_PROVIDER=ollama + no key → no error."""
    s = Settings(
        pg_dsn="postgresql+psycopg://app:app@localhost:5432/app",
        llm_provider="ollama",
        openrouter_api_key=None,
    )
    assert s.llm_provider == "ollama"


def test_settings_openrouter_base_url_default() -> None:
    """openrouter_base_url field ships the correct default."""
    s = Settings(pg_dsn="postgresql+psycopg://app:app@localhost:5432/app")
    assert s.openrouter_base_url == "https://openrouter.ai/api/v1"


def test_settings_repr_masks_api_key() -> None:
    """Safeguard 3: Settings.__repr__ must not expose the raw API key value."""
    s = Settings(
        pg_dsn="postgresql+psycopg://app:app@localhost:5432/app",
        llm_provider="openrouter",
        openrouter_api_key="sk-secret-key-12345",
    )
    assert "sk-secret-key-12345" not in repr(s)


# ---------------------------------------------------------------------------
# get_settings() factory
# ---------------------------------------------------------------------------


def test_get_settings_lru_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC: @lru_cache — repeated calls return the exact same Settings object."""
    monkeypatch.setenv("PG_DSN", "postgresql+psycopg://app:app@localhost:5432/app")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
