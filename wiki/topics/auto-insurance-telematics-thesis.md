# Auto Insurance Telematics Thesis

**Created**: 2026-04-20  
**Last updated**: 2026-04-20  
**Status**: 🚀 Week 1 in progress — experiments ahead of schedule  
**Defense**: ~2026-06-26 (8 weeks from 2026-04-20)

---

## Thesis Title

*"Validating Population Stability Metrics for Dynamic Auto Insurance Pricing with Telematics Data"*

---

## Core Contribution

This thesis validates that PSI (Population Stability Index) — extended with secondary telematics metrics — can detect meaningful distribution drift in dynamic auto insurance pricing using real-route telematics data. The research demonstrates three classes of failure modes where PSI alone gives false negatives, and proposes a **multi-metric monitoring dashboard** as the production solution.

**What makes this different from the prior life insurance thesis**:
- **Life insurance**: Static batch underwriting, annual repricing, stable populations
- **Auto insurance**: Dynamic streaming telematics, continuous repricing, behavioral drift patterns
- PSI thresholds and failure modes are different in a telematics context (driving behavior shifts faster than mortality distributions)

---

## Thesis Structure (6 Chapters)

### Chapter 1: Introduction
- Why dynamic pricing from telematics? (market context, Vietnam and Cambodia adoption)
- Why PSI for drift detection? (industry standard, but understudied in telematics context)
- Research gap: No empirical validation of PSI in emerging-market telematics pricing
- **Chapter 1 written** (`thesis/auto/chapter1_introduction.md`) — ~1,650 words, ITC format ✅

### Chapter 2: Background & Literature Review
- Telematics-based UBI (Usage-Based Insurance) pricing models
- PSI and distribution monitoring in actuarial science
- Related work: Cambodia/Vietnam insurance markets, dynamic pricing systems
- **Status**: ⬜ Pending

### Chapter 3: Methodology
- Synthetic telematics generator (10,000 drivers, real-route patterns)
- PSI calculation with telematics-specific bin definitions
- 4 experiment design (EXP-001 through EXP-004)
- **Status**: ⬜ Pending (Weeks 3-4)

### Chapter 4: Results
- EXP-001 baseline (PSI=0, validates generator correctness)
- EXP-002 monotonicity (PSI increases monotonically with distortion magnitude)
- EXP-003 failure modes (3/3 modes caught using secondary metrics)
- EXP-004 temporal/seasonal drift (planned)
- **Status**: EXP-001/002/003 ✅, EXP-004 ⬜

### Chapter 5: Discussion
- Implications for dynamic pricing systems
- Multi-metric monitoring as production recommendation
- Applicability to Cambodia/Vietnam insurance markets
- Limitations (synthetic data, no real telematics yet)
- **Status**: ⬜ Pending (Weeks 5-6)

### Chapter 6: Conclusion & Future Work
- Summary of findings
- Recommended production monitoring stack
- Future: Real telematics data validation, live repricing engine
- **Status**: ⬜ Pending (Weeks 7-8)

---

## Experiments

### EXP-001: Baseline PSI Validation ✅ PASSED (2026-04-20)
**Hypothesis**: PSI = 0 when reference and evaluation distributions are identical.  
**Result**: PSI = 0.000 (confirmed — generator is stable and seeded correctly)  
**Commit**: `c4386d2`

### EXP-002: Monotonicity ✅ PASSED (2026-04-20)
**Hypothesis**: PSI increases monotonically as distortion magnitude increases (0%→50%).  
**Result**: Monotonic increase confirmed across all distortion levels.  
**Commit**: `c4386d2`

### EXP-003: Behavioral Failure Modes ✅ PASSED (2026-04-17/20)
**Hypothesis**: Three telematics-specific failure modes cause PSI false negatives; secondary metrics catch them.

| Failure Mode | MR PSI | Secondary Metric | Result |
|---|---|---|---|
| FM1: Label Drift (Comorbidity) | 0.0065 GREEN | Co-occurrence PSI: 0.079 | ✅ CAUGHT |
| FM2: Feature Decoupling (Age) | 0.0037 GREEN | Age distribution PSI: 8.31 | ✅ CAUGHT |
| FM3: Bin Edge Camouflage | 0.0083 GREEN | HITL rate change: +3.6% | ✅ CAUGHT |

**Key insight**: Primary PSI would give all-green, but secondary metrics reveal systemic drift. Multi-metric monitoring is necessary.  
**Commit**: `dc16035`

### EXP-004: Temporal/Seasonal Drift ⬜ PLANNED
**Hypothesis**: PSI detects seasonal patterns in driving behavior (weekday vs. weekend, winter vs. summer driving).  
**Target**: Weeks 3-4

---

## Timeline (8 Weeks to Defense)

| Weeks | Deliverables | Status |
|-------|-------------|--------|
| 1-2 | Synthetic telematics data generator + EXP-001/002/003 | ✅ DONE EARLY |
| 3-4 | EXP-004 (seasonal drift) + Ch2 Background writing | ⬜ NEXT |
| 5-6 | Ch3-4 (Methodology + Results with all experiments) | ⬜ |
| 7-8 | Ch5-6 (Discussion + Conclusion) + defense prep | ⬜ |

**Defense**: ~2026-06-26

---

## Platform Integration (DAC Phase 5)

The thesis feeds directly into DAC HealthPrice Phase 5:
- **Telematics product**: Auto insurance tab in the React frontend
- **5-metric dashboard**: PSI + secondary metrics for the underwriter dashboard
- **Quote → Policy → Admin monitor**: Full auto product lifecycle
- **Synthetic dataset**: `case-study/auto_dataset.csv` (~10K drivers) — doubles as platform demo data

---

## Key Files

| File | Purpose |
|------|---------|
| `stress_testing/generator.py` | Synthetic telematics data generator (10K drivers, real-route patterns) |
| `stress_testing/adversarial.py` | EXP-003 failure mode scenarios |
| `stress_testing/experiments/exp_001_baseline.py` | Baseline PSI validation |
| `stress_testing/experiments/exp_002_bmi_courier_spike.py` | Monotonicity validation |
| `stress_testing/experiments/exp_003_adversarial.py` | Behavioral failure mode detection |
| `stress_testing/harness.py` | Experiment runner harness |
| `analytics/monitor.py` | PSI + secondary metric monitoring |
| `thesis/auto/chapter1_introduction.md` | Chapter 1 (written) |

---

## Related Pages

- [Thesis Defense: Stress-Testing Harness](./thesis-defense-stress-testing-framework.md) — Life insurance thesis framework (archived)
- [Thesis Presentation Guide](./thesis-presentation-guide.md) — Defense preparation, speaker notes
- [Stress-Testing EXP-001/002/003 Results](../sources/2026-04-20_exp001-exp003-results.md) — Detailed experiment build records
- [DAC HealthPrice Phase 4 Weeks 2-7](../sources/2026-04-17_phase4-weeks2-7.md) — Platform builds that run in parallel
- [ETL Pipeline + Recalibration](./etl-pipeline-recalibration.md) — Calibration infrastructure shared with thesis
- [Cambodia Smart Underwriting](./cambodia-smart-underwriting.md) — Life insurance product context
