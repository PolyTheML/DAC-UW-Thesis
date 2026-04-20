# CHAPTER II. BACKGROUND AND TECHNICAL CONTEXT

---

## 2.1 Life Insurance Underwriting and the Mortality Ratio

Life insurance underwriting is the process by which an insurer evaluates an applicant's risk profile and assigns them to a risk tier that determines their premium and coverage terms. The core task is to estimate the applicant's expected mortality: the probability that they will make a claim during the policy period, weighted by the claim size. In traditional actuarial practice, this estimation relies on mortality tables, medical examinations, and historical claims experience. In AI-based underwriting systems, the same estimation is performed by a statistical model trained on historical policyholder data.

The *mortality ratio* (MR) is the primary risk aggregation metric used throughout this thesis. It is a scalar value that combines multiple risk factors — age, BMI, smoking status, pre-existing conditions, occupation, and healthcare access — into a single normalized risk score relative to a standard population baseline. A mortality ratio of 1.0 represents standard risk; values above 1.0 indicate elevated risk. The mortality ratio drives the tier classification that determines underwriting disposition:

| Tier | MR Range | Routing | Action |
|------|----------|---------|--------|
| STANDARD | MR ≤ 1.5 | STP (Straight-Through Processing) | Automated approval, standard premium |
| MEDIUM | 1.5 < MR ≤ 2.5 | HITL (Human-In-The-Loop) | Underwriter review required |
| HIGH | 2.5 < MR ≤ 4.0 | ESCALATE | Senior underwriter review |
| DECLINE | MR > 4.0 | DECLINE | Application declined |

**Table 2.1: Underwriting Tier Classification by Mortality Ratio**

This tiered architecture ensures that automated decisions are made only for clearly standard-risk applicants, while borderline and elevated-risk cases receive appropriate human oversight. The proportion of cases requiring HITL review is an operational metric that reflects both model calibration quality and population composition — a point that becomes central to EXP-003 in Chapter IV. [CITATION NEEDED: underwriting tier architecture standards]

---

## 2.2 Population Stability Index

### 2.2.1 Definition and Formula

The Population Stability Index (PSI) is a statistical metric for detecting shifts in the distribution of a model's input or output variable between a reference period and a monitoring period. It was originally developed in consumer credit risk modeling to detect when a scoring model's applicant population had drifted from the population used to build the model [CITATION NEEDED: PSI credit risk origins]. It has since been widely adopted in life insurance underwriting to monitor the mortality ratio distribution.

PSI is defined as:

$$\text{PSI} = \sum_{i=1}^{B} \left( A_i - E_i \right) \times \ln\left( \frac{A_i}{E_i} \right)$$

where $B$ is the number of histogram bins, $A_i$ is the proportion of the current (actual) population falling in bin $i$, and $E_i$ is the proportion of the reference (expected) population falling in bin $i$. When $A_i = E_i$ for all bins, PSI equals exactly zero, indicating no distributional shift. As the actual distribution diverges from the reference, PSI increases monotonically.

### 2.2.2 Standard Alert Thresholds

Three alert levels are universally applied in North American and European actuarial practice [CITATION NEEDED: actuarial PSI standard thresholds]:

| PSI Value | Alert Status | Standard Interpretation |
|-----------|-------------|-------------------------|
| PSI < 0.10 | GREEN | No significant population change; model is stable |
| 0.10 ≤ PSI < 0.25 | AMBER | Minor shift detected; increase monitoring frequency |
| PSI ≥ 0.25 | RED | Major shift; model recalibration or replacement required |

These thresholds were empirically derived from North American consumer credit scoring contexts, where training datasets exceed 100,000 records and population change is gradual. Their applicability to smaller, faster-moving emerging market populations is the central question this thesis investigates.

### 2.2.3 Structural Limitations

PSI has two structural limitations that are directly relevant to this research.

First, PSI operates on a *single aggregated output variable* — in this case, the mortality ratio. Changes to input feature distributions that do not propagate proportionally into the output distribution are invisible to PSI. A clinical intervention that normalizes blood pressure in diabetic patients, for example, changes the joint input feature distribution substantially while producing only a marginal change in aggregate mortality ratios.

Second, PSI is *bin boundary-sensitive*. The measured PSI value depends on the choice of bin count and bin boundaries. Shifts concentrated near bin edges — where applicants cross a decision threshold — are diluted across adjacent bins and may produce smaller PSI values than shifts distributed uniformly across the distribution. [CITATION NEEDED: PSI bin sensitivity analysis]

Both limitations are investigated empirically in Chapter IV.

---

## 2.3 The Cambodian Insurance Market

Cambodia's life insurance market is characteristic of a rapidly growing, data-sparse emerging market. Insurance penetration remains below 30% of the adult population, and the industry operates primarily from demographic assumptions derived from regional proxies rather than domestic longitudinal claims experience [CITATION NEEDED: Cambodia insurance penetration statistics]. Annual premium growth exceeds 20%, driven by expanding urban middle-class incomes and employer-sponsored benefit schemes.

Several structural features of Cambodia's demographic landscape create challenges that are specific to AI-based underwriting:

**Endemic disease burden**: Malaria prevalence in Mondulkiri and Ratanakiri provinces is approximately 15 times higher than in Phnom Penh and other urban centers. Geographic risk differentials of this magnitude must be encoded as location-dependent mortality multipliers, and their magnitude can shift rapidly as national malaria control programs expand. An underwriting model calibrated to a particular prevalence rate will drift silently as that rate changes.

**Occupational sector volatility**: The motorbike courier sector is growing at approximately 12% annually, driven by the expansion of digital food delivery and logistics platforms. This introduces an increasing segment of applicants with elevated occupational mortality risk. If motorbike couriers represent a small fraction of the training population but a growing fraction of incoming applications, the model's implicit weighting of occupational risk becomes progressively miscalibrated.

**Healthcare tier stratification**: Access to tertiary care — hospital facilities capable of managing complex conditions — is concentrated in urban centers. Rural applicants who develop treatable conditions face substantially higher mortality risk due to delayed diagnosis and limited treatment options. This stratification is not static; ongoing rural health infrastructure investment progressively reduces the urban-rural mortality gap, but at a rate that may differ from the model's embedded assumptions.

**Nascent regulatory framework**: Unlike established markets, Cambodia's insurance regulator (the Insurance Regulator of Cambodia, IRC) has not yet issued specific mandates for AI model validation or drift monitoring protocols. The absence of prescribed stress-testing standards creates a governance gap that is addressed by the framework proposed in this thesis.

---

## 2.4 Model Drift in AI-Based Underwriting

Model drift is the degradation of a deployed model's predictive accuracy due to changes in the statistical properties of the input data after the model was trained. In AI-based underwriting, three types of drift are relevant [CITATION NEEDED: concept drift taxonomy]:

**Covariate shift** occurs when the distribution of input features changes while the conditional relationship between features and mortality outcome remains stable. PSI on the mortality ratio distribution is designed to detect this type of shift, as input feature changes that increase mortality should propagate into higher MR values.

**Label shift** (also called prior probability shift) occurs when the mapping from input features to outcome changes — for example, when a new treatment protocol substantially reduces the mortality impact of a condition that was previously high-risk. In this case, the model's embedded multiplier for that condition remains unchanged while the true multiplier has decreased. The aggregate MR distribution may remain stable, masking the underlying calibration error.

**Concept drift** occurs when the fundamental relationship between applicant characteristics and mortality changes in a way that no existing feature can represent — for example, the emergence of a new occupational hazard or a novel endemic disease. Standard monitoring metrics, including PSI, cannot detect concept drift because the new relationship is not encoded in any monitored variable.

Standard industry practice addresses covariate shift effectively through PSI monitoring but lacks systematic approaches for label shift and concept drift detection, particularly in data-sparse markets where ground-truth outcome data accumulates slowly. [CITATION NEEDED: MLOps model monitoring survey]

---

## 2.5 Summary of Technical Context

This chapter has established the four technical premises that motivate the research:

1. **Mortality ratio as aggregation**: The mortality ratio effectively summarizes multi-dimensional applicant risk into a single PSI-monitorable value, but this aggregation creates opportunities for blind spots when input distributions shift without proportionally changing outputs.

2. **PSI threshold origin**: Standard PSI thresholds were calibrated in stable, data-rich markets. Their applicability to Cambodia's dynamic demographic and epidemiological environment has not been validated.

3. **Cambodia's specific dynamics**: Endemic disease volatility, occupational sector growth, and healthcare tier transitions generate realistic drift scenarios that are not represented in the existing PSI literature.

4. **Monitoring gap**: No published stress-testing framework exists for AI underwriting in emerging markets. The multi-metric framework proposed in this thesis is designed to fill this gap with a system that can be deployed without model retraining.

Chapter III describes the methodology developed to validate these observations through controlled experimentation.

---

*Word count: approximately 1,400 words.*
