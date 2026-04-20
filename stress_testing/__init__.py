"""
Stress-Testing Harness for AI Underwriting Framework Robustness Analysis.

Validates PSI (Population Stability Index) monitoring and identifies failure modes
where concept drift evades single-metric drift detection.

Modules:
- scenarios: Predefined distortion scenarios (BASELINE, COURIER_SPIKE, etc.)
- generator: SyntheticApplicantGenerator — 10,000 synthetic Cambodian applicants
- harness: StressTestHarness — run scenarios, compute PSI, validate alerts
- adversarial: FailureModeDetector — 3 classes of silent concept drift
"""
