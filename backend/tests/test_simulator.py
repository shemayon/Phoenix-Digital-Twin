import asyncio

import pytest

from backend import constants
from backend.app.idsl.repository import IDSLRepository
from backend.app.services.simulator import SimPyDigitalTwinSimulator


@pytest.mark.asyncio
async def test_simulator_generates_snapshots_and_faults() -> None:
    repo = IDSLRepository()
    repo.load_from_excel(constants.SAMPLE_DATA_PATH)

    simulator = SimPyDigitalTwinSimulator(repo, tick_seconds=0.5, acceleration=10.0)
    await simulator.start()

    await asyncio.sleep(0.3)
    snapshot = simulator.current_snapshot()
    assert snapshot.telemetry, "telemetry should be populated"

    # trigger a fault and ensure it appears in subsequent snapshots
    simulator.trigger_fault("reactor-temp-spike")
    await asyncio.sleep(0.2)
    active_faults = simulator.active_faults()
    assert active_faults, "fault should become active"

    await simulator.stop()

