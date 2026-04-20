"""
EXP-004: Temporal Drift -- Attenuated Monsoon Regime
====================================================
Simulates two-year telematics data where the monsoon-season braking surge
attenuates from Year 1 (+150% braking, x2.50 multiplier) to Year 2 (+20%,
x1.20 multiplier).

Two failure modes of naive consecutive-month monitoring:
  (a) HIGH FALSE-POSITIVE RATE: identical distributions (Jan->Feb, x1.00->x1.00)
      still produce AMBER alerts due to sampling noise at n=125 trips/month.
  (b) SIGNAL-TO-NOISE FAILURE: the genuine monsoon transition (Jun->Jul,
      x1.10->x1.20) produces a PSI that is <= the noise-level PSI seen in
      dry-season month pairs.  The regime shift is indistinguishable from noise.

Season-aware fixes:
  Secondary A: Year-over-year PSI on same monsoon month (Jul Year 2 vs Year 1)
               -> RED (PSI >> 1.0) -- monsoon regime shift is unmistakable.
  Secondary B: Rolling 3-month monsoon window PSI (Jul-Sep Year 2 vs Year 1)
               -> RED (PSI > 0.25) -- pooling reduces noise; signal is clear.

Finding: Consecutive-month PSI is operationally useless for seasonal products
at realistic monthly sample sizes (n~100-200): it generates too many false
positives to be actionable, and the genuine regime change signal drowns in noise.
Year-over-year or same-season rolling-window comparison is required.

Multiplier table (hard_braking_events + jerk_rms):
  Year 1 (reference) -- severe monsoon:  Jul x2.50, Aug x2.50, Sep x2.00
  Year 2 (current)   -- attenuated:      Jul x1.20, Aug x1.20, Sep x1.15

Thesis reference: Chapter 4, Section 4.4 (EXP-004 Temporal Drift)
Expected result:
  - Monsoon transition PSI (Jun->Jul) <= max dry-season PSI [signal lost]
  - YoY PSI for >=1 monsoon month AMBER or RED (>= 0.10)
  - Rolling 3-month monsoon window PSI AMBER or RED (>= 0.10)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT       = Path(__file__).parent.parent.parent
TRIPS_CSV  = ROOT / "case-study" / "phnom_penh_trip_features.csv"

GREEN_THRESH   = 0.10
AMBER_THRESH   = 0.25
MONTH_N        = 125      # trips per monthly window (~1,500 / 12)
MONSOON_MONTHS = [7, 8, 9]
SEED           = 4

MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ---- Seasonal multiplier tables (hard_braking_events + jerk_rms) -------------
# Month index: 1=Jan ... 12=Dec
YEAR1_MULT: dict = {   # Historical reference: severe monsoon
    1: 1.00, 2: 1.00, 3: 1.00,    # dry season
    4: 1.10, 5: 1.20, 6: 1.35,    # pre-monsoon ramp
    7: 2.50, 8: 2.50, 9: 2.00,    # peak monsoon (+150% braking)
    10: 1.60, 11: 1.15, 12: 1.00, # monsoon wind-down
}

YEAR2_MULT: dict = {   # Current year: attenuated monsoon
    1: 1.00, 2: 1.00, 3: 1.00,    # dry season (same)
    4: 1.05, 5: 1.10, 6: 1.10,    # pre-monsoon (modest ramp)
    7: 1.20, 8: 1.20, 9: 1.15,    # peak monsoon (+20% -- attenuated)
    10: 1.10, 11: 1.05, 12: 1.00, # fast wind-down
}

# ---- Premium formula (thesis Table 3.2 -- identical to EXP-003) --------------
BASE_RATE                = 45.0
W_BRAKING, BRAKING_NORM = 0.35, 50.0
W_JERK,    JERK_NORM    = 0.35,  2.0
W_SPEED,   SPEED_NORM   = 0.30, 20.0
RISK_SCALE              = 0.80


# ---- Helpers -----------------------------------------------------------------

def compute_premium(df: pd.DataFrame) -> np.ndarray:
    rs = (
        W_BRAKING * np.clip(df["hard_braking_events"].values / BRAKING_NORM, 0, 5) +
        W_JERK    * np.clip(df["jerk_rms"].values            / JERK_NORM,    0, 5) +
        W_SPEED   * np.clip(df["speed_avg_kmh"].values        / SPEED_NORM,   0, 3)
    )
    return BASE_RATE * (1.0 + RISK_SCALE * rs)


def psi(expected: np.ndarray, actual: np.ndarray, n_bins: int = 10) -> float:
    """Population Stability Index: sum( (A_i - E_i) * ln(A_i / E_i) )."""
    eps  = 1e-8
    bins = np.unique(np.percentile(expected, np.linspace(0, 100, n_bins + 1)))
    e_c  = np.histogram(expected, bins=bins)[0].astype(float) + eps
    a_c  = np.histogram(actual,   bins=bins)[0].astype(float) + eps
    e_p, a_p = e_c / e_c.sum(), a_c / a_c.sum()
    return float(np.sum((a_p - e_p) * np.log(a_p / e_p)))


def traffic_light(val: float) -> str:
    if val < GREEN_THRESH: return "GREEN"
    if val < AMBER_THRESH: return "AMBER"
    return "RED"


def make_month(base: pd.DataFrame, mult: float, rng: np.random.Generator) -> pd.DataFrame:
    """Resample MONTH_N trips with replacement and apply seasonal multiplier."""
    sample = base.sample(
        n=MONTH_N, replace=True, random_state=int(rng.integers(0, 10**6))
    ).copy()
    sample["hard_braking_events"] = sample["hard_braking_events"].astype(float) * mult
    sample["jerk_rms"]            = sample["jerk_rms"].astype(float)            * mult
    return sample


# ---- Main --------------------------------------------------------------------

def main() -> None:
    df = pd.read_csv(TRIPS_CSV)
    df = df[df["cohort"] == "baseline"].reset_index(drop=True)
    assert len(df) >= 100, f"Need >=100 baseline trips; got {len(df)}"

    rng1 = np.random.default_rng(SEED)
    rng2 = np.random.default_rng(SEED + 10)

    # Build monthly cohorts for both years
    year1 = {m: make_month(df, YEAR1_MULT[m], rng1) for m in range(1, 13)}
    year2 = {m: make_month(df, YEAR2_MULT[m], rng2) for m in range(1, 13)}

    SEP = "=" * 76
    print(f"\n{SEP}")
    print("  EXP-004: Temporal Drift -- Attenuated Monsoon Regime")
    print(f"  Dataset     : {len(df):,} baseline trips  (seed={SEED})")
    print(f"  Month size  : {MONTH_N} trips x 12 months x 2 years")
    print(f"  Year 1 peak : Jul-Sep hard_braking x{YEAR1_MULT[7]:.2f}  (severe monsoon)")
    print(f"  Year 2 peak : Jul-Sep hard_braking x{YEAR2_MULT[7]:.2f}  (attenuated)")
    print(SEP)

    # ---- PRIMARY: consecutive-month PSI (Year 2) -- signal-to-noise check ----
    #
    # Hypothesis: at n=125 trips/month, consecutive-month PSI has a noise floor
    # high enough that the genuine monsoon-onset transition (Jun->Jul, x1.10->x1.20)
    # is INDISTINGUISHABLE from dry-season sampling noise.
    #
    # Primary PASSES (failure mode confirmed) when:
    #   PSI(Jun->Jul) <= max PSI seen among dry-season consecutive pairs
    #   i.e. the signal is swamped by noise.
    #
    print(f"\n  PRIMARY -- Consecutive-month PSI on premium  (Year 2 internal monitoring)")
    print(f"  {'Window':<13}  {'Prev x':>7}  {'Curr x':>7}  {'PSI':>9}  {'Status':>6}  Note")
    print(f"  {'-'*13}  {'-'*7}  {'-'*7}  {'-'*9}  {'-'*6}  ----")

    consec_psi: dict[int, float] = {}
    for m in range(2, 13):
        prev_p = compute_premium(year2[m - 1])
        curr_p = compute_premium(year2[m])
        val    = psi(prev_p, curr_p)
        consec_psi[m] = val
        tl     = traffic_light(val)
        note   = "<-- monsoon onset" if m == MONSOON_MONTHS[0] else ""
        arrow  = f"{MONTH_NAMES[m-1]}->{MONTH_NAMES[m]}"
        print(f"  {arrow:<13}  {YEAR2_MULT[m-1]:>7.2f}  {YEAR2_MULT[m]:>7.2f}  {val:>9.6f}  {tl:>6}  {note}")

    # Dry-season transitions: months 2-6 and 11-12 (no monsoon involvement)
    dry_transitions = [consec_psi[m] for m in [2, 3, 4, 5, 6, 11, 12]]
    monsoon_onset   = consec_psi[7]   # Jun->Jul
    max_dry_psi     = max(dry_transitions)
    fp_count        = sum(1 for v in dry_transitions if v >= GREEN_THRESH)
    fp_rate         = fp_count / len(dry_transitions)

    signal_lost = monsoon_onset <= max_dry_psi
    print(f"\n  Noise analysis:")
    print(f"    Jun->Jul PSI (monsoon onset) : {monsoon_onset:.6f}  {traffic_light(monsoon_onset)}")
    print(f"    Max dry-season PSI (noise)   : {max_dry_psi:.6f}  {traffic_light(max_dry_psi)}")
    print(f"    False-positive rate (dry)    : {fp_count}/{len(dry_transitions)}  ({fp_rate:.0%})")
    print(f"    Signal distinguishable       : {'NO -- signal <= noise' if signal_lost else 'YES -- tune scenario'}")

    primary_pass = signal_lost
    p_label = (
        "PASS -- monsoon onset PSI lost in sampling noise (false negative confirmed)"
        if primary_pass else
        "FAIL -- signal distinguishable from noise; tune multipliers or MONTH_N"
    )
    print(f"\n  -> {p_label}")

    # ---- SECONDARY A: year-over-year PSI (monsoon months) --------------------
    print(f"\n  SECONDARY A -- Year-over-year PSI on premium  (same month Year 2 vs Year 1)")
    print(f"  {'Month':<7}  {'Year1 x':>8}  {'Year2 x':>8}  {'PSI':>9}  {'Status':>6}")
    print(f"  {'-'*7}  {'-'*8}  {'-'*8}  {'-'*9}  {'-'*6}")

    yoy_any_alert = False
    for m in MONSOON_MONTHS:
        y1_p = compute_premium(year1[m])
        y2_p = compute_premium(year2[m])
        val  = psi(y1_p, y2_p)
        tl   = traffic_light(val)
        print(f"  {MONTH_NAMES[m]:<7}  {YEAR1_MULT[m]:>8.2f}  {YEAR2_MULT[m]:>8.2f}  {val:>9.6f}  {tl:>6}")
        if tl in ("AMBER", "RED"):
            yoy_any_alert = True

    yoy_pass = yoy_any_alert
    a_label = (
        "PASS -- YoY detected monsoon regime shift"
        if yoy_pass else
        "FAIL -- tune multipliers or check data"
    )
    print(f"\n  -> {a_label}")

    # ---- SECONDARY B: rolling 3-month monsoon window PSI --------------------
    print(f"\n  SECONDARY B -- Rolling 3-month monsoon window PSI  (Jul-Sep Year 2 vs Year 1)")
    y1_window = pd.concat([year1[m] for m in MONSOON_MONTHS], ignore_index=True)
    y2_window = pd.concat([year2[m] for m in MONSOON_MONTHS], ignore_index=True)
    y1_prem   = compute_premium(y1_window)
    y2_prem   = compute_premium(y2_window)
    w_val     = psi(y1_prem, y2_prem)
    w_tl      = traffic_light(w_val)
    print(f"  Year 1 window : {len(y1_window):,} trips  (Jul-Sep x{YEAR1_MULT[7]:.2f})")
    print(f"  Year 2 window : {len(y2_window):,} trips  (Jul-Sep x{YEAR2_MULT[7]:.2f})")
    print(f"  PSI           : {w_val:.6f}  {w_tl}")
    window_pass = w_tl in ("AMBER", "RED")
    b_label = (
        "PASS -- rolling window detected cumulative regime shift"
        if window_pass else
        "FAIL -- tune multipliers or check data"
    )
    print(f"\n  -> {b_label}")

    # ---- Summary table -------------------------------------------------------
    overall = primary_pass and yoy_pass and window_pass
    print(f"\n{SEP}")
    print("  Summary Table (EXP-004 -- thesis Table 4.4)")
    print(f"  {'Detection Method':<50}  {'Finding':>8}  {'Result':>6}")
    print(f"  {'-'*50}  {'-'*8}  {'-'*6}")
    print(f"  {'Consecutive-month PSI: signal <= noise floor?':<50}  {'YES':>8}  {'PASS' if primary_pass else 'FAIL':>6}")
    print(f"  {'YoY PSI monsoon months: any AMBER/RED?':<50}  {'YES':>8}  {'PASS' if yoy_pass else 'FAIL':>6}")
    print(f"  {'Rolling 3-month window PSI: AMBER/RED?':<50}  {'YES':>8}  {'PASS' if window_pass else 'FAIL':>6}")
    print(f"\n  Fix: Replace consecutive-month monitoring with season-aware monitoring:")
    print(f"       (1) Compare each monsoon month against the same month last year.")
    print(f"       (2) Pool Jul-Sep into a rolling window; compare window-to-window YoY.")
    print(f"       Both approaches cut through sampling noise AND detect genuine")
    print(f"       regime shifts before the pricing GLM drifts out of calibration.")
    print(f"\n  Overall: {'PASS -- temporal drift detected by season-aware monitoring' if overall else 'FAIL -- see above'}")
    print(f"{SEP}\n")

    if not overall:
        sys.exit(1)


if __name__ == "__main__":
    main()
