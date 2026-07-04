"""Streamlit port of the Underwriting Desk (pragmatic scope, 2026-07-04).

Reuses demo/desk/{scoring.py, learning.py} and healthrl/ as-is — no new
modelling math, no duplicated scoring/learning logic. The only thing this
file rewrites is the presentation layer (FastAPI+vanilla-JS -> Streamlit).

Deliberate simplification vs the FastAPI version: "Watch it Learn"'s
Play/Reset/Speed animation is replaced by a round-scrub slider, since
Streamlit has no client-side animation-loop primitive. Everything else
(presets, HITL card, LinUCB-vs-XGB comparison, confidence bar, fairness
panel, alpha slider) is at full parity.

Run: streamlit run demo/streamlit_app/app.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from demo.desk.scoring import SCORER  # noqa: E402
from demo.desk import learning  # noqa: E402

N_ROUNDS = 3000  # matches demo/desk/static/learn.js: reaches ~canonical +25.2% at seed 42
THESIS_RESULTS_PATH = ROOT / "demo" / "static" / "thesis_results.json"

EDUCATIONS = ["No education", "Primary", "Secondary", "Higher"]
WEALTH_QUINTILES = ["Poorest", "Poorer", "Middle", "Richer", "Richest"]
HEALTH_STATUSES = ["Poor", "Fair", "Good"]
CONDITIONS = [
    "Hypertension", "Diabetes", "Heart Disease", "COPD/Asthma",
    "Arthritis", "TB", "Hepatitis B",
]
REGIONS = sorted(SCORER.df_raw["region"].dropna().unique().tolist())
OCCUPATIONS = sorted(SCORER.df_raw["occupation"].dropna().unique().tolist())

# Calibrated preset profiles (see demo/desk/static/desk.js — same values, same
# calibration rationale: verified against the frozen theta + StaticXGBBaseline
# directly, not assumed. See project memory demo_rebuild_status.md 2026-07-04).
PRESETS: dict[str, dict[str, Any]] = {
    "high_risk": dict(
        age=65, gender="Male", bmi=34.0, region="Prey Veng",
        occupation="Rice Farmer", is_smoking=1, alcohol_use=1, is_exercise=0,
        has_family_history=1, conditions=["Hypertension", "Diabetes", "Heart Disease"],
        monthly_income_usd=120.0, education="No education", wealth_quintile="Poorest",
        self_reported_health="Poor", mortality_multiplier=3.5,
    ),
    "low_risk": dict(
        age=24, gender="Female", bmi=21.0, region="Prey Veng",
        occupation="Market Vendor", is_smoking=0, alcohol_use=0, is_exercise=1,
        has_family_history=0, conditions=[],
        monthly_income_usd=250.0, education="Secondary", wealth_quintile="Richest",
        self_reported_health="Good", mortality_multiplier=1.0,
    ),
    "borderline": dict(
        age=38, gender="Male", bmi=32.0, region="Prey Veng",
        occupation="Civil Servant", is_smoking=0, alcohol_use=0, is_exercise=1,
        has_family_history=0, conditions=[],
        monthly_income_usd=150.0, education="Primary", wealth_quintile="Richer",
        self_reported_health="Good", mortality_multiplier=1.36,
    ),
    "refer_case": dict(
        age=45, gender="Male", bmi=27.3, region="Phnom Penh",
        occupation="Construction Worker", is_smoking=0, alcohol_use=1, is_exercise=0,
        has_family_history=0, conditions=["Hypertension", "COPD/Asthma"],
        monthly_income_usd=309.0, education="Primary", wealth_quintile="Middle",
        self_reported_health="Fair", mortality_multiplier=2.69,
    ),
}

FORM_DEFAULTS = dict(
    f_age=35, f_gender="Male", f_region=REGIONS[0], f_occupation=OCCUPATIONS[0],
    f_bmi=23.0, f_health="Fair", f_smoking=False, f_alcohol=False,
    f_exercise=False, f_family=False, f_conditions=[], f_income=250.0,
    f_education="Primary", f_wealth="Middle", f_mortality=1.0,
)

CSS = """
:root{
  --bg:#0f1419; --panel:#1a2230; --panel2:#222c3c; --ink:#e8edf4;
  --muted:#93a1b5; --line:#2c3a4e; --accent:#3b82f6;
  --green:#22c55e; --amber:#f59e0b; --red:#ef4444;
}
.badge{display:inline-block;padding:.25rem .6rem;border-radius:6px;font-weight:700;font-size:.8rem;}
.decision-badge{font-size:1.5rem;padding:.5rem 1rem;}
.b-STANDARD{background:rgba(34,197,94,.15);color:var(--green);}
.b-RATED{background:rgba(245,158,11,.15);color:var(--amber);}
.b-DECLINE{background:rgba(239,68,68,.15);color:var(--red);}
.b-REFER{background:rgba(59,130,246,.15);color:var(--accent);}
.z-GREEN{background:rgba(34,197,94,.15);color:var(--green);}
.z-AMBER{background:rgba(245,158,11,.15);color:var(--amber);}
.z-RED{background:rgba(239,68,68,.15);color:var(--red);}
.group-title{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#22d3ee;margin:.9rem 0 .3rem;}
.muted{color:var(--muted);}
"""


def load_canonical_headline() -> dict[str, Any]:
    """Authoritative 20-seed headline, read from thesis_results.json (no fallback).

    Duplicated from demo/desk/app.py's helper rather than imported, so this
    Streamlit app has no import-time dependency on the FastAPI module.
    """
    data = json.loads(THESIS_RESULTS_PATH.read_text(encoding="utf-8"))
    exp005 = data["exp005"]
    ceiling = next(r for r in data["ladder"]["rows"] if r["policy"] == "AlwaysRATED")
    return {
        "lift_pct": exp005["lift_pct"],
        "cohen_d": exp005["reward_cohen_d"],
        "p_value": exp005["reward_p"],
        "n_seeds": 20,
        "comparator": "Static XGB",
        "scope": data["_meta"]["scope"],
        "ceiling_policy": ceiling["policy"],
        "ceiling_note": ceiling["note"],
    }


# ---- session-state helpers -------------------------------------------------

def _seed_defaults() -> None:
    for k, v in FORM_DEFAULTS.items():
        st.session_state.setdefault(k, v)


def _apply_preset(name: str) -> None:
    p = PRESETS[name]
    st.session_state.f_age = p["age"]
    st.session_state.f_gender = p["gender"]
    st.session_state.f_bmi = p["bmi"]
    st.session_state.f_region = p["region"]
    st.session_state.f_occupation = p["occupation"]
    st.session_state.f_smoking = bool(p["is_smoking"])
    st.session_state.f_alcohol = bool(p["alcohol_use"])
    st.session_state.f_exercise = bool(p["is_exercise"])
    st.session_state.f_family = bool(p["has_family_history"])
    st.session_state.f_conditions = list(p["conditions"])
    st.session_state.f_income = p["monthly_income_usd"]
    st.session_state.f_education = p["education"]
    st.session_state.f_wealth = p["wealth_quintile"]
    st.session_state.f_health = p["self_reported_health"]
    st.session_state.f_mortality = p["mortality_multiplier"]


def _load_cdhs_sample() -> None:
    row = SCORER.df_raw.sample(1).iloc[0]
    conds = str(row.get("pre_existing_conditions", "") or "")
    if conds.lower() == "nan":
        conds = ""
    st.session_state.f_age = int(row["age"])
    st.session_state.f_gender = str(row["gender"])
    st.session_state.f_bmi = float(row["bmi"])
    st.session_state.f_region = str(row["region"])
    st.session_state.f_occupation = str(row["occupation"])
    st.session_state.f_smoking = bool(row["is_smoking"])
    st.session_state.f_alcohol = bool(row["alcohol_use"])
    st.session_state.f_exercise = bool(row["is_exercise"])
    st.session_state.f_family = bool(row["has_family_history"])
    st.session_state.f_conditions = [c for c in CONDITIONS if c in conds]
    st.session_state.f_income = float(row["monthly_income_usd"])
    st.session_state.f_education = str(row.get("education", "Primary"))
    st.session_state.f_wealth = str(row.get("wealth_quintile", "Middle"))
    st.session_state.f_health = str(row.get("self_reported_health", "Fair"))
    st.session_state.f_mortality = float(row["mortality_multiplier"])


def _clear_form() -> None:
    for k, v in FORM_DEFAULTS.items():
        st.session_state[k] = v


def _current_applicant() -> dict[str, Any]:
    return dict(
        age=int(st.session_state.f_age),
        gender=st.session_state.f_gender,
        bmi=float(st.session_state.f_bmi),
        is_smoking=int(st.session_state.f_smoking),
        alcohol_use=int(st.session_state.f_alcohol),
        is_exercise=int(st.session_state.f_exercise),
        has_family_history=int(st.session_state.f_family),
        monthly_income_usd=float(st.session_state.f_income),
        pre_existing_conditions=", ".join(st.session_state.f_conditions),
        region=st.session_state.f_region,
        occupation=st.session_state.f_occupation,
        education=st.session_state.f_education,
        wealth_quintile=st.session_state.f_wealth,
        self_reported_health=st.session_state.f_health,
        mortality_multiplier=float(st.session_state.f_mortality),
    )


# ---- fairness panel ---------------------------------------------------------

def render_fairness_panel() -> None:
    fair = SCORER.fairness
    c1, c2 = st.columns(2)
    for col, key, label in ((c1, "region", "Region"), (c2, "occupation", "Occupation")):
        d = fair[key]
        zone = fair["canonical"][f"{key}_zone"]
        col.markdown(
            f'<span class="muted">{label}: '
            f'<span class="badge z-{d["status"]}">{d["status"]}</span> '
            f'{d["psi"]:.3f} <span style="font-size:.7rem">(canonical: {zone})</span></span>',
            unsafe_allow_html=True,
        )
    st.caption(
        f"{fair['note']} PSI zones: GREEN < 0.10 · AMBER 0.10–0.25 · RED > 0.25 "
        "· canonical: EXP-006, 20 seeds."
    )


# ---- Desk tab ----------------------------------------------------------------

def confidence_badge(pct: float) -> tuple[str, str]:
    # Thresholds calibrated against the real preset confidences (2026-07-04):
    # borderline 50.6%, low/high risk 92.7%/98.7% — see demo/desk/static/desk.js.
    if pct < 55:
        return "⚠️ Margin thin — human review territory", "var(--red)"
    if pct < 85:
        return "👁 Bandit decides, monitored", "var(--accent)"
    return "✅ High margin, automated", "var(--green)"


def render_confidence(conf: float) -> None:
    pct = round(conf * 100)
    label, color = confidence_badge(pct)
    tip = (
        "How decisively this decision beats the runner-up action under the learned "
        "value model (softmax margin, τ=6). Illustrative — not a calibrated "
        "probability. Low margin = actions nearly tied = the natural case for human review."
    )
    st.markdown(
        f"""<div style="margin-top:.5rem" title="{tip}">
          <div style="display:flex;justify-content:space-between;" class="muted">
            <span>Decision confidence (illustrative)</span><span>{pct}%</span>
          </div>
          <div style="background:var(--panel2);border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:{pct}%;height:100%;background:{color};"></div>
          </div>
          <div class="muted" style="color:{color};margin-top:.25rem;">{label}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_comparison(result: dict[str, Any]) -> None:
    bandit = result["decision"]
    xgb = result["static_xgb"]
    er = result["estimated_rewards"]
    disagree = bandit != xgb["action"]
    border = "var(--amber)" if disagree else "var(--green)"
    gap = er[bandit] - er[xgb["action"]]

    st.markdown('<div class="group-title">Adaptive vs static — same applicant</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.markdown(
        f"""<div style="border:1px solid var(--accent);border-radius:8px;padding:.75rem;">
          <div class="muted" style="color:var(--accent);font-weight:600;">LINUCB · ADAPTIVE</div>
          <div style="font-size:1.3rem;font-weight:700;">{bandit}</div>
          <div class="muted">Value estimate: ${er[bandit]:.0f}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"""<div style="border:1px solid {border};border-radius:8px;padding:.75rem;">
          <div class="muted" style="color:{border};font-weight:600;">
            STATIC XGB · BASELINE {'⚡ DISAGREES' if disagree else '✓ AGREES'}</div>
          <div style="font-size:1.3rem;font-weight:700;">{xgb['action']}</div>
          <div class="muted">Value estimate: ${er[xgb['action']]:.0f}</div>
          <div class="muted" style="margin-top:.35rem;">{xgb['reasoning']}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if disagree:
        st.markdown(
            f'<div class="muted" style="color:var(--amber);margin-top:.5rem;">'
            f"⚡ Decision conflict — under the learned value model the static choice "
            f"leaves ${gap:.0f} per applicant on the table (illustrative, seed 42). "
            f"Compounded over 5,000 applicants, differences like this are the +25.2% "
            f"headline (20 seeds, admissible policies).</div>",
            unsafe_allow_html=True,
        )


def render_hitl_card() -> None:
    st.markdown(
        """<div style="border:2px solid var(--amber);border-radius:12px;padding:1rem;margin-top:.75rem;">
          <div style="font-size:1.2rem;font-weight:800;color:var(--amber);">
            🧑‍⚖️ REFERRED TO HUMAN UNDERWRITER</div>
          <div class="muted" style="margin-top:.4rem;">
            The policy's value estimates for this applicant are nearly tied — the case where
            a human judgment adds the most. In the thesis (EXP-008), REFER routes the case to
            a human whose decision replaces the mathematical referral payoff.</div>
          <div class="muted" style="margin-top:.6rem;">
            <b>Canonical result (20 seeds):</b> human-in-the-loop lifts reward
            <b>+14.8%</b> over the unassisted bandit ($103,951 vs $90,540, p &lt; 0.001,
            d = 2.65) — while referring only <b>1.3%</b> of cases and spending
            <b>2.2%</b> of cumulative reward on review.</div>
          <div class="muted" style="font-size:.72rem;font-style:italic;margin-top:.5rem;">
            Scope: +14.8% is vs the vanilla bandit, not vs Static XGB, and HITL does not
            beat the inadmissible AlwaysRATED ceiling (thesis §5.4.2).</div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_result_card(result: dict[str, Any]) -> None:
    decision = result["decision"]
    fair = result["fairness"]
    st.markdown(
        f'<div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;">'
        f'<span class="badge decision-badge b-{decision}">{decision}</span>'
        f'<span class="badge z-{fair["badge_status"]}" title="{fair["note"]}">'
        f'Guardrail: {fair["badge_status"]}</span></div>',
        unsafe_allow_html=True,
    )
    render_confidence(result["confidence"])

    st.markdown('<div class="group-title">Estimated reward by action</div>', unsafe_allow_html=True)
    er = result["estimated_rewards"]
    st.bar_chart(pd.DataFrame({"value": er}))

    render_comparison(result)

    if decision == "REFER":
        render_hitl_card()
    else:
        prem = result["premium"]
        mult = f' <span class="muted" style="font-size:.8rem">×{prem["multiplier"]}</span>' if prem["multiplier"] else ""
        st.markdown('<div class="group-title">Recommended premium</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:1.2rem;font-weight:700">{prem["display"]}{mult}</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="group-title">Why this decision</div>', unsafe_allow_html=True)
    for dr in result["drivers"]:
        arrow = "▲" if dr["direction"] == "up" else "▼"
        color = "var(--green)" if dr["direction"] == "up" else "var(--red)"
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:.3rem 0;'
            f'border-bottom:1px solid var(--line);font-size:.85rem;">'
            f'<span>{dr["label"]}</span>'
            f'<span style="color:{color};">{arrow} {abs(dr["contribution"]):.1f}</span></div>',
            unsafe_allow_html=True,
        )
    st.caption(result["illustrative_note"])


def render_desk_tab() -> None:
    col_form, col_result = st.columns(2)

    with col_form:
        st.subheader("Applicant")
        b1, b2 = st.columns(2)
        b1.button("⟳ Load CDHS sample", key="btn_load", on_click=_load_cdhs_sample, use_container_width=True)
        b2.button("Clear", key="btn_clear", on_click=_clear_form, use_container_width=True)

        st.caption("Try:")
        p1, p2, p3, p4 = st.columns(4)
        p1.button("✅ Low Risk", key="btn_preset_low", on_click=_apply_preset, args=("low_risk",), use_container_width=True)
        p2.button("⚠️ Borderline", key="btn_preset_borderline", on_click=_apply_preset, args=("borderline",), use_container_width=True)
        p3.button("🚫 High Risk", key="btn_preset_high", on_click=_apply_preset, args=("high_risk",), use_container_width=True)
        p4.button("🧑‍⚖️ Referral", key="btn_preset_refer", on_click=_apply_preset, args=("refer_case",), use_container_width=True)

        st.markdown('<div class="group-title">Demographics</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.number_input("Age", min_value=18, max_value=85, key="f_age")
        c2.selectbox("Gender", ["Male", "Female"], key="f_gender")
        c1.selectbox("Region", REGIONS, key="f_region")
        c2.selectbox("Occupation", OCCUPATIONS, key="f_occupation")

        st.markdown('<div class="group-title">Health &amp; lifestyle</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.number_input("BMI", min_value=10.0, max_value=60.0, step=0.1, key="f_bmi")
        c2.selectbox("Self-reported health", HEALTH_STATUSES, key="f_health")
        t1, t2, t3, t4 = st.columns(4)
        t1.toggle("Smoker", key="f_smoking")
        t2.toggle("Alcohol", key="f_alcohol")
        t3.toggle("Exercises", key="f_exercise")
        t4.toggle("Family history", key="f_family")
        st.multiselect("Pre-existing conditions", CONDITIONS, key="f_conditions")

        st.markdown('<div class="group-title">Socioeconomic</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.number_input("Monthly income (USD)", min_value=50.0, max_value=5000.0, step=10.0, key="f_income")
        c2.selectbox("Education", EDUCATIONS, key="f_education")
        st.selectbox("Wealth quintile", WEALTH_QUINTILES, key="f_wealth")

    with col_result:
        st.subheader("Underwriting decision")
        result = SCORER.score(_current_applicant())
        render_result_card(result)


# ---- Learn tab ----------------------------------------------------------------

PRESET_ALPHA = {"Greedy": 0.0, "Balanced": 1.0, "Exploratory": 3.0}


def _sync_alpha_from_exploration() -> None:
    exp = st.session_state.get("l_exploration")
    if exp in PRESET_ALPHA:
        st.session_state.l_alpha = PRESET_ALPHA[exp]


def _render_mix(mix: dict[str, float]) -> None:
    st.bar_chart(pd.DataFrame({"share": mix}))


def render_learn_tab() -> None:
    headline = load_canonical_headline()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Lift vs {headline['comparator']}", f"+{headline['lift_pct']}%")
    m2.metric("Seeds", headline["n_seeds"])
    m3.metric("p-value", headline["p_value"])
    m4.metric("Cohen's d", headline["cohen_d"])
    st.caption(
        f"Scope: admissible policies (ceiling: {headline['ceiling_policy']}) — "
        f"{headline['ceiling_note']} · thesis Ch.5"
    )

    st.session_state.setdefault("l_alpha", PRESET_ALPHA["Balanced"])

    c1, c2 = st.columns([1, 2])
    algo = c1.selectbox("Algorithm", ["LinUCB", "LinTS"], key="l_algo")
    exploration = c2.radio(
        "Exploration", ["Greedy", "Balanced", "Exploratory"], index=1,
        key="l_exploration", horizontal=True, on_change=_sync_alpha_from_exploration,
    ) or "Balanced"

    alpha_override = None
    if algo == "LinUCB":
        alpha_override = st.slider("α override", 0.0, 3.0, step=0.05, key="l_alpha")

    with st.spinner("Simulating 3,000 applicant decisions…"):
        data = learning.run_learn(algo, 42, N_ROUNDS, exploration, alpha=alpha_override)

    sym = "α" if data["param"]["name"] == "alpha" else "v²"
    st.caption(f"{data['illustrative_note']} · {sym} = {data['param']['value']}")

    round_n = st.slider("Round", 1, N_ROUNDS, value=N_ROUNDS, key="l_round")
    chart_df = pd.DataFrame({
        "Adaptive policy": data["adaptive"]["cumulative"][:round_n],
        "Static XGB": data["static"]["cumulative"][:round_n],
    })
    st.line_chart(chart_df)

    adaptive_at_n = data["adaptive"]["cumulative"][round_n - 1]
    static_at_n = data["static"]["cumulative"][round_n - 1]
    lift_at_n = (adaptive_at_n - static_at_n) / abs(static_at_n) * 100 if static_at_n else 0.0
    st.caption(f"round {round_n} · +{lift_at_n:.1f}% (illustrative, seed 42)")

    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown('<div class="group-title">Early (exploring)</div>', unsafe_allow_html=True)
        _render_mix(data["adaptive"]["early_mix"])
    with mc2:
        st.markdown('<div class="group-title">Late (exploiting)</div>', unsafe_allow_html=True)
        _render_mix(data["adaptive"]["late_mix"])


# ---- main ----------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="Adaptive Underwriting Desk", layout="wide")
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    _seed_defaults()

    st.title("Adaptive Underwriting Desk")
    st.caption("Contextual-bandit underwriting · Cambodia (CDHS-anchored)")

    render_fairness_panel()

    tab_desk, tab_learn = st.tabs(["Underwriting Desk", "Watch it Learn"])
    with tab_desk:
        render_desk_tab()
    with tab_learn:
        render_learn_tab()


main()
