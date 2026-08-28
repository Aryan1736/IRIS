"""Future Machine Learning (ML) & Statistical Modeling interface contracts.

IMPORTANT ARCHITECTURAL RULE:
No ML models are trained yet. No mock scores, simulated predictions, or synthetic risk
indicators are permitted in the application.

These protocol definitions establish the contract so future ML teammates can plug in
real, validated models (e.g. delay forecasting, cost overrun risk, anomaly alerting)
without altering the foundation or API routing layer.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, runtime_checkable


class ModelStatus(str, Enum):
    """Lifecycle status for an analytical/statistical model."""
    NOT_TRAINED = "NOT_TRAINED"
    MODEL_NOT_DEPLOYED = "MODEL_NOT_DEPLOYED"
    TRAINING = "TRAINING"
    READY = "READY"
    DEPRECATED = "DEPRECATED"


class ModelMetadata:
    """Metadata describing a registered model artifact."""
    def __init__(
        self,
        model_name: str,
        version: str,
        status: ModelStatus,
        trained_at: str | None = None,
        metrics: dict[str, float] | None = None,
        features: list[str] | None = None,
    ) -> None:
        self.model_name = model_name
        self.version = version
        self.status = status
        self.trained_at = trained_at
        self.metrics = metrics or {}
        self.features = features or []


@runtime_checkable
class PredictionService(Protocol):
    """Protocol for project trajectory and completion prediction services."""

    def predict_completion_date(self, project_code: str) -> dict[str, Any]:
        """Predict completion date for a project observation.
        
        Must return explicit status (e.g. ModelStatus.NOT_TRAINED) until real models are loaded.
        """
        ...

    def predict_cost_overrun(self, project_code: str) -> dict[str, Any]:
        """Predict cost overrun for a project observation."""
        ...


@runtime_checkable
class RiskService(Protocol):
    """Protocol for project risk scoring and vulnerability assessment."""

    def evaluate_project_risk(self, project_code: str) -> dict[str, Any]:
        """Calculate multi-dimensional risk scores from validated model outputs."""
        ...


@runtime_checkable
class AlertService(Protocol):
    """Protocol for anomaly detection and longitudinal divergence alerts."""

    def generate_alerts(self, project_code: str, report_month: str) -> list[dict[str, Any]]:
        """Identify verified anomalous transitions or data warnings."""
        ...


@runtime_checkable
class ModelRegistry(Protocol):
    """Protocol for model artifact tracking, loading, and lineage."""

    def get_model_status(self, model_name: str) -> ModelStatus:
        """Inspect deployment status of a named model."""
        ...

    def get_model_metadata(self, model_name: str) -> ModelMetadata | None:
        """Inspect metadata, version, and validation metrics for a named model."""
        ...
