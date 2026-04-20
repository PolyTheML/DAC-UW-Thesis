"""
Stress-testing harness: run scenarios and validate PSI alert behavior.

Core workflow:
1. Generate applicants via SyntheticApplicantGenerator
2. Extract mortality_ratio values
3. Compute PSI against reference distribution
4. Determine alert level (GREEN / AMBER / RED)
5. Validate against expected PSI band
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from analytics.monitor import calculate_psi, REFERENCE_DISTRIBUTION
from stress_testing.scenarios import DistortionScenario
from stress_testing.generator import SyntheticApplicantGenerator


# ============================================================================
# PSI ALERT THRESHOLDS (Industry Standard)
# ============================================================================

PSI_THRESHOLD_AMBER = 0.10
PSI_THRESHOLD_RED = 0.25


@dataclass
class ScenarioResult:
    """
    Outcome of a single stress-test scenario.

    Captures PSI computation, alert level determination, and bin histogram
    for diagnosis and thesis figures.
    """

    scenario_name: str
    n_applicants: int
    distortion_fraction: float
    psi: float
    alert_level: str  # "GREEN" / "AMBER" / "RED"
    psi_band_met: bool  # Whether PSI falls within expected_psi_band
    actual_bin_proportions: list[float]  # Actual counts per bin
    reference_bin_proportions: list[float]  # Reference expected
    mortality_ratio_values: list[float]  # Raw MR values (for plotting)


class StressTestHarness:
    """
    Harness for running stress-test scenarios and validating PSI behavior.
    """

    def __init__(self, use_empirical_baseline: bool = True):
        """Initialize with generator and reference distribution.

        Args:
            use_empirical_baseline: If True, compute baseline from a generated batch.
                If False, use the hardcoded REFERENCE_DISTRIBUTION.
        """
        self.generator = SyntheticApplicantGenerator()
        self.use_empirical_baseline = use_empirical_baseline
        self._empirical_baseline = None

        if use_empirical_baseline:
            # Generate empirical baseline for more realistic comparison
            print("Generating empirical baseline distribution...")
            from stress_testing.scenarios import BASELINE
            baseline_apps = self.generator.generate(BASELINE, seed=42)
            baseline_mrs = [app["mortality_ratio"] for app in baseline_apps]

            # Compute empirical distribution
            bins = [0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, float("inf")]
            bin_indices = np.digitize(baseline_mrs, bins[1:])
            counts = np.bincount(bin_indices, minlength=8)[:8]
            proportions = counts.astype(float) / len(baseline_mrs)

            self._empirical_baseline = {
                "bins": bins,
                "proportions": list(proportions),
            }
            self.reference_distribution = self._empirical_baseline
        else:
            self.reference_distribution = REFERENCE_DISTRIBUTION["mortality_ratio"]

    def run_scenario(
        self,
        scenario: DistortionScenario,
        verbose: bool = True,
    ) -> ScenarioResult:
        """
        Run a single stress-test scenario.

        Args:
            scenario: DistortionScenario to execute
            verbose: Print debug info during execution

        Returns:
            ScenarioResult with PSI, alert level, and histogram data
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"Scenario: {scenario.name}")
            print(f"{'='*70}")
            print(f"Description: {scenario.description}")
            print(f"N applicants: {scenario.n_applicants}")
            print(f"Distortion fraction: {scenario.distortion_fraction:.1%}")

        # Generate applicants
        applicants = self.generator.generate(scenario)

        # Extract mortality_ratio values
        mortality_ratio_values = [app["mortality_ratio"] for app in applicants]

        if verbose:
            print(f"Generated {len(applicants)} applicants")
            print(f"MR range: [{min(mortality_ratio_values):.3f}, {max(mortality_ratio_values):.3f}]")
            print(f"MR mean: {np.mean(mortality_ratio_values):.3f}")

        # Compute PSI
        psi = calculate_psi(
            self.reference_distribution,
            mortality_ratio_values,
            n_bins=8,
            epsilon=1e-6,
        )

        if verbose:
            print(f"\nPSI = {psi:.6f}")

        # Determine alert level
        if psi < PSI_THRESHOLD_AMBER:
            alert_level = "GREEN"
        elif psi < PSI_THRESHOLD_RED:
            alert_level = "AMBER"
        else:
            alert_level = "RED"

        if verbose:
            symbol = "✅" if alert_level == "GREEN" else ("⚠️" if alert_level == "AMBER" else "🚨")
            print(f"Alert level: {alert_level} {symbol}")

        # Check if PSI falls within expected band
        expected_min, expected_max = scenario.expected_psi_band
        psi_band_met = expected_min <= psi <= expected_max

        if verbose:
            expected_str = f"[{expected_min:.3f}, {expected_max:.3f}]"
            status = "✓" if psi_band_met else "✗"
            print(f"Expected PSI band: {expected_str} {status}")

        # Compute actual bin proportions for diagnosis
        bins = self.reference_distribution["bins"]
        bin_indices = np.digitize(mortality_ratio_values, bins[1:])
        counts = np.bincount(bin_indices, minlength=8)[:8]
        actual_proportions = counts.astype(float) / len(mortality_ratio_values)

        if verbose:
            print(f"\nBin histogram (actual vs reference):")
            for i, (bin_min, bin_max) in enumerate(
                zip(bins[:-1], bins[1:])
            ):
                ref_pct = self.reference_distribution["proportions"][i]
                actual_pct = actual_proportions[i]
                bar_len = int(actual_pct * 50)
                bar = "█" * bar_len
                print(
                    f"  [{bin_min:>4.1f}, {bin_max:>4.1f}): "
                    f"{actual_pct:.1%} ({bar}), ref={ref_pct:.1%}"
                )

        return ScenarioResult(
            scenario_name=scenario.name,
            n_applicants=scenario.n_applicants,
            distortion_fraction=scenario.distortion_fraction,
            psi=psi,
            alert_level=alert_level,
            psi_band_met=psi_band_met,
            actual_bin_proportions=list(actual_proportions),
            reference_bin_proportions=list(self.reference_distribution["proportions"]),
            mortality_ratio_values=mortality_ratio_values,
        )

    def run_scenario_batch(
        self,
        scenarios: list[DistortionScenario],
        verbose: bool = True,
    ) -> list[ScenarioResult]:
        """
        Run multiple scenarios and return results.

        Args:
            scenarios: List of DistortionScenario objects
            verbose: Print debug info

        Returns:
            List of ScenarioResult objects
        """
        results = []
        for scenario in scenarios:
            result = self.run_scenario(scenario, verbose=verbose)
            results.append(result)
        return results


# ============================================================================
# DIAGNOSTIC UTILITIES
# ============================================================================

def summarize_results(results: list[ScenarioResult]) -> None:
    """Print a summary table of all scenario results."""
    print(f"\n{'='*100}")
    print("SCENARIO SUMMARY")
    print(f"{'='*100}")
    print(
        f"{'Scenario':<20} {'n':<8} {'Distortion':<12} {'PSI':<10} {'Alert':<10} {'Band OK?':<10}"
    )
    print("-" * 100)
    for result in results:
        band_ok = "✓" if result.psi_band_met else "✗"
        print(
            f"{result.scenario_name:<20} "
            f"{result.n_applicants:<8} "
            f"{result.distortion_fraction:>10.0%}  "
            f"{result.psi:>9.4f} "
            f"{result.alert_level:<10} "
            f"{band_ok:<10}"
        )
    print(f"{'='*100}")
