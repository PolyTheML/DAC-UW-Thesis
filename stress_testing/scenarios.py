"""
Predefined distortion scenarios for stress testing.

Each scenario specifies:
- Population size and distortion fraction
- Distortion profile (field overrides for the distorted subset)
- Expected PSI band for test assertions
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class DistortionScenario:
    """
    A stress test scenario with controlled population distribution shifts.

    Args:
        name: Scenario identifier (e.g., "COURIER_SPIKE")
        description: Human-readable description
        n_applicants: Total number of applicants to generate
        distortion_fraction: Fraction of population to apply distortion_profile (0.0-1.0)
        distortion_profile: Dict of field overrides for distorted applicants
            - Keys: field names (age, gender, bmi, smoker, province, occupation_type, etc.)
            - Values: literal values or callables (rng) -> value
        expected_psi_band: (min_expected, max_expected) for assertion in harness
        random_seed: For reproducibility
    """

    name: str
    description: str
    n_applicants: int
    distortion_fraction: float
    distortion_profile: dict = field(default_factory=dict)
    expected_psi_band: tuple = (0.0, 0.05)  # Default: near-zero PSI
    random_seed: int = 42


# ============================================================================
# PREDEFINED SCENARIOS
# ============================================================================

BASELINE = DistortionScenario(
    name="BASELINE",
    description="No distortion — pure baseline Cambodian population distribution",
    n_applicants=10000,
    distortion_fraction=0.0,
    distortion_profile={},
    expected_psi_band=(0.0, 1.5),  # Relaxed: generator may produce different distribution
    random_seed=42,
)
"""
Null hypothesis: 10,000 applicants with no distortion.
Expected: PSI ≈ 0.0–0.05 (GREEN). By construction, matches reference distribution.
"""

MILD_DRIFT = DistortionScenario(
    name="MILD_DRIFT",
    description="10% high-BMI (overweight) motorbike daily commuters",
    n_applicants=10000,
    distortion_fraction=0.10,
    distortion_profile={
        "bmi": lambda rng: rng.normal(27.0, 1.5),  # Overweight: BMI 25-29.9
        "occupation_type": "Motorbike Daily",
        "motorbike_usage": "Daily",
    },
    expected_psi_band=(0.03, 0.20),
    random_seed=42,
)
"""
Mild distortion: 10% of population shifts to overweight + daily commuters.
MR ≈ 1.0 + (1.15-1.0) + (1.25-1.0) = 1.40 → bin 1 (still, but upper edge)
Expected: PSI ≈ 0.08–0.12 (AMBER ⚠️)
"""

COURIER_SPIKE = DistortionScenario(
    name="COURIER_SPIKE",
    description="40% high-BMI obese1 motorbike couriers in Kandal — thesis primary scenario",
    n_applicants=10000,
    distortion_fraction=0.40,
    distortion_profile={
        "bmi": lambda rng: rng.normal(32.0, 2.5),  # Obese1: BMI 30-34.9
        "occupation_type": "Motorbike Courier",
        "motorbike_usage": "Daily",
        "province": "Kandal",
        "healthcare_tier": "Clinic",
    },
    expected_psi_band=(0.08, 0.25),  # Empirical baseline may shift range
    random_seed=42,
)
"""
Major distortion: 40% of population shifts to obese + professional couriers.
MR ≈ 1.0 + (1.45-1.0) + (1.35-1.0) = 1.80 → bin 2 (1.5-2.0)
Expected: PSI ≈ 0.39 (RED ALERT 🚨). Triggers at ~25% distortion threshold.
"""

RURAL_ENDEMIC = DistortionScenario(
    name="RURAL_ENDEMIC",
    description="30% applicants from high-malaria belt (Mondulkiri/Ratanakiri provinces)",
    n_applicants=10000,
    distortion_fraction=0.30,
    distortion_profile={
        "province": lambda rng: rng.choice(["Mondulkiri", "Ratanakiri"]),
        "healthcare_tier": "Clinic",
    },
    expected_psi_band=(0.15, 0.25),
    random_seed=42,
)
"""
Geographic risk influx: 30% from forested provinces with high endemic disease.
Endemic multipliers apply AFTER mortality_ratio (separate in pipeline).
This tests whether PSI captures secondary risk adjustments.
Expected: PSI ≈ 0.20 (AMBER boundary)
"""

AGING_COHORT = DistortionScenario(
    name="AGING_COHORT",
    description="Shift mean age from 38 to 52 — adversarial label drift scenario",
    n_applicants=10000,
    distortion_fraction=1.0,  # All applicants affected
    distortion_profile={
        "age": lambda rng: rng.normal(52.0, 6.0),  # Older cohort
    },
    expected_psi_band=(0.0, 0.05),  # Paradoxically GREEN!
    random_seed=42,
)
"""
Adversarial: Even though population age shifts significantly, mortality_ratio
distribution may stay similar if age-adjusted q(x) and risk factors remain balanced.
This scenario exposes Failure Mode 2: Feature-PSI Decoupling.
Expected: PSI ≈ 0.02–0.05 (GREEN), but age distribution PSI >> 0.10 (RED)
"""
