"""ServicesContainer — bundles Settings + LLMService for lifespan wiring."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.services.llm_service import LLMService


@dataclass
class ServicesContainer:
    """Holds all application-scoped service singletons.

    Constructed once inside the FastAPI lifespan and stored on ``app.state``.
    """

    settings: Settings
    llm_service: LLMService
