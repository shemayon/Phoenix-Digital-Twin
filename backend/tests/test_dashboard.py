from backend.app.main import app
from fastapi.testclient import TestClient


def test_dashboard_route_renders_html() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Digital Twin Command Center" in response.text

