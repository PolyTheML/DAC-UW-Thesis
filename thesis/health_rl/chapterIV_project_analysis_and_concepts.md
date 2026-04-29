# CHAPTER IV. PROJECT ANALYSIS AND CONCEPTS

---

## 4.1 FUNCTIONAL REQUIREMENTS

The adaptive underwriting system must satisfy the following functional requirements:

**FR-1: Synthetic Dataset Generation.** The system must generate a reproducible synthetic dataset of 2,000 Cambodian health insurance applicants with the following attributes:
- Demographics: age, BMI, smoking status, exercise frequency, family history.
- Health conditions: hypertension, diabetes, heart disease, COPD, arthritis, tuberculosis, hepatitis B.
- Region: Phnom Penh, Siem Reap, Battambang, Preah Sihanouk, Kampong Cham, Other Rural.
- Occupation: Civil Servant, Teacher, Vendor, Garment Worker, Farmer, Driver, Construction Worker.
- Economic: monthly income in USD.
- The dataset must be generated with a fixed random seed (seed = 42) to ensure full reproducibility.

**FR-2: Bandit Algorithm Implementation.** The system must implement three contextual bandit algorithms and one static baseline:
- LinUCB with configurable exploration coefficient alpha.
- LinTS with configurable posterior variance scale v2.
- Epsilon-Greedy with configurable epsilon.
- Static XGBoost baseline using a pre-trained classifier with deterministic decision rules.

**FR-3: Actuarial Reward Simulation.** The system must compute profit-based rewards for four underwriting actions:
- STANDARD: accept at base premium.
- RATED: accept at 1.25× premium.
- DECLINE: reject application.
- REFER: escalate to manual underwriter.
The reward simulator must incorporate premium levels, expected claims, adverse selection, and customer acceptance probability.

**FR-4: Fairness Monitoring.** The system must compute Population Stability Index (PSI) for region and occupation dimensions, comparing the approved portfolio distribution against the applicant population distribution. PSI alerts must be classified as GREEN (< 0.10), AMBER (0.10–0.25), or RED (> 0.25).

**FR-5: Experimental Validation.** The system must execute three experiments with self-contained pass/fail criteria:
- EXP-005: Convergence validation — LinUCB cumulative reward and regret must outperform static baseline.
- EXP-006: Fairness audit — all regional and occupational segments must pass the 50% approval-rate parity constraint.
- EXP-007: Benchmark comparison — LinTS and LinUCB must achieve lower regret than Epsilon-Greedy and Static XGB.

**FR-6: Reporting and Visualization.** The system must generate cumulative reward curves, cumulative regret curves, action distribution charts, and fairness bar charts for inclusion in the thesis and defense presentation.

---

## 4.2 NON-FUNCTIONAL REQUIREMENTS

**NFR-1: Reproducibility.** All experiments must produce identical results across runs when executed with the same random seed. The codebase must be self-contained and executable without external proprietary dependencies.

**NFR-2: Computational Efficiency.** Bandit decision latency must remain below 200 milliseconds per applicant on standard CPU hardware. No GPU should be required for inference.

**NFR-3: Fairness.** The system must not encode explicit demographic bias in the reward function. Fairness must emerge from the bandit learning process and be verified through independent PSI monitoring.

**NFR-4: Maintainability.** Code must be modular, with separate modules for dataset generation, bandit algorithms, reward simulation, fairness monitoring, and experiment execution. Each module must include docstrings and type hints.

**NFR-5: Extensibility.** The architecture must support the addition of new bandit algorithms (e.g., neural bandits) without modifying existing experiment infrastructure.

**NFR-6: Testability.** Each experiment script must exit with code 0 on pass and code 1 on fail, enabling continuous integration testing.

---

## 4.3 TOOL AND TECHNOLOGY REQUIREMENTS

The project is implemented in Python 3.11 using the following tools and libraries:

| Tool / Library | Version | Purpose |
|---------------|---------|---------|
| Python | 3.11 | Programming language |
| NumPy | 1.26+ | Numerical computation, linear algebra for bandit updates |
| pandas | 2.0+ | Data manipulation and dataset generation |
| XGBoost | 2.0+ | Static baseline classifier training |
| scikit-learn | 1.3+ | Preprocessing, model evaluation metrics |
| Matplotlib | 3.7+ | Figure generation for thesis and presentation |
| python-pptx | 0.6+ | Defense presentation automation |
| PyTorch | 2.5+ | Neural bandit literature review and future extensions |
| pytest | 7.4+ | Testing framework |

**Hardware Requirements:** Standard x86-64 CPU with 8 GB RAM. No GPU required for the linear bandit experiments; PyTorch with CUDA support is available for potential neural extensions.

**Development Environment:** Windows 11 with PowerShell; all scripts are cross-platform compatible.

---

## DETAIL CONCEPT

The adaptive underwriting system follows a modular pipeline architecture:

1. **Data Layer**: `generate_cambodia_dataset.py` produces the synthetic applicant pool.
2. **Model Layer**: `underwriting_bandit.py` implements LinUCB, LinTS, Epsilon-Greedy, and StaticXGBBaseline.
3. **Simulation Layer**: `underwriting_bandit.py` contains the actuarial reward simulator with customer acceptance model.
4. **Monitoring Layer**: Fairness audit functions compute PSI and approval-rate parity.
5. **Experiment Layer**: `exp_005_*.py`, `exp_006_*.py`, `exp_007_*.py` execute validation, fairness, and benchmark experiments.
6. **Presentation Layer**: `build_presentation.py` generates the 20-slide defense deck from experiment outputs.

[INSERT SYSTEM ARCHITECTURE DIAGRAM]

The pipeline is designed to be rerun end-to-end: dataset generation → model training → experiment execution → figure generation → presentation build. Each stage is deterministic given the fixed random seed.

---

*Formatting: Chapter heading IV — Size 16 Bold ALL CAPS new page. Sections 4.1–4.3 and DETAIL CONCEPT — Size 14 Bold. Body — Size 12, 1.5 spacing, justified.*
