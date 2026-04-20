"""
Synthetic Cambodian applicant generator for stress testing.

Generates 10,000 applicants with authentic demographic distributions,
and supports controlled distortions for scenario testing.

Reuses patterns from portfolio/generator.py (Cambodia census parameters,
age-correlated risk factors) but scales to 10K and adds distortion modes.
"""

from typing import Optional
import numpy as np

from medical_reader.pricing.calculator import calculate_mortality_ratio
from medical_reader.pricing.assumptions import (
    ASSUMPTIONS,
    CambodiaOccupationalMultipliers,
    CambodiaEndemicMultipliers,
    CambodiaHealthcareTierDiscount,
)
from stress_testing.scenarios import DistortionScenario


# ============================================================================
# DEMOGRAPHIC PRIORS (from portfolio/generator.py)
# ============================================================================

CAMBODIA_MEDIAN_AGE = 38.0
CAMBODIA_AGE_STD = 8.0
CAMBODIA_MEDIAN_BMI = 23.5
CAMBODIA_BMI_STD = 3.5
MALE_FRACTION = 0.52
MALE_SMOKING_RATE = 0.30
FEMALE_SMOKING_RATE = 0.08


def _age_prob(age: float, condition_rate_at_25: float, condition_rate_at_55: float) -> float:
    """
    Linear interpolation of condition prevalence by age.
    Reused from portfolio/generator.py pattern.

    Args:
        age: Age in years
        condition_rate_at_25: Prevalence at age 25
        condition_rate_at_55: Prevalence at age 55

    Returns:
        Interpolated probability for the given age
    """
    if age <= 25:
        return condition_rate_at_25
    elif age >= 55:
        return condition_rate_at_55
    else:
        # Linear interpolation
        t = (age - 25) / (55 - 25)  # 0 to 1
        return condition_rate_at_25 + t * (condition_rate_at_55 - condition_rate_at_25)


class SyntheticApplicantGenerator:
    """
    Generates 10,000 synthetic Cambodian applicants with optional distortions.

    Replicates demographic and health characteristics from real Cambodia census data
    and actuarial assumptions, then computes authentic mortality_ratio values
    using the real pricing calculator.
    """

    def __init__(self):
        """Initialize with default assumptions."""
        self.assumptions = ASSUMPTIONS
        self.occupational_multipliers = CambodiaOccupationalMultipliers()
        self.endemic_multipliers = CambodiaEndemicMultipliers()
        self.healthcare_tier_discount = CambodiaHealthcareTierDiscount()

    def generate(
        self,
        scenario: DistortionScenario,
        seed: Optional[int] = None,
    ) -> list[dict]:
        """
        Generate synthetic applicants for the given scenario.

        Args:
            scenario: DistortionScenario with n_applicants, distortion_fraction, profile
            seed: Random seed for reproducibility (defaults to scenario.random_seed)

        Returns:
            List of dicts, each with:
            - Demographic: age, gender, province
            - Health: bmi, smoker, systolic, diastolic, alcohol_use,
                      diabetes, hypertension, hyperlipidemia, family_history_chd
            - Occupational: occupation_type, motorbike_usage
            - Medical facility: healthcare_tier
            - Computed: mortality_ratio (via calculate_mortality_ratio)
        """
        if seed is None:
            seed = scenario.random_seed

        rng = np.random.default_rng(seed=seed)

        n_applicants = scenario.n_applicants
        n_distorted = int(n_applicants * scenario.distortion_fraction)
        n_baseline = n_applicants - n_distorted

        # Generate baseline and distorted groups separately
        applicants = []

        # Baseline group
        for _ in range(n_baseline):
            app = self._generate_baseline_applicant(rng)
            applicants.append(app)

        # Distorted group
        for _ in range(n_distorted):
            app = self._generate_baseline_applicant(rng)
            # Apply distortion profile overrides
            for field_name, override in scenario.distortion_profile.items():
                if callable(override):
                    app[field_name] = override(rng)
                else:
                    app[field_name] = override
            applicants.append(app)

        # Compute mortality_ratio for each applicant (after distortions applied)
        for app in applicants:
            mr, _ = calculate_mortality_ratio(
                age=app["age"],
                gender=app["gender"],
                bmi=app["bmi"],
                smoker=app["smoker"],
                alcohol_use=app["alcohol_use"],
                diabetes=app["diabetes"],
                hypertension=app["hypertension"],
                hyperlipidemia=app["hyperlipidemia"],
                family_history_chd=app["family_history_chd"],
                systolic=app["systolic"],
                diastolic=app["diastolic"],
                assumptions=self.assumptions["risk_factors"],
            )
            app["mortality_ratio"] = mr

        return applicants

    def _generate_baseline_applicant(self, rng: np.random.Generator) -> dict:
        """
        Generate a single baseline Cambodian applicant.

        Returns dict with all required fields (demographics, health, occupational).
        """
        # Demographics
        age = int(np.clip(rng.normal(CAMBODIA_MEDIAN_AGE, CAMBODIA_AGE_STD), 25, 65))
        is_male = rng.random() < MALE_FRACTION
        gender = "M" if is_male else "F"

        # BMI
        bmi = float(np.clip(rng.normal(CAMBODIA_MEDIAN_BMI, CAMBODIA_BMI_STD), 16, 45))

        # Smoking (age-independent prevalence)
        smoking_rate = MALE_SMOKING_RATE if is_male else FEMALE_SMOKING_RATE
        smoker = rng.random() < smoking_rate

        # Blood pressure (baseline: normal or hypertensive)
        systolic = int(rng.normal(115, 10))  # Normal baseline
        diastolic = int(rng.normal(75, 8))

        # Age-correlated conditions
        diabetes = rng.random() < _age_prob(age, 0.04, 0.14)
        hypertension = rng.random() < _age_prob(age, 0.08, 0.35)
        hyperlipidemia = rng.random() < _age_prob(age, 0.10, 0.30)
        family_history_chd = rng.random() < 0.15  # Age-independent

        # If hypertensive, adjust systolic BP
        if hypertension:
            systolic = int(rng.normal(145, 12))
            diastolic = int(rng.normal(85, 10))

        # Alcohol use
        heavy_alcohol_rate = 0.12 if is_male else 0.02
        alcohol_use = "Heavy" if rng.random() < heavy_alcohol_rate else None

        # Occupational (default: office/low-risk)
        occupation_type = "Office/Desk"
        motorbike_usage = "Never"

        # Province (default: Phnom Penh / Kandal — urban)
        province = rng.choice(["Phnom Penh", "Kandal", "Siem Reap"])

        # Healthcare facility (default: TierB regional hospital)
        healthcare_tier = "TierB"

        return {
            "age": age,
            "gender": gender,
            "bmi": bmi,
            "smoker": smoker,
            "systolic": systolic,
            "diastolic": diastolic,
            "alcohol_use": alcohol_use,
            "diabetes": diabetes,
            "hypertension": hypertension,
            "hyperlipidemia": hyperlipidemia,
            "family_history_chd": family_history_chd,
            "occupation_type": occupation_type,
            "motorbike_usage": motorbike_usage,
            "province": province,
            "healthcare_tier": healthcare_tier,
        }
