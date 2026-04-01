"""SimPy-powered digital twin simulator for telemetry and predictive insights."""

from __future__ import annotations

import asyncio
import random
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, Dict, Iterable, List, Optional

import simpy

from ... import constants
from ..idsl.repository import IDSLRepository
from ..models.idsl import EquipmentPerformance, HistoricalSensorRecord, PLCTag, SCADASensor
from ..models.simulator import (
    ActiveFault,
    FaultScenario,
    KpiMetric,
    PredictiveSuggestion,
    Severity,
    TelemetrySource,
    TelemetryValue,
    TwinAlert,
    TwinSnapshot,
)
from .anomaly_detector import AnomalyDetector


@dataclass(slots=True)
class SignalState:
    source: TelemetrySource
    signal_id: str
    tag_name: str
    description: Optional[str]
    unit: Optional[str]
    baseline: float
    value: float
    warning_high: float
    critical_high: float
    warning_low: Optional[float]
    critical_low: Optional[float]


@dataclass(slots=True)
class ActiveFaultState:
    scenario: FaultScenario
    remaining_ticks: int
    started_at: datetime


def _to_float(value: object) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        numeric = float(text.split()[0])
        return numeric
    except ValueError:
        return None


class SimPyDigitalTwinSimulator:
    """Runs a discrete-time simulation that enriches IDSL data."""

    def __init__(
        self,
        repo: IDSLRepository,
        tick_seconds: float | None = None,
        acceleration: float | None = None,
    ) -> None:
        self.repo = repo
        self.tick_seconds = tick_seconds or constants.SIMULATION_TICK_SECONDS
        self.acceleration = acceleration or constants.SIMULATION_ACCELERATION_FACTOR
        self.real_sleep = max(self.tick_seconds / self.acceleration, 0.05)

        self.env = simpy.Environment()
        self._snapshot_queue: Deque[TwinSnapshot] = deque()
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

        self._signals: Dict[str, SignalState] = {}
        self._historical: Dict[str, HistoricalSensorRecord] = {
            record.tag_name: record for record in repo.historical_sensor_records()
        }
        self._equipment_index: Dict[str, EquipmentPerformance] = {
            equipment.machine_id: equipment for equipment in repo.equipment_performance()
        }

        self._listeners: set[asyncio.Queue[TwinSnapshot]] = set()
        self._snapshot: TwinSnapshot | None = None

        self._fault_catalog: Dict[str, FaultScenario] = {
            scenario.scenario_id: scenario
            for scenario in self._default_fault_scenarios()
        }
        self._active_faults: Dict[str, ActiveFaultState] = {}

        self._prime_signal_state()
        self._history: deque[TwinSnapshot] = deque(maxlen=100)
        self._anomaly_detector = AnomalyDetector(tag_names=["REACTOR_TEMP", "CRUSHER_VIBE", "REACTOR_PRESSURE", "MOTOR_CURRENT"])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def start(self) -> None:
        if self._task is not None:
            return

        self.env.process(self._simulation_process())
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None
        self._stop_event = asyncio.Event()

    def current_snapshot(self) -> TwinSnapshot:
        if self._snapshot is None:
            self._snapshot = self._build_snapshot(sim_time=0.0)
        return self._snapshot

    def subscribe(self) -> asyncio.Queue[TwinSnapshot]:
        queue: asyncio.Queue[TwinSnapshot] = asyncio.Queue(maxsize=5)
        if self._snapshot is not None:
            queue.put_nowait(self._snapshot)
        self._listeners.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[TwinSnapshot]) -> None:
        self._listeners.discard(queue)

    def list_faults(self) -> list[FaultScenario]:
        return list(self._fault_catalog.values())

    def active_faults(self) -> list[ActiveFault]:
        return [self._serialize_fault(state) for state in self._active_faults.values()]

    def trigger_fault(self, scenario_id: str) -> FaultScenario:
        scenario = self._fault_catalog.get(scenario_id)
        if scenario is None:
            raise KeyError(f"Unknown fault scenario '{scenario_id}'")
        self._active_faults[scenario_id] = ActiveFaultState(
            scenario=scenario,
            remaining_ticks=scenario.duration_ticks,
            started_at=datetime.utcnow(),
        )
        return scenario

    def clear_fault(self, scenario_id: str) -> None:
        self._active_faults.pop(scenario_id, None)

    def clear_all_faults(self) -> None:
        self._active_faults.clear()

    def get_history(self) -> list[TwinSnapshot]:
        return list(self._history)

    def get_topology(self) -> dict:
        """Return the UNS hierarchy as a tree."""
        tree = {"name": "Phoenix", "children": []}
        assets = {}
        for tag in self._signals.keys():
            uns = self._to_uns(tag)
            parts = uns.split("/") # Phoenix, Asset, Category, Metric
            if len(parts) < 4: continue
            
            asset_name = parts[1]
            if asset_name not in assets:
                asset_node = {"name": asset_name, "children": []}
                assets[asset_name] = asset_node
                tree["children"].append(asset_node)
            
            # Simple 2-level tree for now
            assets[asset_name]["children"].append({"name": parts[3], "type": parts[2]})
        return tree

    # ------------------------------------------------------------------
    # Simulation internals
    # ------------------------------------------------------------------
    def _prime_signal_state(self) -> None:
        for tag in self.repo.plc_tags():
            value = _to_float(tag.value)
            if value is None:
                continue
            hist = self._historical.get(tag.tag_name or "")
            warning_high, critical_high, warning_low, critical_low = self._derive_thresholds(value, hist)
            state = SignalState(
                source=TelemetrySource.plc,
                signal_id=tag.plc_id,
                tag_name=tag.tag_name or tag.plc_id,
                description=tag.description,
                unit=tag.unit,
                baseline=value,
                value=value,
                warning_high=warning_high,
                critical_high=critical_high,
                warning_low=warning_low,
                critical_low=critical_low,
            )
            self._signals[state.tag_name] = state

        for sensor in self.repo.scada_sensors():
            value = _to_float(sensor.value)
            if value is None:
                continue
            hist = self._historical.get(sensor.tag_name or "")
            warning_high, critical_high, warning_low, critical_low = self._derive_thresholds(value, hist)
            state = SignalState(
                source=TelemetrySource.scada,
                signal_id=sensor.sensor_id,
                tag_name=sensor.tag_name or sensor.sensor_id,
                description=sensor.description,
                unit=sensor.unit,
                baseline=value,
                value=value,
                warning_high=warning_high,
                critical_high=critical_high,
                warning_low=warning_low,
                critical_low=critical_low,
            )
            self._signals.setdefault(state.tag_name, state)

        # --- Phoenix Synthetic Signals (always present for fault injection) ---
        _synthetic: list[tuple[str, str, float, str]] = [
            ("REACTOR_TEMP",     "Reactor-05 Temperature",       65.0, "°C"),
            ("CRUSHER_VIBE",     "Cement Crusher Vibration",      2.5, "mm/s"),
            ("REACTOR_PRESSURE", "Reactor-05 Pressure",           4.2, "bar"),
            ("MOTOR_CURRENT",    "Drive Motor Current",          35.0, "A"),
        ]
        for tag, desc, baseline, unit in _synthetic:
            if tag not in self._signals:
                wh, ch, wl, cl = self._derive_thresholds(baseline, None)
                self._signals[tag] = SignalState(
                    source=TelemetrySource.plc,
                    signal_id=f"phoenix-{tag.lower()}",
                    tag_name=tag,
                    description=desc,
                    unit=unit,
                    baseline=baseline,
                    value=baseline,
                    warning_high=wh,
                    critical_high=ch,
                    warning_low=wl,
                    critical_low=cl,
                )

    def _derive_thresholds(
        self,
        base_value: float,
        hist: Optional[HistoricalSensorRecord],
    ) -> tuple[float, float, Optional[float], Optional[float]]:
        if hist and hist.max_value is not None:
            warning_high = hist.max_value * 1.05
            critical_high = hist.max_value * 1.15
        else:
            warning_high = base_value * 1.1
            critical_high = base_value * 1.25

        if base_value <= 0:
            return warning_high, critical_high, None, None

        if hist and hist.min_value is not None:
            warning_low = hist.min_value * 0.95
            critical_low = hist.min_value * 0.85
        else:
            warning_low = base_value * 0.9
            critical_low = base_value * 0.8

        return warning_high, critical_high, warning_low, critical_low

    def _simulation_process(self):
        while True:
            yield self.env.timeout(self.tick_seconds)
            snapshot = self._build_snapshot(sim_time=self.env.now)
            self._snapshot_queue.append(snapshot)

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            if not self.env._queue:
                await asyncio.sleep(self.real_sleep)
                continue
            self.env.step()
            while self._snapshot_queue:
                snapshot = self._snapshot_queue.popleft()
                self._snapshot = snapshot
                self._history.append(snapshot)
                self._broadcast(snapshot)
            await asyncio.sleep(self.real_sleep)

        # Drain any pending snapshots on shutdown
        while self._snapshot_queue:
            snapshot = self._snapshot_queue.popleft()
            self._snapshot = snapshot
            self._broadcast(snapshot)

    def _broadcast(self, snapshot: TwinSnapshot) -> None:
        for queue in list(self._listeners):
            try:
                queue.put_nowait(snapshot)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    queue.put_nowait(snapshot)
                except asyncio.QueueFull:
                    # listener is too slow; drop it
                    self._listeners.discard(queue)

    def _build_snapshot(self, sim_time: float) -> TwinSnapshot:
        telemetry: List[TelemetryValue] = []
        alerts: List[TwinAlert] = []
        suggestions: List[PredictiveSuggestion] = []
        active_faults_list: List[ActiveFault] = []

        now = datetime.utcnow()
        
        # 1. Update Faults
        for fault_id, state in list(self._active_faults.items()):
            active_faults_list.append(self._serialize_fault(state))
            state.remaining_ticks -= 1
            if state.remaining_ticks <= 0:
                self._active_faults.pop(fault_id, None)

        # 2. Physics & Telemetry Engine
        # Track previous values for trend prediction
        for state in self._signals.values():
            prev_value = state.value
            
            # Physics Coupling (Phoenix Thermodynamic Engine)
            coupling_delta = 0.0
            if state.tag_name == "REACTOR_PRESSURE":
                # Pressure follows Temperature (approx Boyle/Charles law)
                temp_state = self._signals.get("REACTOR_TEMP")
                if temp_state:
                    coupling_delta = (temp_state.value - temp_state.baseline) * 0.15
            
            if state.tag_name == "CRUSHER_VIBE":
                # Vibration follows Current/Load
                cur_state = self._signals.get("MOTOR_CURRENT")
                if cur_state:
                    coupling_delta = (cur_state.value - cur_state.baseline) * 0.08

            fault_delta = sum(
                fault.scenario.delta
                for fault in self._active_faults.values()
                if fault.scenario.target_tag == state.tag_name
            )
            
            noise = random.gauss(0, abs(state.baseline) * 0.01)
            drift = (state.baseline - state.value) * 0.03
            state.value += noise + drift + fault_delta + coupling_delta

            # Linear Trend (TTC prediction)
            delta_v = state.value - prev_value
            ttc_min = None
            if delta_v > 0 and state.critical_high:
                ttc_min = (state.critical_high - state.value) / max(delta_v, 0.001) / 60.0
            elif delta_v < 0 and state.critical_low:
                ttc_min = (state.critical_low - state.value) / min(delta_v, -0.001) / 60.0

            status = self._evaluate_status(state)
            
            # Map to UNS Namespace
            uns_tag = self._to_uns(state.tag_name)
            
            telemetry.append(
                TelemetryValue(
                    source=state.source,
                    signalId=state.signal_id,
                    tagName=uns_tag,
                    description=state.description,
                    unit=state.unit,
                    value=round(state.value, 3),
                    status=status,
                    timestamp=now,
                )
            )

            # 3. Intelligent Alerts (with TTC)
            if status is not Severity.normal or (ttc_min and 0 < ttc_min < 10):
                msg = self._alert_message(state, status)
                if ttc_min and 0 < ttc_min < 10:
                    msg += f" (Predictive Warning: TTC {ttc_min:.1f}m)"
                    if status == Severity.normal:
                        status = Severity.warning # Elevate due to trend

                alerts.append(
                    TwinAlert(
                        alertId=f"alert-{state.tag_name}",
                        message=msg,
                        severity=status,
                        tagName=uns_tag,
                        originatedFrom=state.source,
                        detectedAt=now,
                    )
                )
                
                # Predictive Suggestion
                suggestion = self._prediction_for_state(state, status, now)
                if ttc_min and 0 < ttc_min < 10:
                    suggestion.title = f"PREDICTIVE: {state.tag_name} Violation"
                    suggestion.confidence = 0.85
                suggestions.append(suggestion)

        # 4. Deep Learning Anomaly Detection
        current_data = {tag: state.value for tag, state in self._signals.items()}
        self._anomaly_detector.add_data_point(current_data)
        anomaly_score = self._anomaly_detector.detect_anomaly()

        # If score is high, elevate predictive suggestions
        if anomaly_score > 0.6:
            suggestions.append(
                PredictiveSuggestion(
                    suggestionId="ml-anomaly",
                    title="LSTM: Multi-variate Anomaly Detected",
                    description=f"Neural network has detected a non-linear deviation in current telemetry patterns (Score: {anomaly_score:.2f})",
                    severity=Severity.critical,
                    relatedAssets=["Reactor-05", "Cement-Crusher"],
                    recommendedActions=["Inspect spatial digital twin for heat-spots", "Recalibrate edge sensors", "Execute safety SOP"],
                    confidence=anomaly_score,
                    etaHours=0.1
                )
            )

        kpis = self._compute_kpis()

        return TwinSnapshot(
            generatedAt=now,
            simulationTime=sim_time,
            telemetry=telemetry,
            alerts=alerts,
            predictiveSuggestions=suggestions,
            kpis=kpis,
            activeFaults=active_faults_list,
            anomalyScore=anomaly_score,
        )

    def _to_uns(self, tag: str) -> str:
        """Map internal tags to Phoenix Unified Name Space."""
        if "REACTOR" in tag:
            part = "Reactor_05"
        elif "CRUSHER" in tag or "MOTOR" in tag:
            part = "Cement_Crusher"
        else:
            return tag
            
        metric = tag.split("_")[-1].capitalize()
        return f"Phoenix/{part}/Telemetry/{metric}"

    def apply_command(self, tag_name: str, value_delta: float) -> None:
        """Bi-directional control: Apply a one-time adjustment to an internal signal."""
        # Find internal tag from potentially UNS tag
        internal_tag = tag_name.split("/")[-1].upper() if "/" in tag_name else tag_name
        # Match mapping
        tag_map = {
            "TEMPERATURE": "REACTOR_TEMP",
            "PRESSURE": "REACTOR_PRESSURE",
            "VIBRATION": "CRUSHER_VIBE",
            "VIBE": "CRUSHER_VIBE",
            "CURRENT": "MOTOR_CURRENT",
        }
        target = tag_map.get(internal_tag, tag_name)
        if target in self._signals:
            self._signals[target].value += value_delta

    def _evaluate_status(self, state: SignalState) -> Severity:
        value = state.value
        if state.critical_high is not None and value >= state.critical_high:
            return Severity.critical
        if state.warning_high is not None and value >= state.warning_high:
            return Severity.warning
        if state.critical_low is not None and value <= state.critical_low:
            return Severity.critical
        if state.warning_low is not None and value <= state.warning_low:
            return Severity.warning
        return Severity.normal

    def _alert_message(self, state: SignalState, severity: Severity) -> str:
        direction = "high" if state.value >= state.baseline else "low"
        return (
            f"{state.tag_name} {direction} deviation detected (value={state.value:.2f} {state.unit or ''})."
            f" Severity: {severity.value.upper()}"
        )

    def _prediction_for_state(self, state: SignalState, severity: Severity, now: datetime) -> PredictiveSuggestion:
        related_assets = self._suggest_assets_for_signal(state)
        title = f"Investigate {state.tag_name} deviation"
        description = (
            f"The signal {state.tag_name} has drifted {('above' if state.value >= state.baseline else 'below')}"
            f" its baseline of {state.baseline:.2f}{state.unit or ''}."
        )
        recommended_actions = [
            "Validate live readings via SCADA/PLC",
            "Consult relevant SOP for corrective actions",
            "Evaluate resource availability for maintenance",
        ]

        return PredictiveSuggestion(
            suggestionId=f"ps-{state.tag_name}",
            title=title,
            description=description,
            severity=severity,
            relatedAssets=related_assets,
            recommendedActions=recommended_actions,
            confidence=0.75 if severity is Severity.warning else 0.55,
            etaHours=2.0 if severity is Severity.warning else 0.5,
        )

    def _suggest_assets_for_signal(self, state: SignalState) -> List[str]:
        related: List[str] = []
        for equipment in self._equipment_index.values():
            if state.tag_name.split("_")[0].lower() in equipment.machine_name.lower():
                related.append(equipment.machine_id)
        return related or [state.signal_id]

    def _compute_kpis(self) -> List[KpiMetric]:
        assets = self.repo.assets()
        if assets:
            avg_performance = sum(asset.performance_pct or 0 for asset in assets) / len(assets)
            avg_downtime = sum(asset.downtime_hours or 0 for asset in assets) / len(assets)
        else:
            avg_performance = 0.0
            avg_downtime = 0.0

        performance_status = Severity.normal if avg_performance >= 90 else Severity.warning
        downtime_status = Severity.normal if avg_downtime <= 4 else Severity.warning

        return [
            KpiMetric(
                id="asset-performance",
                name="Average Asset Performance",
                value=round(avg_performance, 2),
                unit="%",
                trend=random.uniform(-0.5, 0.5),
                status=performance_status,
            ),
            KpiMetric(
                id="asset-downtime",
                name="Average Downtime",
                value=round(avg_downtime, 2),
                unit="hrs",
                trend=random.uniform(-0.2, 0.2),
                status=downtime_status,
            ),
        ]

    def _serialize_fault(self, state: ActiveFaultState) -> ActiveFault:
        return ActiveFault(
            scenarioId=state.scenario.scenario_id,
            name=state.scenario.name,
            severity=state.scenario.severity,
            remainingTicks=max(state.remaining_ticks, 0),
            startedAt=state.started_at,
        )

    def _default_fault_scenarios(self) -> Iterable[FaultScenario]:
        return [
            FaultScenario(
                scenarioId="reactor-temp-spike",
                name="Reactor-05 High Temperature",
                description="Simulate rapid temperature rise in Reactor-05 to trigger alarm and SOP guidance.",
                targetTag="REACTOR_TEMP",
                delta=18.0,
                durationTicks=600,
                severity=Severity.critical,
            ),
            FaultScenario(
                scenarioId="crusher-vibration-spike",
                name="Cement Crusher VFD Overvoltage",
                description="VFD instability on Cement Crusher causing vibration surge and electrical alerts.",
                targetTag="CRUSHER_VIBE",
                delta=15.0,
                durationTicks=600,
                severity=Severity.critical,
            ),
            FaultScenario(
                scenarioId="coolant-flow-drop",
                name="Coolant Flow Drop",
                description="Reduce coolant flow to trigger predictive maintenance suggestions.",
                targetTag="REACTOR_PRESSURE",
                delta=-6.0,
                durationTicks=600,
                severity=Severity.warning,
            ),
            FaultScenario(
                scenarioId="motor-current-rise",
                name="Motor Current Overload",
                description="Increase motor current to emulate overload conditions on drive systems.",
                targetTag="MOTOR_CURRENT",
                delta=4.0,
                durationTicks=600,
                severity=Severity.warning,
            ),
        ]


