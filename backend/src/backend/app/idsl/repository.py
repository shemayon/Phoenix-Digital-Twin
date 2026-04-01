"""In-memory repository acting as the Unified Namespace (IDSL) cache."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from ..models.idsl import IDSLPayload
from .loader import ExcelIDSLLoader


class IDSLRepository:
    """Simple in-memory store for the digital twin MVP."""

    def __init__(self) -> None:
        self._payload: IDSLPayload | None = None
        self._subscribers: list[Callable[[IDSLPayload], None]] = []

    @property
    def payload(self) -> IDSLPayload:
        if self._payload is None:
            raise RuntimeError("IDSL payload has not been loaded yet.")
        return self._payload

    def load_from_excel(self, workbook_path: Path) -> IDSLPayload:
        loader = ExcelIDSLLoader(workbook_path)
        payload = loader.load()
        self._payload = payload
        self._notify(payload)
        return payload

    # ------------------------------------------------------------------
    # Subscription support (used later by the simulator/streaming layer)
    # ------------------------------------------------------------------
    def subscribe(self, callback: Callable[[IDSLPayload], None]) -> None:
        self._subscribers.append(callback)

    def _notify(self, payload: IDSLPayload) -> None:
        for callback in list(self._subscribers):
            callback(payload)

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------
    def assets(self):  # noqa: D401 - short proxy docstring unnecessary
        return self.payload.assets

    def maintenance_records(self):
        return self.payload.maintenance_records

    def inventory_items(self):
        return self.payload.inventory_items

    def purchase_orders(self):
        return self.payload.purchase_orders

    def production_schedules(self):
        return self.payload.production_schedules

    def financial_transactions(self):
        return self.payload.financial_transactions

    def mes_jobs(self):
        return self.payload.mes_jobs

    def equipment_performance(self):
        return self.payload.equipment_performance

    def material_usage(self):
        return self.payload.material_usage

    def operator_performance(self):
        return self.payload.operator_performance

    def plc_tags(self):
        return self.payload.plc_tags

    def plc_alarms(self):
        return self.payload.plc_alarms

    def plc_control_signals(self):
        return self.payload.plc_control_signals

    def scada_sensors(self):
        return self.payload.scada_sensors

    def scada_alarms(self):
        return self.payload.scada_alarms

    def scada_commands(self):
        return self.payload.scada_commands

    def historical_sensor_records(self):
        return self.payload.historical_sensor_records

    def sop_documents(self):
        return self.payload.sop_documents

    def guidelines(self):
        return self.payload.guidelines


