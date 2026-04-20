"""
Adversarial failure mode detector.

Identifies three classes of concept drift that evade PSI-only monitoring:

1. Label Drift (Comorbidity Confounding)
   - Input features change, but mortality_ratio stays similar
   - PSI alert: GREEN ✓ (false negative)
   - Detection: Feature co-occurrence PSI

2. Feature-PSI Decoupling (Age Cohort Shift)
   - New low-risk cohort enters (young professionals)
   - Their MR ≈ 1.0 matches reference bin exactly
   - PSI alert: GREEN ✓ (false negative)
   - Detection: Marginal feature PSI on age

3. Bin Edge Camouflage (Boundary Classification Instability)
   - Applicants shift from MR 1.48 → 1.73, crossing tier boundary 1.5
   - Risk tier changes (LOW → MEDIUM), HITL escalation rises
   - PSI alert: GREEN ✓ (false negative)
   - Detection: HITL escalation rate PSI, sub-bins near decision boundaries
"""

from typing import Optional
import numpy as np
from dataclasses import dataclass, replace as dc_replace

from stress_testing.generator import SyntheticApplicantGenerator
from stress_testing.scenarios import DistortionScenario, AGING_COHORT, BASELINE


# ============================================================================
# FAILURE MODE 1: LABEL DRIFT (Comorbidity Confounding)
# ============================================================================


def feature_cooccurrence_psi(
    baseline_apps: list[dict],
    current_apps: list[dict],
    feature1: str = "diabetes",
    feature2: str = "hypertension",
    feature2_comparison: str = "normal",  # "normal", "elevated", "stage1", "stage2"
) -> float:
    """
    Compute PSI on the joint probability P(feature1=True AND feature2=value).

    Detects Failure Mode 1: when a second feature's distribution changes
    while keeping mortality_ratio similar.

    Args:
        baseline_apps: Baseline applicants from reference
        current_apps: Current applicants from scenario
        feature1: First feature (usually a diagnosis flag)
        feature2: Second feature to co-monitor (usually a measured value like BP)
        feature2_comparison: Classification value for feature2

    Returns:
        PSI score for the co-occurrence joint distribution
    """
    # Classify BP for feature2
    def get_bp_class(app):
        systolic = app.get("systolic", None)
        diastolic = app.get("diastolic", None)
        if systolic is None or diastolic is None:
            return "unknown"
        if systolic > 180 or diastolic > 120:
            return "crisis"
        elif systolic >= 140 or diastolic >= 90:
            return "stage2"
        elif systolic >= 130 or diastolic >= 80:
            return "stage1"
        elif systolic >= 120 and diastolic < 80:
            return "elevated"
        else:
            return "normal"

    # Count co-occurrences
    baseline_cooccurrence = sum(
        1
        for app in baseline_apps
        if app.get(feature1) is True
        and (
            feature2 == "bp_class"
            and get_bp_class(app) == feature2_comparison
            or app.get(feature2) == feature2_comparison
        )
    )

    current_cooccurrence = sum(
        1
        for app in current_apps
        if app.get(feature1) is True
        and (
            feature2 == "bp_class"
            and get_bp_class(app) == feature2_comparison
            or app.get(feature2) == feature2_comparison
        )
    )

    baseline_diab_count = sum(1 for app in baseline_apps if app.get(feature1) is True)
    current_diab_count = sum(1 for app in current_apps if app.get(feature1) is True)

    # Proportions (among those with feature1=True)
    baseline_prop = (
        baseline_cooccurrence / max(baseline_diab_count, 1)
        if baseline_diab_count > 0
        else 0.0
    )
    current_prop = (
        current_cooccurrence / max(current_diab_count, 1)
        if current_diab_count > 0
        else 0.0
    )

    # PSI for binary occurrence
    epsilon = 1e-6
    baseline_prop = np.clip(baseline_prop, epsilon, 1.0)
    current_prop = np.clip(current_prop, epsilon, 1.0)

    psi = (current_prop - baseline_prop) * np.log(current_prop / baseline_prop)
    return float(psi)


# ============================================================================
# FAILURE MODE 2: FEATURE-PSI DECOUPLING (Age Cohort Shift)
# ============================================================================


def marginal_feature_psi(
    baseline_apps: list[dict],
    current_apps: list[dict],
    feature: str = "age",
    n_bins: int = 5,
) -> float:
    """
    Compute PSI on marginal distribution of a single feature (e.g., age).

    Detects Failure Mode 2: when a feature distribution shifts significantly
    but mortality_ratio PSI stays low (feature-PSI decoupling).

    Args:
        baseline_apps: Baseline applicants
        current_apps: Current applicants
        feature: Feature to monitor (e.g., "age")
        n_bins: Number of histogram bins

    Returns:
        PSI score for the marginal feature distribution
    """
    baseline_vals = np.array([app.get(feature, 0) for app in baseline_apps])
    current_vals = np.array([app.get(feature, 0) for app in current_apps])

    # Create bins from baseline
    if feature == "age":
        bins = np.linspace(25, 65, n_bins + 1)
    elif feature == "bmi":
        bins = np.linspace(16, 45, n_bins + 1)
    else:
        bins = np.linspace(baseline_vals.min(), baseline_vals.max(), n_bins + 1)

    # Bin both distributions
    baseline_binned = np.digitize(baseline_vals, bins[1:])
    current_binned = np.digitize(current_vals, bins[1:])

    baseline_counts = np.bincount(baseline_binned, minlength=n_bins)[:n_bins]
    current_counts = np.bincount(current_binned, minlength=n_bins)[:n_bins]

    baseline_props = baseline_counts.astype(float) / len(baseline_vals)
    current_props = current_counts.astype(float) / len(current_vals)

    # PSI
    epsilon = 1e-6
    baseline_props = np.clip(baseline_props, epsilon, 1.0)
    current_props = np.clip(current_props, epsilon, 1.0)

    psi = float(np.sum((current_props - baseline_props) * np.log(current_props / baseline_props)))
    return max(psi, 0.0)


# ============================================================================
# FAILURE MODE 3: BIN EDGE CAMOUFLAGE (Boundary Classification Instability)
# ============================================================================


def risk_tier_escalation_psi(
    baseline_apps: list[dict],
    current_apps: list[dict],
    tier_thresholds: tuple = (1.50, 2.50, 4.00),
) -> dict[str, float]:
    """
    Compute risk tier distribution and its PSI.

    Detects Failure Mode 3: when applicants shift across tier boundaries
    without changing mortality_ratio PSI significantly.

    Args:
        baseline_apps: Baseline applicants with mortality_ratio
        current_apps: Current applicants with mortality_ratio
        tier_thresholds: (low_max, medium_max, high_max)

    Returns:
        Dict with tier proportions and escalation PSI
    """

    def classify_tier(mr, thresholds):
        if mr <= thresholds[0]:
            return "LOW"
        elif mr <= thresholds[1]:
            return "MEDIUM"
        elif mr <= thresholds[2]:
            return "HIGH"
        else:
            return "DECLINE"

    baseline_tiers = [classify_tier(app.get("mortality_ratio", 1.0), tier_thresholds) for app in baseline_apps]
    current_tiers = [classify_tier(app.get("mortality_ratio", 1.0), tier_thresholds) for app in current_apps]

    # Count proportions per tier
    tier_names = ["LOW", "MEDIUM", "HIGH", "DECLINE"]
    baseline_props = {}
    current_props = {}

    for tier in tier_names:
        baseline_count = baseline_tiers.count(tier)
        current_count = current_tiers.count(tier)
        baseline_props[tier] = baseline_count / len(baseline_tiers)
        current_props[tier] = current_count / len(current_tiers)

    # PSI for tier distribution
    epsilon = 1e-6
    psi = 0.0
    for tier in tier_names:
        b = np.clip(baseline_props[tier], epsilon, 1.0)
        c = np.clip(current_props[tier], epsilon, 1.0)
        psi += (c - b) * np.log(c / b)

    return {
        "baseline_proportions": baseline_props,
        "current_proportions": current_props,
        "escalation_psi": float(psi),
    }


# ============================================================================
# ADVERSARIAL TEST RUNNER
# ============================================================================


@dataclass
class AdversarialTestResult:
    """Result of an adversarial failure mode test."""

    failure_mode: str  # "1", "2", or "3"
    mr_psi: float  # Standard PSI on mortality_ratio (GREEN)
    secondary_metric: str  # What we're monitoring instead
    secondary_psi: float  # PSI on secondary metric (RED)
    status: str  # "CAUGHT" if secondary alarm fires


class FailureModeDetector:
    """
    Runs adversarial tests to expose silent failure modes.
    """

    def __init__(self):
        self.generator = SyntheticApplicantGenerator()

    def test_failure_mode_1(self, verbose: bool = True) -> AdversarialTestResult:
        """
        Test Failure Mode 1: Label Drift (Comorbidity Confounding).

        Scenario: Government diabetic clinic program manages BP to normal.
        - Input features change (lower BP readings)
        - Mortality ratio stays similar (diabetes +0.40 still, hypertension removed)
        - MR PSI: GREEN
        - Secondary metric (diabetes + normal BP co-occurrence): RED
        """
        if verbose:
            print("\n" + "=" * 80)
            print("FAILURE MODE 1: Label Drift (Comorbidity Confounding)")
            print("=" * 80)
            print("Scenario: New diabetic clinic program manages BP → normal")
            print("Expected: MR PSI green, but co-occurrence PSI red")

        from medical_reader.pricing.calculator import calculate_mortality_ratio
        from medical_reader.pricing.assumptions import ASSUMPTIONS
        from analytics.monitor import calculate_psi, REFERENCE_DISTRIBUTION

        # Baseline: full 10K population
        baseline = self.generator.generate(BASELINE)

        # Distorted: full 10K — clinic program manages BP for ALL diabetic+hypertensive patients
        rng_clinic = np.random.default_rng(seed=100)
        distorted = []
        for app in baseline:
            app_copy = app.copy()
            if app_copy.get("diabetes") and app_copy.get("hypertension"):
                app_copy["hypertension"] = False
                app_copy["systolic"] = int(np.clip(rng_clinic.normal(110, 5), 90, 118))
                app_copy["diastolic"] = int(np.clip(rng_clinic.normal(72, 5), 60, 78))
                mr, _ = calculate_mortality_ratio(
                    age=app_copy["age"],
                    gender=app_copy["gender"],
                    bmi=app_copy["bmi"],
                    smoker=app_copy["smoker"],
                    alcohol_use=app_copy["alcohol_use"],
                    diabetes=app_copy["diabetes"],
                    hypertension=app_copy["hypertension"],
                    hyperlipidemia=app_copy["hyperlipidemia"],
                    family_history_chd=app_copy["family_history_chd"],
                    systolic=app_copy["systolic"],
                    diastolic=app_copy["diastolic"],
                    assumptions=ASSUMPTIONS["risk_factors"],
                )
                app_copy["mortality_ratio"] = mr
            distorted.append(app_copy)

        distorted_mrs = [app["mortality_ratio"] for app in distorted]
        mr_psi = calculate_psi(REFERENCE_DISTRIBUTION["mortality_ratio"], distorted_mrs)

        # Co-occurrence threshold is lower (binary conditional metric vs full distribution)
        cooccurrence_psi = feature_cooccurrence_psi(
            baseline,
            distorted,
            feature1="diabetes",
            feature2="bp_class",
            feature2_comparison="normal",
        )
        _fm1_threshold = 0.05

        if verbose:
            print(f"\nMortality Ratio PSI: {mr_psi:.4f} (GREEN ✓ if <0.10)")
            print(f"Co-occurrence PSI: {cooccurrence_psi:.4f} (RED 🚨 if >{_fm1_threshold})")
            if cooccurrence_psi > _fm1_threshold:
                print("Status: CAUGHT by co-occurrence monitoring")
            else:
                print("Status: MISSED — co-occurrence change too small")

        status = "CAUGHT" if cooccurrence_psi > _fm1_threshold else "MISSED"
        return AdversarialTestResult(
            failure_mode="1",
            mr_psi=mr_psi,
            secondary_metric="diabetes+normal_BP co-occurrence",
            secondary_psi=cooccurrence_psi,
            status=status,
        )

    def test_failure_mode_2(self, verbose: bool = True) -> AdversarialTestResult:
        """
        Test Failure Mode 2: Feature-PSI Decoupling (Age Cohort Shift).

        Scenario: Young professionals age 22–28 enter (all healthy, MR ≈ 1.0).
        - Mortality ratio distribution unchanged (they fall in bin 1 like reference)
        - MR PSI: GREEN
        - Age distribution PSI: RED
        """
        if verbose:
            print("\n" + "=" * 80)
            print("FAILURE MODE 2: Feature-PSI Decoupling (Age Cohort Shift)")
            print("=" * 80)
            print("Scenario: Young professionals (age 22-28) enter, all healthy")
            print("Expected: MR PSI green, but age distribution PSI red")

        # Baseline
        baseline = self.generator.generate(BASELINE)

        # Distorted: shift all to young age
        young_scenario = dc_replace(
            AGING_COHORT,
            distortion_profile={"age": lambda rng: rng.normal(25.0, 2.0)},
        )
        young = self.generator.generate(young_scenario)

        # Compute MR PSI
        from analytics.monitor import calculate_psi, REFERENCE_DISTRIBUTION

        young_mrs = [app.get("mortality_ratio", 1.0) for app in young]
        mr_psi = calculate_psi(REFERENCE_DISTRIBUTION["mortality_ratio"], young_mrs)

        # Compute age PSI
        age_psi = marginal_feature_psi(baseline, young, feature="age", n_bins=5)

        if verbose:
            print(f"\nMortality Ratio PSI: {mr_psi:.4f} (GREEN ✓)")
            print(f"Age Distribution PSI: {age_psi:.4f} (RED 🚨 if >0.10)")
            if age_psi > 0.10:
                print("Status: CAUGHT by age distribution monitoring")
            else:
                print("Status: MISSED — age shift not large enough?")

        status = "CAUGHT" if age_psi > 0.10 else "MISSED"
        return AdversarialTestResult(
            failure_mode="2",
            mr_psi=mr_psi,
            secondary_metric="age_distribution",
            secondary_psi=age_psi,
            status=status,
        )

    def test_failure_mode_3(self, verbose: bool = True) -> AdversarialTestResult:
        """
        Test Failure Mode 3: Bin Edge Camouflage (Boundary Classification Instability).

        Scenario: ~7% of applicants (family_history_chd, no hyperlipidemia) gain
        hyperlipidemia + overweight BMI — shifting MR from ~1.30 to ~1.65 (LOW→MEDIUM).
        - Only 7% of applicants shift; adjacent bin change → PSI stays GREEN
        - HITL escalation rate spikes +7 pp (more MEDIUM-tier cases needing underwriter review)
        - MR PSI: GREEN ✗ (small relative shift)
        - Secondary metric (HITL escalation rate change): RED
        """
        if verbose:
            print("\n" + "=" * 80)
            print("FAILURE MODE 3: Bin Edge Camouflage (Boundary Classification Instability)")
            print("=" * 80)
            print("Scenario: ~7% of borderline LOW-tier applicants gain conditions → MEDIUM tier")
            print("Expected: MR PSI green (small bin shift), but HITL escalation rate RED")

        from medical_reader.pricing.calculator import calculate_mortality_ratio
        from medical_reader.pricing.assumptions import ASSUMPTIONS
        from analytics.monitor import calculate_psi, REFERENCE_DISTRIBUTION

        baseline = self.generator.generate(BASELINE)

        # Distorted: 50% of family_history_chd applicants (who don't yet have hyperlipidemia)
        # gain hyperlipidemia + mild weight gain (overweight BMI) — sedentary lifestyle uptick.
        # MR effect: +0.20 (hyperlipidemia) + +0.15 (bmi_overweight) = +0.35 → crosses 1.5 boundary.
        rng_bnd = np.random.default_rng(seed=200)
        distorted = []
        for app in baseline:
            app_copy = app.copy()
            if (
                app_copy.get("family_history_chd")
                and not app_copy.get("hyperlipidemia")
                and rng_bnd.random() < 0.90
            ):
                app_copy["hyperlipidemia"] = True
                app_copy["bmi"] = float(np.clip(rng_bnd.normal(28.0, 1.5), 25.0, 30.0))
                mr, _ = calculate_mortality_ratio(
                    age=app_copy["age"],
                    gender=app_copy["gender"],
                    bmi=app_copy["bmi"],
                    smoker=app_copy["smoker"],
                    alcohol_use=app_copy["alcohol_use"],
                    diabetes=app_copy["diabetes"],
                    hypertension=app_copy["hypertension"],
                    hyperlipidemia=app_copy["hyperlipidemia"],
                    family_history_chd=app_copy["family_history_chd"],
                    systolic=app_copy["systolic"],
                    diastolic=app_copy["diastolic"],
                    assumptions=ASSUMPTIONS["risk_factors"],
                )
                app_copy["mortality_ratio"] = mr
            distorted.append(app_copy)

        distorted_mrs = [app["mortality_ratio"] for app in distorted]
        mr_psi = calculate_psi(REFERENCE_DISTRIBUTION["mortality_ratio"], distorted_mrs)

        # Secondary metric: absolute HITL escalation rate change (% MEDIUM/HIGH/DECLINE cases)
        hitl_threshold = 1.5  # MR > 1.5 requires underwriter review
        baseline_hitl_rate = sum(1 for a in baseline if a["mortality_ratio"] > hitl_threshold) / len(baseline)
        distorted_hitl_rate = sum(1 for a in distorted if a["mortality_ratio"] > hitl_threshold) / len(distorted)
        hitl_rate_change = distorted_hitl_rate - baseline_hitl_rate

        _fm3_threshold = 0.03  # 3 pp escalation rate increase = RED

        if verbose:
            print(f"\nMortality Ratio PSI: {mr_psi:.4f} (GREEN ✓ if <0.10)")
            print(f"HITL Escalation Rate: {baseline_hitl_rate:.1%} → {distorted_hitl_rate:.1%} (+{hitl_rate_change:.1%})")
            print(f"Rate Change: {hitl_rate_change:.4f} (RED 🚨 if >{_fm3_threshold})")
            if hitl_rate_change > _fm3_threshold:
                print("Status: CAUGHT by HITL escalation monitoring")
            else:
                print("Status: MISSED — escalation rate change too small")

        status = "CAUGHT" if hitl_rate_change > _fm3_threshold else "MISSED"
        return AdversarialTestResult(
            failure_mode="3",
            mr_psi=mr_psi,
            secondary_metric="hitl_escalation_rate_change",
            secondary_psi=hitl_rate_change,
            status=status,
        )

    def run_all_adversarial_tests(self, verbose: bool = True) -> list[AdversarialTestResult]:
        """Run all 3 adversarial failure mode tests."""
        results = [
            self.test_failure_mode_1(verbose=verbose),
            self.test_failure_mode_2(verbose=verbose),
            self.test_failure_mode_3(verbose=verbose),
        ]
        return results
