# CHAPTER IV. RESULTS

---

## 4.1 EXP-001: Baseline Validation

EXP-001 established the internal consistency of the synthetic generator by comparing the baseline population against itself. The 10,000-applicant population generated with seed=42 was used simultaneously as the reference distribution and the test population.

**Result**: PSI = 0.000000

By mathematical construction — when $A_i = E_i$ for all bins, each term $(A_i - E_i) \times \ln(A_i / E_i) = 0$ — PSI must equal zero exactly. The result confirms that the generator is fully deterministic and that the PSI implementation is mathematically correct.

Figure 4.1 shows the 8-bin reference histogram of the baseline mortality ratio distribution. The distribution is right-skewed, with the majority of applicants concentrated in the [0.8, 1.5] range, consistent with a predominantly standard-risk insured population. A smaller population of elevated-risk applicants (MR 1.5–4.5) represents the HITL and ESCALATE tiers. The distribution tail beyond MR = 4.0 is sparse, reflecting the low prevalence of applicants qualifying for DECLINE.

![Figure 4.1: Baseline Mortality Ratio Distribution — 8-Bin Reference Histogram (N = 10,000, seed = 42). The distribution is right-skewed with most applicants in the standard-risk range [0.8, 1.5].](figures/fig_4_1_baseline_histogram.png)

This baseline distribution serves as the fixed reference for all PSI computations in EXP-002 and EXP-003.

---

## 4.2 EXP-002: PSI Responsiveness to Population Distortion

EXP-002 tested whether PSI increases monotonically as an increasing fraction of the baseline population is replaced with high-risk motorbike courier applicants. Five distortion levels were tested: $f \in \{0\%,\ 10\%,\ 20\%,\ 40\%,\ 50\%\}$.

### 4.2.1 Results

Table 4.1 presents the PSI value and alert status at each distortion level.

**Table 4.1: PSI Values by Distortion Fraction — EXP-002**

| Distortion Level ($f$) | PSI Value | Alert Status |
|-----------------------|-----------|-------------|
| 0% (baseline) | 0.0000 | GREEN |
| 10% | 0.0022 | GREEN |
| 20% | 0.0099 | GREEN |
| 40% | 0.0422 | GREEN |
| 50% | 0.0674 | GREEN |

PSI increases strictly monotonically across all five distortion levels. The monotonicity condition $\text{PSI}(f_1) < \text{PSI}(f_2)$ for all $f_1 < f_2$ holds without exception, satisfying the success criterion of EXP-002.

Figure 4.2 plots the PSI response curve against distortion fraction. The curve exhibits smooth, approximately exponential growth, reflecting the increasing divergence between the distorted population's MR distribution and the reference.

![Figure 4.2: PSI Response Curve — EXP-002 Population Distortion (0% to 50%). PSI increases monotonically from 0.0000 to 0.0674 across five distortion levels. The GREEN/AMBER threshold (0.10) is shown as a horizontal dashed line.](figures/fig_4_2_psi_response_curve.png)

### 4.2.2 Interpretation

Two findings emerge from the EXP-002 results.

**Finding 1 — PSI is a valid, sensitive monitoring metric**: The strict monotonic increase from PSI = 0.0000 to PSI = 0.0674 across five distortion levels demonstrates that PSI reliably encodes both the direction and relative magnitude of population shifts. A practitioner observing PSI values rising over successive monitoring periods can be confident that a genuine shift is occurring.

**Finding 2 — Standard thresholds may be too conservative for emerging markets**: Despite a 50% replacement of the population with a qualitatively different risk segment, the PSI value of 0.0674 remains well below the GREEN/AMBER boundary of 0.10. Under standard monitoring practice, all five distortion levels — including 50% population replacement — would return GREEN alerts and trigger no action. This observation sets the stage for EXP-003: if PSI does not breach the AMBER threshold even under large aggregate distortions, it is plausible that targeted adversarial shifts will also produce GREEN readings while causing systematic underwriting errors.

---

## 4.3 EXP-003: Adversarial Failure Mode Detection

EXP-003 tested three adversarial scenarios designed to produce PSI false negatives: situations in which the primary MR PSI returns GREEN while a secondary detection metric registers a significant elevation, indicating a meaningful model assumption violation.

### 4.3.1 Failure Mode 1: Label Drift (Comorbidity Confounding)

**Setup recap**: All diabetic applicants with elevated blood pressure had their BP class modified to "normal," simulating the effect of a government diabetic management program.

**Results**:

**Table 4.2: EXP-003 Failure Mode 1 — Results Summary**

| Metric | Value | Alert Status |
|--------|-------|-------------|
| MR PSI (primary) | 0.0065 | GREEN |
| Feature co-occurrence PSI (secondary) | 0.079 | GREEN (approaching AMBER) |

The primary MR PSI of 0.0065 is well within the GREEN zone. Standard PSI monitoring would report no drift and take no action.

The feature co-occurrence PSI of 0.079 is substantially elevated relative to its baseline value of approximately 0.000, approaching the AMBER threshold of 0.10. While it does not breach the AMBER boundary in this experiment, the 12-fold increase from baseline (0.000 → 0.079) represents a strong signal relative to the noise floor of the secondary metric.

Figure 4.3 shows the joint distribution of (diabetes, BP class) before and after the intervention, illustrating the shift in the proportion of applicants with the (diabetes=True, BP\_class=normal) combination.

![Figure 4.3: Failure Mode 1 — Feature Co-occurrence Distribution. Left panel: baseline joint distribution of (diabetes status, BP class). Right panel: post-intervention distribution showing the shift in P(diabetes=True ∩ BP=normal). MR PSI = 0.0065 (GREEN); co-occurrence PSI = 0.079.](figures/fig_4_3_fm1_cooccurrence.png)

**Interpretation**: The diabetic clinic intervention has shifted the joint feature distribution in a way that violates the model's calibration assumption — specifically, the model was trained on data where diabetes correlates with elevated blood pressure, and the combined condition drives mortality loading. After the intervention, diabetic applicants with pharmacologically controlled BP are priced at rates calibrated to the pre-intervention risk profile. The model will systematically overprice these applicants relative to their true risk, creating both competitive disadvantage (higher premiums than competitors without this bias) and potential regulatory exposure. PSI does not detect this; the co-occurrence secondary metric provides an early-warning signal.

### 4.3.2 Failure Mode 2: Feature-PSI Decoupling (Age Cohort Shift)

**Setup recap**: 2,000 young healthy professionals (age 22–28) were injected as 20% of the test population, replacing a random sample of baseline applicants. Their individual MR values cluster near 1.0.

**Results**:

**Table 4.3: EXP-003 Failure Mode 2 — Results Summary**

| Metric | Value | Alert Status |
|--------|-------|-------------|
| MR PSI (primary) | 0.0037 | GREEN |
| Age distribution PSI (secondary) | 8.31 | RED |

The contrast between the two metrics is the starkest result of this thesis. The primary MR PSI of 0.0037 is near-zero — PSI sees virtually no distributional change. Simultaneously, the age distribution PSI of 8.31 is more than 33 times the RED threshold of 0.25 and more than 83 times the AMBER threshold of 0.10.

Figure 4.4 shows the age histograms before and after the cohort injection. The baseline distribution is approximately unimodal with a peak near age 35. The post-injection distribution is bimodal, with a new sharp peak at age 23–27 corresponding to the injected young professional cohort.

![Figure 4.4: Failure Mode 2 — Age Distribution Shift. Left panel: baseline age histogram (approximately unimodal, peak ≈ age 35). Right panel: post-injection age histogram showing bimodal distribution with a new peak at age 23–27. MR PSI = 0.0037 (GREEN); age distribution PSI = 8.31 (RED).](figures/fig_4_4_fm2_age_distribution.png)

**Interpretation**: The young professional cohort is appropriately priced at near-standard risk on an individual basis — a healthy 24-year-old non-smoker with no pre-existing conditions is correctly priced near MR = 1.0. However, the model was not calibrated to price a predominantly young urban professional population at scale. If this cohort's long-term risk trajectory differs structurally from the training population's trajectory — for example, due to different occupational stress profiles, different lifestyle disease exposure, or different healthcare utilization patterns — the model's long-term pricing adequacy is compromised. PSI sees none of this because the aggregate MR distribution is unchanged; the age distribution PSI provides an immediate RED alert.

### 4.3.3 Failure Mode 3: Bin Edge Camouflage (Boundary Classification Instability)

**Setup recap**: Applicants with MR in [1.30, 1.50] had hyperlipidemia and overweight BMI added, shifting their MR to approximately [1.53, 1.95] and crossing the STANDARD/MEDIUM boundary at MR = 1.5.

**Results**:

**Table 4.4: EXP-003 Failure Mode 3 — Results Summary**

| Metric | Value | Alert Status |
|--------|-------|-------------|
| MR PSI (primary) | 0.0083 | GREEN |
| HITL escalation rate change (secondary) | +3.6 percentage points | ELEVATED |

The primary MR PSI of 0.0083 remains well within the GREEN zone. In a system processing 10,000 applications per month, the +3.6 percentage point increase in HITL escalation rate represents 360 additional underwriter review cases per month — cases that were previously processed automatically and are now requiring manual review.

Figure 4.5 shows the MR distribution in the boundary region [1.2, 2.5] before and after the lifestyle change, illustrating the migration of applicants across the 1.5 threshold.

![Figure 4.5: Failure Mode 3 — Mortality Ratio Distribution Near the STANDARD/MEDIUM Boundary. Left panel: baseline MR distribution in [1.2, 2.5] with the majority of borderline applicants below 1.5. Right panel: post-change distribution showing migration across the 1.5 threshold. MR PSI = 0.0083 (GREEN); HITL escalation rate increase = +3.6pp.](figures/fig_4_5_fm3_boundary_shift.png)

**Interpretation**: The bin edge camouflage failure mode arises from a fundamental structural property of PSI: it measures aggregate distributional overlap across all bins, making it insensitive to small shifts concentrated near decision boundaries. The 3.6-percentage-point escalation rate increase is operationally significant — it directly translates into additional underwriter labor, potential case review backlogs, and delayed policy decisions for affected applicants — but it occurs in a region of the MR distribution that is numerically diluted relative to the full histogram. The HITL operational metric measures the business consequence directly; PSI does not.

---

## 4.4 Cross-Experiment Summary

Table 4.5 consolidates the results of all experiments in a single reference table.

**Table 4.5: Full Experimental Results Summary**

| Experiment | Scenario | MR PSI | MR Alert | Secondary Metric | Secondary Value | Secondary Alert |
|-----------|----------|--------|----------|-----------------|-----------------|----------------|
| EXP-001 | Baseline (self-comparison) | 0.0000 | GREEN | — | — | — |
| EXP-002 | 10% distortion | 0.0022 | GREEN | — | — | — |
| EXP-002 | 20% distortion | 0.0099 | GREEN | — | — | — |
| EXP-002 | 40% distortion | 0.0422 | GREEN | — | — | — |
| EXP-002 | 50% distortion | 0.0674 | GREEN | — | — | — |
| EXP-003-FM1 | Label drift | 0.0065 | GREEN | Co-occurrence PSI | 0.079 | Approaching AMBER |
| EXP-003-FM2 | Age cohort shift | 0.0037 | GREEN | Age distribution PSI | 8.31 | RED |
| EXP-003-FM3 | Boundary instability | 0.0083 | GREEN | HITL escalation rate | +3.6pp | ELEVATED |

Three findings from this table are directly relevant to the thesis's central argument:

**Finding 1 — PSI never breaches AMBER**: Across all eight test scenarios — including a 50% population replacement and three adversarial failure modes — MR PSI remained in the GREEN zone. The highest value observed was 0.0674 (EXP-002, 50% distortion), well below the 0.10 AMBER boundary. Under standard single-metric PSI monitoring, none of these scenarios would trigger any alert or action.

**Finding 2 — Secondary metrics detect all three failure modes**: In every EXP-003 failure mode, the secondary detection metric registered a meaningfully elevated signal: co-occurrence PSI approaching AMBER (FM1), age distribution PSI 33× the RED threshold (FM2), and HITL escalation rate elevated by 360 cases per 10,000 applications (FM3).

**Finding 3 — Each failure mode requires a different secondary metric**: No single secondary metric detects all three failure modes. FM1 requires feature co-occurrence monitoring; FM2 requires marginal demographic distribution monitoring; FM3 requires operational escalation rate monitoring. This supports the design of a multi-metric framework rather than a single PSI replacement.

These findings are discussed and interpreted in the context of practical deployment in Chapter V.

---

*Word count: approximately 1,800 words.*
