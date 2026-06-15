"""Backend tests for the clean Underwriting Desk demo (spec §11)."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from demo.desk.app import app

client = TestClient(app)

ROOT = Path(__file__).resolve().parent.parent
THESIS_RESULTS = ROOT / "demo" / "static" / "thesis_results.json"


def test_health_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_applicant_fields_nonempty():
    r = client.get("/api/applicant/fields")
    assert r.status_code == 200
    data = r.json()
    for key in ("regions", "occupations", "educations", "wealth_quintiles",
                "health_statuses", "conditions"):
        assert isinstance(data[key], list) and len(data[key]) > 0


def test_random_applicant_valid():
    r = client.get("/api/applicant/random")
    assert r.status_code == 200
    data = r.json()
    app_ = data["applicant"]
    assert 18 <= app_["age"] <= 85
    assert app_["gender"] in ("Male", "Female")
    assert isinstance(app_["region"], str) and app_["region"]
    assert "mortality_multiplier" in app_


def test_canonical_reads_from_file():
    r = client.get("/api/canonical")
    assert r.status_code == 200
    data = r.json()
    on_disk = json.loads(THESIS_RESULTS.read_text(encoding="utf-8"))
    # Value must come from the file, not a hardcoded literal.
    assert data["lift_pct"] == on_disk["exp005"]["lift_pct"]
    assert data["cohen_d"] == on_disk["exp005"]["reward_cohen_d"]
    assert data["p_value"] == on_disk["exp005"]["reward_p"]
    assert data["n_seeds"] == 20
    # Admissible-scope ceiling carried alongside the headline (_meta.scope).
    assert data["ceiling_policy"] == "AlwaysRATED"
