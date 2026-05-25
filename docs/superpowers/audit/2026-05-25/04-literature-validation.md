# Literature Validation Report

**Date**: 2026-05-25
**Audited file**: `thesis/health_rl/chapter2_literature_review.md` (17 refs) + cross-chapter cited works
**Method**: Web search per citation; cross-check authors, year, venue, DOI/URL

---

## Summary

| Status | Count |
|---|---|
| Verified real — citation accurate | **15** |
| Verified real — citation context misapplied | **1** |
| Cited but missing from any references list | **2** |
| Chapter 1 grey-literature citations (paraphrased titles, sources real) | **6** |

**Headline issues:**
1. **Bastani et al. (2021)** is cited 3 times to justify the "37.8 % action accuracy ≠ oracle convergence" finding, but the paper is about *covariate-diversity-driven exploration-free greedy*, NOT a "hidden-context phenomenon". Misapplied — needs a correct citation or removal.
2. **Bastani et al. 2021** and **Shadish, Cook & Leviton 1991** appear in chapter bodies but are absent from every references list. They must be added to Ch III references for the thesis to satisfy ITC bibliography standards.
3. Chapter 1's six grey-literature references (BIMA, ADB, Swiss Re, World Bank, ILO, MAFF) use titles that don't exactly match published documents. The underlying institutions and topical reports exist, but specific subtitles/years should be tightened. The "BIMA (2022): 430,000 mobile life policies in 18 months" statistic could not be corroborated by web sources — verify against original BIMA press material or remove.

---

## Per-citation verification

### Chapter 2 (Literature Review) — 17 refs

| # | Citation (as in thesis) | Verified? | Notes / corrections |
|---|---|---|---|
| 1 | Agrawal, S., & Goyal, N. (2013). *Thompson sampling for contextual bandits with linear payoffs*. ICML, pp 127-135. | ✅ Real | Confirmed: PMLR v28, ICML 2013. arXiv:1209.3352. |
| 2 | Ban, Y., Yan, Y., Banerjee, A., & He, J. (2022). *EE-Net: Exploitation-exploration neural networks in contextual bandits*. ICLR. | ✅ Real | ICLR 2022, arXiv:2110.03177. |
| 3 | Barocas, S., Hardt, M., & Narayanan, A. (2019). *Fairness and machine learning*. fairmlbook.org. | ✅ Real | fairmlbook.org; hardcover MIT Press 2023, ISBN 9780262048613. Citation accurate. |
| 4 | Ensign, D., Friedler, S. A., Neville, S., Scheidegger, C., & Venkatasubramanian, S. (2018). *Runaway feedback loops in predictive policing*. FAccT. | ✅ Real | PMLR v81, FAccT '18, pp 160-171. arXiv:1706.09847. |
| 5 | Lattimore, T., & Szepesvári, C. (2020). *Bandit algorithms*. Cambridge UP. DOI 10.1017/9781108571401. | ✅ Real | Confirmed. ISBN 9781108486828. DOI exact. |
| 6 | Lewis, E. M. (1994). *An introduction to credit scoring* (2nd ed.). Athena Press. | ✅ Real | Edward M. Lewis, Athena Press San Rafael CA, 1994. ISBN 9789995642235. Minor: "2nd ed." not verified independently but matches description. |
| 7 | Li, L., Chu, W., Langford, J., & Schapire, R. E. (2010). *A contextual-bandit approach to personalized news article recommendation*. WWW, pp 661-670. DOI 10.1145/1772690.1772758. | ✅ Real | Exact match. arXiv:1003.0146. Received 2023 Seoul Test-of-Time Award. |
| 8 | Lin, J. (1991). *Divergence measures based on the Shannon entropy*. IEEE TIT 37(1), 145-151. DOI 10.1109/18.61115. | ✅ Real | Exact match. |
| 9 | National Institute of Statistics (NIS) & ICF. (2023). *Cambodia Demographic and Health Survey 2021–22*. | ✅ Real | Published Mar 2023 by NIS, MoH **and** ICF. Thesis omits MoH co-publisher — add it. DHS Program publication code FR377. |
| 10 | Robbins, H. (1952). *Some aspects of the sequential design of experiments*. Bull AMS 58(5), 527-535. | ✅ Real | Exact match. DOI 10.1090/S0002-9904-1952-09620-8. |
| 11 | Russo, D. J., et al. (2018). *A tutorial on Thompson sampling*. FnT in ML 11(1), 1-96. | ✅ Real | Now Publishers, DOI 10.1561/2200000070. |
| 12 | Siddiqi, N. (2006). *Credit risk scorecards*. Wiley. | ✅ Real | ISBN 9780471754510. |
| 13 | Siddiqi, N. (2012). *Credit risk scorecards* (Reprint ed.). Wiley. | ⚠ Likely real | A "2012 reprint" is plausible (Wiley reprint program), but listing both 2006 and 2012 separately is unusual — typical practice is one canonical citation. Note: Siddiqi later published a separate *Intelligent Credit Scoring* book (2017, ISBN 9781119279150) which is distinct. If you intended the 2nd edition (the rewrite), cite the 2017 book instead of a "reprint". |
| 14 | Sutton, R. S., & Barto, A. G. (2018). *Reinforcement learning: An introduction* (2nd ed.). MIT Press. | ✅ Real | ISBN 9780262039246. |
| 15 | Thomas, L. C., Edelman, D. B., & Crook, J. N. (2002). *Credit scoring and its applications*. SIAM. DOI 10.1137/1.9780898718317. | ✅ Real | Exact match. ISBN 9780898714838 (1st ed.). |
| 16 | Yurdakul, B., & Naranjo, J. (2020). *Statistical properties of the population stability index*. JRMV 14(4), 89-100. | ✅ Real | DOI 10.21314/JRMV.2020.227. JRMV Dec 2020 issue confirms publication. |
| 17 | Zhang, W., Zhou, D., Li, L., & Gu, Q. (2021). *Neural Thompson sampling*. ICLR. | ✅ Real | ICLR 2021, arXiv:2010.00827. |
| 18 | Zhou, D., Li, L., & Gu, Q. (2020). *Neural contextual bandits with UCB-based exploration*. ICML, pp 11492-11502. | ✅ Real | PMLR v119, arXiv:1911.04462. |

### Cited but missing from any references list (CRITICAL)

| # | Citation (as it appears in chapter body) | Found? | Notes |
|---|---|---|---|
| M1 | **Bastani et al. (2021)** — cited 3× in chs 3, 4_results, 5_concl as authority for "hidden-context discovery" / "bandit discovers a different but profitable policy". | ✅ Real paper, ❌ Misapplied | The actual paper is Bastani, H., Bayati, M., & Khosravi, K. (2021). *Mostly Exploration-Free Algorithms for Contextual Bandits*. Management Science 67(3), 1329-1349. arXiv:1704.09011. Its thesis is that **covariate diversity** can make naive greedy near-optimal, **not** that bandits converge to "different but profitable" policies due to missing oracle features. **Action**: either replace with a correct reference for the hidden-context / partial-information argument (consider Krishnamurthy et al. 2017 "Contextual Decision Processes with Low Bellman Rank" or Foster & Krishnamurthy 2021 *Efficient First-Order Contextual Bandits*), or rewrite the paragraph to honestly describe what Bastani et al. actually prove. |
| M2 | **Shadish, Cook, and Leviton (1991)** — cited in ch4_results §5.5.4 for the "framework of threats to validity". | ✅ Real | Foundations of Program Evaluation: Theories of Practice. Sage Publications, 1991. ISBN 9780803935518. **Note**: the canonical reference for internal/external/construct/statistical-conclusion validity is **Shadish, Cook & Campbell (2002)** *Experimental and Quasi-Experimental Designs for Generalized Causal Inference*. The 1991 book by Shadish/Cook/Leviton is a different work — it surveys evaluation theorists. If you are using the four-threats framework, cite Shadish/Cook/Campbell 2002 instead. |

### Chapter 1 — grey literature (6 refs)

These are all institutional / industry sources where the institution is real but exact titles/subtitles may not match published documents.

| # | Citation (thesis) | Status | Notes |
|---|---|---|---|
| C1 | Asian Development Bank. (2023). *Cambodia: Country diagnostic study on long-term mortgage finance*. | ⚠ Not verified | ADB has done a Cambodia Country Diagnostic Study (general) and a separate Affordable Mortgage Finance project (52187-001); no single 2023 publication with the exact title was located. Suspicion: title may have been guessed. The factual claim it supports (Wing reaching 14 million users) is a fintech/telecom statistic, not a topic mortgage diagnostics would cover. Likely **wrong source attribution** — find the actual Wing-user-count source (e.g., NBC Cambodia FinScope, Wing corporate disclosures). |
| C2 | BIMA. (2022). *Annual impact report: Mobile-delivered insurance in emerging markets*. | ⚠ Specific claim unverified | BIMA publishes impact reports, but the specific claim "430,000 mobile life policies in 18 months" with this exact framing was not corroborated. Public sources cite "more than 1 million Cambodians" cumulatively across BIMA × Smart Axiata over multiple years. **Action**: verify against original BIMA report or replace number with a corroborated figure (e.g., from Khmer Times or BIMA press release). |
| C3 | ILO. (2022). *The Cambodian garment, footwear and travel goods industry: Workforce profile and labour conditions*. | ⚠ Title paraphrased | ILO does publish on Cambodian GFT sector via Better Factories Cambodia (annual reports + bulletins). The 2022-23 Better Factories Cambodia annual report covers this content but has a different title. **Action**: either cite the exact ILO Better Factories Cambodia annual report or the ILO Cambodia GFT Sector Bulletin (https://www.ilo.org/media/407586/download). |
| C4 | Ministry of Agriculture, Forestry and Fisheries of Cambodia. (2022). *Annual report on agricultural sector performance*. | ⚠ Specific claim unverified | MAFF Cambodia does publish annual sector reports; the "2.5 million rice farmers" figure is plausible but not directly located in the 2022 report excerpts retrieved. **Action**: cite the specific page or replace with a corroborated source (e.g., FAO Cambodia country brief). |
| C5 | Swiss Re Institute. (2023). *Sigma world insurance report: Insurance penetration in emerging Asia*. | ⚠ Title paraphrased | The Swiss Re *sigma* series exists; the relevant 2023 issue is **sigma 3/2023: "World Insurance 2023: Stirred, and not shaken"**. Subtitle in thesis is invented. Penetration figures cited in Table 1.1 (Vietnam 2.5 % of GDP, Thailand 5.5 %) are roughly consistent with sigma data but should be sourced to the exact sigma issue with page reference. |
| C6 | World Bank. (2023). *Cambodia economic update: Financial inclusion and insurance market development*. | ⚠ Title paraphrased | World Bank publishes the Cambodia Economic Update twice annually. The November 2023 issue discusses financial inclusion and recommends expanding insurance products, but the document's actual title is just *Cambodia Economic Update — November 2023* (https://documents1.worldbank.org/curated/en/099112023082512660/pdf/...). The thesis subtitle is invented. |

---

## Recommended actions (prioritized)

1. **CRITICAL**: Replace or rewrite the Bastani et al. (2021) citation. The current usage misrepresents the cited paper. This is the kind of issue that will be flagged in defense Q&A and could embarrass the candidate.
2. **CRITICAL**: Add Bastani et al. (2021) and Shadish/Cook/Leviton (1991) to the References list of Chapter III — currently they appear in body text only.
3. **IMPORTANT**: Tighten Chapter 1's six institutional citations. Replace paraphrased titles with the actual document titles + URLs/page numbers. The BIMA "430,000 policies" claim needs an exact source.
4. **IMPORTANT**: Verify whether you mean Shadish, Cook & Campbell (2002) *Experimental and Quasi-Experimental Designs* (the canonical Campbellian validity text) rather than Shadish, Cook & Leviton (1991).
5. **MINOR**: Add MoH to the NIS/ICF 2023 CDHS attribution.
6. **MINOR**: Consolidate Siddiqi 2006 + Siddiqi 2012 into a single canonical reference, or replace with Siddiqi (2017) *Intelligent Credit Scoring* if that is the edition actually consulted.
