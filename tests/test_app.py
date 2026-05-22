from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_live_health_check() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "x-request-id" in response.headers

