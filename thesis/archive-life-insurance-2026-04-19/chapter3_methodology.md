# CHAPTER III. METHODOLOGY

---

## 3.1 Research Design

This research employs an experimental design with three controlled experiments, each addressing a distinct aspect of PSI's monitoring performance in an emerging market underwriting context. The experimental approach was chosen for two reasons. First, real Cambodian policyholder data was unavailable due to data privacy constraints and the limited availability of longitudinal claims records in Cambodia's nascent insurance market. Second, controlled experiments allow precise manipulation of specific population characteristics, enabling systematic investigation of targeted failure modes that would be difficult to isolate in observational data.

The three experiments are:

- **EXP-001 (Baseline Validation)**: Confirms that the synthetic generator produces a stable, reproducible reference distribution. This is a necessary internal consistency check before any drift detection experiments can be trusted.
- **EXP-002 (PSI Responsiveness)**: Validates that PSI responds monotonically to increasing levels of population distortion, establishing its sensitivity as a detection instrument.
- **EXP-003 (Adversarial Failure Mode Detection)**: Identifies three scenarios in which PSI produces false negatives — returning a GREEN alert while meaningful model assumption violations have occurred.

All experiments use the same core synthetic data generator and PSI calculation framework, described in Sections 3.2 and 3.3 respectively. Full reproducibility is guaranteed by fixing the random seed to 42 throughout all generation steps.

---

## 3.2 Synthetic Population Generator

### 3.2.1 Design Rationale

The synthetic generator produces a population of 10,000 Cambodian insurance applicants with internally consistent demographic profiles, health histories, and computed mortality ratios. The demographic parameters are calibrated to approximate Cambodia's insured population using publicly available demographic and epidemiological reference data [CITATION NEEDED: Cambodia census data, WHO Cambodia mortality profile].

Synthetic generation was chosen over anonymized real records for three reasons: (1) it allows precise, reproducible control of distributional properties needed for adversarial experimentation; (2) it avoids privacy and regulatory constraints associated with real policyholder data; and (3) it enables exact construction of failure mode scenarios that would be rare or non-existent in historical data. The limitation of this choice — that synthetic distributions may diverge from real distributions in unknown ways — is discussed in Section 5.4.

### 3.2.2 Demographic Parameters

Each applicant is generated with the following base attributes, drawn independently from the specified distributions:

**Table 3.1: Synthetic Applicant Base Attribute Distributions**

| Attribute | Distribution | Parameters | Rationale |
|-----------|-------------|------------|-----------|
| Age | Truncated normal | μ = 35, σ = 10, range [18, 65] | Cambodia's young insured population; median applicant age below developed market norms |
| Gender | Bernoulli | P(male) = 0.55 | Slight male majority in Cambodian insurance applicant pool [CITATION NEEDED] |
| BMI | Normal | μ = 23.5, σ = 3.5, clipped [15, 45] | Southeast Asian BMI norms; lower than Western reference values [CITATION NEEDED] |
| Smoking status | Bernoulli | P(smoker) = 0.22 | National smoking prevalence, male-weighted [CITATION NEEDED: Cambodia tobacco survey] |

### 3.2.3 Cambodia-Specific Risk Factors

Beyond standard demographic attributes, each applicant is assigned Cambodia-specific health and contextual risk factors:

**Pre-existing conditions** are assigned with age-correlated prevalence rates, reflecting the increasing incidence of chronic conditions with age:

**Table 3.2: Pre-existing Condition Prevalence Parameters**

| Condition | Baseline Prevalence | Age Dependency | Notes |
|-----------|---------------------|----------------|-------|
| Hypertension | 15% for age ≥ 40; 5% otherwise | Strong positive | Calibrated to ASEAN hypertension surveys [CITATION NEEDED] |
| Diabetes | 8% | Moderate positive | Calibrated to Cambodia diabetes prevalence [CITATION NEEDED] |
| Heart disease | 5% for age ≥ 50; 2% otherwise | Strong positive | Age-gated onset assumption |
| Malaria history | 3% (rural provinces only) | None | Location-dependent; endemic in Mondulkiri, Ratanakiri [CITATION NEEDED] |

**Occupational risk tier** is assigned based on random sampling with age-weighted probabilities, reflecting the distribution of occupations in Cambodia's insured working population:

- **Low-risk (60%)**: Sedentary and professional occupations (office workers, civil servants, teachers)
- **Medium-risk (25%)**: Manual labor and trade occupations (farmers, mechanics, factory workers)
- **High-risk (15%)**: Elevated-hazard occupations (motorbike couriers, construction workers, fishermen)

**Healthcare access tier** is assigned based on simulated geographic distribution:

- **Urban (70%)**: Access to tertiary care facilities; standard mortality assumption
- **Rural (30%)**: Limited to primary care; healthcare access penalty applied

### 3.2.4 Mortality Ratio Computation

The mortality ratio for each applicant is computed as a product of a standard baseline and multiplicative risk loading factors:

$$\text{MR} = 1.0 \times \prod_{k \in \mathcal{F}} m_k$$

where $\mathcal{F}$ is the set of applicable risk factors for the applicant and $m_k$ is the mortality loading multiplier for factor $k$. This multiplicative structure follows standard actuarial convention for excess mortality loading [CITATION NEEDED: multiplicative mortality loading, actuarial practice].

**Table 3.3: Mortality Ratio Loading Multipliers**

| Risk Factor | Condition | Multiplier $m_k$ |
|-------------|-----------|-----------------|
| Age | Per decade above age 30 | × 1.08 per decade |
| BMI | Overweight (BMI 27.5–30) | × 1.10 |
| BMI | Obese (BMI 30–35) | × 1.20 |
| BMI | Severely obese (BMI > 35) | × 1.40 |
| Smoking | Current smoker | × 1.45 |
| Hypertension | Diagnosed | × 1.25 |
| Diabetes | Diagnosed | × 1.30 |
| Heart disease | Diagnosed | × 1.60 |
| Malaria history | Documented | × 1.15 |
| Occupation | High-risk tier | × 1.35 |
| Healthcare | Rural access | × 1.15 |

These multipliers are applied multiplicatively, so an applicant with multiple risk factors accumulates compounding loadings. The resulting MR distribution spans approximately [0.7, 8.5], with the majority of applicants concentrated in [0.8, 2.0], consistent with the distribution expected in a predominantly standard-risk insured population.

---

## 3.3 PSI Calculation Framework

### 3.3.1 Reference Distribution Construction

The reference distribution is established once from the baseline population of 10,000 applicants generated with seed=42. The mortality ratio values are binned into $B = 8$ equal-width bins spanning the empirical range [0.7, 4.5]. The reference proportion for bin $i$ is:

$$E_i = \frac{n_i^{\text{ref}}}{10{,}000}$$

where $n_i^{\text{ref}}$ is the count of reference applicants falling in bin $i$. This reference distribution is fixed and reused as the expected distribution ($E$) in all three experiments.

The choice of $B = 8$ bins follows standard PSI practice in insurance model monitoring [CITATION NEEDED: PSI bin count conventions]. Sensitivity to bin count is discussed in Section 5.4.

### 3.3.2 PSI Formula

For a given test population of $N$ applicants, the actual bin proportions are computed as:

$$A_i = \frac{n_i^{\text{test}} + \varepsilon}{\sum_{j=1}^{B} (n_j^{\text{test}} + \varepsilon)}$$

and PSI is computed as:

$$\text{PSI} = \sum_{i=1}^{B} \left( A_i - E_i \right) \times \ln\left( \frac{A_i}{E_i} \right)$$

### 3.3.3 Epsilon Smoothing

To prevent undefined logarithm values when a bin is empty in either the actual or reference distribution, an additive smoothing term $\varepsilon = 0.0001$ is applied to all bin counts before computing proportions, as shown in the formula above. This follows standard PSI implementation practice [CITATION NEEDED: PSI epsilon smoothing convention] and has negligible effect on the computed PSI value for non-empty bins.

### 3.3.4 Alert Thresholds

The three-tier alert system is implemented using the standard thresholds established in Section 2.2.2:

| PSI Value | Alert Status | Action |
|-----------|-------------|--------|
| PSI < 0.10 | GREEN | No action; continue routine monitoring |
| 0.10 ≤ PSI < 0.25 | AMBER | Investigate; flag for senior actuarial review |
| PSI ≥ 0.25 | RED | Halt automated underwriting; initiate model recalibration |

---

## 3.4 EXP-001: Baseline Validation

**Objective**: Confirm that the synthetic generator produces a stable, internally consistent reference distribution.

**Method**: The baseline population of 10,000 applicants (seed=42) is generated and used simultaneously as both the reference distribution and the test population. PSI is computed by comparing the population to itself.

**Expected result**: By mathematical construction, when $A_i = E_i$ for all bins, each term $(A_i - E_i) \times \ln(A_i / E_i) = 0$. Therefore, PSI must equal exactly zero.

**Success criterion**: PSI = 0.000000 to six decimal places, confirming that the generator is deterministic, the histogram binning is consistent, and the PSI implementation is mathematically correct.

**Interpretation**: A result of PSI = 0 validates that the generator can serve as the anchor for all subsequent experiments. Any non-zero result would indicate an implementation error in either the generator or the PSI calculation.

---

## 3.5 EXP-002: PSI Responsiveness to Population Distortion

**Objective**: Validate that PSI responds monotonically and predictably to increasing levels of population distortion, establishing it as a valid detection instrument before testing its limits.

**Method**: A controlled distortion is applied to the baseline population by replacing a fraction $f$ of applicants with synthetic applicants representing Phnom Penh motorbike couriers. The distorted applicant profile is held constant across all distortion levels: male, age uniform [28, 35], BMI normal(29.5, 2.0), non-smoker, no pre-existing conditions, occupation = high-risk tier (motorbike courier, multiplier × 1.35), healthcare = urban.

This distortion was chosen because motorbike couriers represent a realistic and growing applicant segment in Cambodia (sector growth ~12% annually) and because their elevated occupational risk loading produces a predictable rightward shift in the MR distribution.

Five distortion levels are tested: $f \in \{0\%,\ 10\%,\ 20\%,\ 40\%,\ 50\%\}$.

At each level, the PSI of the distorted population against the reference distribution is computed. The experiment tests the null hypothesis that PSI does not increase monotonically, against the alternative that strict monotonicity holds: $\text{PSI}(f_1) < \text{PSI}(f_2)$ whenever $f_1 < f_2$.

**Success criterion**: Strict monotonic increase across all five distortion levels.

---

## 3.6 EXP-003: Adversarial Failure Mode Detection

EXP-003 tests three adversarial scenarios in which PSI is predicted to remain GREEN while the underlying model assumption violations would cause systematic underwriting errors. For each failure mode, both the primary PSI metric and a secondary detection metric are computed and compared.

### 3.6.1 Failure Mode 1: Label Drift (Comorbidity Confounding)

**Scenario construction**: A government-sponsored diabetic management program introduces nationwide antihypertensive treatment for diabetic patients. Before the program, the joint distribution of (diabetes=True, BP\_class="elevated") is the model's learned correlation for high-risk diabetic applicants. After the program, affected applicants have (diabetes=True, BP\_class="normal") — their blood pressure is pharmacologically controlled. The diabetes mortality multiplier (× 1.30) remains in the model, but the associated BP loading is no longer triggered.

**Implementation**: In the 10,000-applicant baseline population, all applicants with diabetes=True and BP\_class="elevated" have their BP\_class modified to "normal". Because the diabetes multiplier is preserved, the change in MR for each affected applicant is small (the BP normalization reduces loading slightly), and the aggregate MR distribution remains close to the reference.

**Primary metric**: MR PSI — the standard PSI computed on the mortality ratio distribution.

**Secondary metric**: Feature co-occurrence PSI — PSI computed on the proportion of applicants meeting the condition (diabetes=True AND BP\_class="normal") versus the reference proportion. This is implemented as a two-bin PSI: bin 1 = P(co-occurrence=True), bin 2 = P(co-occurrence=False).

**Detection hypothesis**: MR PSI will remain GREEN (< 0.10) while the co-occurrence PSI will be significantly elevated relative to baseline, providing a detectable early-warning signal of the label drift.

### 3.6.2 Failure Mode 2: Feature-PSI Decoupling (Age Cohort Shift)

**Scenario construction**: A wave of young urban professionals aged 22–28 enters the insurance market following the introduction of mandatory corporate group life insurance benefits. All are healthy: non-smokers, normal BMI, no pre-existing conditions, urban healthcare access, low-risk occupation. Their individual mortality ratios cluster near 1.0 because healthy young adults with no risk factors naturally receive near-standard pricing. Since the reference distribution already includes a proportion of near-standard applicants, the aggregate MR distribution changes minimally.

**Implementation**: 2,000 synthetic young professional applicants are generated with the following parameters: age uniform[22, 28], BMI normal(21.5, 2.0), all health conditions=False, smoking=False, occupation=low-risk, healthcare=urban. These 2,000 applicants replace a random 2,000 from the baseline population (20% replacement).

**Primary metric**: MR PSI — standard PSI on the mortality ratio distribution.

**Secondary metric**: Marginal age distribution PSI — PSI computed on an 8-bin histogram of applicant ages spanning [18, 65].

**Detection hypothesis**: MR PSI will remain GREEN because the young professionals' MR values are distributed similarly to the reference. The age distribution PSI will register a large RED value, reflecting the dramatic demographic composition shift toward younger applicants.

### 3.6.3 Failure Mode 3: Bin Edge Camouflage (Boundary Classification Instability)

**Scenario construction**: A sedentary lifestyle trend (increased desk work, reduced physical activity) causes a subset of borderline-LOW-risk applicants to develop mild hyperlipidemia and transition to the overweight BMI category. Their mortality ratios shift from approximately 1.48 — just below the STANDARD/MEDIUM boundary at MR = 1.5 — to approximately 1.73, placing them in the MEDIUM tier and routing them to human-in-the-loop review. The affected applicants represent approximately 15% of the baseline population.

**Implementation**: Applicants with MR in the range [1.30, 1.50] have two modifications applied: (1) hyperlipidemia=True (multiplier × 1.18) and (2) BMI adjusted to overweight range (multiplier × 1.10). The combined multiplicative effect shifts their MR to approximately [1.53, 1.95].

**Primary metric**: MR PSI — standard PSI on the mortality ratio distribution.

**Secondary metric**: HITL escalation rate — the percentage of applicants classified as MEDIUM tier (MR > 1.5) in the test population, compared against the baseline escalation rate. The delta is reported in percentage points.

**Detection hypothesis**: MR PSI will remain GREEN because the shift is confined to the boundary region of the MR histogram and is diluted by the remaining 85% of the unchanged population. The HITL escalation rate will increase measurably, translating to a concrete operational impact in underwriting workload.

---

## 3.7 Summary of Experimental Design

Table 3.4 provides a consolidated summary of all experiments, their objectives, metrics, and pass criteria.

**Table 3.4: Summary of Experimental Design**

| Experiment | Objective | Primary Metric | Secondary Metric | Pass Criterion |
|-----------|-----------|----------------|-----------------|---------------|
| EXP-001 | Generator internal consistency | MR PSI | — | PSI = 0.000000 |
| EXP-002 | PSI monotonicity | MR PSI at $f$ = 0–50% | — | Strict monotonic increase |
| EXP-003-FM1 | Label drift detection | MR PSI | Feature co-occurrence PSI | MR PSI GREEN; co-occurrence elevated |
| EXP-003-FM2 | Cohort shift detection | MR PSI | Age distribution PSI | MR PSI GREEN; age PSI RED |
| EXP-003-FM3 | Boundary instability detection | MR PSI | HITL escalation rate delta | MR PSI GREEN; escalation rate elevated |

All experiments share the same reference distribution (seed=42, $N$ = 10,000, $B$ = 8 bins) and use identical PSI implementation with $\varepsilon = 0.0001$ smoothing. Chapter IV presents the results.

---

*Word count: approximately 2,100 words.*
