# CHAPTER II. LITERATURE REVIEW

---

## 2.1 Health Insurance Underwriting in Emerging Markets

Health insurance underwriting is the process by which an insurer evaluates an applicant's risk profile and assigns a premium and coverage terms conditional on that risk. In traditional actuarial practice, this evaluation relies on mortality tables, medical examinations, and historical claims experience. In emerging markets such as Cambodia, these inputs are often unavailable or unreliable. The absence of longitudinal health records, the concentration of healthcare access in urban centers, and the prevalence of informal employment without standardized income documentation create an information asymmetry that static underwriting models struggle to resolve [CITATION: World Bank 2024 insurance report].

Digital underwriting — in which applicants complete a short questionnaire on a mobile device and receive an instant decision — has emerged as a promising alternative. BIMA-Smart Axiata's deployment of 430,000 mobile life policies in Cambodia within eighteen months demonstrates both demand and feasibility [CITATION: BIMA case study]. However, the underwriting engines behind these products typically use simple rule-based scorecards or shallow decision trees that cannot learn from feedback or adapt to changing applicant populations. The academic literature on algorithmic underwriting in emerging markets remains sparse, with most published work focusing on credit scoring or crop insurance rather than health [CITATION: emerging market algorithmic finance survey].

---

## 2.2 Contextual Bandits for Sequential Decision Making

### 2.2.1 From Multi-Armed Bandits to Contextual Bandits

The multi-armed bandit problem, first formalized by Robbins (1952), captures the fundamental exploration-exploitation dilemma: an agent must repeatedly choose among multiple actions (arms) with unknown reward distributions, balancing the need to explore poorly understood arms against the desire to exploit arms known to yield high rewards. In the stochastic bandit setting, each arm has a fixed but unknown expected reward, and the agent's objective is to minimize cumulative regret — the difference between the reward obtained and the reward that would have been obtained by always pulling the optimal arm [CITATION: Robbins 1952; Lattimore & Szepesvari 2020].

Contextual bandits extend this framework by associating each decision round with a context vector describing the current state of the environment. In the insurance setting, the context is the applicant's feature vector (age, BMI, region, occupation, health conditions). The agent's goal is to learn a policy that maps contexts to actions in a way that maximizes expected cumulative reward. Formally, at each round $t$, the agent observes context $x_t \in \mathbb{R}^d$, selects an action $a_t \in \mathcal{A}$, and receives reward $r_t \in \mathbb{R}$ drawn from a distribution depending on $x_t$ and $a_t$ [CITATION: Li et al. 2010 LinUCB].

### 2.2.2 LinUCB and LinTS

**LinUCB** (Li et al., 2010) is the most widely studied frequentist contextual bandit algorithm. It assumes the expected reward of each action $a$ is linear in the context vector: $E[r_t | x_t, a] = \theta_a^T x_t$. The algorithm maintains a ridge regression estimate $\hat{\theta}_a$ and an associated confidence ellipsoid for each action. The selection criterion combines the estimated reward with an optimism bonus proportional to the uncertainty:

$$a_t = \arg\max_{a \in \mathcal{A}} \left( \hat{\theta}_a^T x_t + \alpha \sqrt{x_t^T A_a^{-1} x_t} \right)$$

where $A_a$ is the design matrix and $\alpha$ controls the exploration-exploitation trade-off. Li et al. proved that LinUCB achieves regret bounded by $\tilde{O}(d \sqrt{T})$, making it near-optimal for linear reward functions [CITATION: Li et al. 2010].

**LinTS** (Agrawal & Goyal, 2013) takes a Bayesian approach. Rather than constructing an explicit confidence bound, it samples a parameter vector $\tilde{\theta}_a$ from the posterior distribution $N(\hat{\theta}_a, v^2 A_a^{-1})$ and selects the action maximizing the sampled reward: $a_t = \arg\max_a \tilde{\theta}_a^T x_t$. Thompson Sampling has been shown to achieve comparable theoretical regret bounds while often outperforming UCB-based methods empirically, particularly in problems with correlated arms or complex posterior geometries [CITATION: Agrawal & Goyal 2013; Russo et al. 2018 TS tutorial].

Both algorithms are computationally efficient for low-dimensional contexts: each update requires only a rank-one matrix update and a linear solve, operations that complete in milliseconds on standard hardware. This efficiency is essential for emerging-market deployment where GPU resources may be unavailable and decision latency must remain below 200 milliseconds.

### 2.2.3 Epsilon-Greedy and Baseline Comparisons

**Epsilon-Greedy** serves as the simplest exploration baseline: with probability $\epsilon$, select a random action; otherwise, select the action with highest estimated reward. While easy to implement, Epsilon-Greedy is known to be suboptimal because it explores uniformly regardless of uncertainty — wasting exploration budget on actions that are already well understood. It remains useful as a pedagogical baseline against which to measure the value of principled uncertainty-directed exploration [CITATION: Sutton & Barto 2018].

**Static baselines** — pre-trained classification or regression models applied deterministically — represent the current industry standard. An XGBoost model trained on historical data and thresholded to produce accept/rate/decline decisions has no exploration mechanism and cannot improve from feedback. Its regret grows linearly with time, whereas bandit algorithms achieve sublinear regret. The gap between static and adaptive performance is the primary empirical quantity this thesis measures.

---

## 2.3 Neural Contextual Bandits and Dynamic Pricing

### 2.3.1 Limitations of Linear Reward Assumptions

The linear reward assumption $E[r | x, a] = \theta_a^T x$ is computationally convenient but restrictive. In health insurance underwriting, the relationship between applicant features and expected profit is almost certainly non-linear. Consider three examples:

- **Age-BMI interaction**: A BMI of thirty-two is moderately elevated for a twenty-five-year-old but carries substantially higher mortality risk for a fifty-five-year-old. A linear model can capture this only if the interaction term is explicitly engineered.
- **Regional-occupational compounding**: A construction worker in Phnom Penh has access to tertiary trauma care; a construction worker in a rural province does not. The same occupation label carries different risk depending on region, a three-way interaction that linear models learn poorly without exhaustive feature engineering.
- **Disease comorbidity clusters**: Diabetes and hypertension co-occur non-additively; the joint mortality impact exceeds the sum of individual impacts. Capturing this requires either interaction terms or a more expressive function class.

Neural contextual bandits address these limitations by replacing the linear reward model with a neural network $f_\theta(x, a)$, which can learn complex feature interactions from data.

### 2.3.2 NeuralUCB

**NeuralUCB** (Zhou et al., ICML 2020) extends the optimism principle of LinUCB to neural networks. The algorithm trains a deep neural network to predict rewards via gradient descent, then constructs an upper confidence bound using the gradient information of the network. Specifically, the confidence width at context $x$ is proportional to $\sqrt{g(x; \theta)^T A^{-1} g(x; \theta)}$, where $g(x; \theta)$ is the gradient of the network output with respect to its parameters and $A$ is the outer-product matrix of historical gradients [CITATION: Zhou et al. 2020 NeuralUCB].

Theoretical analysis shows that NeuralUCB achieves regret $\tilde{O}(\tilde{d}\sqrt{T})$, where $\tilde{d}$ is an effective dimension determined by the neural tangent kernel (NTK) of the network. In the linear case, this reduces exactly to the LinUCB bound. The practical significance is that NeuralUCB provides a principled exploration mechanism for deep models without requiring Bayesian inference or ensemble methods.

### 2.3.3 NeuralTS

**NeuralTS** (Zhang et al., ICLR 2021) extends Thompson Sampling to neural networks. At each round, the algorithm samples a neural network parameter vector from an approximate posterior and selects the action maximizing the sampled network's predicted reward. The posterior approximation uses gradient information analogous to NeuralUCB, but the sampling-based exploration often produces more adaptive behavior in practice [CITATION: Zhang et al. 2021 NeuralTS].

Empirically, NeuralTS has demonstrated strong performance on recommendation and advertising benchmarks where user preferences exhibit complex, non-linear structure. The algorithm's natural uncertainty quantification — regions of feature space with few historical observations produce high posterior variance — makes it attractive for high-stakes domains such as insurance where exploration must be cautious.

### 2.3.4 EE-Net and Hybrid Approaches

**EE-Net** (Chen et al., 2022) proposes a more radical architecture: two separate neural networks, one for exploitation and one for exploration. The exploitation network predicts expected reward; the exploration network predicts the value of exploring (the expected information gain). The final decision combines both predictions [CITATION: Chen et al. 2022 EE-Net].

A more pragmatic middle ground is the **Neural Linear Bandit**, in which a neural network learns a feature representation $\phi(x)$ from raw inputs, and a linear bandit (LinUCB or LinTS) operates on the learned representation. This approach decouples representation learning from exploration, making it more stable to train and easier to interpret. It has been successfully deployed in production systems at several technology companies [CITATION: neural linear bandit production].

### 2.3.5 Applications in Dynamic Pricing

Neural contextual bandits have become the dominant paradigm in dynamic pricing and revenue management. Amazon uses neural bandits for real-time product recommendations, where the context includes user browsing history, purchase patterns, and item embeddings, and the action space contains millions of candidate products [CITATION: Amazon bandit pricing]. Uber applies contextual bandits to adjust UberEats delivery fees in real time based on demand forecasts, courier availability, and customer price sensitivity [CITATION: Uber dynamic pricing]. Stitch Fix uses bandit algorithms to optimize inventory selection for personalized clothing boxes, learning customer preferences from keep/return feedback [CITATION: Stitch Fix bandits].

The dynamic pricing literature is particularly relevant to insurance underwriting because both problems share the same mathematical structure: a context (customer/applicant features), a finite action space (price tiers/underwriting decisions), and a noisy reward (profit/premium minus claims). The key difference is risk asymmetry: in advertising, showing a suboptimal ad costs only a click; in insurance, accepting a high-risk applicant at standard rates can generate substantial losses. This asymmetry motivates the conservative reward design and PSI guardrails proposed in this thesis.

### 2.3.6 Implications for This Thesis

While neural bandits offer superior representational capacity, they require larger datasets and more careful hyperparameter tuning than linear models. With a synthetic dataset of 2,000 records and 25 features after one-hot encoding, the risk of overfitting outweighs the potential gains from non-linear modeling. The experiments in this thesis therefore focus on linear bandits, which achieve strong performance with minimal computational requirements. The neural bandit literature review provides the theoretical foundation and implementation pathway for future work with larger, real-world Cambodian insurance portfolios.

---

## 2.4 Fairness and Population Stability in Adaptive Systems

### 2.4.1 Algorithmic Fairness in Insurance

Algorithmic fairness has received substantial attention in the machine learning literature, with definitions spanning demographic parity, equalized odds, and individual fairness [CITATION: Barocas et al. 2019 fairness book]. In insurance, fairness concerns are amplified by the industry's social role: underwriting decisions determine who receives financial protection against health shocks. A model that systematically declines applicants from rural provinces or informal occupations deepens existing inequalities.

Most fairness research focuses on static models trained on fixed datasets. Fairness in adaptive systems — where the algorithm's decisions influence the training data it sees next — introduces additional complexity. If a bandit learns that rural applicants are less profitable, it may decline them more often, reducing the rural data it receives and reinforcing the initial bias. This **feedback loop** is well documented in lending and criminal justice applications but has not been systematically studied in health insurance underwriting [CITATION: Ensign et al. 2018 feedback loops].

### 2.4.2 Population Stability Index (PSI)

The Population Stability Index (PSI) is a statistical metric for detecting distributional shifts between a reference population and a monitoring population. It is defined as:

$$\text{PSI} = \sum_{i=1}^{B} (A_i - E_i) \times \ln\left(\frac{A_i}{E_i}\right)$$

where $A_i$ is the actual proportion and $E_i$ is the expected proportion in bin $i$. PSI is a symmetric form of the Kullback-Leibler divergence; it appears in the statistical literature as the "J divergence" (Lin, 1991) [CITATION: Lin 1991]. The term "Population Stability Index" and the associated threshold values were first introduced by Lewis (1994), who proposed the benchmarks as a practical diagnostic for credit-scoring practitioners [CITATION: Lewis 1994]. Thomas et al. (2002, pp. 155 ff.) codified PSI within the credit-scoring textbook literature, and Siddiqi (2006, 2012) popularised the traffic-light system in scorecard development guides [CITATION: Thomas et al. 2002; Siddiqi 2006].

The canonical industry reference for PSI thresholds is Siddiqi (2006, reprinted 2012), who describes the traffic-light system as: GREEN ($<$ 0.10) indicates little or no shift; AMBER (0.10–0.25) signals a moderate shift requiring investigation; RED ($>$ 0.25) indicates a significant shift that may warrant model recalibration or retraining [CITATION: Siddiqi 2006]. These thresholds — sometimes called the "Lewis constants" after their originator — are widely adopted in actuarial and banking model-risk management frameworks.

A more recent statistical treatment by Yurdakul and Naranjo (2020) provides the first formal justification for the Lewis constants. They derive the asymptotic distribution of PSI under the null hypothesis of no population shift and show that the 0.10 and 0.25 benchmarks are reasonable for sample sizes typical of scorecard development (roughly 100–600 observations per bin), though they caution that the thresholds become conservative for larger samples [CITATION: Yurdakul & Naranjo 2020]. Their simulation study confirms that PSI $>$ 0.25 controls Type I error at acceptable levels while retaining power to detect meaningful distributional shifts.

In this thesis, PSI is applied not to model outputs but to demographic distributions: comparing the region and occupation distributions of the *approved* portfolio against the *applicant* population. This usage treats PSI as a fairness guardrail rather than a model-drift detector. If the approved portfolio diverges demographically from the applicant pool, the bandit may be exploiting or excluding specific segments, triggering an AMBER or RED alert regardless of profitability. The choice of PSI for this purpose is motivated by its interpretability, its symmetry with respect to the reference and monitored distributions, and its established regulatory acceptance in actuarial practice.

---

## 2.5 Gap Analysis

The literature review reveals three gaps that this thesis addresses:

1. **Domain gap**: Contextual bandits have been extensively studied in advertising, recommendation, and dynamic pricing, but their application to health insurance underwriting in emerging markets is virtually unexplored. The specific constraints of Cambodian health insurance — low data volume, mobile-first distribution, and high social value of inclusion — create a unique problem setting.

2. **Fairness gap**: Existing bandit fairness literature focuses on regret-fairness trade-offs in simulated environments. This thesis is the first to validate fairness through PSI demographic monitoring and approval-rate parity constraints on a Cambodia-calibrated dataset.

3. **Bridge gap**: While neural bandits represent the methodological frontier in dynamic pricing, no published work connects these methods to emerging-market insurance or explains when linear models suffice. This thesis provides that bridge, positioning linear bandits as the appropriate starting point while mapping the neural extension path.

---

## 2.6 Summary

This chapter has established the theoretical landscape within which the thesis operates. Contextual bandits provide a principled framework for online learning in underwriting, with LinUCB and LinTS offering strong theoretical guarantees and computational efficiency. Neural extensions — NeuralUCB, NeuralTS, and EE-Net — remove the linearity constraint at the cost of increased data requirements and training complexity. Fairness considerations and PSI monitoring provide necessary guardrails for high-stakes adaptive systems. The following chapter describes the methodology developed to validate these concepts empirically.

---

*Word count: approximately 2,200 words. Length: ~5.5 pages at 1.5 spacing, Times New Roman 12pt.*
