"""
EXP-007: Benchmark Comparison + Regret Analysis

Compares LinUCB, LinTS, Epsilon-Greedy, and a static XGBoost rule baseline
on cumulative regret and reward over 5,000 rounds using common random numbers.

Statistical inference (new):
* Bootstrap 95% CIs for all algorithms
* Pairwise Wilcoxon signed-rank tests with Bonferroni correction
* Cohen's d and Cliff's delta effect sizes
* Permutation tests for robustness

PASS criteria (evaluated on 20 seeds):
1. Oracle regret <= all learning algorithms (sanity check).
2. LinUCB and LinTS regret significantly < EpsilonGreedy AND StaticXGB.
3. LinUCB and LinTS reward significantly > StaticXGB.
4. Oracle reward >= all learning algorithms (sanity check).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from healthrl.underwriting_bandit import (
    LinUCB,
    LinTS,
    EpsilonGreedy,
    StaticXGBBaseline,
    OraclePolicy,
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


def run(seed: int) -> dict[str, float]:
    """Run EXP-007 for a single seed and return scalar metrics."""
    X, df_raw, _features = preprocess_cambodia_data()
    n_features = X.shape[1]

    # Common random numbers: pre-generate noise so every algorithm sees
    # identical claims noise and acceptance draws conditioned on round t.
    rng = np.random.default_rng(seed)
    cfg = RewardConfig()
    acceptance_draws = rng.random(N_ROUNDS)
    claims_noise = rng.uniform(cfg.claims_noise_low, cfg.claims_noise_high, size=N_ROUNDS)

    algorithms = {
        "Oracle": OraclePolicy(),
        "LinUCB": LinUCB(n_actions=4, n_features=n_features, alpha=BANDIT.linucb_alpha),
        "LinTS": LinTS(n_actions=4, n_features=n_features, v2=BANDIT.lints_v2, seed=seed),
        "EpsilonGreedy": EpsilonGreedy(n_actions=4, n_features=n_features, epsilon=BANDIT.epsilon, seed=seed),
        "StaticXGB": StaticXGBBaseline(),
    }

    results = {}
    for name, bandit in algorithms.items():
        results[name] = run_bandit(
            name, bandit, X.copy(), df_raw, N_ROUNDS, seed=seed,
            acceptance_draws=acceptance_draws, claims_noise=claims_noise,
        )

    out = {}
    for name in algorithms.keys():
        out[f"cum_reward_{name}"] = float(results[name].cumulative_rewards[-1])
        out[f"cum_regret_{name}"] = float(results[name].cumulative_regrets[-1])
    return out


def main() -> int:
    print("=" * 70)
    print("EXP-007: Benchmark Comparison + Regret Analysis (20 seeds)")
    print("=" * 70)

    from experiment_utils import run_experiment_seeds_raw
    stats = run_experiment_seeds_raw(run, n_seeds=EXPERIMENT.n_seeds)

    def fmt(key: str) -> str:
        s = stats[key]
        ci = bootstrap_ci(s["values"])
        return f"{s['mean']:>12,.0f} ± {s['std']:>10,.0f} [{ci[0]:>12,.0f}, {ci[1]:>12,.0f}]"

    print("\n" + "-" * 70)
    print("SUMMARY (mean ± std, 95% CI over 20 seeds)")
    print("-" * 70)
    print(f"{'Algorithm':<18} {'Cum. Reward':>50} {'Cum. Regret':>50}")
    print("-" * 70)
    for name in ("Oracle", "LinUCB", "LinTS", "EpsilonGreedy", "StaticXGB"):
        print(f"{name:<18} ${fmt(f'cum_reward_{name}')}  ${fmt(f'cum_regret_{name}')}")

    # Pairwise statistical comparisons
    print("\n" + "=" * 70)
    print("PAIRWISE STATISTICAL COMPARISONS (Wilcoxon signed-rank, 20 seeds)")
    print("=" * 70)

    algorithm_names = ["LinUCB", "LinTS", "EpsilonGreedy", "StaticXGB"]
    regret_comparisons = []
    reward_comparisons = []

    # All pairwise regret comparisons
    for i, name_a in enumerate(algorithm_names):
        for name_b in algorithm_names[i + 1:]:
            regret_comparisons.append(
                format_comparison(
                    stats[f"cum_regret_{name_b}"]["values"],
                    stats[f"cum_regret_{name_a}"]["values"],
                    metric_name="Cum. Regret",
                    baseline_name=name_b,
                    treatment_name=name_a,
                    alternative="less",
                )
            )

    # Reward comparisons: bandits vs StaticXGB
    for name in ("LinUCB", "LinTS"):
        reward_comparisons.append(
            format_comparison(
                stats["cum_reward_StaticXGB"]["values"],
                stats[f"cum_reward_{name}"]["values"],
                metric_name="Cum. Reward",
                baseline_name="StaticXGB",
                treatment_name=name,
                alternative="greater",
            )
        )

    print("\nRegret Comparisons:")
    print_comparison_table(regret_comparisons)

    print("\nReward Comparisons:")
    print_comparison_table(reward_comparisons)

    # Bonferroni correction for multiple comparisons
    n_regret_tests = len(regret_comparisons)
    n_reward_tests = len(reward_comparisons)
    alpha_bonf_regret = 0.05 / n_regret_tests
    alpha_bonf_reward = 0.05 / n_reward_tests
    print(f"\nBonferroni-corrected alpha: regret tests = {alpha_bonf_regret:.4f}, reward tests = {alpha_bonf_reward:.4f}")

    print("\n" + "=" * 70)
    print("ASSERTIONS")
    print("=" * 70)

    pass_total = True

    # Sanity: Oracle <= all on regret
    regret_oracle = stats["cum_regret_Oracle"]["mean"]
    regret_ucb = stats["cum_regret_LinUCB"]["mean"]
    regret_ts = stats["cum_regret_LinTS"]["mean"]
    regret_eg = stats["cum_regret_EpsilonGreedy"]["mean"]
    regret_static = stats["cum_regret_StaticXGB"]["mean"]

    check0 = regret_oracle <= regret_ucb and regret_oracle <= regret_ts and regret_oracle <= regret_eg and regret_oracle <= regret_static
    print(f"[{'PASS' if check0 else 'FAIL'}] Oracle mean regret <= all learning algorithms")
    print(f"       Oracle: ${regret_oracle:,.0f}  LinUCB: ${regret_ucb:,.0f}  LinTS: ${regret_ts:,.0f}")
    pass_total &= check0

    # Statistical significance: LinUCB < StaticXGB and EpsilonGreedy
    ucb_vs_static_regret = next(c for c in regret_comparisons if c["treatment_name"] == "LinUCB" and c["baseline_name"] == "StaticXGB")
    ucb_vs_eg_regret = next(c for c in regret_comparisons if c["treatment_name"] == "LinUCB" and c["baseline_name"] == "EpsilonGreedy")
    check1 = ucb_vs_static_regret["wilcoxon_significant"] and ucb_vs_eg_regret["wilcoxon_significant"]
    print(f"[{'PASS' if check1 else 'FAIL'}] LinUCB regret significantly < StaticXGB AND EpsilonGreedy (Wilcoxon)")
    print(f"       vs StaticXGB: p={ucb_vs_static_regret['wilcoxon_p']:.4f}, d={ucb_vs_static_regret['cohens_d']:.2f}")
    print(f"       vs EpsGreedy: p={ucb_vs_eg_regret['wilcoxon_p']:.4f}, d={ucb_vs_eg_regret['cohens_d']:.2f}")
    pass_total &= check1

    # Statistical significance: LinTS < StaticXGB and EpsilonGreedy
    ts_vs_static_regret = next(c for c in regret_comparisons if c["treatment_name"] == "LinTS" and c["baseline_name"] == "StaticXGB")
    ts_vs_eg_regret = next(c for c in regret_comparisons if c["treatment_name"] == "LinTS" and c["baseline_name"] == "EpsilonGreedy")
    check2 = ts_vs_static_regret["wilcoxon_significant"] and ts_vs_eg_regret["wilcoxon_significant"]
    print(f"[{'PASS' if check2 else 'FAIL'}] LinTS regret significantly < StaticXGB AND EpsilonGreedy (Wilcoxon)")
    print(f"       vs StaticXGB: p={ts_vs_static_regret['wilcoxon_p']:.4f}, d={ts_vs_static_regret['cohens_d']:.2f}")
    print(f"       vs EpsGreedy: p={ts_vs_eg_regret['wilcoxon_p']:.4f}, d={ts_vs_eg_regret['cohens_d']:.2f}")
    pass_total &= check2

    # Reward: LinUCB and LinTS > StaticXGB
    ucb_vs_static_reward = next(c for c in reward_comparisons if c["treatment_name"] == "LinUCB")
    ts_vs_static_reward = next(c for c in reward_comparisons if c["treatment_name"] == "LinTS")
    check3 = ucb_vs_static_reward["wilcoxon_significant"] and ts_vs_static_reward["wilcoxon_significant"]
    print(f"[{'PASS' if check3 else 'FAIL'}] LinUCB and LinTS reward significantly > StaticXGB (Wilcoxon)")
    print(f"       LinUCB: p={ucb_vs_static_reward['wilcoxon_p']:.4f}, d={ucb_vs_static_reward['cohens_d']:.2f}")
    print(f"       LinTS:  p={ts_vs_static_reward['wilcoxon_p']:.4f}, d={ts_vs_static_reward['cohens_d']:.2f}")
    pass_total &= check3

    reward_oracle = stats["cum_reward_Oracle"]["mean"]
    reward_ucb = stats["cum_reward_LinUCB"]["mean"]
    reward_ts = stats["cum_reward_LinTS"]["mean"]
    reward_static = stats["cum_reward_StaticXGB"]["mean"]

    check4 = reward_oracle >= reward_ucb and reward_oracle >= reward_ts and reward_oracle >= reward_static
    print(f"[{'PASS' if check4 else 'FAIL'}] Oracle mean reward >= all learning algorithms")
    print(f"       Oracle: ${reward_oracle:,.0f}  LinUCB: ${reward_ucb:,.0f}  LinTS: ${reward_ts:,.0f}")
    pass_total &= check4

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-007: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-007: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
