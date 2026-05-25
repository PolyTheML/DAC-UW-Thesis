"""
EXP-012: Sensitivity Analysis — Hyperparameters and Reward Structure

Evaluates robustness of conclusions to hyperparameter choices and structural
assumptions in the reward function.

Sensitivity dimensions:
1. LinUCB alpha (exploration parameter): {0.1, 0.5, 1.0, 2.0, 5.0}
   Tests whether the default alpha=1.0 is near-optimal.
2. Adverse-selection factor: {1.0, 1.35, 1.7}
   Tests whether the default 1.35 is conservative or optimistic.
3. Customer elasticity slope: {2.5, 3.5, 4.5}
   Tests sensitivity to price-demand responsiveness.

For each parameter value, runs LinUCB and StaticXGB for 5,000 rounds across
10 seeds and compares cumulative reward.

PASS criteria:
1. alpha=1.0 achieves the lowest (or near-lowest) regret among alpha values.
2. LinUCB outperforms StaticXGB across all adverse-selection factors.
3. LinUCB outperforms StaticXGB across all elasticity slopes.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from healthrl.underwriting_bandit import (
    LinUCB,
    StaticXGBBaseline,
    RewardConfig,
    preprocess_cambodia_data,
    run_bandit,
)
from healthrl.config import EXPERIMENT, BANDIT
from statistical_utils import (
    format_comparison,
    print_comparison_table,
    bootstrap_ci,
)

N_ROUNDS = EXPERIMENT.n_rounds
N_SEEDS = 10  # 10 by design — sensitivity sweep runs many conditions; full 20 would be prohibitive


def run_alpha_sweep(alpha: float, seed: int) -> dict[str, float]:
    """Run LinUCB with specified alpha."""
    X, df_raw, _features = preprocess_cambodia_data()
    bandit = LinUCB(n_actions=4, n_features=X.shape[1], alpha=alpha)
    result = run_bandit(f"LinUCB_a{alpha}", bandit, X.copy(), df_raw, N_ROUNDS, seed=seed)
    return {
        "reward": float(result.cumulative_rewards[-1]),
        "regret": float(result.cumulative_regrets[-1]),
    }


def run_adverse_sweep(adverse_factor: float, seed: int) -> dict[str, float]:
    """Run LinUCB vs StaticXGB with specified adverse-selection factor."""
    X, df_raw, _features = preprocess_cambodia_data()
    cfg = RewardConfig(adverse_factor=adverse_factor)

    bandit = LinUCB(n_actions=4, n_features=X.shape[1], alpha=BANDIT.linucb_alpha)
    result_ucb = run_bandit("LinUCB", bandit, X.copy(), df_raw, N_ROUNDS, seed=seed, config=cfg)

    static = StaticXGBBaseline()
    result_static = run_bandit("StaticXGB", static, X.copy(), df_raw, N_ROUNDS, seed=seed, config=cfg)

    return {
        "reward_ucb": float(result_ucb.cumulative_rewards[-1]),
        "reward_static": float(result_static.cumulative_rewards[-1]),
        "regret_ucb": float(result_ucb.cumulative_regrets[-1]),
        "regret_static": float(result_static.cumulative_regrets[-1]),
    }


def run_elasticity_sweep(slope: float, seed: int) -> dict[str, float]:
    """Run LinUCB vs StaticXGB with specified customer elasticity slope."""
    X, df_raw, _features = preprocess_cambodia_data()
    cfg = RewardConfig(acceptance_slope=slope)

    bandit = LinUCB(n_actions=4, n_features=X.shape[1], alpha=BANDIT.linucb_alpha)
    result_ucb = run_bandit("LinUCB", bandit, X.copy(), df_raw, N_ROUNDS, seed=seed, config=cfg)

    static = StaticXGBBaseline()
    result_static = run_bandit("StaticXGB", static, X.copy(), df_raw, N_ROUNDS, seed=seed, config=cfg)

    return {
        "reward_ucb": float(result_ucb.cumulative_rewards[-1]),
        "reward_static": float(result_static.cumulative_rewards[-1]),
        "regret_ucb": float(result_ucb.cumulative_regrets[-1]),
        "regret_static": float(result_static.cumulative_regrets[-1]),
    }


def main() -> int:
    print("=" * 70)
    print("EXP-012: Sensitivity Analysis (10 seeds per condition)")
    print("=" * 70)

    from experiment_utils import run_experiment_seeds_raw

    # ── 1. Alpha sweep ──────────────────────────────────────────────────────
    print("\n" + "-" * 70)
    print("1. LinUCB alpha sweep")
    print("-" * 70)

    alphas = [0.1, 0.5, 1.0, 2.0, 5.0]
    alpha_stats = {}
    for alpha in alphas:
        print(f"\n  alpha = {alpha}:")
        alpha_stats[alpha] = run_experiment_seeds_raw(
            lambda seed: run_alpha_sweep(alpha, seed), n_seeds=N_SEEDS
        )

    print("\n  Results:")
    print(f"  {'Alpha':>8} {'Cum. Reward':>35} {'Cum. Regret':>35}")
    print("  " + "-" * 78)
    for alpha in alphas:
        s_rwd = alpha_stats[alpha]["reward"]
        s_reg = alpha_stats[alpha]["regret"]
        ci_rwd = bootstrap_ci(s_rwd["values"])
        ci_reg = bootstrap_ci(s_reg["values"])
        print(
            f"  {alpha:>8} ${s_rwd['mean']:>10,.0f} ± {s_rwd['std']:>8,.0f} [{ci_rwd[0]:>10,.0f}, {ci_rwd[1]:>10,.0f}]"
            f"  ${s_reg['mean']:>10,.0f} ± {s_reg['std']:>8,.0f} [{ci_reg[0]:>10,.0f}, {ci_reg[1]:>10,.0f}]"
        )

    best_alpha = min(alphas, key=lambda a: alpha_stats[a]["regret"]["mean"])
    print(f"\n  Best alpha (lowest regret): {best_alpha}")

    # ── 2. Adverse-selection factor sweep ───────────────────────────────────
    print("\n" + "-" * 70)
    print("2. Adverse-selection factor sweep")
    print("-" * 70)

    adverse_factors = [1.0, 1.35, 1.7]
    adverse_stats = {}
    for af in adverse_factors:
        print(f"\n  adverse_factor = {af}:")
        adverse_stats[af] = run_experiment_seeds_raw(
            lambda seed: run_adverse_sweep(af, seed), n_seeds=N_SEEDS
        )

    print("\n  Results:")
    print(f"  {'Adverse':>10} {'LinUCB Reward':>28} {'Static Reward':>28} {'Advantage':>15}")
    print("  " + "-" * 80)
    for af in adverse_factors:
        s_ucb = adverse_stats[af]["reward_ucb"]
        s_stat = adverse_stats[af]["reward_static"]
        ci_ucb = bootstrap_ci(s_ucb["values"])
        ci_stat = bootstrap_ci(s_stat["values"])
        adv = s_ucb["mean"] - s_stat["mean"]
        print(
            f"  {af:>10} ${s_ucb['mean']:>10,.0f} [{ci_ucb[0]:>10,.0f}, {ci_ucb[1]:>10,.0f}]"
            f"  ${s_stat['mean']:>10,.0f} [{ci_stat[0]:>10,.0f}, {ci_stat[1]:>10,.0f}]"
            f"  ${adv:>+10,.0f}"
        )

    # Statistical comparisons for adverse sweep
    print("\n  Statistical comparisons (LinUCB vs StaticXGB):")
    adverse_comparisons = []
    for af in adverse_factors:
        adverse_comparisons.append(
            format_comparison(
                adverse_stats[af]["reward_static"]["values"],
                adverse_stats[af]["reward_ucb"]["values"],
                metric_name="Cum. Reward",
                baseline_name=f"StaticXGB (af={af})",
                treatment_name=f"LinUCB (af={af})",
                alternative="greater",
            )
        )
    print_comparison_table(adverse_comparisons)

    # ── 3. Elasticity slope sweep ───────────────────────────────────────────
    print("\n" + "-" * 70)
    print("3. Customer elasticity slope sweep")
    print("-" * 70)

    slopes = [2.5, 3.5, 4.5]
    slope_stats = {}
    for slope in slopes:
        print(f"\n  slope = {slope}:")
        slope_stats[slope] = run_experiment_seeds_raw(
            lambda seed: run_elasticity_sweep(slope, seed), n_seeds=N_SEEDS
        )

    print("\n  Results:")
    print(f"  {'Slope':>8} {'LinUCB Reward':>28} {'Static Reward':>28} {'Advantage':>15}")
    print("  " + "-" * 80)
    for slope in slopes:
        s_ucb = slope_stats[slope]["reward_ucb"]
        s_stat = slope_stats[slope]["reward_static"]
        ci_ucb = bootstrap_ci(s_ucb["values"])
        ci_stat = bootstrap_ci(s_stat["values"])
        adv = s_ucb["mean"] - s_stat["mean"]
        print(
            f"  {slope:>8} ${s_ucb['mean']:>10,.0f} [{ci_ucb[0]:>10,.0f}, {ci_ucb[1]:>10,.0f}]"
            f"  ${s_stat['mean']:>10,.0f} [{ci_stat[0]:>10,.0f}, {ci_stat[1]:>10,.0f}]"
            f"  ${adv:>+10,.0f}"
        )

    print("\n  Statistical comparisons (LinUCB vs StaticXGB):")
    slope_comparisons = []
    for slope in slopes:
        slope_comparisons.append(
            format_comparison(
                slope_stats[slope]["reward_static"]["values"],
                slope_stats[slope]["reward_ucb"]["values"],
                metric_name="Cum. Reward",
                baseline_name=f"StaticXGB (slope={slope})",
                treatment_name=f"LinUCB (slope={slope})",
                alternative="greater",
            )
        )
    print_comparison_table(slope_comparisons)

    # ── Assertions ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ASSERTIONS")
    print("=" * 70)

    pass_total = True

    # 1. alpha=1.0 is optimal or near-optimal
    alpha_regrets = {a: alpha_stats[a]["regret"]["mean"] for a in alphas}
    best_alpha_by_regret = min(alpha_regrets, key=alpha_regrets.get)
    check1 = best_alpha_by_regret == 1.0 or alpha_regrets[1.0] <= alpha_regrets[best_alpha_by_regret] * 1.05
    print(f"[{'PASS' if check1 else 'FAIL'}] alpha=1.0 is optimal or within 5% of optimal")
    print(f"       Best: alpha={best_alpha_by_regret} (regret=${alpha_regrets[best_alpha_by_regret]:,.0f})")
    print(f"       alpha=1.0: regret=${alpha_regrets[1.0]:,.0f})")
    pass_total &= check1

    # 2. LinUCB > StaticXGB for all adverse-selection factors
    check2 = all(c["wilcoxon_significant"] and c["mean_diff"] > 0 for c in adverse_comparisons)
    print(f"[{'PASS' if check2 else 'FAIL'}] LinUCB reward > StaticXGB for all adverse-selection factors")
    for c in adverse_comparisons:
        sig = "***" if c["wilcoxon_p"] < 0.001 else "**" if c["wilcoxon_p"] < 0.01 else "*" if c["wilcoxon_p"] < 0.05 else "ns"
        print(f"       {c['treatment_name']}: p={c['wilcoxon_p']:.4f} {sig}, d={c['cohens_d']:.2f}")
    pass_total &= check2

    # 3. LinUCB > StaticXGB for all elasticity slopes
    check3 = all(c["wilcoxon_significant"] and c["mean_diff"] > 0 for c in slope_comparisons)
    print(f"[{'PASS' if check3 else 'FAIL'}] LinUCB reward > StaticXGB for all elasticity slopes")
    for c in slope_comparisons:
        sig = "***" if c["wilcoxon_p"] < 0.001 else "**" if c["wilcoxon_p"] < 0.01 else "*" if c["wilcoxon_p"] < 0.05 else "ns"
        print(f"       {c['treatment_name']}: p={c['wilcoxon_p']:.4f} {sig}, d={c['cohens_d']:.2f}")
    pass_total &= check3

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-012: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-012: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
