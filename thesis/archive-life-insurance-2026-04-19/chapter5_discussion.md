# CHAPTER V. DISCUSSION AND IMPLICATIONS

---

## 5.1 Interpretation of Results

### 5.1.1 PSI Confirms Its Core Value

The EXP-001 and EXP-002 results confirm that PSI is a sound, mathematically well-behaved monitoring metric within its design envelope. The generator produces a stable, reproducible reference distribution (PSI = 0 by construction in EXP-001), and PSI responds monotonically to increasing population distortions (EXP-002). A practitioner operating a life insurance underwriting system in Cambodia can deploy PSI with confidence that it will detect large-magnitude aggregate distributional shifts.

The computational properties that make PSI attractive in practice — its reliance on histogram proportions, its interpretable KL-divergence structure, its single scalar output — are genuine advantages. PSI is easy to explain to regulators, easy to compute at scale, and easy to set alert thresholds for. This thesis does not argue for replacing PSI. It argues for supplementing it.

### 5.1.2 The Threshold Gap

The most consequential finding from EXP-002 is not that PSI is wrong, but that standard PSI thresholds may be inappropriate for Cambodia's insurance market. A 50% replacement of the applicant population with a qualitatively different risk segment produces a PSI of 0.0674 — well within the GREEN zone. If this magnitude of population change generates no alert under standard monitoring, practitioners in an emerging market context should not assume that a GREEN reading guarantees model stability.

This observation suggests a need to recalibrate PSI thresholds downward for emerging market use. A plausible set of tighter thresholds — such as GREEN < 0.05, AMBER 0.05–0.10, RED ≥ 0.10 — would convert the 50% distortion result from EXP-002 into an AMBER alert. However, recalibrating thresholds requires empirical data from real market deployments to avoid generating excessive false positives. This calibration is an important direction for future work and beyond the scope of this thesis. [CITATION NEEDED: PSI threshold recalibration methods]

### 5.1.3 Three Structural Blind Spots

The EXP-003 results provide empirical evidence of three distinct structural blind spots in PSI monitoring. Each blind spot arises from a different property of how PSI summarizes distributional information.

**Blind Spot 1 — Relational shifts (FM1)**: PSI operates on a single variable. When the *relationship between features* changes — as when a clinical intervention decouples a previously correlated pair of risk factors — the aggregate output distribution can remain stable while the model's calibration assumptions are violated. PSI cannot detect this because it has no visibility into the input feature space.

**Blind Spot 2 — Compositional shifts (FM2)**: PSI cannot detect changes in who is applying for insurance when those applicants happen to be priced correctly as individuals. The extreme age distribution PSI of 8.31 alongside MR PSI of 0.0037 demonstrates that a population can be demographically unrecognizable — entirely unlike the training population in age composition — while PSI reports perfect stability. This is the most striking failure mode because it could lead a practitioner to misplace confidence in a model that is pricing an unfamiliar population.

**Blind Spot 3 — Boundary shifts (FM3)**: PSI is a global metric. It smooths local shifts across the full distribution, making it insensitive to shifts concentrated near decision thresholds. The 3.6 percentage point HITL escalation rate increase is directly operationally significant, but its footprint in the MR histogram is too narrow to register in PSI.

All three blind spots share the same root cause: PSI is a single-variable global summary statistic. This is also what makes it simple and efficient. The implication is not that PSI is defective, but that its simplicity imposes a coverage limit that must be addressed by monitoring additional signals.

---

## 5.2 The Multi-Metric Monitoring Framework

### 5.2.1 Framework Design

Based on the experimental findings, this thesis proposes the following multi-metric monitoring framework for AI-based life insurance underwriting in emerging markets. The framework adds three targeted secondary metrics alongside the existing PSI computation, each addressing one identified blind spot.

**Table 5.1: Multi-Metric Monitoring Framework**

| Metric | Targets | Computation | Alert Threshold |
|--------|---------|-------------|----------------|
| **MR PSI** (primary) | Large aggregate distributional shifts | Standard PSI on mortality ratio histogram | AMBER ≥ 0.10, RED ≥ 0.25 |
| **Feature co-occurrence PSI** | Label drift / comorbidity confounding | PSI on P(high-risk feature pair co-occurrence) | Elevated ≥ 0.05 |
| **Marginal age distribution PSI** | Demographic cohort composition shifts | PSI on 8-bin age histogram | AMBER ≥ 0.10, RED ≥ 0.25 |
| **HITL escalation rate** | Boundary classification instability | % applicants routed to HITL vs baseline | Elevated ≥ +2 percentage points |

All four metrics are computed in parallel on each incoming applicant batch. An alert is triggered when *any* metric exceeds its threshold. This "any-fires" logic ensures that no individual failure mode goes undetected because the monitoring system was waiting for a different metric to trigger.

### 5.2.2 Alert Correlation Logic

Individual metric alerts carry different diagnostic meaning. When multiple metrics fire simultaneously, the combination narrows the probable cause:

| Alert Pattern | Most Likely Cause | Recommended Action |
|--------------|------------------|--------------------|
| MR PSI RED alone | Large aggregate distributional shift | Review model calibration; assess retraining need |
| Co-occurrence PSI elevated alone | Label drift; clinical or behavioral change affecting feature correlations | Investigate recent healthcare policy or treatment changes |
| Age PSI elevated alone | Cohort composition shift; new applicant segment entering the market | Review whether model was trained on similar demographics |
| HITL rate elevated + MR PSI GREEN | Boundary instability; lifestyle or occupational change shifting borderline applicants | Inspect applicants near MR = 1.5; consider finer boundary monitoring |
| Multiple metrics elevated simultaneously | Systemic population shift | Escalate to full actuarial review; consider model retraining |

This correlation logic is intended as guidance for the underwriting team, not a rigid decision rule. Real-world alerts will require human judgment about the plausibility of underlying causes.

### 5.2.3 Deployment Requirements

A key design property of the multi-metric framework is that it requires no model retraining. All four metrics are computed from data already flowing through the underwriting pipeline:

- MR PSI uses the mortality ratio values already computed by the underwriting engine.
- Feature co-occurrence PSI requires logging the full feature matrix per batch (applicant demographics and health conditions), rather than only the final MR value. This is a minor data engineering change.
- Age distribution PSI uses the applicant age attribute already collected during the application intake process.
- HITL escalation rate is a by-product of the routing engine's existing decision logs.

Implementation effort for a team already operating the underwriting pipeline is estimated at two to four engineering weeks, including metric computation logic, alerting infrastructure, and a monitoring dashboard. [CITATION NEEDED: MLOps monitoring implementation effort estimates]

---

## 5.3 Implications for Actuarial Governance

### 5.3.1 Cambodia Insurance Regulatory Framework

Cambodia's Insurance Regulator of Cambodia (IRC) currently does not mandate specific model validation or drift monitoring standards for AI-based underwriting systems [CITATION NEEDED: IRC regulatory framework]. As the market matures and AI adoption increases, regulatory guidance on model monitoring will become necessary to protect consumers from systematic mispricing and to ensure insurer solvency.

The multi-metric framework proposed in this thesis offers a concrete, technically grounded basis for such guidance. Its metrics are interpretable — regulators do not need expertise in machine learning to understand that a 3.6 percentage point increase in human review cases is operationally significant, or that an age distribution PSI of 8.31 indicates that the applicant pool has changed dramatically. This interpretability is a practical advantage in a regulatory context where deep technical expertise may be limited.

### 5.3.2 Applicability to Other Emerging Markets

The three failure modes identified in EXP-003 — government healthcare programs (FM1), urban professional migration (FM2), and lifestyle transitions (FM3) — are not specific to Cambodia. They represent dynamics common to insurance markets across Southeast Asia, Sub-Saharan Africa, and South Asia at analogous stages of development. The stress-testing harness developed in this research is parameterized for Cambodian demographic assumptions but is structurally transferable to other markets through adjustment of the base demographic parameters and risk multipliers in the synthetic generator.

Insurers in other emerging markets facing similar dynamics — rapid urbanization, expanding middle classes, government public health investment — can adapt the framework to their local context without fundamental methodological changes. [CITATION NEEDED: emerging market insurance dynamics, ASEAN insurance report]

### 5.3.3 AI Governance Alignment

The thesis findings are consistent with emerging international principles in AI governance. The OECD AI Principles and similar frameworks emphasize that AI systems in high-stakes domains should be monitored across multiple performance dimensions, not just primary accuracy metrics [CITATION NEEDED: OECD AI principles]. The multi-metric framework implements this principle concretely in the insurance domain: it monitors output distribution (MR PSI), input feature structure (co-occurrence PSI), demographic representation (age PSI), and operational outcomes (HITL rate) as a coordinated ensemble.

This multi-layer monitoring approach is also consistent with actuarial governance best practices in more mature markets, where A/E ratio monitoring, model performance reviews, and experience studies are conducted alongside drift metrics. [CITATION NEEDED: actuarial governance standards]

---

## 5.4 Limitations

### 5.4.1 Synthetic Data Constraints

The most significant limitation of this research is that all experiments were conducted on synthetic data calibrated to approximate Cambodia's insured population, not on real policyholder records. The demographic parameters and risk multipliers are derived from publicly available statistics and actuarial convention rather than estimated from actual Cambodian claims experience. The true mortality ratio distribution for Cambodian insureds may differ from the synthetic distribution in ways that affect which failure modes manifest most prominently and at what magnitude.

This limitation means that the secondary metric thresholds proposed in Table 5.1 — co-occurrence PSI ≥ 0.05, HITL rate +2pp — are heuristic. They successfully detect the failure modes in the synthetic experiments but may require recalibration for real deployment. Validating the framework on real anonymized policyholder data is the most important direction for future work.

### 5.4.2 Adversarial Scenario Idealization

The EXP-003 failure mode scenarios are idealized constructions designed to isolate a single type of drift. In practice, multiple drift mechanisms may occur simultaneously — for example, a government health program (FM1) coinciding with a demographic cohort shift (FM2). The behavior of the multi-metric framework under compound simultaneous drifts was not tested and represents an important gap.

Additionally, the adversarial scenarios were designed to produce clean separations between primary and secondary metric signals. Real-world drift scenarios may be noisier, producing weaker secondary signals that are harder to distinguish from natural monitoring variance.

### 5.4.3 Bin Count Sensitivity

The 8-bin PSI histogram is a conventional choice but not the only defensible one. Different bin counts may produce different PSI values for the same underlying shift, and PSI's sensitivity to boundary-concentrated shifts (FM3) could potentially be improved by using finer bins near the MR = 1.5 decision threshold. The sensitivity of both primary and secondary PSI metrics to bin count choices was not systematically investigated in this research.

### 5.4.4 Long-Term Calibration Drift

The multi-metric framework assumes a static reference distribution derived at model training time. Over longer deployment periods, even gradual legitimate market evolution — as opposed to the abrupt shifts tested in EXP-003 — will cause secondary metrics to drift upward naturally. Without a mechanism for periodically updating the reference distribution (rolling windows, seasonal adjustments), the framework may generate increasing false-positive rates over time. A reference update protocol is needed for production deployment.

---

## 5.5 Future Research Directions

**Real-data validation**: The most important next step is testing the multi-metric framework on real, anonymized Cambodian policyholder records. This would validate whether the synthetically constructed failure modes manifest empirically, whether the proposed thresholds produce acceptable false-positive rates, and whether additional failure modes not identified in this thesis emerge from real data.

**Adaptive PSI binning**: A natural improvement to both the primary MR PSI and secondary demographic PSI metrics is adaptive binning — using finer resolution near decision thresholds and coarser resolution in stable distribution tails. Adaptive binning could improve FM3 detection sensitivity without increasing overall computational cost. [CITATION NEEDED: adaptive histogram methods]

**Intelligent routing integration**: The multi-metric framework identifies when drift is occurring and which type of drift is present. A natural extension is to automate the response — routing applicants from a detected cohort shift to a pricing model calibrated for that cohort, or triggering a feature-specific recalibration when co-occurrence drift is detected. LangGraph's conditional routing architecture provides a natural implementation framework for this kind of alert-driven workflow branching, where different alert patterns trigger different remediation paths.

**Rolling reference window protocol**: A practical production requirement is a protocol for updating the reference distribution over time as the market evolves legitimately. A rolling 12-month reference window, updated quarterly, would allow the monitoring system to distinguish rapid abrupt drift (alert-worthy) from slow gradual market evolution (expected and acceptable).

**Journal publication**: The failure mode taxonomy developed in this thesis — label drift via comorbidity confounding, feature-PSI decoupling via cohort shift, and bin edge camouflage via boundary instability — may contribute to the broader machine learning monitoring literature beyond the insurance domain. These failure modes are structurally relevant to any high-stakes classification system operating on changing populations. A journal submission to a computational actuarial science or applied machine learning venue would extend the reach of these findings beyond the Cambodian insurance context.

---

*Word count: approximately 1,800 words.*
