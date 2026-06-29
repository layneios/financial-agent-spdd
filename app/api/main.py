from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import get_settings
from app.core.logging import bind_request_id
from app.core.services_container import ServicesContainer
from app.services.llm_client import LLMHTTPClient
from app.services.llm_service import LLMService


@asynccontextmanager
async def _lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Build the ServicesContainer once and store it on app.state."""
    settings = get_settings()
    http_client = LLMHTTPClient(
        base_url=(
            settings.openrouter_base_url
            if settings.llm_provider == "openrouter"
            else settings.ollama_base_url
        ),
        api_key=settings.openrouter_api_key,
    )
    llm_service = LLMService(settings=settings, http_client=http_client)
    application.state.container = ServicesContainer(
        settings=settings, llm_service=llm_service
    )
    yield
    await http_client.aclose()


app = FastAPI(title="Financial Helpdesk Agent", version="0.0.0", lifespan=_lifespan)


class _RequestIdMiddleware(BaseHTTPMiddleware):
    """Echo ``X-Request-Id`` from the incoming request or generate a UUIDv4.

    Binds the id via :func:`bind_request_id` so every log line in the
    request's async context carries it automatically.
    Sets ``X-Request-Id`` on the outgoing response.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        bind_request_id(request_id)
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


app.add_middleware(_RequestIdMiddleware)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> JSONResponse:
    """Readiness probe — returns 200 once the lifespan container is wired."""
    return JSONResponse({"status": "ok"})

