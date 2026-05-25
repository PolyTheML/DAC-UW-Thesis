"""Publication-quality statistical inference for bandit experiments.

Provides bootstrap confidence intervals, paired Wilcoxon signed-rank tests,
Cohen's d effect sizes, Cliff's delta, and formatted comparison reports.

All functions are designed for paired multi-seed experiments where the same
seed generates observations for both baseline and treatment algorithms.
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def bootstrap_ci(
    data: np.ndarray,
    n_bootstrap: int = 10000,
    ci: float = 0.95,
    rng_seed: int = 42,
) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for the mean.

    Args:
        data: 1-D array of observations (e.g., cumulative rewards across seeds).
        n_bootstrap: Number of bootstrap resamples.
        ci: Confidence level (default 0.95 for 95% CI).
        rng_seed: Seed for reproducible bootstrap sampling.

    Returns:
        (lower_bound, upper_bound) of the percentile bootstrap CI.
    """
    rng = np.random.default_rng(rng_seed)
    boots = rng.choice(data, size=(n_bootstrap, len(data)), replace=True)
    means = boots.mean(axis=1)
    lower = float(np.percentile(means, (1 - ci) / 2 * 100))
    upper = float(np.percentile(means, (1 + ci) / 2 * 100))
    return lower, upper


def bootstrap_ci_paired_diff(
    baseline: np.ndarray,
    treatment: np.ndarray,
    n_bootstrap: int = 10000,
    ci: float = 0.95,
    rng_seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap CI for the mean paired difference (treatment - baseline).

    Args:
        baseline: 1-D array of baseline observations.
        treatment: 1-D array of treatment observations (same length as baseline).
        n_bootstrap: Number of bootstrap resamples.
        ci: Confidence level.
        rng_seed: Seed for reproducibility.

    Returns:
        (lower_bound, upper_bound) for the mean difference.
    """
    diff = treatment - baseline
    return bootstrap_ci(diff, n_bootstrap=n_bootstrap, ci=ci, rng_seed=rng_seed)


def paired_wilcoxon(
    baseline: np.ndarray,
    treatment: np.ndarray,
    alternative: str = "two-sided",
) -> tuple[float, float]:
    """Paired Wilcoxon signed-rank test for algorithm comparison.

    This is the non-parametric analogue of the paired t-test. It is appropriate
    for regret distributions which are typically non-normal and right-skewed.

    Args:
        baseline: Baseline metric values (e.g., StaticXGB cumulative regrets).
        treatment: Treatment metric values (e.g., LinUCB cumulative regrets).
        alternative: 'two-sided', 'less' (treatment < baseline), or 'greater'.

    Returns:
        (statistic, p_value)
    """
    baseline = np.asarray(baseline)
    treatment = np.asarray(treatment)
    assert len(baseline) == len(treatment), (
        f"Arrays must be same length (paired by seed): "
        f"{len(baseline)} vs {len(treatment)}"
    )
    stat, p = stats.wilcoxon(treatment, baseline, alternative=alternative)
    return float(stat), float(p)


def cohens_d_paired(
    baseline: np.ndarray,
    treatment: np.ndarray,
) -> float:
    """Cohen's d effect size for paired samples.

    Uses the standard deviation of the differences (not pooled SD).
    Interpretation: |d| < 0.2 = negligible, 0.2–0.5 = small,
    0.5–0.8 = medium, > 0.8 = large.

    Args:
        baseline: Baseline metric values.
        treatment: Treatment metric values.

    Returns:
        Cohen's d (signed: positive means treatment > baseline).
    """
    diff = np.asarray(treatment) - np.asarray(baseline)
    if diff.std(ddof=1) == 0:
        return float("inf") if diff.mean() != 0 else 0.0
    return float(diff.mean() / diff.std(ddof=1))


def cliffs_delta(
    baseline: np.ndarray,
    treatment: np.ndarray,
) -> float:
    """Cliff's delta — a non-parametric effect size.

    Measures the probability that a randomly chosen treatment observation
    is larger than a randomly chosen baseline observation, minus the reverse.

    Interpretation: |delta| < 0.147 = negligible, 0.147–0.33 = small,
    0.33–0.474 = medium, > 0.474 = large (Romano et al. 2006).

    Args:
        baseline: Baseline metric values.
        treatment: Treatment metric values.

    Returns:
        Cliff's delta in [-1, 1].
    """
    x = np.asarray(baseline)
    y = np.asarray(treatment)
    comparisons = np.sum(y[:, None] > x[None, :]) - np.sum(y[:, None] < x[None, :])
    return float(comparisons / (len(x) * len(y)))


def permutation_test_paired(
    baseline: np.ndarray,
    treatment: np.ndarray,
    n_permutations: int = 10000,
    alternative: str = "two-sided",
    rng_seed: int = 42,
) -> tuple[float, float]:
    """Permutation test for paired differences.

    Appropriate when the independence assumption of parametric tests is
    violated (e.g., repeated observations from a finite pool).

    Args:
        baseline: Baseline metric values.
        treatment: Treatment metric values.
        n_permutations: Number of random sign flips.
        alternative: 'two-sided', 'less', or 'greater'.
        rng_seed: Seed for reproducibility.

    Returns:
        (observed_difference, p_value)
    """
    rng = np.random.default_rng(rng_seed)
    diff = np.asarray(treatment) - np.asarray(baseline)
    observed = float(diff.mean())
    n = len(diff)

    perm_diffs = np.zeros(n_permutations)
    for i in range(n_permutations):
        signs = rng.choice([-1, 1], size=n)
        perm_diffs[i] = (diff * signs).mean()

    if alternative == "two-sided":
        p = np.mean(np.abs(perm_diffs) >= np.abs(observed))
    elif alternative == "less":
        p = np.mean(perm_diffs <= observed)
    elif alternative == "greater":
        p = np.mean(perm_diffs >= observed)
    else:
        raise ValueError(f"Unknown alternative: {alternative}")

    return observed, float(p)


def format_comparison(
    baseline_vals: np.ndarray,
    treatment_vals: np.ndarray,
    metric_name: str = "Metric",
    baseline_name: str = "Baseline",
    treatment_name: str = "Treatment",
    alternative: str = "two-sided",
) -> dict:
    """Full statistical comparison report for paired multi-seed experiments.

    Returns a dictionary with mean, std, bootstrap CI, Wilcoxon test,
    Cohen's d, Cliff's delta, and permutation test. Suitable for direct
    inclusion in thesis tables or experiment output logs.

    Args:
        baseline_vals: Baseline metric values across seeds.
        treatment_vals: Treatment metric values across seeds.
        metric_name: Human-readable metric name.
        baseline_name: Name of baseline algorithm.
        treatment_name: Name of treatment algorithm.
        alternative: Hypothesis direction for Wilcoxon test.

    Returns:
        Dictionary with keys:
            metric, baseline_name, treatment_name,
            baseline_mean, baseline_std, baseline_ci_95,
            treatment_mean, treatment_std, treatment_ci_95,
            mean_diff, diff_ci_95,
            wilcoxon_stat, wilcoxon_p, wilcoxon_significant,
            cohens_d, effect_size_interpretation,
            cliffs_delta, permutation_p, permutation_significant.
    """
    baseline_vals = np.asarray(baseline_vals)
    treatment_vals = np.asarray(treatment_vals)

    mean_diff = float(treatment_vals.mean() - baseline_vals.mean())
    diff_ci_lower, diff_ci_upper = bootstrap_ci_paired_diff(baseline_vals, treatment_vals)
    w_stat, w_p = paired_wilcoxon(baseline_vals, treatment_vals, alternative=alternative)
    d = cohens_d_paired(baseline_vals, treatment_vals)
    cd = cliffs_delta(baseline_vals, treatment_vals)
    perm_obs, perm_p = permutation_test_paired(baseline_vals, treatment_vals)

    # Effect size interpretation (Cohen's d)
    abs_d = abs(d)
    if abs_d > 0.8:
        effect_label = "large"
    elif abs_d > 0.5:
        effect_label = "medium"
    elif abs_d > 0.2:
        effect_label = "small"
    else:
        effect_label = "negligible"

    # Individual CIs
    b_ci = bootstrap_ci(baseline_vals)
    t_ci = bootstrap_ci(treatment_vals)

    return {
        "metric": metric_name,
        "baseline_name": baseline_name,
        "treatment_name": treatment_name,
        "baseline_mean": float(baseline_vals.mean()),
        "baseline_std": float(baseline_vals.std(ddof=1)),
        "baseline_ci_95": [float(b_ci[0]), float(b_ci[1])],
        "treatment_mean": float(treatment_vals.mean()),
        "treatment_std": float(treatment_vals.std(ddof=1)),
        "treatment_ci_95": [float(t_ci[0]), float(t_ci[1])],
        "mean_diff": mean_diff,
        "diff_ci_95": [float(diff_ci_lower), float(diff_ci_upper)],
        "wilcoxon_stat": float(w_stat),
        "wilcoxon_p": float(w_p),
        "wilcoxon_significant": w_p < 0.05,
        "cohens_d": float(d),
        "effect_size_interpretation": effect_label,
        "cliffs_delta": float(cd),
        "permutation_p": float(perm_p),
        "permutation_significant": perm_p < 0.05,
    }


def print_comparison_table(comparisons: list[dict]) -> None:
    """Pretty-print a list of comparison dictionaries as an aligned table."""
    print("\n" + "=" * 100)
    print("STATISTICAL COMPARISON REPORT")
    print("=" * 100)
    print(
        f"{'Comparison':<35} {'Mean Diff':>14} {'95% CI':>24} "
        f"{'p (Wilcoxon)':>14} {'Cohens d':>12} {'Effect':>10}"
    )
    print("-" * 100)
    for c in comparisons:
        label = f"{c['treatment_name']} vs {c['baseline_name']} ({c['metric']})"
        ci = f"[{c['diff_ci_95'][0]:+,.0f}, {c['diff_ci_95'][1]:+,.0f}]"
        sig = "***" if c["wilcoxon_p"] < 0.001 else "**" if c["wilcoxon_p"] < 0.01 else "*" if c["wilcoxon_p"] < 0.05 else "ns"
        print(
            f"{label:<35} {c['mean_diff']:>+14,.2f} {ci:>24} "
            f"{c['wilcoxon_p']:>12.4f} {sig:>2} {c['cohens_d']:>10.2f} {c['effect_size_interpretation']:>10}"
        )
    print("=" * 100)
    print("Significance: *** p<0.001, ** p<0.01, * p<0.05, ns = not significant")


def power_analysis_ttest(
    effect_size: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Required sample size (seeds) for a two-sample t-test.

    Uses the standard formula for sample size per group.

    Args:
        effect_size: Cohen's d (expected effect size).
        alpha: Significance level.
        power: Desired statistical power (1 - beta).

    Returns:
        Minimum number of seeds needed per group.
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    return int(np.ceil(n))
