"""Utilities to ingest the Excel workbook into structured IDSL payloads."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Type

import math

import pandas as pd
from pydantic import BaseModel

from ..models.idsl import (
    Asset,
    EquipmentPerformance,
    FinancialTransaction,
    Guideline,
    HistoricalSensorRecord,
    IDSLPayload,
    InventoryItem,
    MaintenanceRecord,
    MaterialUsage,
    MesJob,
    OperatorPerformance,
    PLCAlarm,
    PLCControlSignal,
    PLCTag,
    ProductionSchedule,
    PurchaseOrder,
    SCADAAlarm,
    SCADACommand,
    SCADASensor,
    SOPDocument,
)


@dataclass(slots=True)
class TableSpec:
    """Definition for extracting a structured table from the worksheet."""

    key: str
    header: Sequence[str]
    model: Type[BaseModel]
    label: Optional[str] = None


TABLE_SPECS: Sequence[TableSpec] = (
    TableSpec(
        key="assets",
        header=(
            "Asset_ID",
            "Asset_Name",
            "Location",
            "Status",
            "Last_Maintenance",
            "Next_Maintenance",
            "Performance (%)",
            "Energy_Usage (kWh)",
            "Temperature (°C)",
            "Downtime (hrs)",
        ),
        model=Asset,
    ),
    TableSpec(
        key="maintenance_records",
        header=(
            "Time",
            "Shift",
            "Area",
            "Equipment",
            "Issue",
            "Team",
            "Safety Impact",
            "Production Impact",
            "Fault Type",
            "Action Taken",
            "REQ-ID",
            "GEN-ID",
            "Resourse",
        ),
        model=MaintenanceRecord,
    ),
    TableSpec(
        key="inventory_items",
        header=(
            "Item_ID",
            "Item_Name",
            "Category",
            "Quantity",
            "Unit_Price ($)",
            "Location",
            "Reorder_Level",
            "Supplier_ID",
            "Last_Updated",
        ),
        model=InventoryItem,
    ),
    TableSpec(
        key="purchase_orders",
        header=(
            "Purchase_ID",
            "Item_ID",
            "Quantity",
            "Supplier_ID",
            "Purchase_Date",
            "Delivery_Date",
            "Status",
            "Total_Cost ($)",
        ),
        model=PurchaseOrder,
    ),
    TableSpec(
        key="production_schedules",
        header=(
            "Production_ID",
            "Product_Name",
            "Batch_Size",
            "Start_Date",
            "End_Date",
            "Status",
            "Machine_ID",
            "Operator_ID",
            "Cost ($)",
        ),
        model=ProductionSchedule,
    ),
    TableSpec(
        key="financial_transactions",
        header=(
            "Transaction_ID",
            "Type",
            "Account",
            "Amount ($)",
            "Date",
            "Description",
        ),
        model=FinancialTransaction,
    ),
    TableSpec(
        key="mes_jobs",
        header=(
            "Job_ID",
            "Product_Name",
            "Batch_ID",
            "Start_Time",
            "End_Time",
            "Status",
            "Machine_ID",
            "Operator_ID",
            "Quantity",
            "Scrap (%)",
            "Yield (%)",
        ),
        model=MesJob,
    ),
    TableSpec(
        key="equipment_performance",
        header=(
            "Machine_ID",
            "Machine_Name",
            "Location",
            "Status",
            "Downtime (hrs)",
            "Utilization (%)",
            "Last_Maintenance",
            "Next_Maintenance",
            "Fault_Type",
        ),
        model=EquipmentPerformance,
    ),
    TableSpec(
        key="material_usage",
        header=(
            "Material_ID",
            "Material_Name",
            "Batch_ID",
            "Quantity_Used",
            "Unit",
            "Waste (%)",
            "Cost ($)",
            "Supplier_ID",
            "Last_Updated",
        ),
        model=MaterialUsage,
    ),
    TableSpec(
        key="operator_performance",
        header=(
            "Operator_ID",
            "Operator_Name",
            "Shift",
            "Area",
            "Job_ID",
            "Efficiency (%)",
            "Errors",
            "Downtime (hrs)",
            "Last_Training",
        ),
        model=OperatorPerformance,
    ),
    TableSpec(
        key="plc_tags",
        header=(
            "PLC_ID",
            "Tag_Name",
            "Description",
            "Value",
            "Unit",
            "Timestamp",
            "Status",
        ),
        model=PLCTag,
    ),
    TableSpec(
        key="plc_alarms",
        header=(
            "Alarm_ID",
            "PLC_ID",
            "Tag_Name",
            "Alarm_Type",
            "Alarm_Description",
            "Timestamp",
            "Acknowledged",
            "Resolved",
        ),
        model=PLCAlarm,
        label="Alarm and Event Data",
    ),
    TableSpec(
        key="plc_control_signals",
        header=(
            "Signal_ID",
            "PLC_ID",
            "Tag_Name",
            "Control_Command",
            "Command_Value",
            "Timestamp",
            "Status",
        ),
        model=PLCControlSignal,
    ),
    TableSpec(
        key="scada_sensors",
        header=(
            "Sensor_ID",
            "Tag_Name",
            "Description",
            "Value",
            "Unit",
            "Timestamp",
            "Status",
        ),
        model=SCADASensor,
    ),
    TableSpec(
        key="scada_alarms",
        header=(
            "Alarm_ID",
            "Sensor_ID",
            "Tag_Name",
            "Alarm_Type",
            "Alarm_Description",
            "Timestamp",
            "Acknowledged",
            "Resolved",
        ),
        model=SCADAAlarm,
        label="Alarm Data",
    ),
    TableSpec(
        key="scada_commands",
        header=(
            "Command_ID",
            "Sensor_ID",
            "Tag_Name",
            "Command_Type",
            "Command_Value",
            "Timestamp",
            "Status",
        ),
        model=SCADACommand,
    ),
    TableSpec(
        key="historical_sensor_records",
        header=(
            "Sensor_ID",
            "Tag_Name",
            "Description",
            "Average_Value",
            "Unit",
            "Min_Value",
            "Max_Value",
            "Timestamp_Start",
            "Timestamp_End",
        ),
        model=HistoricalSensorRecord,
    ),
)


class ExcelIDSLLoader:
    """Parse the supplied workbook into the Unified Namespace representation."""

    def __init__(self, workbook_path: Path):
        self.workbook_path = workbook_path
        self.df = pd.read_excel(workbook_path, header=None)

    def load(self) -> IDSLPayload:
        payload_kwargs: dict[str, Any] = {}
        for spec in TABLE_SPECS:
            rows = self._extract_table(spec)
            payload_kwargs[spec.key] = [spec.model.model_validate(r) for r in rows]

        payload_kwargs.setdefault("sop_documents", self._extract_sops())
        payload_kwargs.setdefault("guidelines", self._extract_guidelines())

        return IDSLPayload(**payload_kwargs)

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------
    def _extract_table(self, spec: TableSpec) -> list[dict[str, Any]]:
        header_idx = self._find_header_index(spec)
        if header_idx is None:
            return []

        header_row = self.df.iloc[header_idx]
        columns = [c for c in header_row.tolist() if isinstance(c, str) and c.strip()]
        entries: list[dict[str, Any]] = []

        for row_idx in range(header_idx + 1, len(self.df)):
            row = self.df.iloc[row_idx]
            if self._is_termination_row(row, len(columns)):
                break

            record = self._row_to_record(row, columns)
            if record is None:
                break

            entries.append(record)

        return entries

    def _find_header_index(self, spec: TableSpec) -> Optional[int]:
        target_header = [self._normalize(cell) for cell in spec.header]

        for idx in range(len(self.df)):
            row = self.df.iloc[idx]
            row_header = [self._normalize(row.iloc[col_idx]) for col_idx in range(len(spec.header))]
            if row_header == target_header:
                if spec.label is None or self._preceding_label_matches(idx, spec.label):
                    return idx
        return None

    def _preceding_label_matches(self, header_idx: int, label: str) -> bool:
        label_normalized = self._normalize(label)
        for offset in range(1, 4):
            idx = header_idx - offset
            if idx < 0:
                break
            first_cell = self._normalize(self.df.iloc[idx, 0])
            if first_cell:
                return first_cell == label_normalized
        return False

    def _is_termination_row(self, row: pd.Series, width: int) -> bool:
        values = [row.iloc[i] for i in range(width)]
        if all(self._is_nan(v) for v in values):
            return True
        return False

    def _row_to_record(self, row: pd.Series, columns: Sequence[str]) -> Optional[dict[str, Any]]:
        record: dict[str, Any] = {}
        has_data = False
        for idx, column in enumerate(columns):
            value = row.iloc[idx] if idx < len(row) else None
            cleaned = None if self._is_nan(value) else value
            if cleaned is not None:
                has_data = True
            record[column] = cleaned

        return record if has_data else None

    def _extract_sops(self) -> list[SOPDocument]:
        results: list[SOPDocument] = []
        title = "SOP Sample"
        for idx in range(len(self.df)):
            if self._row_contains(idx, title):
                content_row = self._find_next_nonempty_row(idx)
                if content_row is not None:
                    content = str(self._first_nonempty_cell(content_row))
                    results.append(SOPDocument(title=title, content=content.strip()))
                break
        return results

    def _extract_guidelines(self) -> list[Guideline]:
        results: list[Guideline] = []
        title = "Guidelines"
        for idx in range(len(self.df)):
            if self._row_contains(idx, title):
                content_row = self._find_next_nonempty_row(idx)
                if content_row is not None:
                    content = str(self._first_nonempty_cell(content_row))
                    results.append(Guideline(title=title, content=content.strip()))
                break
        return results

    def _find_next_nonempty_row(self, start_idx: int) -> Optional[int]:
        for idx in range(start_idx + 1, len(self.df)):
            if self._row_contains(idx):
                return idx
        return None

    def _row_contains(self, idx: int, target: str | None = None) -> bool:
        row = self.df.iloc[idx]
        for value in row.tolist():
            if target is None:
                if not self._is_nan(value):
                    return True
            else:
                if self._normalize(value) == self._normalize(target):
                    return True
        return False

    def _first_nonempty_cell(self, idx: int) -> Any:
        row = self.df.iloc[idx]
        for value in row.tolist():
            if not self._is_nan(value):
                return value
        return ""

    def _normalize(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        if self._is_nan(value):
            return ""
        return str(value).strip().lower()

    @staticmethod
    def _is_nan(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and math.isnan(value):
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False


