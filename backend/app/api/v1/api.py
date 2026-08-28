"""API v1 Router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.v1.endpoints import health, projects, system

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(system.router, tags=["System"])
api_router.include_router(projects.router, tags=["Projects"])

