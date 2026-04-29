"""
EXP-006: Fairness Audit
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from stress_testing.rl.underwriting_bandit import (
    LinUCB,
    preprocess_cambodia_data,
    run_bandit,
    ACTION_STANDARD,
    ACTION_RATED,
)

N_ROUNDS = 5000
SEED = 42


def compute_psi(expected_dist: np.ndarray, actual_dist: np.ndarray) -> float:
    eps = 1e-8
    expected_dist = expected_dist / (expected_dist.sum() + eps)
    actual_dist = actual_dist / (actual_dist.sum() + eps)
    psi = 0.0
    for e, a in zip(expected_dist, actual_dist):
        if e > eps:
            psi += (a - e) * np.log((a + eps) / (e + eps))
        elif a > eps:
            psi += a - e
    return float(psi)


def main() -> int:
    print("=" * 70)
    print("EXP-006: Fairness Audit — Regional and Occupational Bias")
    print("=" * 70)

    X, df_raw, features = preprocess_cambodia_data()
    n_features = X.shape[1]

    print(f"\nRunning LinUCB for {N_ROUNDS:,} rounds ...")
    linucb = LinUCB(n_actions=4, n_features=n_features, alpha=1.0)
    result = run_bandit("LinUCB", linucb, X.copy(), df_raw, N_ROUNDS, seed=SEED)

    decisions = pd.DataFrame({
        "round": np.arange(N_ROUNDS),
        "action": result.actions,
        "region": [df_raw.iloc[i % len(df_raw)]["region"] for i in range(N_ROUNDS)],
        "occupation": [df_raw.iloc[i % len(df_raw)]["occupation"] for i in range(N_ROUNDS)],
    })
    decisions["approved"] = decisions["action"].isin([ACTION_STANDARD, ACTION_RATED])

    print("\n" + "-" * 70)
    print("REGIONAL APPROVAL RATES")
    print("-" * 70)
    region_stats = []
    for region in df_raw["region"].unique():
        subset = decisions[decisions["region"] == region]
        total = len(subset)
        approved = subset["approved"].sum()
        rate = approved / total if total > 0 else 0.0
        region_stats.append({"region": region, "total": total, "approved": approved, "rate": rate})

    region_df = pd.DataFrame(region_stats).sort_values("rate", ascending=False)
    max_rate = region_df["rate"].max()
    for _, row in region_df.iterrows():
        flag = "OK" if row["rate"] >= 0.5 * max_rate else "WARN"
        print(f"  {row['region']:20s} | Total: {row['total']:4d} | Approved: {row['approved']:4d} | Rate: {row['rate']:6.1%} [{flag}]")

    print("\n" + "-" * 70)
    print("OCCUPATIONAL APPROVAL RATES")
    print("-" * 70)
    occ_stats = []
    for occ in df_raw["occupation"].unique():
        subset = decisions[decisions["occupation"] == occ]
        total = len(subset)
        approved = subset["approved"].sum()
        rate = approved / total if total > 0 else 0.0
        occ_stats.append({"occupation": occ, "total": total, "approved": approved, "rate": rate})

    occ_df = pd.DataFrame(occ_stats).sort_values("rate", ascending=False)
    max_occ_rate = occ_df["rate"].max()
    for _, row in occ_df.iterrows():
        flag = "OK" if row["rate"] >= 0.5 * max_occ_rate else "WARN"
        print(f"  {row['occupation']:25s} | Total: {row['total']:4d} | Approved: {row['approved']:4d} | Rate: {row['rate']:6.1%} [{flag}]")

    print("\n" + "-" * 70)
    print("POPULATION STABILITY INDEX (PSI)")
    print("-" * 70)

    region_labels = sorted(df_raw["region"].unique())
    full_r = np.array([df_raw["region"].value_counts().get(r, 0) for r in region_labels])
    app_r = np.array([decisions[decisions["approved"]]["region"].value_counts().get(r, 0) for r in region_labels])
    region_psi = compute_psi(full_r, app_r)
    status_r = "GREEN" if region_psi < 0.10 else "AMBER" if region_psi < 0.25 else "RED"
    print(f"  Region PSI (full vs approved):     {region_psi:.4f}  ({status_r})")

    occ_labels = sorted(df_raw["occupation"].unique())
    full_o = np.array([df_raw["occupation"].value_counts().get(o, 0) for o in occ_labels])
    app_o = np.array([decisions[decisions["approved"]]["occupation"].value_counts().get(o, 0) for o in occ_labels])
    occ_psi = compute_psi(full_o, app_o)
    status_o = "GREEN" if occ_psi < 0.10 else "AMBER" if occ_psi < 0.25 else "RED"
    print(f"  Occupation PSI (full vs approved): {occ_psi:.4f}  ({status_o})")

    print("\n" + "=" * 70)
    print("ASSERTIONS")
    print("=" * 70)

    pass_total = True

    min_region_rate = region_df["rate"].min()
    check1 = min_region_rate >= 0.5 * max_rate
    print(f"[{'PASS' if check1 else 'FAIL'}] Min region approval rate >= 50% of max  (min={min_region_rate:.1%}, max={max_rate:.1%})")
    pass_total &= check1

    min_occ_rate = occ_df["rate"].min()
    check2 = min_occ_rate >= 0.5 * max_occ_rate
    print(f"[{'PASS' if check2 else 'FAIL'}] Min occupation approval rate >= 50% of max  (min={min_occ_rate:.1%}, max={max_occ_rate:.1%})")
    pass_total &= check2

    check3 = region_psi < 0.25
    print(f"[{'PASS' if check3 else 'FAIL'}] Region PSI < 0.25  (got {region_psi:.4f})")
    pass_total &= check3

    check4 = occ_psi < 0.25
    print(f"[{'PASS' if check4 else 'FAIL'}] Occupation PSI < 0.25  (got {occ_psi:.4f})")
    pass_total &= check4

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-006: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-006: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
