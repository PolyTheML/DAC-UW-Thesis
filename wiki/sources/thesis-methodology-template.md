# Thesis Chapter 3: Methodology Template

**Created**: 2026-04-17  
**Format**: ITC Cambodia standard  
**Chapter**: III (METHODOLOGY)  
**Pages**: Typically 4-8 pages  
**Typical Word Count**: 2,500-3,500 words

---

## Chapter 3 Structure

### Formatting Rules
- **Chapter Header**: "CHAPTER III. METHODOLOGY" (all caps, 16pt bold, centered)
- **Section Headers**: "3.1 [Section Title]" (12pt bold)
- **Subsection Headers**: "3.1.1 [Subsection]" (12pt, italic)
- **Font**: Times New Roman, 12pt
- **Spacing**: 1.5 or double line spacing
- **Include**: Diagrams, flowcharts, equations, pseudo-code as appropriate

### Six-Section Structure

1. **3.1 Research Design** — What is your overall approach?
2. **3.2 Data and Data Generation** — What data do you use? How is it generated?
3. **3.3 Procedures and Algorithms** — What methods/algorithms do you apply?
4. **3.4 Experimental Design** — How are experiments structured?
5. **3.5 Evaluation Metrics** — How do you measure success?
6. **3.6 Implementation Details** — Tools, libraries, reproducibility info

---

## Example 1: Methodology (Stress-Testing Thesis)

```
CHAPTER III. METHODOLOGY


3.1 Research Design

This thesis employs a mixed-methods approach combining synthetic data generation, algorithmic 
stress-testing, and empirical validation. The research design is structured as three controlled 
experiments with increasing complexity:

Experiment 1 (Baseline Validation): Generate synthetic applicants and verify that the generated 
population matches a reference distribution (by construction, PSI should be ≈0).

Experiment 2 (Responsiveness): Inject controlled population distortions (0%, 10%, 20%, ..., 50%) 
and measure PSI's response. Hypothesis: PSI increases monotonically with distortion.

Experiment 3 (Adversarial Scenarios): Test three specific failure modes where PSI may give false 
negatives, and validate secondary detection metrics. Hypothesis: Multi-metric monitoring detects 
scenarios that PSI alone misses.

This design enables us to (1) validate that our synthetic generator is working correctly, (2) 
confirm PSI's primary strength (detecting large shifts), and (3) expose PSI's weaknesses under 
realistic emerging market conditions.


3.2 Synthetic Data Generation and Calibration

3.2.1 Demographic Priors

We use Cambodian census data and health surveys to establish demographic priors for synthetic 
applicant generation. Key statistics:

| Feature | Distribution | Source |
|---------|--------------|--------|
| Age | N(38, 8), clipped [25, 65] | Cambodia census 2019 |
| BMI | N(23.5, 3.5), clipped [16, 45] | WHO regional health survey |
| Gender | 52% male | Census |
| Smoking (Male) | 30% | Cambodia behavioral study |
| Smoking (Female) | 8% | Cambodia behavioral study |
| BP Systolic (HTN) | N(150, 15) | Clinical baseline |
| BP Systolic (Normal) | N(118, 12) | Clinical baseline |

Age-dependent conditions are modeled using logistic regression:
  P(diabetes | age) = 1 / (1 + exp(-(-5.0 + 0.12 * age)))
  P(hypertension | age) = 1 / (1 + exp(-(-6.5 + 0.15 * age)))
  P(hyperlipidemia | age) = 1 / (1 + exp(-(-5.5 + 0.13 * age)))

These parameters ensure that chronic conditions increase with age, matching real-world epidemiology.

3.2.2 Mortality Ratio Calculation

For each synthetic applicant, we calculate a mortality ratio (MR) using the Cambodia Smart 
Underwriting Engine (from `medical_reader/pricing/calculator.py`):

  MR = q_x × CAM_MORTALITY_ADJ × CAM_OCCUPATIONAL[occupation] × CAM_ENDEMIC[province] × HEALTHCARE_TIER[tier]

Where:
- q_x is the age-based baseline mortality (actuarial table)
- CAM_MORTALITY_ADJ = 0.85 (Cambodia-specific adjustment)
- CAM_OCCUPATIONAL includes: Motorbike Courier +45%, Construction +35%, Farmer -5%, Office +0%, etc.
- CAM_ENDEMIC includes: Phnom Penh baseline, Kandal +10%, Mondulkiri +30%, Ratanakiri +28%, etc.
- HEALTHCARE_TIER includes: Private -3%, Hospital baseline, Clinic +5%

For each synthetic applicant, we randomly assign:
- Province (uniform: Phnom Penh 40%, Kandal 30%, Mondulkiri 10%, Ratanakiri 10%, Other 10%)
- Occupation (uniform: Office 50%, Motorbike 15%, Construction 15%, Farmer 15%, Other 5%)
- Healthcare Tier (uniform: Hospital 40%, Clinic 50%, Private 10%)

This produces a synthetic portfolio with authentic MR distribution calibrated to Cambodia-specific 
risk factors.

3.2.3 Reference Distribution

The reference distribution is computed empirically from a baseline batch of 10,000 synthetic 
applicants generated with seed=42:

  baseline_batch = generator.generate(BASELINE scenario, seed=42)
  baseline_mr_values = [applicant.mortality_ratio for applicant in baseline_batch]
  
Reference distribution (8-bin histogram):
  Bin [0.0, 1.0):   5.0%
  Bin [1.0, 1.5):  53.4%
  Bin [1.5, 2.0):  25.3%
  Bin [2.0, 2.5):  14.7%
  Bin [2.5, 3.0):   1.0%
  Bin [3.0, 3.5):   0.4%
  Bin [3.5, 4.0):   0.2%
  Bin [4.0, ∞):     0.0%

This distribution reflects the expected portfolio: most applicants fall in [1.0, 2.0) range 
(low-to-moderate risk), with tail extending to very high risk.

[Include histogram figure showing baseline distribution]


3.3 PSI Calculation and Thresholds

3.3.1 PSI Formula

Population Stability Index is calculated as:

  PSI = Σ_{i=1}^{n_bins} (Actual_i - Expected_i) × ln(Actual_i / Expected_i)

Where:
- Actual_i is the proportion of applicants in bin i in the new population
- Expected_i is the proportion of applicants in bin i in the reference distribution
- n_bins = 8 (as defined above)

PSI is scale-free and symmetric, making it robust to minor distributional differences.

3.3.2 Alert Thresholds

Based on industry standards and our stress-testing objectives:

  PSI < 0.10    → GREEN   (Stable; no alert)
  0.10 ≤ PSI < 0.25 → AMBER   (Moderate drift; investigate)
  PSI ≥ 0.25    → RED     (Significant drift; trigger recalibration)

These thresholds are not arbitrary—they are validated empirically via EXP-002 (PSI monotonicity 
test). We measure at what distortion fraction PSI crosses each threshold.


3.4 Experimental Design

3.4.1 Experiment 1: Baseline Validation

Objective: Confirm that the synthetic generator produces a stable distribution.

Procedure:
1. Generate 10,000 synthetic applicants (seed=42)
2. Extract mortality_ratio values
3. Compute PSI using empirical baseline (distribution of same batch)
4. Verify: PSI ≈ 0.0 (by construction)

Expected Result: PSI = 0.0000 ± 0.0001

This experiment serves as a sanity check that the generator and PSI calculation are correctly 
implemented.

3.4.2 Experiment 2: PSI Responsiveness

Objective: Demonstrate that PSI increases monotonically with population distortion.

Procedure:
1. Start with baseline 10,000 applicants
2. For each distortion fraction f in {0%, 10%, 15%, 20%, 25%, 30%, 40%, 50%}:
   a. Inject f% of applicants as "high-BMI motorbike couriers" (high-risk profile)
   b. Compute PSI for new population
   c. Record PSI and distortion fraction
3. Plot PSI vs. distortion fraction
4. Verify: PSI increases monotonically (PSI_i ≤ PSI_{i+1})

Distortion Profile (High-BMI Motorbike Couriers):
  occupation_type = "Motorbike Courier"
  bmi = N(32.0, 2.5)  [Obese class 1]
  province = "Kandal"
  healthcare_tier = "Clinic"
  → Expected MR ≈ 1.80 (placed in [1.5, 2.0) bin)

Expected Result:
  Distortion 0%:  PSI = 0.0000
  Distortion 10%: PSI ≈ 0.0022
  Distortion 20%: PSI ≈ 0.0099
  Distortion 40%: PSI ≈ 0.0422
  Distortion 50%: PSI ≈ 0.0674

This experiment validates PSI's primary strength: detecting population distribution changes.

3.4.3 Experiment 3: Adversarial Failure Modes

Objective: Expose scenarios where PSI gives false negatives.

3.4.3.1 Failure Mode 1: Label Drift (Comorbidity Confounding)

Scenario: New government diabetes management clinic normalizes BP readings for diabetic patients.
  - Input feature change: BP distribution shifts lower
  - Mortality ratio: Stays approximately same (diabetes offset ≈ hypertension offset)
  - PSI prediction: GREEN (no drift on MR)
  - Reality: Model over-prices these patients (still applies hypertension multiplier)

Detection Method: Feature co-occurrence PSI
  - Monitor joint distribution P(diabetes=True AND bp_class="normal")
  - Alert if rises >20% above baseline

3.4.3.2 Failure Mode 2: Feature-PSI Decoupling (Age Cohort Shift)

Scenario: Digital health partnership brings 3,000 young professionals (age 22-28), all healthy.
  - Age distribution: Mean shifts from 38 to 35 (dramatic shift)
  - Mortality ratio: ≈ 1.0 (matches baseline LOW bin [0.8, 1.2))
  - PSI prediction: GREEN (no drift on MR)
  - Reality: Model assumptions (trained on 38yo cohort) no longer valid

Detection Method: Marginal age distribution PSI
  - Compute separate PSI on age distribution (histogram of ages)
  - Alert if age PSI > 0.10

3.4.3.3 Failure Mode 3: Bin Edge Camouflage (Tier Boundary Shift)

Scenario: Motorbike courier influx (job market shift). MR shifts from 1.48 → 1.73 (crosses 1.5 
boundary).
  - Relative shift in bins: small (15% of bin 1 → bin 2)
  - PSI value: ≈ 0.05 (GREEN alert threshold)
  - Risk tier: Changes from LOW → MEDIUM (triggers different pricing/HITL routing)
  - Reality: HITL escalation rate doubles, but PSI doesn't alarm

Detection Method: HITL escalation rate monitoring
  - Track % of applicants routed to MEDIUM vs. LOW tier
  - Alert if escalation rate rises >15% from baseline

[Include three scenario diagrams]


3.5 Evaluation Metrics

For each experiment, we record:

| Metric | Description | Use |
|--------|-------------|-----|
| PSI | Population Stability Index | Primary drift metric |
| Distortion Fraction | % of distorted applicants injected | EXP-002 independent variable |
| Feature Drift PSI | PSI on feature co-occurrence | EXP-003 failure mode 1 |
| Age Dist PSI | PSI on age distribution | EXP-003 failure mode 2 |
| HITL Escalation Rate | % of MEDIUM tier decisions | EXP-003 failure mode 3 |
| Model Performance Delta | AUC or accuracy change | Secondary: does PSI-missed drift hurt performance? |

Success Criteria:
- ✓ EXP-001: PSI < 0.01 (baseline ≈ 0)
- ✓ EXP-002: All distortion fractions show monotonic PSI increase
- ✓ EXP-003: All three failure modes trigger secondary metrics while PSI remains GREEN


3.6 Implementation Details

3.6.1 Tools and Libraries

| Tool | Purpose | Version |
|------|---------|---------|
| Python | Language | 3.9+ |
| NumPy | Numerical computing | 1.21+ |
| Pandas | Data manipulation | 1.3+ |
| Matplotlib / Seaborn | Visualization | 3.4+ / 0.11+ |
| scikit-learn | ML utilities | 0.24+ |
| Anthropic SDK | Claude API (for Phase 1 LangGraph) | 0.3+ |

3.6.2 Reproducibility

All experiments are seeded for reproducibility:
  - Generator seed: 42 (baseline)
  - Distortion injection: deterministic (first f% of batch → distorted)
  - Random splits: seeded

Code is available at: https://github.com/[user]/stress-testing/ (or institutional repository)

To reproduce:
```bash
python -m stress_testing.experiments.exp_001_baseline
python -m stress_testing.experiments.exp_002_responsiveness
python -m stress_testing.experiments.exp_003_adversarial
```

3.6.3 Computational Requirements

- CPU: Intel i5 equivalent or better (experiments run in <1 minute total)
- RAM: 4GB minimum
- GPU: Optional (not required; experiments are CPU-bound on <10K applicants)
- Disk: <100MB for code, data, and outputs

---

## Methodology Checklist

- [ ] Research design clearly articulated (3 experiments, specific hypotheses)
- [ ] Data generation process fully documented with parameters
- [ ] Reference distribution explained and justified
- [ ] PSI calculation formula provided with threshold justification
- [ ] All three experiments have clear objectives and expected results
- [ ] Evaluation metrics defined and linked to success criteria
- [ ] Implementation tools listed with versions
- [ ] Reproducibility instructions provided (code repo, seeds, etc.)
- [ ] Diagrams/flowcharts included where helpful
- [ ] No undefined jargon (explain terms on first use)
- [ ] No forward-looking statements ("will validate", "should find") unless you do them
- [ ] Page length: 4-8 pages

---

## Common Pitfalls to Avoid

❌ **Don't**:
- Describe results in methodology (results go in Chapter 4)
- Include implementation code in methodology (reference it, don't embed)
- Use ill-defined terms ("validate", "test")—be specific
- Skip justification for design choices
- Assume reader knows your domain (define context)
- Use passive voice excessively (prefer active)

✅ **Do**:
- Be specific and concrete
- Justify every choice (Why 8 bins? Why these thresholds?)
- Use numbered lists for clarity
- Include equations where relevant
- Reference code/tools without embedding them
- Provide enough detail for replication
- Explain assumptions clearly

---

**Next Step**: After completing Chapter 3 (Methodology), proceed to Chapter 4 (Results) using `thesis-results-template.md`.
