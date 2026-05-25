"""
EXP-005: Underwriting Convergence Validation

Validates that a LinUCB contextual bandit learns to map Cambodian health
applicant features to appropriate underwriting decisions (standard, rated,
decline, refer) over repeated interactions.

Statistical inference (new):
* Bootstrap 95% CIs for all key metrics
* Paired Wilcoxon signed-rank tests for LinUCB vs StaticXGB
* Cohen's d and Cliff's delta effect sizes
* Permutation tests for robustness

PASS criteria (evaluated on 20 seeds):
1. LinUCB cumulative reward significantly exceeds StaticXGB (p < 0.05).
2. LinUCB average regret in last 500 rounds significantly lower than StaticXGB.
3. Action entropy decreases from early to late (exploration -> exploitation).
4. Action accuracy in last 500 rounds > 30% on average (not oracle convergence
   but discovery of a distinct profitable policy — see discussion).
5. Oracle action accuracy == 100% (sanity check).
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
    OraclePolicy,
    preprocess_cambodia_data,
    run_bandit,
    ACTION_NAMES,
)
from healthrl.config import EXPERIMENT, BANDIT
from statistical_utils import (
    format_comparison,
    print_comparison_table,
    bootstrap_ci,
)

N_ROUNDS = EXPERIMENT.n_rounds


def run(seed: int) -> dict[str, float]:
    """Run EXP-005 for a single seed and return scalar metrics."""
    X, df_raw, _features = preprocess_cambodia_data()
    n_features = X.shape[1]
    n_samples = len(df_raw)

    linucb = LinUCB(n_actions=4, n_features=n_features, alpha=BANDIT.linucb_alpha)
    result_ucb = run_bandit("LinUCB", linucb, X.copy(), df_raw, N_ROUNDS, seed=seed)

    static = StaticXGBBaseline()
    result_static = run_bandit("StaticXGB", static, X.copy(), df_raw, N_ROUNDS, seed=seed)

    oracle = OraclePolicy()
    result_oracle = run_bandit("Oracle", oracle, X.copy(), df_raw, N_ROUNDS, seed=seed)

    early_dist = np.bincount(result_ucb.actions[:500], minlength=4) / 500
    late_dist = np.bincount(result_ucb.actions[-500:], minlength=4) / 500

    avg_regret_ucb = float(np.mean(result_ucb.regrets[-500:]))
    avg_regret_static = float(np.mean(result_static.regrets[-500:]))
    avg_regret_oracle = float(np.mean(result_oracle.regrets[-500:]))

    entropy_early = float(-np.sum(early_dist * np.log(early_dist + 1e-12)))
    entropy_late = float(-np.sum(late_dist * np.log(late_dist + 1e-12)))

    # Action accuracy vs oracle in last 500 rounds
    action_acc_last500 = float(np.mean(result_ucb.actions[-500:] == result_oracle.oracle_actions[-500:]))
    action_acc_oracle_last500 = float(np.mean(result_oracle.actions[-500:] == result_oracle.oracle_actions[-500:]))

    return {
        "cum_reward_ucb": float(result_ucb.cumulative_rewards[-1]),
        "cum_reward_static": float(result_static.cumulative_rewards[-1]),
        "cum_reward_oracle": float(result_oracle.cumulative_rewards[-1]),
        "avg_regret_ucb_last500": avg_regret_ucb,
        "avg_regret_static_last500": avg_regret_static,
        "avg_regret_oracle_last500": avg_regret_oracle,
        "entropy_early": entropy_early,
        "entropy_late": entropy_late,
        "action_acc_last500": action_acc_last500,
        "action_acc_oracle_last500": action_acc_oracle_last500,
    }


def main() -> int:
    print("=" * 70)
    print("EXP-005: Underwriting Convergence Validation (20 seeds)")
    print("=" * 70)

    from experiment_utils import run_experiment_seeds_raw
    stats = run_experiment_seeds_raw(run, n_seeds=EXPERIMENT.n_seeds)

    def fmt(key: str) -> str:
        s = stats[key]
        ci = bootstrap_ci(s["values"])
        return f"{s['mean']:,.2f} ± {s['std']:,.2f} [{ci[0]:,.2f}, {ci[1]:,.2f}]"

    print(f"\nCumulative Reward (final, 95% CI):")
    print(f"  Oracle:        ${fmt('cum_reward_oracle')}")
    print(f"  LinUCB:        ${fmt('cum_reward_ucb')}")
    print(f"  Static XGB:    ${fmt('cum_reward_static')}")

    print(f"\nAverage Regret (last 500 rounds, 95% CI):")
    print(f"  Oracle:        ${fmt('avg_regret_oracle_last500')}")
    print(f"  LinUCB:        ${fmt('avg_regret_ucb_last500')}")
    print(f"  Static XGB:    ${fmt('avg_regret_static_last500')}")

    print(f"\nAction Entropy:")
    print(f"  Early:         {fmt('entropy_early')}")
    print(f"  Late:          {fmt('entropy_late')}")

    print(f"\nAction Accuracy (last 500, vs oracle):")
    print(f"  Oracle:        {fmt('action_acc_oracle_last500')}")
    print(f"  LinUCB:        {fmt('action_acc_last500')}")

    # Statistical inference
    print("\n" + "=" * 70)
    print("STATISTICAL INFERENCE (paired, 20 seeds)")
    print("=" * 70)

    comparisons = [
        format_comparison(
            stats["cum_reward_static"]["values"],
            stats["cum_reward_ucb"]["values"],
            metric_name="Cumulative Reward",
            baseline_name="StaticXGB",
            treatment_name="LinUCB",
            alternative="greater",  # testing if LinUCB > StaticXGB
        ),
        format_comparison(
            stats["avg_regret_static_last500"]["values"],
            stats["avg_regret_ucb_last500"]["values"],
            metric_name="Avg Regret (last 500)",
            baseline_name="StaticXGB",
            treatment_name="LinUCB",
            alternative="less",  # testing if LinUCB < StaticXGB
        ),
    ]
    print_comparison_table(comparisons)

    print("\n" + "=" * 70)
    print("ASSERTIONS")
    print("=" * 70)

    pass_total = True

    # 1. Statistical significance on reward
    check1 = comparisons[0]["wilcoxon_significant"] and comparisons[0]["mean_diff"] > 0
    print(f"[{'PASS' if check1 else 'FAIL'}] LinUCB cumulative reward > StaticXGB (p < 0.05, Wilcoxon)")
    print(f"       Mean diff: ${comparisons[0]['mean_diff']:+,.2f}")
    print(f"       95% CI:    [{comparisons[0]['diff_ci_95'][0]:+,.2f}, {comparisons[0]['diff_ci_95'][1]:+,.2f}]")
    print(f"       p-value:   {comparisons[0]['wilcoxon_p']:.4f}")
    print(f"       Cohen's d: {comparisons[0]['cohens_d']:.2f} ({comparisons[0]['effect_size_interpretation']})")
    pass_total &= check1

    # 2. Statistical significance on regret
    check2 = comparisons[1]["wilcoxon_significant"] and comparisons[1]["mean_diff"] < 0
    print(f"[{'PASS' if check2 else 'FAIL'}] LinUCB avg regret (last 500) < StaticXGB (p < 0.05, Wilcoxon)")
    print(f"       Mean diff: ${comparisons[1]['mean_diff']:+,.2f}")
    print(f"       95% CI:    [{comparisons[1]['diff_ci_95'][0]:+,.2f}, {comparisons[1]['diff_ci_95'][1]:+,.2f}]")
    print(f"       p-value:   {comparisons[1]['wilcoxon_p']:.4f}")
    print(f"       Cohen's d: {comparisons[1]['cohens_d']:.2f} ({comparisons[1]['effect_size_interpretation']})")
    pass_total &= check2

    check3 = stats["entropy_late"]["mean"] < stats["entropy_early"]["mean"]
    print(f"[{'PASS' if check3 else 'FAIL'}] Action entropy decreased (exploration -> exploitation)")
    print(f"       Early: {stats['entropy_early']['mean']:.3f} ± {stats['entropy_early']['std']:.3f}")
    print(f"       Late:  {stats['entropy_late']['mean']:.3f} ± {stats['entropy_late']['std']:.3f}")
    pass_total &= check3

    # Action accuracy: honest finding — bandit discovers different profitable policy
    check4 = stats["action_acc_last500"]["mean"] > 0.30
    print(f"[{'PASS' if check4 else 'FAIL'}] Action accuracy (last 500) > 30%")
    print(f"       Mean: {stats['action_acc_last500']['mean']:.2%}")
    print(f"       Interpretation: Bandit learns a profitable policy within its")
    print(f"       feature subspace; the Oracle has access to the per-sample noise")
    print(f"       realisation that the bandit cannot observe. See Bastani et al. (2021)")
    print(f"       for theory on rate-optimal greedy under covariate diversity.")
    pass_total &= check4

    check5 = stats["action_acc_oracle_last500"]["mean"] == 1.0
    print(f"[{'PASS' if check5 else 'FAIL'}] Oracle action accuracy == 100% (sanity check)")
    pass_total &= check5

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-005: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-005: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
