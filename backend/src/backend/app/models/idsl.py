"""Pydantic schemas representing the IDSL datasets loaded from the sample workbook."""

from __future__ import annotations

from datetime import datetime, time as time_type
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Asset(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    asset_id: str = Field(alias="Asset_ID")
    name: str = Field(alias="Asset_Name")
    location: Optional[str] = Field(default=None, alias="Location")
    status: Optional[str] = Field(default=None, alias="Status")
    last_maintenance: Optional[datetime] = Field(alias="Last_Maintenance", default=None)
    next_maintenance: Optional[datetime] = Field(alias="Next_Maintenance", default=None)
    performance_pct: Optional[float] = Field(alias="Performance (%)", default=None)
    energy_usage_kwh: Optional[float] = Field(alias="Energy_Usage (kWh)", default=None)
    temperature_c: Optional[float] = Field(alias="Temperature (°C)", default=None)
    downtime_hours: Optional[float] = Field(alias="Downtime (hrs)", default=None)


class MaintenanceRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    time: Optional[time_type] = Field(alias="Time", default=None)
    shift: Optional[str] = Field(alias="Shift", default=None)
    area: Optional[str] = Field(alias="Area", default=None)
    equipment: Optional[str] = Field(alias="Equipment", default=None)
    issue: Optional[str] = Field(alias="Issue", default=None)
    team: Optional[str] = Field(alias="Team", default=None)
    safety_impact: Optional[str] = Field(alias="Safety Impact", default=None)
    production_impact: Optional[str] = Field(alias="Production Impact", default=None)
    fault_type: Optional[str] = Field(alias="Fault Type", default=None)
    action_taken: Optional[str] = Field(alias="Action Taken", default=None)
    req_id: Optional[str] = Field(alias="REQ-ID", default=None)
    gen_id: Optional[str] = Field(alias="GEN-ID", default=None)
    resource_code: Optional[str] = Field(alias="Resourse", default=None)


class InventoryItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    item_id: str = Field(alias="Item_ID")
    name: Optional[str] = Field(alias="Item_Name", default=None)
    category: Optional[str] = Field(alias="Category", default=None)
    quantity: Optional[float] = Field(alias="Quantity", default=None)
    unit_price_usd: Optional[float] = Field(alias="Unit_Price ($)", default=None)
    location: Optional[str] = Field(alias="Location", default=None)
    reorder_level: Optional[float] = Field(alias="Reorder_Level", default=None)
    supplier_id: Optional[str] = Field(alias="Supplier_ID", default=None)
    last_updated: Optional[datetime] = Field(alias="Last_Updated", default=None)


class PurchaseOrder(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    purchase_id: str = Field(alias="Purchase_ID")
    item_id: Optional[str] = Field(alias="Item_ID", default=None)
    quantity: Optional[float] = Field(alias="Quantity", default=None)
    supplier_id: Optional[str] = Field(alias="Supplier_ID", default=None)
    purchase_date: Optional[datetime] = Field(alias="Purchase_Date", default=None)
    delivery_date: Optional[datetime] = Field(alias="Delivery_Date", default=None)
    status: Optional[str] = Field(alias="Status", default=None)
    total_cost_usd: Optional[float] = Field(alias="Total_Cost ($)", default=None)


class ProductionSchedule(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    production_id: str = Field(alias="Production_ID")
    product_name: Optional[str] = Field(alias="Product_Name", default=None)
    batch_size: Optional[float] = Field(alias="Batch_Size", default=None)
    start_date: Optional[datetime] = Field(alias="Start_Date", default=None)
    end_date: Optional[datetime] = Field(alias="End_Date", default=None)
    status: Optional[str] = Field(alias="Status", default=None)
    machine_id: Optional[str] = Field(alias="Machine_ID", default=None)
    operator_id: Optional[str] = Field(alias="Operator_ID", default=None)
    cost_usd: Optional[float] = Field(alias="Cost ($)", default=None)


class FinancialTransaction(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    transaction_id: str = Field(alias="Transaction_ID")
    type: Optional[str] = Field(alias="Type", default=None)
    account: Optional[str] = Field(alias="Account", default=None)
    amount_usd: Optional[float] = Field(alias="Amount ($)", default=None)
    date: Optional[datetime] = Field(alias="Date", default=None)
    description: Optional[str] = Field(alias="Description", default=None)


class MesJob(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    job_id: str = Field(alias="Job_ID")
    product_name: Optional[str] = Field(alias="Product_Name", default=None)
    batch_id: Optional[str] = Field(alias="Batch_ID", default=None)
    start_time: Optional[datetime] = Field(alias="Start_Time", default=None)
    end_time: Optional[datetime] = Field(alias="End_Time", default=None)
    status: Optional[str] = Field(alias="Status", default=None)
    machine_id: Optional[str] = Field(alias="Machine_ID", default=None)
    operator_id: Optional[str] = Field(alias="Operator_ID", default=None)
    quantity: Optional[float] = Field(alias="Quantity", default=None)
    scrap_pct: Optional[float] = Field(alias="Scrap (%)", default=None)
    yield_pct: Optional[float] = Field(alias="Yield (%)", default=None)


class EquipmentPerformance(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    machine_id: str = Field(alias="Machine_ID")
    machine_name: Optional[str] = Field(alias="Machine_Name", default=None)
    location: Optional[str] = Field(alias="Location", default=None)
    status: Optional[str] = Field(alias="Status", default=None)
    downtime_hours: Optional[float] = Field(alias="Downtime (hrs)", default=None)
    utilization_pct: Optional[float] = Field(alias="Utilization (%)", default=None)
    last_maintenance: Optional[datetime] = Field(alias="Last_Maintenance", default=None)
    next_maintenance: Optional[datetime] = Field(alias="Next_Maintenance", default=None)
    fault_type: Optional[str] = Field(alias="Fault_Type", default=None)


class MaterialUsage(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    material_id: str = Field(alias="Material_ID")
    material_name: Optional[str] = Field(alias="Material_Name", default=None)
    batch_id: Optional[str] = Field(alias="Batch_ID", default=None)
    quantity_used: Optional[float] = Field(alias="Quantity_Used", default=None)
    unit: Optional[str] = Field(alias="Unit", default=None)
    waste_pct: Optional[float] = Field(alias="Waste (%)", default=None)
    cost_usd: Optional[float] = Field(alias="Cost ($)", default=None)
    supplier_id: Optional[str] = Field(alias="Supplier_ID", default=None)
    last_updated: Optional[datetime] = Field(alias="Last_Updated", default=None)


class OperatorPerformance(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    operator_id: str = Field(alias="Operator_ID")
    operator_name: Optional[str] = Field(alias="Operator_Name", default=None)
    shift: Optional[str] = Field(alias="Shift", default=None)
    area: Optional[str] = Field(alias="Area", default=None)
    job_id: Optional[str] = Field(alias="Job_ID", default=None)
    efficiency_pct: Optional[float] = Field(alias="Efficiency (%)", default=None)
    errors: Optional[float] = Field(alias="Errors", default=None)
    downtime_hours: Optional[float] = Field(alias="Downtime (hrs)", default=None)
    last_training: Optional[datetime] = Field(alias="Last_Training", default=None)


class PLCTag(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    plc_id: str = Field(alias="PLC_ID")
    tag_name: Optional[str] = Field(alias="Tag_Name", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    value: Optional[float] = Field(alias="Value", default=None)
    unit: Optional[str] = Field(alias="Unit", default=None)
    timestamp: Optional[datetime] = Field(alias="Timestamp", default=None)
    status: Optional[str] = Field(alias="Status", default=None)


class PLCAlarm(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    alarm_id: str = Field(alias="Alarm_ID")
    plc_id: Optional[str] = Field(alias="PLC_ID", default=None)
    tag_name: Optional[str] = Field(alias="Tag_Name", default=None)
    alarm_type: Optional[str] = Field(alias="Alarm_Type", default=None)
    description: Optional[str] = Field(alias="Alarm_Description", default=None)
    timestamp: Optional[datetime] = Field(alias="Timestamp", default=None)
    acknowledged: Optional[str] = Field(alias="Acknowledged", default=None)
    resolved: Optional[str] = Field(alias="Resolved", default=None)


class PLCControlSignal(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    signal_id: str = Field(alias="Signal_ID")
    plc_id: Optional[str] = Field(alias="PLC_ID", default=None)
    tag_name: Optional[str] = Field(alias="Tag_Name", default=None)
    control_command: Optional[str] = Field(alias="Control_Command", default=None)
    command_value: Optional[str | float] = Field(alias="Command_Value", default=None)
    timestamp: Optional[datetime] = Field(alias="Timestamp", default=None)
    status: Optional[str] = Field(alias="Status", default=None)


class SCADASensor(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    sensor_id: str = Field(alias="Sensor_ID")
    tag_name: Optional[str] = Field(alias="Tag_Name", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    value: Optional[float] = Field(alias="Value", default=None)
    unit: Optional[str] = Field(alias="Unit", default=None)
    timestamp: Optional[datetime] = Field(alias="Timestamp", default=None)
    status: Optional[str] = Field(alias="Status", default=None)


class SCADAAlarm(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    alarm_id: str = Field(alias="Alarm_ID")
    sensor_id: Optional[str] = Field(alias="Sensor_ID", default=None)
    tag_name: Optional[str] = Field(alias="Tag_Name", default=None)
    alarm_type: Optional[str] = Field(alias="Alarm_Type", default=None)
    description: Optional[str] = Field(alias="Alarm_Description", default=None)
    timestamp: Optional[datetime] = Field(alias="Timestamp", default=None)
    acknowledged: Optional[str] = Field(alias="Acknowledged", default=None)
    resolved: Optional[str] = Field(alias="Resolved", default=None)


class SCADACommand(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    command_id: str = Field(alias="Command_ID")
    sensor_id: Optional[str] = Field(alias="Sensor_ID", default=None)
    tag_name: Optional[str] = Field(alias="Tag_Name", default=None)
    command_type: Optional[str] = Field(alias="Command_Type", default=None)
    command_value: Optional[str | float] = Field(alias="Command_Value", default=None)
    timestamp: Optional[datetime] = Field(alias="Timestamp", default=None)
    status: Optional[str] = Field(alias="Status", default=None)


class HistoricalSensorRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    sensor_id: str = Field(alias="Sensor_ID")
    tag_name: Optional[str] = Field(alias="Tag_Name", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    average_value: Optional[float] = Field(alias="Average_Value", default=None)
    unit: Optional[str] = Field(alias="Unit", default=None)
    min_value: Optional[float] = Field(alias="Min_Value", default=None)
    max_value: Optional[float] = Field(alias="Max_Value", default=None)
    timestamp_start: Optional[datetime] = Field(alias="Timestamp_Start", default=None)
    timestamp_end: Optional[datetime] = Field(alias="Timestamp_End", default=None)


class SOPDocument(BaseModel):
    title: str
    content: str


class Guideline(BaseModel):
    title: str
    content: str


class IDSLPayload(BaseModel):
    assets: list[Asset]
    maintenance_records: list[MaintenanceRecord]
    inventory_items: list[InventoryItem]
    purchase_orders: list[PurchaseOrder]
    production_schedules: list[ProductionSchedule]
    financial_transactions: list[FinancialTransaction]
    mes_jobs: list[MesJob]
    equipment_performance: list[EquipmentPerformance]
    material_usage: list[MaterialUsage]
    operator_performance: list[OperatorPerformance]
    plc_tags: list[PLCTag]
    plc_alarms: list[PLCAlarm]
    plc_control_signals: list[PLCControlSignal]
    scada_sensors: list[SCADASensor]
    scada_alarms: list[SCADAAlarm]
    scada_commands: list[SCADACommand]
    historical_sensor_records: list[HistoricalSensorRecord]
    sop_documents: list[SOPDocument]
    guidelines: list[Guideline]


