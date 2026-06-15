"""Backend tests for the clean Underwriting Desk demo (spec §11)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from demo.desk.app import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
