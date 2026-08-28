"""Main FastAPI application factory and entry point."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.api import api_router
from backend.app.core.config import settings
from backend.app.core.errors import register_exception_handlers
from backend.app.core.logging import setup_logging

setup_logging(debug=settings.DEBUG)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    )

    # 1. Request ID and Timing Middleware
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", f"req-{uuid.uuid4().hex[:12]}")
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        return response

    # 2. CORS Middleware Configuration
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.BACKEND_CORS_ORIGINS),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 3. Register Structured Exception Handlers
    register_exception_handlers(app)

    # 4. Mount API v1 Router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # 5. Root Info Endpoint
    @app.get("/", tags=["Root"], summary="API Root Info")
    def root_info() -> dict[str, str]:
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": f"{settings.API_V1_PREFIX}/docs",
            "health": f"{settings.API_V1_PREFIX}/health",
        }

    return app


app = create_application()
