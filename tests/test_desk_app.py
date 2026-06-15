"""Backend tests for the clean Underwriting Desk demo (spec §11)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from demo.desk.app import app
from demo.desk.learning import EXPLORATION_PRESETS, run_learn
from healthrl.underwriting_bandit import ACTION_NAMES

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


# A fixed manual applicant (mortality_multiplier defaults to neutral 1.0).
SAMPLE_APPLICANT = {
    "age": 45, "gender": "Female", "bmi": 24.5,
    "is_smoking": 0, "alcohol_use": 0, "is_exercise": 1,
    "has_family_history": 0, "monthly_income_usd": 350.0,
    "pre_existing_conditions": "", "region": "Phnom Penh",
    "occupation": "Civil Servant", "education": "Secondary",
    "wealth_quintile": "Middle", "self_reported_health": "Good",
}


def test_score_card_well_formed():
    r = client.post("/api/score", json=SAMPLE_APPLICANT)
    assert r.status_code == 200, r.text
    data = r.json()
    # Decision is a valid action.
    assert data["decision"] in ACTION_NAMES
    assert data["decision_index"] == ACTION_NAMES.index(data["decision"])
    # Four numeric estimated rewards, one per action.
    er = data["estimated_rewards"]
    assert set(er.keys()) == set(ACTION_NAMES)
    assert all(isinstance(v, (int, float)) for v in er.values())
    # Confidence is a probability-like scalar, non-degenerate range enforced elsewhere.
    assert 0.0 <= data["confidence"] <= 1.0
    # Exactly three drivers, each signed.
    assert len(data["drivers"]) == 3
    for d in data["drivers"]:
        assert d["direction"] in ("up", "down")
        assert isinstance(d["label"], str) and d["label"]
    # Premium consistent with the decision.
    prem = data["premium"]
    if data["decision"] == "DECLINE":
        assert prem["amount"] is None and prem["status"] == "declined"
    elif data["decision"] == "REFER":
        assert prem["amount"] is None and prem["status"] == "refer"
    else:
        assert isinstance(prem["amount"], (int, float)) and prem["amount"] > 0


def test_score_decision_matches_theta_argmax():
    r = client.post("/api/score", json=SAMPLE_APPLICANT).json()
    er = r["estimated_rewards"]
    best = max(er, key=er.get)
    assert r["decision"] == best


def test_score_validation_rejects_bad_age():
    bad = dict(SAMPLE_APPLICANT, age=5)
    r = client.post("/api/score", json=bad)
    assert r.status_code == 422


def test_score_includes_model_fairness():
    data = client.post("/api/score", json=SAMPLE_APPLICANT).json()
    fair = data["fairness"]
    assert fair["badge_status"] in ("GREEN", "AMBER", "RED")
    for key in ("region", "occupation"):
        assert fair[key]["status"] in ("GREEN", "AMBER", "RED")
        assert isinstance(fair[key]["psi"], (int, float))
    # Canonical EXP-006 footnote (read from thesis_results.json, not invented).
    assert fair["canonical"]["region_zone"] == "GREEN"
    assert fair["canonical"]["occupation_zone"] == "AMBER"


def test_model_fairness_is_constant_across_applicants():
    """Model-level (not per-applicant): identical for any applicant."""
    a = client.post("/api/score", json=SAMPLE_APPLICANT).json()["fairness"]
    other = dict(SAMPLE_APPLICANT, region="Siem Reap", occupation="Rice Farmer", age=70)
    b = client.post("/api/score", json=other).json()["fairness"]
    assert a["region"]["psi"] == b["region"]["psi"]
    assert a["occupation"]["psi"] == b["occupation"]["psi"]


def test_learn_run_trajectories():
    payload = {"algorithm": "LinUCB", "seed": 42, "n_rounds": 300}
    r = client.post("/api/learn/run", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["algorithm"] == "LinUCB"
    assert data["n_rounds"] == 300
    assert len(data["adaptive"]["cumulative"]) == 300
    assert len(data["static"]["cumulative"]) == 300
    assert len(data["rounds"]) == 300
    # Early/late action mixes are distributions over the 4 actions.
    for mix in (data["adaptive"]["early_mix"], data["adaptive"]["late_mix"]):
        # Components are rounded to 4 dp for the payload, so sum ≈ 1 (not exact).
        assert abs(sum(mix.values()) - 1.0) < 1e-3
        assert set(mix.keys()) == set(ACTION_NAMES)
    # Illustrative lift readout present and labelled.
    assert "lift_pct" in data and isinstance(data["lift_pct"], (int, float))
    # Default carries the Balanced preset + resolved param (spec §9).
    assert data["exploration"] == "Balanced"
    assert data["param"] == {"name": "alpha", "value": 1.0}


def test_learn_run_rejects_bad_algorithm():
    r = client.post("/api/learn/run", json={"algorithm": "Nope", "n_rounds": 300})
    assert r.status_code == 422


# ---- Exploration speed-control: backend (spec 2026-06-15-learn-speed-control §4/§6/§9) ----

def test_exploration_presets_table():
    # Anchor constants must match spec §4 exactly.
    assert EXPLORATION_PRESETS["Greedy"] == {"alpha": 0.0, "v2": 0.25}
    assert EXPLORATION_PRESETS["Balanced"] == {"alpha": 1.0, "v2": 1.0}
    assert EXPLORATION_PRESETS["Exploratory"] == {"alpha": 3.0, "v2": 4.0}


def test_run_learn_greedy_linucb_echoes_alpha():
    out = run_learn("LinUCB", seed=42, n_rounds=300, exploration="Greedy")
    assert out["exploration"] == "Greedy"
    assert out["param"] == {"name": "alpha", "value": 0.0}


def test_run_learn_exploratory_lints_echoes_v2():
    out = run_learn("LinTS", seed=42, n_rounds=300, exploration="Exploratory")
    assert out["exploration"] == "Exploratory"
    assert out["param"] == {"name": "v2", "value": 4.0}


def test_run_learn_presets_change_trajectory():
    # The knob is actually wired through: Greedy and Exploratory diverge.
    greedy = run_learn("LinUCB", seed=42, n_rounds=300, exploration="Greedy")
    explor = run_learn("LinUCB", seed=42, n_rounds=300, exploration="Exploratory")
    assert greedy["adaptive"]["cumulative"] != explor["adaptive"]["cumulative"]


def test_run_learn_rejects_unknown_preset():
    with pytest.raises(ValueError):
        run_learn("LinUCB", n_rounds=300, exploration="Wild")


# ---- Exploration speed-control: HTTP boundary (spec §6/§9) ----

def test_learn_run_http_greedy_param():
    r = client.post(
        "/api/learn/run",
        json={"algorithm": "LinUCB", "n_rounds": 300, "exploration": "Greedy"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["exploration"] == "Greedy"
    assert data["param"] == {"name": "alpha", "value": 0.0}


def test_learn_run_rejects_bad_exploration():
    r = client.post(
        "/api/learn/run",
        json={"algorithm": "LinUCB", "n_rounds": 300, "exploration": "Wild"},
    )
    assert r.status_code == 422
