"""Pydantic schemas representing simulator outputs and fault scenarios."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    normal = "normal"
    warning = "warning"
    critical = "critical"


class TelemetrySource(str, Enum):
    plc = "plc"
    scada = "scada"


class KpiMetric(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    value: float
    unit: Optional[str] = None
    trend: float = 0.0
    status: Severity = Severity.normal


class TelemetryValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: TelemetrySource
    signal_id: str = Field(alias="signalId")
    tag_name: str = Field(alias="tagName")
    description: Optional[str] = None
    unit: Optional[str] = None
    value: float
    status: Severity = Severity.normal
    timestamp: datetime


class TwinAlert(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    alert_id: str = Field(alias="alertId")
    message: str
    severity: Severity
    tag_name: Optional[str] = Field(alias="tagName", default=None)
    originated_from: TelemetrySource = Field(alias="originatedFrom")
    detected_at: datetime = Field(alias="detectedAt")


class PredictiveSuggestion(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    suggestion_id: str = Field(alias="suggestionId")
    title: str
    description: str
    severity: Severity = Severity.warning
    related_assets: List[str] = Field(default_factory=list, alias="relatedAssets")
    recommended_actions: List[str] = Field(default_factory=list, alias="recommendedActions")
    confidence: float = 0.7
    eta_hours: float = Field(default=0.0, alias="etaHours")


class FaultScenario(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    name: str
    description: str
    target_tag: str = Field(alias="targetTag")
    delta: float
    duration_ticks: int = Field(alias="durationTicks")
    severity: Severity


class ActiveFault(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_id: str = Field(alias="scenarioId")
    name: str
    severity: Severity
    remaining_ticks: int = Field(alias="remainingTicks")
    started_at: datetime = Field(alias="startedAt")


class TwinSnapshot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    generated_at: datetime = Field(alias="generatedAt")
    simulation_time: float = Field(alias="simulationTime")
    telemetry: List[TelemetryValue] = []
    alerts: List[TwinAlert] = []
    predictive_suggestions: List[PredictiveSuggestion] = Field(default_factory=list, alias="predictiveSuggestions")
    kpis: List[KpiMetric] = []
    active_faults: List[ActiveFault] = Field(default_factory=list, alias="activeFaults")
    anomaly_score: float = Field(default=0.0, alias="anomalyScore")


class TwinCommand(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tag_name: str = Field(alias="tagName")
    value_delta: float = Field(alias="valueDelta")


