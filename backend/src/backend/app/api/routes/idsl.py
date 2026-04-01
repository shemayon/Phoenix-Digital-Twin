"""Routes exposing read access to the IDSL namespace."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...idsl.repository import IDSLRepository
from ...models.idsl import (
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
from ..deps import get_ids_repo


router = APIRouter(prefix="/idsl", tags=["idsl"])


@router.get("/", response_model=IDSLPayload)
async def fetch_ids_payload(repo: IDSLRepository = Depends(get_ids_repo)) -> IDSLPayload:
    """Return the full Unified Namespace payload."""

    return repo.payload


@router.get("/assets", response_model=list[Asset])
async def list_assets(repo: IDSLRepository = Depends(get_ids_repo)) -> list[Asset]:
    return repo.assets()


@router.get("/maintenance-records", response_model=list[MaintenanceRecord])
async def list_maintenance_records(repo: IDSLRepository = Depends(get_ids_repo)) -> list[MaintenanceRecord]:
    return repo.maintenance_records()


@router.get("/inventory", response_model=list[InventoryItem])
async def list_inventory(repo: IDSLRepository = Depends(get_ids_repo)) -> list[InventoryItem]:
    return repo.inventory_items()


@router.get("/purchase-orders", response_model=list[PurchaseOrder])
async def list_purchase_orders(repo: IDSLRepository = Depends(get_ids_repo)) -> list[PurchaseOrder]:
    return repo.purchase_orders()


@router.get("/production", response_model=list[ProductionSchedule])
async def list_production(repo: IDSLRepository = Depends(get_ids_repo)) -> list[ProductionSchedule]:
    return repo.production_schedules()


@router.get("/financials", response_model=list[FinancialTransaction])
async def list_financials(repo: IDSLRepository = Depends(get_ids_repo)) -> list[FinancialTransaction]:
    return repo.financial_transactions()


@router.get("/mes-jobs", response_model=list[MesJob])
async def list_mes_jobs(repo: IDSLRepository = Depends(get_ids_repo)) -> list[MesJob]:
    return repo.mes_jobs()


@router.get("/equipment-performance", response_model=list[EquipmentPerformance])
async def list_equipment_performance(repo: IDSLRepository = Depends(get_ids_repo)) -> list[EquipmentPerformance]:
    return repo.equipment_performance()


@router.get("/material-usage", response_model=list[MaterialUsage])
async def list_material_usage(repo: IDSLRepository = Depends(get_ids_repo)) -> list[MaterialUsage]:
    return repo.material_usage()


@router.get("/operator-performance", response_model=list[OperatorPerformance])
async def list_operator_performance(repo: IDSLRepository = Depends(get_ids_repo)) -> list[OperatorPerformance]:
    return repo.operator_performance()


@router.get("/plc/tags", response_model=list[PLCTag])
async def list_plc_tags(repo: IDSLRepository = Depends(get_ids_repo)) -> list[PLCTag]:
    return repo.plc_tags()


@router.get("/plc/alarms", response_model=list[PLCAlarm])
async def list_plc_alarms(repo: IDSLRepository = Depends(get_ids_repo)) -> list[PLCAlarm]:
    return repo.plc_alarms()


@router.get("/plc/control-signals", response_model=list[PLCControlSignal])
async def list_plc_control_signals(repo: IDSLRepository = Depends(get_ids_repo)) -> list[PLCControlSignal]:
    return repo.plc_control_signals()


@router.get("/scada/sensors", response_model=list[SCADASensor])
async def list_scada_sensors(repo: IDSLRepository = Depends(get_ids_repo)) -> list[SCADASensor]:
    return repo.scada_sensors()


@router.get("/scada/alarms", response_model=list[SCADAAlarm])
async def list_scada_alarms(repo: IDSLRepository = Depends(get_ids_repo)) -> list[SCADAAlarm]:
    return repo.scada_alarms()


@router.get("/scada/commands", response_model=list[SCADACommand])
async def list_scada_commands(repo: IDSLRepository = Depends(get_ids_repo)) -> list[SCADACommand]:
    return repo.scada_commands()


@router.get("/historical-records", response_model=list[HistoricalSensorRecord])
async def list_historical_records(repo: IDSLRepository = Depends(get_ids_repo)) -> list[HistoricalSensorRecord]:
    return repo.historical_sensor_records()


@router.get("/sops", response_model=list[SOPDocument])
async def list_sops(repo: IDSLRepository = Depends(get_ids_repo)) -> list[SOPDocument]:
    return repo.sop_documents()


@router.get("/guidelines", response_model=list[Guideline])
async def list_guidelines(repo: IDSLRepository = Depends(get_ids_repo)) -> list[Guideline]:
    return repo.guidelines()


