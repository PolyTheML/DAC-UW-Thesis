# CHAPTER I. INTRODUCTION

---

## 1.1 Presentation of Internship

This thesis is conducted as the final project for the Master of Science degree at the Institute of Technology of Cambodia (ITC), under the supervision of Dr. Has Sothea. The research is carried out in collaboration with DAC (Decent Actuarial Consultants), a consulting firm specializing in actuarial science and insurance technology solutions for emerging markets. The internship integrates academic research in machine learning and actuarial science with practical industry challenges in digital health insurance underwriting.

The internship spans the period from [START DATE] to [END DATE], representing [X] months of full-time research and development work. The workplace is located at [DAC OFFICE ADDRESS], with regular supervision meetings held both on-site and remotely. The author's role is Research Assistant and Data Scientist, responsible for designing, implementing, and validating machine learning algorithms for adaptive insurance underwriting.

The project assigned during this internship is to develop and empirically validate a contextual bandit framework for health insurance underwriting decisions in Cambodia. The author's responsibilities include:

- Designing a synthetic dataset calibrated to Cambodian demographic and health statistics.
- Implementing contextual bandit algorithms (LinUCB, LinTS, Epsilon-Greedy) and a static XGBoost baseline.
- Building a profit-based actuarial reward simulator to evaluate underwriting decisions.
- Conducting three controlled experiments (EXP-005, EXP-006, EXP-007) to validate convergence, fairness, and benchmark performance.
- Developing PSI-based fairness guardrails to ensure demographic parity in approved portfolios.
- Documenting results and preparing the thesis manuscript and defense presentation.

### 1.1.1 Objective of Internship

The internship serves multiple objectives. Academically, it provides a practical setting for applying reinforcement learning and statistical modeling techniques to a real-world actuarial problem. Professionally, it develops expertise in the intersection of machine learning and insurance technology — a rapidly growing field in emerging markets. The internship also strengthens research skills, including experimental design, reproducible software engineering, and technical communication in both written and presentation formats.

For DAC, the internship advances the firm's research agenda in algorithmic underwriting, contributing intellectual property and experimental evidence that may inform future product development. For the Cambodian insurance industry, the research provides evidence-based guidance on whether adaptive machine learning systems can improve underwriting accuracy and fairness while remaining deployable on low-resource mobile infrastructure.

### 1.1.2 Duration of Internship

The internship commenced on [START DATE] and concluded on [END DATE], totaling approximately [X] months. The working schedule was [full-time / part-time], with [X] hours per week dedicated to thesis research and [X] hours to supporting DAC's ongoing consulting projects. Key milestones during the internship period included:

- Month 1–2: Literature review, dataset design, and baseline model development.
- Month 3–4: Bandit algorithm implementation, reward simulator calibration, and initial experiments.
- Month 5–6: Fairness audit, benchmark comparison, results analysis, and thesis writing.
- Month 7–8: Defense preparation, presentation design, and final manuscript revision.

[INSERT INTERNSHIP TIMELINE TABLE OR GANTT CHART]

---

## 1.2 Presentation of Organization

### 1.2.1 General Information of Company

DAC (Decent Actuarial Consultants) is an actuarial consulting firm focused on emerging-market insurance technology. The firm advises insurers, reinsurers, and regulators on pricing, reserving, risk management, and the application of data science to insurance operations. DAC maintains active research programs in health insurance micro-pricing, telematics-based auto insurance, and AI governance for actuarial models.

[INSERT DAC LOGO]

The firm operates from [LOCATION] and serves clients across Southeast Asia, with particular depth of experience in Cambodia, Vietnam, and Laos. DAC's team combines actuarial credentials (Fellowship of the Institute of Actuaries, Society of Actuaries) with software engineering and data science expertise.

### 1.2.2 Services of Company

DAC provides the following core services:

- **Actuarial Consulting**: Pricing and reserving for life, health, and general insurance products.
- **Insurance Technology**: Development of digital underwriting platforms, mobile distribution systems, and automated claims processing tools.
- **Data Science & AI**: Predictive modeling, risk scoring, and machine learning system design for insurance applications.
- **Regulatory Advisory**: Support for insurance regulators on solvency assessment, market conduct, and AI model governance frameworks.

### 1.2.3 Vision & Mission

**Vision**: To make quality insurance accessible to emerging-market populations through technology-driven risk assessment and affordable micro-premium products.

**Mission**: To combine actuarial rigor with modern data science to build insurance systems that are accurate, fair, and scalable — reducing transaction costs and expanding financial protection to underserved communities.

### 1.2.4 Organization Chart

[INSERT ORGANIZATION CHART SHOWING: Director / Partners → Actuarial Team → Data Science Team → Consulting Team → Intern/Research Assistant]

The author's reporting line during the internship was:

- **Academic Advisor**: Dr. Has Sothea (ITC)
- **Industry Supervisors**: Chris and Peter (DAC)
- **Peer Collaborators**: DAC data science and actuarial teams

### 1.2.5 Address & Contact

**DAC (Decent Actuarial Consultants)**
- Address: [FULL ADDRESS]
- Email: [CONTACT EMAIL]
- Website: [WEBSITE URL]

---

*Formatting: Chapter heading I — Size 16 Bold ALL CAPS new page. Sections 1.1, 1.2 — Size 14 Bold. Subsections 1.1.1, 1.2.1 — Size 12 Bold indent once. Body — Size 12, 1.5 spacing, justified.*
