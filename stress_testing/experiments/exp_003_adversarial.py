"""
Experiment 003: Adversarial Failure Mode Detection

Hypothesis: While PSI-only monitoring gives false negatives in three
specific failure modes, supplementary metrics can catch them.

This validates the thesis argument: Single-metric PSI is insufficient.
Recommendation: Multi-metric drift detection.

Failure Modes:
1. Label Drift — Comorbidity confounding: MR stays similar, but input feature distribution changes
2. Feature-PSI Decoupling — Age cohort shift: New young healthy cohort enters with MR ≈ 1.0
3. Bin Edge Camouflage — Boundary classification: Applicants shift across tier boundaries

Expected: All 3 should show PSI=GREEN (false negative) but secondary metrics=RED (caught).
"""

from stress_testing.adversarial import FailureModeDetector


def main():
    """Run adversarial failure mode detection experiment."""
    print("\n" + "=" * 100)
    print("EXP-003: Adversarial Failure Mode Detection")
    print("=" * 100)
    print("Hypothesis: PSI-only monitoring misses 3 failure modes")
    print("Expected: All 3 modes show PSI=GREEN but secondary metrics alarm")

    detector = FailureModeDetector()
    results = detector.run_all_adversarial_tests(verbose=True)

    # Validate results
    print("\n" + "=" * 100)
    print("ADVERSARIAL SUMMARY")
    print("=" * 100)

    caught_count = 0
    for result in results:
        mode_name = {
            "1": "Label Drift (Comorbidity)",
            "2": "Feature-PSI Decoupling (Age)",
            "3": "Bin Edge Camouflage (Tier Boundary)",
        }[result.failure_mode]

        print(f"\nFailure Mode {result.failure_mode}: {mode_name}")
        print(f"  MR PSI (primary):        {result.mr_psi:.4f} (GREEN ✓ — false negative)")
        print(f"  Secondary metric ({result.secondary_metric}): {result.secondary_psi:.4f}")
        print(f"  Detection status:        {result.status}")

        if result.status == "CAUGHT":
            print(f"  ✓ CAUGHT by secondary metric")
            caught_count += 1
        else:
            print(f"  ✗ MISSED — secondary change too small")

    print(f"\n{'='*100}")
    print(f"Caught {caught_count}/3 failure modes with secondary metrics")
    print(f"{'='*100}")

    if caught_count >= 2:
        print("\n✅ EXPERIMENT PASSED: Multi-metric monitoring can catch silent drift")
        print("   Recommendation: Supplement PSI with:")
        print("   - Feature co-occurrence PSI (label drift detection)")
        print("   - Marginal feature PSI on age (cohort shift detection)")
        print("   - Risk tier escalation rate monitoring (boundary instability)")
    else:
        print("\n⚠️ EXPERIMENT WARNING: Secondary metrics not sensitive enough")
        print("   Consider refining detection thresholds or adding more metrics")


if __name__ == "__main__":
    main()
