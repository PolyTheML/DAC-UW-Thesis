# CHAPTER III. LITERATURE REVIEW

---

## Related Work

### Health Insurance Underwriting in Emerging Markets

Health insurance underwriting is the process by which an insurer evaluates an applicant's risk profile and assigns a premium and coverage terms conditional on that risk. In traditional actuarial practice, this evaluation relies on mortality tables, medical examinations, and historical claims experience. In emerging markets such as Cambodia, these inputs are often unavailable or unreliable. The absence of longitudinal health records, the concentration of healthcare access in urban centers, and the prevalence of informal employment without standardized income documentation create an information asymmetry that static underwriting models struggle to resolve [CITATION: World Bank 2024 insurance report].

Digital underwriting — in which applicants complete a short questionnaire on a mobile device and receive an instant decision — has emerged as a promising alternative. BIMA-Smart Axiata's deployment of 430,000 mobile life policies in Cambodia within eighteen months demonstrates both demand and feasibility [CITATION: BIMA case study]. However, the underwriting engines behind these products typically use simple rule-based scorecards or shallow decision trees that cannot learn from feedback or adapt to changing applicant populations. The academic literature on algorithmic underwriting in emerging markets remains sparse, with most published work focusing on credit scoring or crop insurance rather than health [CITATION: emerging market algorithmic finance survey].

### Contextual Bandits for Sequential Decision Making

The multi-armed bandit problem, first formalized by Robbins (1952), captures the fundamental exploration-exploitation dilemma: an agent must repeatedly choose among multiple actions with unknown reward distributions, balancing the need to explore poorly understood actions against the desire to exploit actions known to yield high rewards [CITATION: Robbins 1952; Lattimore & Szepesvari 2020].

Contextual bandits extend this framework by associating each decision round with a context vector describing the current state. In the insurance setting, the context is the applicant's feature vector. The agent's goal is to learn a policy that maps contexts to actions in a way that maximizes expected cumulative reward. Formally, at each round $t$, the agent observes context $x_t \in \mathbb{R}^d$, selects an action $a_t \in \mathcal{A}$, and receives reward $r_t$ drawn from a distribution depending on $x_t$ and $a_t$ [CITATION: Li et al. 2010 LinUCB].

**LinUCB** (Li et al., 2010) is the most widely studied frequentist contextual bandit algorithm. It assumes the expected reward of each action is linear in the context vector: $E[r_t | x_t, a] = \theta_a^T x_t$. The algorithm maintains a ridge regression estimate and a confidence ellipsoid for each action, selecting the action with highest upper confidence bound. Li et al. proved that LinUCB achieves regret bounded by $\tilde{O}(d \sqrt{T})$, making it near-optimal for linear reward functions [CITATION: Li et al. 2010].

**LinTS** (Agrawal & Goyal, 2013) takes a Bayesian approach, sampling a parameter vector from the posterior distribution and selecting the action maximizing the sampled reward. Thompson Sampling has been shown to achieve comparable theoretical regret bounds while often outperforming UCB-based methods empirically [CITATION: Agrawal & Goyal 2013; Russo et al. 2018 TS tutorial].

**Epsilon-Greedy** serves as the simplest exploration baseline: with probability $\epsilon$, select a random action; otherwise, select the action with highest estimated reward. While easy to implement, it is known to be suboptimal because it explores uniformly regardless of uncertainty [CITATION: Sutton & Barto 2018].

### Neural Contextual Bandits and Dynamic Pricing

Neural contextual bandits extend linear bandits by replacing the linear reward model with a neural network, enabling the learning of complex feature interactions. This is particularly relevant to insurance underwriting, where risk factors interact non-linearly: a BMI of thirty-two carries different mortality implications for a twenty-five-year-old than for a fifty-five-year-old, and the same occupation label carries different risk depending on region and healthcare access.

**NeuralUCB** (Zhou et al., ICML 2020) extends the optimism principle of LinUCB to neural networks. The algorithm trains a deep neural network to predict rewards via gradient descent, then constructs an upper confidence bound using gradient information. The confidence width is proportional to $\sqrt{g(x; \theta)^T A^{-1} g(x; \theta)}$, where $g(x; \theta)$ is the gradient of the network output with respect to its parameters. NeuralUCB achieves regret $\tilde{O}(\tilde{d}\sqrt{T})$, where $\tilde{d}$ is an effective dimension determined by the neural tangent kernel [CITATION: Zhou et al. 2020 NeuralUCB].

**NeuralTS** (Zhang et al., ICLR 2021) extends Thompson Sampling to neural networks by sampling a parameter vector from an approximate posterior and selecting the action maximizing the sampled network's predicted reward. Empirically, NeuralTS has demonstrated strong performance on recommendation and advertising benchmarks where user preferences exhibit complex, non-linear structure [CITATION: Zhang et al. 2021 NeuralTS].

**EE-Net** (Chen et al., 2022) proposes two separate neural networks — one for exploitation and one for exploration — with the final decision combining both predictions. A more pragmatic middle ground is the **Neural Linear Bandit**, in which a neural network learns a feature representation and a linear bandit operates on the learned representation [CITATION: Chen et al. 2022 EE-Net].

These approaches have become dominant in dynamic pricing. Amazon uses neural bandits for real-time product recommendations; Uber applies contextual bandits to adjust delivery fees based on demand forecasts and customer price sensitivity; Stitch Fix uses bandit algorithms to optimize inventory selection for personalized clothing boxes [CITATIONS: Amazon, Uber, Stitch Fix bandit applications]. The dynamic pricing literature is directly relevant to insurance underwriting because both problems share the same mathematical structure: a context, a finite action space, and a noisy profit signal. The key difference is risk asymmetry: in advertising, showing a suboptimal ad costs only a click; in insurance, accepting a high-risk applicant at standard rates can generate substantial losses.

While neural bandits offer superior representational capacity, they require larger datasets and more careful hyperparameter tuning than linear models. With a synthetic dataset of 2,000 records and 25 features, the risk of overfitting outweighs the potential gains from non-linear modeling. The experiments in this thesis therefore focus on linear bandits, with the neural bandit literature providing the theoretical foundation for future work.

### Fairness and Population Stability in Adaptive Systems

Algorithmic fairness has received substantial attention in the machine learning literature, with definitions spanning demographic parity, equalized odds, and individual fairness [CITATION: Barocas et al. 2019]. In insurance, fairness concerns are amplified by the industry's social role: underwriting decisions determine who receives financial protection against health shocks.

Most fairness research focuses on static models. Fairness in adaptive systems introduces additional complexity through feedback loops: if a bandit learns that rural applicants are less profitable, it may decline them more often, reducing rural data and reinforcing initial bias [CITATION: Ensign et al. 2018].

The **Population Stability Index (PSI)** is a statistical metric for detecting distributional shifts between a reference population and a monitoring population. It is defined as $\text{PSI} = \sum_{i=1}^{B} (A_i - E_i) \times \ln(A_i / E_i)$, where $A_i$ is the actual proportion and $E_i$ is the expected proportion in bin $i$. PSI is widely used in actuarial practice with standard thresholds of GREEN ($<$ 0.10), AMBER (0.10–0.25), and RED ($>$ 0.25) [CITATION: Siddiqi 2012]. In this thesis, PSI is applied to demographic distributions — comparing approved portfolio against applicant population — as a fairness guardrail rather than a model-drift detector.

### Gap Analysis

The literature review reveals three gaps this thesis addresses: (1) contextual bandits have been extensively studied in advertising and pricing but their application to health insurance underwriting in emerging markets is virtually unexplored; (2) existing bandit fairness literature focuses on simulated environments rather than validated demographic monitoring on locally calibrated data; and (3) while neural bandits represent the methodological frontier, no published work connects these methods to emerging-market insurance or explains when linear models suffice.

---

*Formatting: Chapter heading III — Size 16 Bold ALL CAPS new page. Section "Related Work" — Size 14 Bold. Subsections — Size 12 Bold indent once. Body — Size 12, 1.5 spacing, justified.*
