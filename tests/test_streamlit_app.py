"""Smoke tests for the Streamlit Underwriting Desk (demo/streamlit_app/app.py).

Uses streamlit.testing.v1.AppTest — no browser needed. Mirrors the same
preset-decision assertions as tests/test_desk_app.py (the FastAPI version)
since both apps share the exact same PRESETS/scoring logic.
"""
from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parent.parent / "demo" / "streamlit_app" / "app.py"


def _all_markdown(at: AppTest) -> str:
    return "\n".join(m.value for m in at.markdown)


def test_app_boots_without_exception():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    assert not at.exception


def test_low_risk_preset_gives_standard():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    at.button(key="btn_preset_low").click().run()
    md = _all_markdown(at)
    assert 'b-STANDARD">STANDARD' in md
    assert "AGREES" in md and "DISAGREES" not in md


def test_borderline_preset_disagrees_with_xgb():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    at.button(key="btn_preset_borderline").click().run()
    md = _all_markdown(at)
    assert 'b-RATED">RATED' in md
    assert "DISAGREES" in md
    assert "leaves $" in md


def test_high_risk_preset_gives_decline():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    at.button(key="btn_preset_high").click().run()
    md = _all_markdown(at)
    assert 'b-DECLINE">DECLINE' in md


def test_refer_preset_shows_hitl_card():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    at.button(key="btn_preset_refer").click().run()
    md = _all_markdown(at)
    assert 'b-REFER">REFER' in md
    assert "REFERRED TO HUMAN UNDERWRITER" in md
    assert "+14.8%" in md
    assert "AlwaysRATED" in md


def test_fairness_panel_shows_canonical_zones():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    md = _all_markdown(at)
    assert "z-GREEN" in md
    assert "z-AMBER" in md
    assert "canonical: GREEN" in md
    assert "canonical: AMBER" in md


def test_learn_tab_headline_metrics():
    at = AppTest.from_file(str(APP_PATH), default_timeout=60)
    at.run()
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Lift vs Static XGB"] == "+25.2%"
    assert metrics["Seeds"] == "20"


def test_clear_form_resets_defaults():
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    at.button(key="btn_preset_high").click().run()
    at.button(key="btn_clear").click().run()
    assert at.number_input(key="f_age").value == 35
    assert at.multiselect(key="f_conditions").value == []
