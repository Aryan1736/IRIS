"""Risk serving integration service for deterministic IRIS risk records."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from fastapi import HTTPException

from backend.app.core.config import settings
from src.serving.repository import ServingRepository


_CACHED_REPOSITORY: ServingRepository | None = None
_CACHED_DIR: Path | None = None


def resolve_serving_dir(configured_path: str | Path) -> Path:
    """Resolve serving artifact directory with fallback to repository root."""
    target = Path(configured_path)
    if target.is_absolute() and target.exists():
        return target
    cwd_candidate = (Path.cwd() / target).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    repo_root = Path(__file__).resolve().parents[3]
    repo_candidate = (repo_root / target).resolve()
    if repo_candidate.exists():
        return repo_candidate
    return cwd_candidate


def get_serving_repository(artifact_dir: Path | None = None) -> ServingRepository:
    """Retrieve or initialize the read-only ServingRepository."""
    global _CACHED_REPOSITORY, _CACHED_DIR
    target_dir = resolve_serving_dir(artifact_dir or settings.SERVING_DIR)

    if _CACHED_REPOSITORY is None or _CACHED_DIR != target_dir:
        try:
            _CACHED_REPOSITORY = ServingRepository(target_dir)
            _CACHED_DIR = target_dir
        except (FileNotFoundError, RuntimeError) as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Serving artifact is unavailable ({exc}); run python -m src.serving.builder first",
            ) from exc

    return _CACHED_REPOSITORY



_CACHED_UNIFIED_PREDICTOR: Any = None


def get_unified_risk_predictor(artifacts_dir: Path | str | None = None) -> Any:
    """Retrieve or initialize the cached UnifiedRiskPredictor."""
    global _CACHED_UNIFIED_PREDICTOR
    if _CACHED_UNIFIED_PREDICTOR is None:
        from src.ml.unified_risk_predictor import UnifiedRiskPredictor
        target = resolve_serving_dir(artifacts_dir or "artifacts/ml/schedule_extension_3m")
        _CACHED_UNIFIED_PREDICTOR = UnifiedRiskPredictor.load(target)
    return _CACHED_UNIFIED_PREDICTOR


def reset_cached_repository() -> None:
    """Reset cached repository and predictor instances (useful for hermetic test fixtures)."""
    global _CACHED_REPOSITORY, _CACHED_DIR, _CACHED_UNIFIED_PREDICTOR
    _CACHED_REPOSITORY = None
    _CACHED_DIR = None
    _CACHED_UNIFIED_PREDICTOR = None

