from backend.app.idsl.repository import IDSLRepository
from backend import constants


def test_ids_repository_loads_excel_payload() -> None:
    repo = IDSLRepository()
    payload = repo.load_from_excel(constants.SAMPLE_DATA_PATH)

    assert len(payload.assets) > 0
    assert len(payload.maintenance_records) > 0
    assert payload.sop_documents
    assert payload.guidelines

