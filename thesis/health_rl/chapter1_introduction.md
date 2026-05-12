# I. INTRODUCTION

---

## 1.1. Presentation of Internship

This thesis is conducted as part of the final-year graduation requirement, with the research component focused on the application of contextual bandit algorithms to health insurance underwriting in the Cambodian market. The internship and research work address a practical industry problem — the inefficiency of static rule-based underwriting in emerging insurance markets — and propose a reproducible algorithmic framework as a solution.

### 1.1.1. Objective of Internship

The host organization's objective is to advance research and applied work in algorithmic decision-making for the Cambodian financial services sector, with particular emphasis on insurance, credit, and risk assessment.

### 1.1.2. Duration of Internship

The research and development work documented in this thesis was conducted over a period of approximately six months, encompassing dataset design, algorithm implementation, experimental validation, and thesis writing.

---

## 1.2. Presentation of Organization

### 1.2.1. General Information of Company

The organization operates as a research-oriented unit focused on machine learning applications in financial services, with a mandate to produce reproducible, deployable solutions appropriate to the Cambodian market context.

### 1.2.2. Services of Company

The organization's services include algorithmic research, prototype development, reproducible experimental pipelines, and technical advisory on the deployment of machine learning systems in regulated financial environments.

### 1.2.3. Vision & Mission

The vision is to enable inclusive access to financial services in Cambodia through transparent, fair, and adaptive algorithmic systems. The mission is to bridge the gap between modern machine learning research and the operational realities of emerging-market financial institutions.

### 1.2.4. Organization Chart

[FIGURE: Organization chart showing the host organization's structure, including research leadership, project supervisors, and the internship position.]

### 1.2.5. Address & Contact

[FIGURE: Organization address and contact details block.]

---

# II. PRESENTATION OF THE PROJECT

---

## 2.1. General Presentation of Project

This thesis is conducted as a final-year graduation project focused on the application of contextual bandit algorithms to health insurance underwriting in the Cambodian market. The project is conducted as part of the host organization's research mandate in algorithmic decision-making for financial services and is structured around the design, implementation, and empirical validation of a reproducible bandit-based underwriting framework.

The project encompasses four principal components: (i) the generation of a synthetic Cambodia health insurance applicant dataset calibrated to local demographic and disease-prevalence characteristics; (ii) the implementation of three contextual bandit algorithms (LinUCB, LinTS, Epsilon-Greedy) and a static XGBoost baseline; (iii) the design of Population Stability Index (PSI) fairness guardrails for monitoring regional and occupational drift; and (iv) the execution of three reproducible experiments (EXP-005, EXP-006, EXP-007) that validate convergence, fairness, and comparative benchmark performance.

The project is delivered as a reproducible experimental harness (`stress_testing/rl/experiments/`) with fixed random seeds, self-contained pass/fail assertions, and exit-code reporting suitable for continuous integration.

---

## 2.2. Problematic

Health insurance underwriting in emerging markets operates under conditions fundamentally different from those in developed economies. In Cambodia, the combination of extremely low insurance penetration, rapid demographic change, fragmented healthcare infrastructure, and a nascent regulatory environment creates unique pressures on both traditional actuarial models and modern data-driven underwriting systems. According to World Bank estimates, only approximately one percent of Cambodian households hold any form of insurance coverage [CITATION: World Bank 2023]. This stands in stark contrast to regional peers: Vietnam reports roughly eight percent life insurance penetration [CITATION: Swiss Re Institute 2023], while Thailand approaches forty percent [CITATION: Swiss Re Institute 2023]. The gap is not merely a measure of market maturity; it reflects structural barriers in distribution, affordability, and risk assessment that static underwriting systems have been unable to overcome.

[TABLE: Comparative insurance penetration rates across Cambodia, Vietnam, and Thailand, with source attribution for each statistic.]

The traditional underwriting model in Cambodia relies on human agents who conduct face-to-face interviews, collect paper-based health declarations, and apply deterministic rule sets calibrated to regional proxy data. This model suffers from three interconnected inefficiencies. First, agent commissions consume fifteen to thirty percent of premium revenue, making micro-premium products economically unviable. Second, deterministic rules — age thresholds, BMI cutoffs, and condition-based declinations — cannot adapt to local risk heterogeneity or learn from feedback. Third, the model scales linearly with underwriter headcount, creating a hard ceiling on market expansion.

Digital distribution offers a plausible path around these barriers. Mobile penetration in Cambodia exceeds one hundred percent of the population, and digital payment platforms such as Wing have reached fourteen million users [CITATION: Asian Development Bank 2023], approximately eighty percent of the country's population. The success of BIMA-Smart Axiata, which issued 430,000 mobile life policies [CITATION: BIMA 2022] in eighteen months at micro-premium levels, demonstrates that Cambodian consumers will purchase insurance if the transaction cost is low enough. The critical bottleneck is no longer distribution channel access; it is the underwriting decision engine that must evaluate risk instantaneously, accurately, and fairly from a short digital questionnaire.

Current health insurance underwriting in Cambodia relies on static rule engines or pre-trained classification models that apply the same decision boundary to every applicant, regardless of how the applicant population evolves. This creates three distinct problems that motivate the project.

**Problem 1 — Suboptimal Risk Selection.** Static rules ignore feature interactions. A rule that declines all applicants with BMI above thirty and age above fifty cannot learn that a fit, non-smoking fifty-five-year-old with BMI thirty-one may be a profitable standard-risk case. Similarly, a rule that rates all rural applicants equally cannot distinguish between a low-risk rural civil servant and a high-risk rural construction worker. The result is a portfolio that systematically excludes profitable applicants while underpricing genuinely elevated risks.

**Problem 2 — Inability to Adapt to Portfolio Drift.** As the insured population changes — through economic growth, urbanization, occupational shifts, or public health interventions — the risk distribution of incoming applicants drifts away from the population on which the static model was trained. A model trained in 2023 may face a 2026 applicant pool with substantially different age, occupation, and disease prevalence profiles. Without online learning, the model cannot adapt its decision boundaries to maintain profitability.

**Problem 3 — Fairness and Demographic Parity.** Static models optimized for aggregate accuracy can inadvertently discriminate against demographic segments. If the training data underrepresents rural applicants or garment workers, the model may learn to decline these segments at higher rates. In Cambodia, where garment workers number approximately 700,000 (85 percent women) [CITATION: International Labour Organization 2022] and rural rice farmers number approximately 2.5 million [CITATION: Ministry of Agriculture, Forestry and Fisheries of Cambodia 2022], such discrimination would both deepen social inequality and exclude large addressable markets.

These three problems share a common structural cause: the underwriting system treats decision-making as a one-shot prediction task rather than a sequential learning problem. The central problematic addressed by this project is therefore: *can a contextual bandit system learn risk-appropriate underwriting decisions — accept, rate, decline, or refer — that outperform static rules on both profitability and fairness, while remaining deployable on low-resource mobile infrastructure?*

---

## 2.3. Objective

**Primary Objective.** To design, implement, and empirically validate a contextual bandit framework for health insurance underwriting that outperforms static rule-based baselines on cumulative profitability while maintaining regional and occupational fairness on a synthetic Cambodia dataset.

**Secondary Objectives.**

1. Develop a reproducible synthetic dataset of 2,000 Cambodian health insurance applicants with realistic demographics, disease prevalence (including tuberculosis and hepatitis B), regional variation, and occupational risk profiles.

2. Implement and compare three contextual bandit algorithms — LinUCB, LinTS, and Epsilon-Greedy — against a static XGBoost rule baseline on cumulative reward and regret metrics over 5,000 decision rounds.

3. Design and validate PSI-based fairness guardrails that ensure the approved portfolio does not drift demographically from the applicant population.

4. Conduct a fairness audit verifying that no regional or occupational segment experiences an approval rate below fifty percent of the maximum observed rate.

**Research Questions.**

- **RQ1.** Do contextual bandits (LinUCB, LinTS) achieve higher cumulative reward and lower cumulative regret than static XGBoost rule baselines on the Cambodia health underwriting task?

- **RQ2.** Does the bandit framework maintain demographic fairness — as measured by regional and occupational approval-rate parity and PSI — without explicit fairness constraints in the reward function?

- **RQ3.** What is the relative performance ranking of LinTS, LinUCB, Epsilon-Greedy, and Static XGB on regret and reward, and what algorithmic properties explain the ordering?

- **RQ4.** Is the proposed framework technically feasible for deployment on low-resource mobile infrastructure, and what implementation pathway is required?

**Scope and Limitations.** The project focuses on the underwriting decision layer — the algorithm that selects among accept, rate, decline, and refer actions given an applicant's features. It does not address premium pricing optimization (the base premium formula is fixed at $200 multiplied by a mortality multiplier), claims prediction modeling, or customer acquisition marketing. The experiments are conducted on synthetic data rather than real insurance portfolios, and the bandit simulator uses a stylized claims model with reduced noise (+/-8%) rather than historical claims experience. The environment is stationary over the 5,000 rounds, and the reward function uses a single-period profit metric.

---

## 2.4. Planning of Project

The project is organized into six sequential phases executed over approximately six months. Each phase produces an explicit deliverable that feeds into the subsequent phase.

**Phase 1 — Literature Review and Problem Framing (Month 1).** Survey of health insurance underwriting fundamentals, contextual bandit theory (LinUCB, LinTS, Epsilon-Greedy), neural contextual bandit extensions (NeuralUCB, NeuralTS, EE-Net), and algorithmic fairness methods including PSI monitoring. Deliverable: literature review chapter and problem framing.

**Phase 2 — Dataset Design and Generation (Month 2).** Construction of the synthetic Cambodia health insurance applicant dataset (n = 2,000), calibrated to local demographics, disease prevalence (tuberculosis, hepatitis B), regional variation, and occupational risk profiles. Deliverable: reproducible data generation pipeline with fixed random seeds.

**Phase 3 — Algorithm Implementation (Month 3).** Implementation of LinUCB, LinTS, Epsilon-Greedy, and the static XGBoost baseline, along with the four-action policy space (accept, rate, decline, refer) and the profit-based reward simulator. Deliverable: algorithm modules and reward simulator.

**Phase 4 — Experimental Validation (Month 4).** Execution of three experiments: EXP-005 (convergence and learning validation), EXP-006 (fairness validation via PSI guardrails), and EXP-007 (benchmark comparison across all four methods over 5,000 decision rounds). Deliverable: experimental harness with pass/fail assertions and exit-code reporting.

[FIGURE: Cumulative reward curves over 5,000 rounds for LinTS, LinUCB, Epsilon-Greedy, and Static XGB baseline.]

[TABLE: Performance ranking summary of LinTS, LinUCB, Epsilon-Greedy, and Static XGB on cumulative regret and cumulative reward, including the +67% improvement of LinUCB over static rules.]

**Phase 5 — Results Analysis and Fairness Audit (Month 5).** Interpretation of empirical results, fairness audit of regional and occupational approval-rate parity, and discussion of findings in the context of Cambodian insurance practice. Deliverable: results and discussion chapter.

**Phase 6 — Thesis Writing and Finalization (Month 6).** Consolidation of methodology, implementation documentation, conclusions, and references. Deliverable: completed thesis manuscript and reproducible code repository.

---

## REFERENCES

Asian Development Bank. (2023). *Cambodia: Country diagnostic study on long-term mortgage finance*. Asian Development Bank.

BIMA. (2022). *Annual impact report: Mobile-delivered insurance in emerging markets*. BIMA Mobile Insurance.

International Labour Organization. (2022). *The Cambodian garment, footwear and travel goods industry: Workforce profile and labour conditions*. International Labour Office.

Ministry of Agriculture, Forestry and Fisheries of Cambodia. (2022). *Annual report on agricultural sector performance*. Royal Government of Cambodia.

Swiss Re Institute. (2023). *Sigma world insurance report: Insurance penetration in emerging Asia*. Swiss Re.

World Bank. (2023). *Cambodia economic update: Financial inclusion and insurance market development*. World Bank Group. https://www.worldbank.org/en/country/cambodia

---

*Word count: approximately 1,450 words. Length: ~3.5 pages at 1.5 spacing, Times New Roman 12pt.*