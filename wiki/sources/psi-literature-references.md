# Verified Literature References — Population Stability Index (PSI)

> Compiled for thesis report writing. All references verified via publisher databases, DOI resolution, and peer-reviewed citation networks.

---

## 1. Origin of PSI and the Thresholds ("Lewis Constants")

**Lewis, E. M. (1994).** *An Introduction to Credit Scoring.* Athena Press, London.

- **Why it matters:** Lewis coined the term "Population Stability Index" and first proposed the 0.10 / 0.25 threshold values (now called the "Lewis constants") as practical diagnostics for credit-scoring practitioners.
- **Verified in:** Cited by Yurdakul & Naranjo (2020, p. 89), the arXiv paper "The Population Resemblance Statistic" (2023), and the MDPI paper "A New Measure of Population Stability" (2019).
- **Availability:** Out of print; available via inter-library loan and cited extensively in the credit-risk literature.

---

## 2. Early Credit-Scoring Textbook Reference

**Thomas, L. C., Edelman, D. B., & Crook, J. N. (2002).** *Credit Scoring and Its Applications.* SIAM Monographs on Mathematical Modeling and Computation. Philadelphia: Society for Industrial and Applied Mathematics.

- **Why it matters:** Codified PSI within the academic credit-scoring literature (pp. 155 ff.).
- **ISBN:** 978-0-89871-483-8 (1st ed., 2002)
- **URL:** https://epubs.siam.org/doi/book/10.1137/1.9780898718317
- **Note:** A 2nd edition was published in 2017 (ISBN 978-1-61197-455-3, DOI:10.1137/1.9781611974560).

---

## 3. Canonical Industry Reference for Scorecard Monitoring

**Siddiqi, N. (2006).** *Credit Risk Scorecards: Developing and Implementing Intelligent Credit Scoring.* Hoboken, NJ: John Wiley & Sons.

- **Why it matters:** The industry-standard reference that popularised the traffic-light threshold system (GREEN < 0.10, AMBER 0.10–0.25, RED > 0.25) among scorecard developers.
- **ISBN:** 978-0-471-75451-0 (hardcover, 2006)
- **Reprint:** 2012 (e-book, DOI:10.1002/9781119201731)
- **URL:** https://onlinelibrary.wiley.com/doi/book/10.1002/9781119201731
- **Note:** Siddiqi's 2017 book (*Intelligent Credit Scoring*, 2nd ed.) is a separate title with ISBN 978-1-119-27915-0. The 2006/2012 edition is the one that established the PSI conventions.

---

## 4. Statistical Validation of the Thresholds (Peer-Reviewed)

**Yurdakul, B., & Naranjo, J. (2020).** Statistical properties of the population stability index. *Journal of Risk Model Validation*, 14(4), 89–100.

- **Why it matters:** First peer-reviewed paper to derive the asymptotic distribution of PSI under the null hypothesis of no shift. Validates that the 0.10 and 0.25 thresholds control Type I error for sample sizes typical of scorecard development, while cautioning that they become conservative for large samples.
- **DOI:** 10.21314/JRMV.2020.227
- **Direct PDF:** https://wmich.edu/sites/default/files/attachments/u730/2022/PSIfinal.pdf
- **Verified in:** Cited by 30+ subsequent papers (arXiv 2307.11878, Springer 2025, etc.).
- **BibTeX:**
  ```bibtex
  @article{yurdakul2020statistical,
    title={Statistical properties of the population stability index},
    author={Yurdakul, Bilal and Naranjo, Joshua},
    journal={Journal of Risk Model Validation},
    volume={14},
    number={4},
    pages={89--100},
    year={2020},
    publisher={Infopro Digital},
    doi={10.21314/JRMV.2020.227}
  }
  ```

---

## 5. Statistical Foundation (J-Divergence)

**Lin, J. (1991).** Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory*, 37(1), 145–151.

- **Why it matters:** Introduces the "J divergence," of which PSI is a special case (symmetric KL divergence). Provides the information-theoretic foundation.
- **DOI:** 10.1109/18.61115
- **Verified in:** Cited by the arXiv information-theoretic credit-risk framework paper (2025) and 2,000+ other works.
- **BibTeX:**
  ```bibtex
  @article{lin1991divergence,
    title={Divergence measures based on the Shannon entropy},
    author={Lin, Jianhua},
    journal={IEEE Transactions on Information Theory},
    volume={37},
    number={1},
    pages={145--151},
    year={1991},
    publisher={IEEE},
    doi={10.1109/18.61115}
  }
  ```

---

## Quick Citation Summary for Reports

| Role | Author (Year) | What they contributed |
|------|---------------|----------------------|
| **Originator** | Lewis (1994) | Coined "PSI" and proposed 0.10 / 0.25 thresholds |
| **Textbook codification** | Thomas et al. (2002) | Described PSI in credit-scoring context (p. 155 ff.) |
| **Industry standardisation** | Siddiqi (2006) | Popularised traffic-light system in scorecard guides |
| **Statistical validation** | Yurdakul & Naranjo (2020) | Derived asymptotic distribution; validated thresholds |
| **Information-theoretic foundation** | Lin (1991) | J-divergence, the statistical basis of PSI |

---

## Where These Citations Appear in the Thesis Repo

- `thesis/health_rl/chapter2_literature_review.md` — §2.4.2 (full prose with inline citations)
- `thesis/health_rl/chapter3_methodology.md` — §3.4.1 (threshold table + formula)
- `thesis/health_rl/build_thesis_docx.py` — auto-generated References section
- `demo/pricing_engine.py` — `compute_psi()` docstring
- `healthrl/experiments/exp_006_fairness_audit.py` — `compute_psi()` docstring
- `AGENTS.md` — PSI threshold table with literature-basis column

---

*Last verified: 2026-05-07*
