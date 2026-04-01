"""Routes exposing the simulated twin telemetry and control hooks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi import WebSocket, WebSocketDisconnect

from ...models.simulator import (
    ActiveFault,
    FaultScenario,
    KpiMetric,
    PredictiveSuggestion,
    TelemetryValue,
    TwinAlert,
    TwinSnapshot,
    TwinCommand,
)
from ..deps import get_simulator
from ...services.simulator import SimPyDigitalTwinSimulator


router = APIRouter(prefix="/twin", tags=["twin"])


@router.get("/snapshot", response_model=TwinSnapshot)
async def get_snapshot(simulator = Depends(get_simulator)) -> TwinSnapshot:
    return simulator.current_snapshot()


@router.get("/telemetry", response_model=list[TelemetryValue])
async def get_telemetry(simulator = Depends(get_simulator)) -> list[TelemetryValue]:
    return simulator.current_snapshot().telemetry


@router.get("/alerts", response_model=list[TwinAlert])
async def get_alerts(simulator = Depends(get_simulator)) -> list[TwinAlert]:
    return simulator.current_snapshot().alerts


@router.get("/predictive", response_model=list[PredictiveSuggestion])
async def get_predictive(simulator = Depends(get_simulator)) -> list[PredictiveSuggestion]:
    return simulator.current_snapshot().predictive_suggestions


@router.get("/kpis", response_model=list[KpiMetric])
async def get_kpis(simulator = Depends(get_simulator)) -> list[KpiMetric]:
    return simulator.current_snapshot().kpis


@router.get("/fault-scenarios", response_model=list[FaultScenario])
async def list_fault_scenarios(simulator = Depends(get_simulator)) -> list[FaultScenario]:
    return simulator.list_faults()


@router.get("/faults/active", response_model=list[ActiveFault])
async def list_active_faults(simulator = Depends(get_simulator)) -> list[ActiveFault]:
    return simulator.active_faults()


@router.post("/fault-scenarios/{scenario_id}/trigger", response_model=FaultScenario)
async def trigger_fault(scenario_id: str, simulator = Depends(get_simulator)) -> FaultScenario:
    try:
        return simulator.trigger_fault(scenario_id)
    except KeyError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/fault-scenarios/{scenario_id}/clear", status_code=204)
async def clear_fault(scenario_id: str, simulator = Depends(get_simulator)) -> None:
    simulator.clear_fault(scenario_id)


@router.post("/fault-scenarios/clear-all", status_code=204)
async def clear_all_faults(simulator = Depends(get_simulator)) -> None:
    simulator.clear_all_faults()


@router.post("/command", status_code=204)
async def apply_command(command: TwinCommand, simulator = Depends(get_simulator)) -> None:
    simulator.apply_command(command.tag_name, command.value_delta)


@router.get("/history", response_model=list[TwinSnapshot])
async def get_history(simulator = Depends(get_simulator)) -> list[TwinSnapshot]:
    return simulator.get_history()


@router.get("/topology")
async def get_topology(simulator = Depends(get_simulator)) -> dict:
    return simulator.get_topology()


@router.websocket("/stream")
async def twin_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    simulator: SimPyDigitalTwinSimulator | None = getattr(websocket.app.state, "simulator", None)  # type: ignore[attr-defined]
    if simulator is None:
        await websocket.close(code=1011)
        return

    queue = simulator.subscribe()
    try:
        while True:
            snapshot = await queue.get()
            await websocket.send_json(snapshot.model_dump(mode="json", by_alias=True))
    except WebSocketDisconnect:
        pass
    finally:
        simulator.unsubscribe(queue)


