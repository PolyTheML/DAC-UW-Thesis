# Thesis Chapter 4: Results Template

**Created**: 2026-04-17  
**Format**: ITC Cambodia standard  
**Chapter**: IV (RESULTS)  
**Pages**: Typically 4-8 pages  
**Typical Word Count**: 2,000-3,000 words

---

## Chapter 4 Structure

### Formatting Rules
- **Chapter Header**: "CHAPTER IV. RESULTS" (all caps, 16pt bold, centered)
- **Section Headers**: "4.1 [Experiment Title]" (12pt bold)
- **Subsection Headers**: "4.1.1 [Result Component]" (12pt, italic)
- **Font**: Times New Roman, 12pt for text; figures and tables as needed
- **Spacing**: 1.5 or double line spacing
- **Emphasis**: Use tables and figures liberally; minimize prose redundancy

### Three-Experiment Structure

1. **4.1 Experiment 1: Baseline Validation**
2. **4.2 Experiment 2: PSI Responsiveness**
3. **4.3 Experiment 3: Adversarial Failure Modes**

**Important**: Results chapter is FACTUAL. Do not interpret or discuss implications here—save that for Chapter 5.

---

## Example 1: Results Chapter (Stress-Testing Thesis)

```
CHAPTER IV. RESULTS


4.1 Experiment 1: Baseline Validation

Objective: Confirm that the synthetic generator produces a stable distribution with PSI ≈ 0 by 
construction.

Method: Generate 10,000 synthetic Cambodian applicants with seed=42, compute their mortality_ratio 
distribution, and compare to the empirical reference distribution (same batch).

4.1.1 Baseline Distribution Histogram

We generated 10,000 synthetic applicants and extracted their mortality_ratio values. The distribution 
across 8 bins:

Table 4.1: Baseline Mortality Ratio Distribution (Experiment 1)

| Bin Range | Count | Proportion | Expected | Delta |
|-----------|-------|------------|----------|-------|
| [0.0, 1.0) | 500 | 5.00% | 5.00% | 0.00% |
| [1.0, 1.5) | 5,340 | 53.40% | 53.40% | 0.00% |
| [1.5, 2.0) | 2,530 | 25.30% | 25.30% | 0.00% |
| [2.0, 2.5) | 1,470 | 14.70% | 14.70% | 0.00% |
| [2.5, 3.0) | 100 | 1.00% | 1.00% | 0.00% |
| [3.0, 3.5) | 40 | 0.40% | 0.40% | 0.00% |
| [3.5, 4.0) | 20 | 0.20% | 0.20% | 0.00% |
| [4.0, ∞) | 0 | 0.00% | 0.00% | 0.00% |
| **Total** | **10,000** | **100%** | **100%** | **0.00%** |

Result: PSI = 0.000000 (exactly zero by construction, as expected)

[Include histogram figure: "Figure 4.1: Baseline Mortality Ratio Distribution (10,000 applicants, 
seed=42). Actual distribution overlays perfectly with reference distribution (8-bin histogram)."]

4.1.2 Interpretation

The baseline validation confirms that:
1. ✓ The synthetic generator produces a stable distribution consistent across runs
2. ✓ The generator respects the 8-bin reference distribution exactly
3. ✓ The PSI calculation is correctly implemented (PSI = 0.0 when comparing identical distributions)
4. ✓ Random seed 42 is reproducible (re-running with same seed yields identical PSI)

This serves as a control experiment validating our entire setup. Experiment 1 is PASSED.


4.2 Experiment 2: PSI Responsiveness

Objective: Demonstrate that PSI increases monotonically and smoothly as population distortion 
increases from 0% to 50%.

Method: For each distortion fraction f ∈ {0%, 10%, 15%, 20%, 25%, 30%, 40%, 50%}, inject f% of 
applicants as high-BMI motorbike couriers and compute PSI.

Distortion Profile: Age N(22, 2), BMI N(32, 2.5), occupation="Motorbike Courier", province="Kandal", 
healthcare_tier="Clinic"
→ Expected MR ≈ 1.80 (placed in [1.5, 2.0) bin)

4.2.1 PSI Values Across Distortion Fractions

Table 4.2: PSI Response to Population Distortion (Experiment 2)

| Distortion % | New Bin [1.5,2.0) Count | PSI Value | Alert Level | Interpretation |
|--------------|------------------------|-----------|-------------|-----------------|
| 0% | 2,530 (baseline) | 0.0000 | GREEN | No drift |
| 10% | 2,597 | 0.0022 | GREEN | Small shift |
| 15% | 2,631 | 0.0049 | GREEN | Moderate shift |
| 20% | 2,665 | 0.0099 | GREEN | Moderate shift |
| 25% | 2,699 | 0.0167 | GREEN | Approaching AMBER |
| 30% | 2,733 | 0.0256 | AMBER | Moderate drift alert |
| 40% | 2,801 | 0.0422 | AMBER | Moderate drift alert |
| 50% | 2,869 | 0.0674 | AMBER | High drift alert |

4.2.2 PSI Monotonicity Plot

[Include figure: "Figure 4.2: PSI Response to Population Distortion (0%-50%). PSI increases smoothly 
and monotonically from 0.0000 (0% distortion) to 0.0674 (50% distortion). Smooth S-curve indicates 
predictable, sensitive response. Thresholds: GREEN <0.10 (green shaded), AMBER 0.10-0.25 (yellow 
shaded)."]

Key observations:
- PSI increases smoothly without sharp jumps
- Monotonicity holds across all distortion levels: PSI_0% ≤ PSI_10% ≤ ... ≤ PSI_50%
- RED threshold (0.25) is not reached even at 50% distortion in this scenario
- Minimum distortion to trigger AMBER alert (0.10): ≈ 27% (interpolating between 25% and 30%)

4.2.3 Statistical Properties

| Property | Value |
|----------|-------|
| Min PSI (0% distortion) | 0.0000 |
| Max PSI (50% distortion) | 0.0674 |
| PSI Range | 0.0674 |
| Rate of change (PSI/% distortion) | 0.00135 |
| Distortion needed for AMBER alert (PSI=0.10) | ~27% |
| Distortion needed for RED alert (PSI=0.25) | >50% |

4.2.4 Interpretation

Results confirm:
1. ✓ PSI is sensitive: even small distortions (10%) produce measurable PSI increase
2. ✓ PSI is predictable: smooth monotonic curve enables forecasting alert triggers
3. ✓ PSI is resistant to small noise: <20% distortion stays in GREEN zone
4. ✓ Threshold appropriateness: 30% distortion correctly triggers AMBER (moderate concern)

For practical use: If distortion in population mirrors the high-BMI courier scenario, expect 
RED alert when >27% of portfolio shifts. However, this assumes distortion is in high-MR bins. 
See Experiment 3 for scenarios where PSI fails to alert despite distortion.

Experiment 2 is PASSED: PSI monotonicity confirmed.


4.3 Experiment 3: Adversarial Failure Modes

Objective: Expose three scenarios where PSI gives false negatives (PSI=GREEN despite population 
change). Validate secondary detection metrics for each failure mode.

4.3.1 Failure Mode 1: Label Drift (Comorbidity Confounding)

Scenario: Government diabetes clinic in Phnom Penh successfully manages patient BP. New applicant 
cohort: 30% with (diabetes=True, BP_normal=True). Old baseline: diabetics typically had hypertension.

Method:
1. Generate baseline 10K applicants (seed=42)
2. Replace 30% of diabetic applicants with newly managed ones (diabetes=True, BP class changes from 
   elevated to normal)
3. Compute: (a) PSI on mortality_ratio, (b) Feature co-occurrence PSI on P(diabetes=True AND bp_normal)

Results:

Table 4.3a: Label Drift Detection — PSI on Mortality Ratio

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| Original MR PSI | 0.0000 | Baseline |
| Label Drift Scenario PSI | 0.0034 | GREEN alert (no drift detected) |
| Change in PSI | +0.0034 | Very small increase |
| Alert Level | GREEN ✗ | **FALSE NEGATIVE** |

This is the failure: mortality_ratio distribution barely changes (both old and new diabetics land 
in similar MR bins due to offset effects), so PSI doesn't alert.

Table 4.3b: Label Drift Detection — Feature Co-occurrence PSI

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| Baseline P(diabetes=True ∩ bp_normal) | 2.1% | Rare combination |
| Label Drift Scenario P(diabetes=True ∩ bp_normal) | 32.1% | Common now |
| Feature Co-occurrence PSI | 0.847 | **RED alert** ✓ |

Secondary metric detects the failure: feature co-occurrence PSI correctly flags this scenario as 
problematic.

[Include figure: "Figure 4.3a: Label Drift Failure Mode. Left: PSI on MR stays GREEN (false negative). 
Right: Feature co-occurrence PSI correctly alerts RED."]

4.3.2 Failure Mode 2: Feature-PSI Decoupling (Age Cohort Shift)

Scenario: Digital health partnership brings 3,000 young professionals (age 22-28), all healthy with 
MR ≈ 1.0.

Method:
1. Baseline: 10K applicants, age mean = 38
2. Inject 3K young professionals (age 22-28, MR ≈ 1.0, matching baseline LOW bin [0.8, 1.2))
3. Compute: (a) PSI on mortality_ratio, (b) PSI on age distribution

Results:

Table 4.4a: Cohort Shift — PSI on Mortality Ratio

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| Original MR PSI | 0.0000 | Baseline |
| Cohort Shift PSI | 0.0056 | GREEN alert (no drift detected) |
| Alert Level | GREEN ✗ | **FALSE NEGATIVE** |

PSI on mortality_ratio doesn't alert because new cohort has MR matching baseline bins.

Table 4.4b: Cohort Shift — PSI on Age Distribution

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| Original age mean | 38.2 years | Baseline |
| Cohort Shift age mean | 35.1 years | -3.1 years |
| Original age distribution PSI | 0.0000 | Baseline |
| Cohort Shift age distribution PSI | 0.156 | **AMBER alert** ✓ |
| Alert Level | AMBER ✓ | **Detects shift** |

Secondary metric correctly identifies cohort shift via age distribution PSI.

[Include figure: "Figure 4.3b: Cohort Shift Failure Mode. Left: Age distribution shows clear shift 
(histogram overlay, baseline vs. shifted). Right: PSI on age distribution correctly alerts."]

4.3.3 Failure Mode 3: Bin Edge Camouflage (Tier Boundary Shift)

Scenario: Motorbike courier influx causes 15% of applicants to shift from MR 1.48 → 1.73 (crossing 
1.5 LOW/MEDIUM boundary).

Method:
1. Baseline: 10K applicants with risk tiers assigned at MR=1.5 boundary
2. Shift 15% of borderline applicants (MR 1.48 → 1.73)
3. Compute: (a) PSI on mortality_ratio, (b) HITL escalation rate (% MEDIUM tier decisions)

Results:

Table 4.5a: Tier Boundary Shift — PSI on Mortality Ratio

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| Original PSI | 0.0000 | Baseline |
| Tier Shift PSI | 0.0067 | GREEN alert (small shift) |
| Alert Level | GREEN ✗ | **FALSE NEGATIVE** |

PSI is relatively insensitive because the shift is small and within adjacent bins.

Table 4.5b: Tier Boundary Shift — HITL Escalation Rate

| Metric | Baseline | After Shift | Change | Alert |
|--------|----------|-------------|--------|-------|
| % MEDIUM tier decisions | 14.7% | 29.4% | +14.7pp | **RED** ✓ |
| % LOW tier decisions | 53.4% | 38.7% | -14.7pp | RED ✓ |
| HITL queue depth | +0% | +50% | +50% | **RED** ✓ |

Secondary metric successfully detects tier boundary shift through escalation rate monitoring.

[Include figure: "Figure 4.3c: Bin Edge Camouflage. Stacked bar chart showing tier distribution before/after shift. 
Clear migration from LOW to MEDIUM tier visible."]

4.3.4 Summary of Failure Modes

Table 4.6: Adversarial Scenario Summary

| Failure Mode | PSI Alert | Secondary Metric | Correctly Detects? |
|--------------|-----------|------------------|--------------------|
| Label Drift (comorbidity) | GREEN ✗ | Feature Co-occurrence PSI | YES ✓ |
| Feature-PSI Decoupling (age shift) | GREEN ✗ | Marginal Age Distribution PSI | YES ✓ |
| Bin Edge Camouflage (tier shift) | GREEN ✗ | HITL Escalation Rate | YES ✓ |

All three failure modes are successfully detected by secondary metrics while PSI gives false negatives.

Experiment 3 is PASSED: Multi-metric monitoring framework validated.


4.4 Overall Summary of Findings

| Finding | Confirmation |
|---------|--------------|
| EXP-001: Synthetic generator is stable (PSI ≈ 0) | ✓ PASSED |
| EXP-002: PSI increases monotonically with distortion | ✓ PASSED |
| EXP-003a: Label drift missed by PSI | ✓ PASSED |
| EXP-003b: Feature-PSI decoupling missed by PSI | ✓ PASSED |
| EXP-003c: Bin edge camouflage missed by PSI | ✓ PASSED |
| Secondary metrics detect all three failure modes | ✓ PASSED |

---

## Results Writing Guidelines

### Structure
1. **Results, not discussion**: State findings factually without interpretation
2. **Use tables and figures**: Let data speak; minimize prose
3. **Organize by experiment**: One section per experiment/hypothesis
4. **Be specific**: "PSI = 0.0000" not "PSI is zero"
5. **Include uncertainty where relevant**: ± std dev, confidence intervals

### Formatting
- **Table captions above**: "Table 4.1: [Title]"
- **Figure captions below**: "Figure 4.1: [Title]"
- **All tables/figures referenced in text**: "See Table 4.1..."
- **Cross-references**: "Experiment 2 (Section 4.2) shows..."

### Tone
- Objective and factual
- Avoid speculation or interpretation
- Use past tense: "Results showed...", "Data indicated..."
- No "as we expected" or "surprisingly"—save that for Discussion

---

## Results Checklist

- [ ] All three experiments have dedicated sections
- [ ] Results are presented factually without interpretation
- [ ] Tables include all relevant metrics and row/column labels
- [ ] Figures are clear, labeled, and referenced in text
- [ ] Numbers are specific (not "small" or "large"—give values)
- [ ] Summary table at end ties experiments together
- [ ] No discussion of implications (save for Chapter 5)
- [ ] No forward-looking statements ("suggests", "implies")
- [ ] Page length: 4-8 pages (including figures and tables)
- [ ] All section numbers correct (4.1, 4.2, 4.3, 4.4)

---

**Next Step**: After completing Chapter 4 (Results), proceed to Chapter 5 (Discussion & Implications) using `thesis-discussion-template.md`.
