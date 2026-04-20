# CHAPTER I. INTRODUCTION

---

## 1.1 Motivation and Context

Life insurance underwriting in emerging markets operates under conditions fundamentally different from those in developed economies. In markets such as Cambodia, the combination of limited historical outcome data, rapid population change, fragmented healthcare infrastructure, and nascent regulatory frameworks creates unique pressures on both traditional actuarial models and modern AI-driven underwriting systems. The Cambodian insurance market, with penetration rates below 30% of the adult population, relies heavily on assumptions calibrated from regional proxies rather than domestic longitudinal experience. Risk factor distributions—driven by endemic disease burden (malaria in Mondulkiri and Ratanakiri provinces is 15× higher than urban centers), occupational hazards (motorbike courier sector growing at 12% annually), and tiered healthcare access—shift faster than actuarial models can be recalibrated.

The global insurance industry increasingly adopts Population Stability Index (PSI) as the de facto standard for monitoring distribution drift in underwriting models. PSI measures the divergence between a reference mortality ratio distribution (established at model training) and the distribution observed in current applicant batches. It is interpretable, computationally efficient, and documented extensively in North American and European actuarial practice. The standard PSI alert thresholds—GREEN below 0.10, AMBER at 0.10–0.25, and RED above 0.25—were empirically derived in data-rich, stable-population contexts where population shifts are gradual and training datasets are large (> 100,000 historical policy records).

This thesis argues that PSI's established merits do not automatically extend to emerging market settings. Three observations motivate the investigation:

First, the volatility of emerging market risk factor distributions can produce *silent failures*—scenarios where PSI registers GREEN while meaningful model assumption violations have occurred. A government-mandated diabetes management program, for example, can normalize blood pressure readings for thousands of insured applicants, changing the input feature distribution materially without a corresponding change in the model's output (mortality ratio) distribution. PSI, monitoring only the output, would not detect this.

Second, Cambodia's insurance market is growing rapidly, with annual premium growth exceeding 20% in recent years, and new applicant cohorts—young urban professionals, migrant workers from rural provinces—exhibit risk profiles that may differ systematically from the training population. If new cohorts happen to share mortality ratio distributions with the reference, PSI will remain GREEN despite the composition of the insured pool having changed dramatically.

Third, AI-based underwriting systems in emerging markets lack established stress-testing frameworks. Unlike North American actuarial practice, which has decades of model validation precedent, Cambodia's insurance industry has minimal published guidance on testing model drift in dynamic-population contexts. Empirical evidence of PSI's strengths and limitations is therefore both scientifically and practically necessary.

This thesis addresses these gaps by developing a synthetic stress-testing harness calibrated to Cambodian actuarial assumptions, conducting three controlled experiments, and empirically identifying three failure modes where PSI monitoring gives false negatives. The results support a practical recommendation: supplement PSI with a multi-metric monitoring framework incorporating feature co-occurrence monitoring, marginal demographic distribution tracking, and operational escalation rate monitoring.


## 1.2 Problem Statement

Current drift detection in AI-based life insurance underwriting relies primarily on a single metric: Population Stability Index (PSI) computed over the mortality ratio distribution. While PSI is well-validated for detecting large-magnitude population shifts, this thesis investigates the hypothesis that PSI produces systematic false negatives in three distinct failure mode categories specific to emerging market contexts.

**Failure Mode 1 — Label Drift (Comorbidity Confounding)**: A government diabetic management program normalizes blood pressure in diabetic patients, shifting the joint distribution of (diabetes, blood pressure) without proportionally changing the mortality ratio distribution. Under standard PSI monitoring (MR PSI = 0.0065), the system reports GREEN. However, the feature co-occurrence distribution has shifted meaningfully (co-occurrence PSI = 0.079), violating the model's calibration assumption that diabetes correlates with elevated BP.

**Failure Mode 2 — Feature-PSI Decoupling (Age Cohort Shift)**: A wave of young healthy professionals (mean age 25) applies for life insurance. Their individual mortality ratios cluster near the reference mean, producing near-zero MR PSI (0.0037). However, the age distribution has shifted dramatically (age distribution PSI = 8.31), representing a cohort that the pricing model was not calibrated to price. The model appears stable while pricing a qualitatively different insured population.

**Failure Mode 3 — Bin Edge Camouflage (Boundary Classification Instability)**: A sedentary lifestyle influx causes approximately 7% of borderline LOW-risk applicants to develop additional conditions (hyperlipidemia, overweight BMI), crossing the LOW/MEDIUM tier boundary. Because only a small fraction of the population changes bins, MR PSI remains GREEN (0.0083). However, the HITL escalation rate rises by +3.6 percentage points—representing 360 additional underwriter review cases per 10,000 applications—signaling operational stress that PSI does not reveal.

These failure modes share a common structure: the single-metric PSI signal is insufficient because the mortality ratio distribution, despite encoding aggregate risk, can remain stable while underlying model assumptions are violated. The practical consequences include systematic mispricing, adverse selection, A/E ratio distortion, and potential regulatory non-compliance if drift is not detected.


## 1.3 Research Objectives

**Primary Objective**: Empirically validate whether single-metric PSI monitoring is sufficient for drift detection in emerging market life insurance underwriting, and identify the scenarios in which it produces false negatives.

**Secondary Objectives**:

1. Develop a reproducible synthetic data generator calibrated to Cambodian demographic and actuarial assumptions, producing authentic applicant profiles with computed mortality ratios.

2. Conduct three controlled experiments (EXP-001: baseline validation; EXP-002: PSI responsiveness; EXP-003: adversarial failure mode detection) to characterize PSI's performance envelope.

3. Design and empirically validate secondary monitoring metrics that detect the three PSI failure modes.

4. Propose a practical multi-metric monitoring framework deployable in production underwriting systems without requiring model retraining.

**Research Questions**:

- **RQ1**: How reliably does PSI detect population distribution shifts across distortion magnitudes from 0% to 50%? Does it respond monotonically and predictably?

- **RQ2**: Under which realistic emerging market scenarios does PSI fail to alert despite meaningful model assumption violations?

- **RQ3**: What secondary monitoring metrics successfully detect the three failure modes that PSI misses, and what thresholds are appropriate?

- **RQ4**: Can a multi-metric monitoring framework combining PSI with secondary metrics detect all identified failure modes, providing a practical improvement over single-metric monitoring?


## 1.4 Main Contributions

This thesis makes the following novel contributions to the actuarial and AI underwriting literature:

**Contribution 1 — First Empirical Stress-Test of PSI in an Emerging Market Context**: Prior actuarial literature assumes PSI thresholds validated in North American markets apply universally. This is the first rigorous empirical investigation of PSI performance specifically in an emerging market context (Cambodia), using a population generator calibrated to local demographics, endemic risk factors, and healthcare tier distributions. The results provide evidence-based guidance on where PSI is reliable and where it is not.

**Contribution 2 — Identification and Empirical Validation of Three PSI Failure Modes**: The thesis identifies and empirically demonstrates three distinct scenarios in which PSI produces false negatives. These are not theoretical edge cases but operationally realistic scenarios that follow naturally from Cambodia's development trajectory: government healthcare programs (FM1), urban professional influx (FM2), and lifestyle changes in borderline-risk populations (FM3). All three failure modes are validated with controlled experiments producing MR PSI = GREEN while secondary metrics fire RED alerts.

**Contribution 3 — Multi-Metric Monitoring Framework**: Rather than proposing a replacement for PSI (which remains a sound and interpretable metric), this thesis proposes a practical supplementary framework. The framework adds three secondary metrics—feature co-occurrence PSI, marginal demographic distribution PSI, and HITL operational escalation rate—each targeting a specific failure mode. The framework is designed to be immediately deployable without model retraining.

**Contribution 4 — Reproducible Synthetic Stress-Testing Harness**: The thesis delivers a reusable, open-source stress-testing harness (`stress_testing/`) for validating underwriting AI systems against controlled population distortions. The harness is parameterized for Cambodian risk factors but structured for adaptation to other emerging markets. It provides a template for the validation component of AI governance frameworks in data-sparse insurance markets.

**Contribution 5 — Calibrated Synthetic Population Generator**: The generator (`stress_testing/generator.py`) produces 10,000 synthetic Cambodian applicants with internally consistent demographics, health conditions, occupational risk, and computed mortality ratios (seed=42 for full reproducibility). The reference distribution derived from this baseline provides a validated, stable calibration target for PSI computation, correcting the common practice of using manually estimated reference proportions.


## 1.5 Thesis Organization

The remainder of this thesis is structured as follows:

**Chapter II: Background and Literature Review** establishes the theoretical and empirical context. It introduces the life insurance underwriting process and the role of mortality ratio as a risk aggregation metric. It reviews the PSI literature (derivation, standard thresholds, actuarial applications) and discusses the emerging concept drift literature (concept drift, covariate shift, label shift, dataset shift). The chapter concludes by identifying the specific gaps in PSI validation for emerging market contexts that motivate this thesis.

**Chapter III: Methodology** describes the research design in full detail. It covers the synthetic data generation process (Cambodia census parameters, age-correlated risk factor distributions, the mortality ratio calculator), the PSI calculation procedure (8-bin reference distribution, epsilon-smoothed estimation), and the design of each experiment. For EXP-003, the chapter describes the construction of three adversarial failure mode scenarios and the corresponding secondary detection metrics, including the rationale for each secondary threshold.

**Chapter IV: Results** presents the empirical findings from all three experiments. EXP-001 establishes that the synthetic generator produces a stable, reproducible reference distribution (PSI = 0 by construction). EXP-002 demonstrates that PSI increases monotonically with distortion magnitude across five distortion levels (0%–50%), validating PSI sensitivity for large shifts. EXP-003 presents the three adversarial failure modes, showing MR PSI = GREEN for all three while secondary metrics provide RED alerts, validating the multi-metric framework.

**Chapter V: Discussion and Implications** interprets the results in the context of Cambodian insurance practice and the broader emerging markets literature. It discusses the practical deployment of the multi-metric framework, the limitations of the synthetic approach (calibration uncertainty, adversarial scenario idealization), and implications for actuarial governance. The chapter concludes with recommendations for future research, including real-data validation and adaptive binning approaches.

**Chapter VI: Conclusion** synthesizes the thesis's contributions and restates the central argument: PSI is a necessary but not sufficient monitoring metric for AI underwriting in emerging markets. Multi-metric monitoring—combining PSI with feature co-occurrence, demographic distribution, and operational escalation metrics—provides the coverage needed to detect silent drift and maintain model governance standards appropriate for high-stakes underwriting decisions.

---

*Word count: approximately 1,650 words. Length: 4 pages at 1.5 spacing, Times New Roman 12pt.*
