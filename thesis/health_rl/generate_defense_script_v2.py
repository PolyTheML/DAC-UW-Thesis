"""
Generate Poly_defense_script_v2.docx and inject speaker notes
into Poly_defense_presentation_v3.pptx.

Run from C:\\DAC-UW-Thesis\\:
    python thesis/health_rl/generate_defense_script_v2.py
"""

import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.dml.color import RGBColor as DRGBColor
from pptx import Presentation

DOCX_OUT  = r"thesis\health_rl\Poly_defense_script_v2.docx"
PPTX_PATH = r"thesis\health_rl\Poly_defense_presentation_v3.pptx"
SLIDES_DIR = r"thesis\health_rl\slide_thumbnails_v3"
_APPENDIX_OFFSET = 38   # appendix A1 starts at pptx slide index 38 (0-based: slides 39-43)

# ---------------------------------------------------------------------------
# SLIDES — 43 entries: slides 1–38 + appendix A1–A5
# ---------------------------------------------------------------------------
SLIDES = [
    # ── Slide 1: Title ─────────────────────────────────────────────────────
    {
        "num": 1,
        "title": "TITLE SLIDE",
        "timing": "~1 min",
        "script": (
            "Good morning, Distinguished Committee. I am Lun Chanpoly, and I am "
            "here to defend my master's thesis — Adaptive Health Insurance "
            "Underwriting via Contextual Bandits: A Reinforcement Learning "
            "Approach for Cambodia.\n\n"
            "This work was carried out during my internship at Decent Actuarial "
            "Consultants in Phnom Penh, from March to June 2026, under the "
            "supervision of Dr. Has Sothea and the guidance of Mr. ON Radet at DAC.\n\n"
            "I hope by the end of this presentation, I can convince you that the "
            "question I was given — how do we make underwriting smarter for Cambodia "
            "— has a rigorous, honest, and practically useful answer."
        ),
    },
    # ── Slide 2: Table of Contents ─────────────────────────────────────────
    {
        "num": 2,
        "title": "TABLE OF CONTENTS",
        "timing": "~30 sec",
        "script": (
            "I will take you through five sections. We begin with why this problem "
            "matters — which I will show you through a story. Then a brief survey "
            "of what the research literature offers. Then the methodology I designed "
            "and implemented. Then the results — including some honest findings that "
            "did not go as expected. And finally, what all of this means for Cambodia.\n\n"
            "I also have five technical appendix slides available if the Committee "
            "wishes to go deeper on any specific point."
        ),
    },
    # ── Slide 3: Meet Sophea — HOOK (Sophea beat MANDATORY) ───────────────
    {
        "num": 3,
        "title": "MEET SOPHEA",
        "timing": "~1.5 min",
        "script": (
            "[Point to the left card on screen.]\n\n"
            "I would like to introduce you to Sophea. You can see her profile here "
            "on the left: 42 years old, rice farmer from Kampong Cham Province. "
            "BMI 24.1 — normal range. Non-smoker. High physical activity from field "
            "farming. One clinical flag: managed hypertension.\n\n"
            "[Point to the two amber flag boxes on the right.]\n\n"
            "In 2023, Sophea walks into a private insurer in Phnom Penh and applies "
            "for voluntary health insurance. The static rule-based system checks "
            "two fields: OCCUPATION — Agriculture. CONDITION FLAG — Hypertension. "
            "Both thresholds are crossed.\n\n"
            "[Point to the red DECLINE box.]\n\n"
            "The system decision, shown here in red: DECLINE. Sophea leaves without "
            "coverage.\n\n"
            "Was that the right answer? This research begins with that question."
        ),
    },
    # ── Slide 4: About DAC ─────────────────────────────────────────────────
    {
        "num": 4,
        "title": "ABOUT DECENT ACTUARIAL CONSULTANTS",
        "timing": "~1 min",
        "script": (
            "To answer that question, I joined Decent Actuarial Consultants — DAC "
            "— as a research intern in March 2026.\n\n"
            "DAC is a regional actuarial consultancy with offices in Taipei, Phnom "
            "Penh, and Vietnam. Their services span life and non-life insurance — "
            "appointed actuary work, IFRS 17 implementation, product development, "
            "ALM and ERM, M&A advisory, and university partnerships.\n\n"
            "Their clients include some of the insurers who work with applicants "
            "like Sophea every day. Supervised by Mr. ON Radet, my task was to "
            "design and validate an adaptive underwriting system — and build a "
            "working prototype. The thesis and demonstration you will see today "
            "are the outputs of that internship."
        ),
    },
    # ── Slide 5: Cambodia Context (Sophea beat MANDATORY) ─────────────────
    {
        "num": 5,
        "title": "CAMBODIA HEALTH INSURANCE MARKET",
        "timing": "~1.5 min",
        "script": (
            "[Point to the large stat on the left.]\n\n"
            "This number — under two percent — is the estimated health insurance "
            "penetration in Cambodia in 2023. Not 10 percent. Not 20 percent. Under "
            "two percent of the population with private voluntary health coverage.\n\n"
            "The NSSF provides mandatory coverage, but only to formal-sector workers "
            "— roughly 16 percent of the population. Private underwriting is manual "
            "and rule-based. Agent networks consume 15 to 30 percent of premium "
            "revenue. And there is no demographic-parity monitoring in practice.\n\n"
            "[Point to the SDG panel on the right.]\n\n"
            "This research connects directly to three of Cambodia's SDGs. SDG 3 — "
            "Good Health and Well-being — by widening access. SDG 1 — No Poverty "
            "— by shielding households from catastrophic health costs. SDG 10 — "
            "Reduced Inequalities — through the PSI fairness guardrail.\n\n"
            "Sophea's situation is not an edge case — she is one of the 98 percent "
            "the current market was not built for."
        ),
    },
    # ── Slide 6: Problem Statement ─────────────────────────────────────────
    {
        "num": 6,
        "title": "PROBLEM STATEMENT",
        "timing": "~1.5 min",
        "script": (
            "The static system that declined Sophea has four specific failure modes — "
            "each one visible in her case.\n\n"
            "First: Static Thresholds. Fixed cutoffs ignore context. Sophea's BMI, "
            "her physical activity, her non-smoking status — all invisible to the "
            "rule engine. Two ones triggered two thresholds and the system said no.\n\n"
            "Second: No Online Adaptation. Claims feedback never reaches the model. "
            "Static weights trained once on historical data do not update from new "
            "outcomes. Every applicant — including Sophea — is assessed against "
            "stale beliefs.\n\n"
            "Third: Demographic Blindspot. No parity metric is tracked. If the "
            "system systematically declined farmers or rural applicants at elevated "
            "rates, that pattern would be invisible to the insurer.\n\n"
            "Fourth: No Intelligent Triage. Human experts review routine cases "
            "instead of the borderline ones — like Sophea's — that actually need "
            "expert judgment.\n\n"
            "Each failure costs Sophea. Together, they define the problem."
        ),
    },
    # ── Slide 7: Research Questions ────────────────────────────────────────
    {
        "num": 7,
        "title": "RESEARCH QUESTIONS",
        "timing": "~1.5 min",
        "script": (
            "Four research questions frame this work.\n\n"
            "RQ1 asks the primary empirical question: do contextual bandits achieve "
            "higher cumulative reward and lower regret than the Static XGBoost "
            "baseline over 5,000 rounds?\n\n"
            "RQ2 asks about fairness: does the bandit framework maintain demographic "
            "parity on regional and occupational approval rates — without explicit "
            "fairness constraints baked into the reward?\n\n"
            "RQ3 asks about the ranking: what is the relative performance of LinTS, "
            "LinUCB, Epsilon-Greedy, and Static XGB?\n\n"
            "RQ4 asks about deployment feasibility: is the system technically viable "
            "for low-resource mobile infrastructure — under 200 milliseconds latency?\n\n"
            "All four questions have empirical answers in the results section. "
            "I will tell you which ones came back exactly as expected — and which "
            "ones did not."
        ),
    },
    # ── Slide 8: Objectives & Deliverables ────────────────────────────────
    {
        "num": 8,
        "title": "PROJECT OBJECTIVES & DELIVERABLES",
        "timing": "~1.5 min",
        "script": (
            "The project produced four deliverables and five measurable secondary "
            "objectives.\n\n"
            "On the left — the four deliverables.\n\n"
            "D1: a 2,000-record synthetic Cambodia health insurance dataset, anchored "
            "on CDHS 2021-22, STEPS, ILO, and WHO sources. Sophea is one of those "
            "2,000. She is statistically realistic — not a cartoon.\n\n"
            "D2: the contextual bandit underwriting engine — LinUCB, LinTS, and "
            "Epsilon-Greedy — with sub-200 millisecond latency.\n\n"
            "D3: the actuarial reward simulator that converts underwriting decisions "
            "into a profit signal the bandit can learn from.\n\n"
            "D4: the PSI fairness monitoring framework with GREEN-AMBER-RED alerts.\n\n"
            "On the right — the five secondary objectives that map directly to the "
            "experiments I will describe in the results section."
        ),
    },
    # ── Slide 9: Literature Review Section Divider ────────────────────────
    {
        "num": 9,
        "title": "SECTION DIVIDER — Literature Review",
        "timing": "~5 sec",
        "script": (
            "Before I show you the system I built, let me briefly survey what "
            "the research literature told me about how to build it."
        ),
    },
    # ── Slide 10: Literature Review ────────────────────────────────────────
    {
        "num": 10,
        "title": "LITERATURE REVIEW",
        "timing": "~2 min",
        "script": (
            "Five research areas shaped the design of this system.\n\n"
            "First: emerging-market health insurance. Reports from CDHS 2021-22, "
            "ILO 2023, and ADB established Cambodia's context. Under 2 percent "
            "penetration. NSSF covering only the formal sector. Private insurers "
            "working with manual, rule-based systems.\n\n"
            "Second: linear contextual bandits. LinUCB from Li et al. 2010 and "
            "LinTS from Agrawal and Goyal 2013 both achieve sub-linear regret of "
            "order d-root-T-log-T. This theoretical guarantee is why I chose them: "
            "provably efficient, interpretable, and low compute.\n\n"
            "Third: neural bandits. NeuralUCB, NeuralTS, and EE-Net relax the "
            "linear reward assumption. Natural future-work candidates, but they "
            "require large datasets and risk overfitting on 2,000 records.\n\n"
            "Fourth: fairness in insurance machine learning. Barocas et al. and "
            "Ensign et al. warned specifically about feedback loops that harm rural "
            "and occupational groups — exactly Sophea's category.\n\n"
            "Fifth: Population Stability Index. PSI gives us three interpretable "
            "zones: GREEN below 0.10, AMBER 0.10 to 0.25, RED above 0.25. The "
            "full review cites 25 sources in APA format."
        ),
    },
    # ── Slide 11: Algorithm Comparison ────────────────────────────────────
    {
        "num": 11,
        "title": "ALGORITHM COMPARISON",
        "timing": "~1.5 min",
        "script": (
            "[Point to the table.]\n\n"
            "Five algorithms appear in this comparison. The two highlighted rows — "
            "LinUCB and LinTS — are our proposed policies.\n\n"
            "Both achieve sub-linear regret of order d-root-T-log-T. Both have "
            "per-round cost of order d-squared — fast enough for real-time "
            "underwriting decisions. Both require only moderate data.\n\n"
            "LinUCB uses a deterministic UCB exploration bonus — a confidence "
            "interval around the estimated reward. LinTS uses posterior sampling "
            "— it draws a sample from the Bayesian posterior and picks the best "
            "arm under that sample.\n\n"
            "NeuralUCB and EE-Net are included for context. They relax the linear "
            "reward assumption but require much larger datasets and are not viable "
            "for our 2,000-record setting.\n\n"
            "Epsilon-Greedy is included as a weaker admissible baseline — it "
            "achieves only O of T to the two-thirds regret in the worst case."
        ),
    },
    # ── Slide 12: Methodology Section Divider ─────────────────────────────
    {
        "num": 12,
        "title": "SECTION DIVIDER — Methodology & Model Design",
        "timing": "~5 sec",
        "script": "Let me now show you the system I built to give Sophea a better answer.",
    },
    # ── Slide 13: System Architecture ─────────────────────────────────────
    {
        "num": 13,
        "title": "SYSTEM ARCHITECTURE",
        "timing": "~1.5 min",
        "script": (
            "[Point to the pipeline diagram left to right.]\n\n"
            "The system is a closed-loop pipeline. An applicant's context vector "
            "enters on the left. A bandit policy selects one of four underwriting "
            "arms. An actuarial reward simulator returns a profit signal. PSI and "
            "HITL guardrails monitor the decision. The final decision goes out "
            "on the right — and the reward loops back to update the bandit.\n\n"
            "Five key components:\n\n"
            "One — a 34-dimensional standardised context vector per applicant.\n\n"
            "Two — four underwriting arms: STANDARD, RATED, DECLINE, REFER.\n\n"
            "Three — actuarial simulator returning revenue minus expected claims "
            "plus noise of plus-or-minus 8 percent.\n\n"
            "Four — PSI guardrail on a 500-round sliding window.\n\n"
            "Five — HITL wrapper that escalates when the bandit's uncertainty "
            "exceeds threshold kappa.\n\n"
            "Every decision feeds back into making the next decision sharper. "
            "That is the fundamental difference from the static system."
        ),
    },
    # ── Slide 14: ZOOM-IN — Applicant Context ─────────────────────────────
    {
        "num": 14,
        "title": "ZOOM-IN: APPLICANT CONTEXT",
        "timing": "~15 sec",
        "script": (
            "We have seen the architecture pipeline from left to right. "
            "We now zoom in to the first stage — applicant context.\n\n"
            "[Point to the highlighted input block.]\n\n"
            "Each applicant is encoded as a 34-dimensional vector drawn from "
            "CDHS-anchored features. That vector is the bandit's sole input "
            "to every underwriting decision."
        ),
    },
    # ── Slide 15: Dataset & Context (Sophea beat MANDATORY) ───────────────
    {
        "num": 15,
        "title": "DATASET & CONTEXT",
        "timing": "~1.5 min",
        "script": (
            "Here is how the system sees Sophea: 34 numbers, nothing more.\n\n"
            "[Point to the stat boxes at the top.]\n\n"
            "2,000 synthetic applicants. 34 context features. 4 underwriting arms. "
            "4 real-world anchoring sources.\n\n"
            "[Point to the feature table.]\n\n"
            "The 34 dimensions come from seven feature categories. Demographics "
            "and vitals — age, gender, BMI. Lifestyle — smoking, alcohol, exercise. "
            "Social determinants — education, wealth, self-rated health. Economic "
            "features. Clinical flags — hypertension, diabetes, heart disease, "
            "COPD, arthritis, TB, hepatitis B. Region — eight one-hot encoded "
            "CDHS macro-regions. Occupation — seven one-hot encoded categories.\n\n"
            "Sophea is represented in this dataset as a vector: age 42, female, "
            "BMI 24.1, non-smoker, hypertension flag on, Kampong Cham indicator "
            "on, agriculture indicator on, and twenty-seven more features. The "
            "static system saw two of those features. The bandit sees all 34."
        ),
    },
    # ── Slide 16: ZOOM-IN — Actuarial Reward ──────────────────────────────
    {
        "num": 16,
        "title": "ZOOM-IN: ACTUARIAL REWARD",
        "timing": "~15 sec",
        "script": (
            "We have seen how the context enters the pipeline. "
            "We now zoom in to the reward stage.\n\n"
            "[Point to the highlighted reward block.]\n\n"
            "After the bandit selects an arm, the actuarial simulator scores "
            "that decision — premium revenue minus expected claims, with an "
            "adverse-selection penalty and noise of plus-or-minus 8 percent. "
            "That number is the signal that drives learning."
        ),
    },
    # ── Slide 17: Reward Simulator ─────────────────────────────────────────
    {
        "num": 17,
        "title": "ACTUARIAL REWARD SIMULATOR (TABLE 8)",
        "timing": "~1.5 min",
        "script": (
            "[Point to the reward formula at the top.]\n\n"
            "Reward equals premium revenue minus expected claims, with noise "
            "of plus-or-minus 8 percent. The adverse-selection factor of 1.35 "
            "applies when the risk multiplier exceeds 2.0 — this penalises "
            "overloading high-risk applicants who then drop out of the pool.\n\n"
            "[Point to the table rows.]\n\n"
            "STANDARD: accept at standard premium. Positive net reward for a "
            "correctly priced risk. Sophea at STANDARD earns a healthy actuarial "
            "margin.\n\n"
            "RATED: accept with a 25 percent loading. Higher revenue, but elastic "
            "demand penalises over-charging healthy applicants. The slope is "
            "negative 3.5.\n\n"
            "DECLINE: reject. Zero premium revenue. The penalty of minus $10 "
            "captures the opportunity cost of refusing a viable applicant.\n\n"
            "REFER: escalate to human. Deferred reward — 70 percent of the best "
            "available arm, minus $35 review cost. This incentivises selective "
            "escalation, not blanket referral."
        ),
    },
    # ── Slide 18: ZOOM-IN — Bandit Policy & Action ────────────────────────
    {
        "num": 18,
        "title": "ZOOM-IN: BANDIT POLICY & ACTION",
        "timing": "~15 sec",
        "script": (
            "We have seen how the reward is constructed. "
            "We now zoom in to the decision stage.\n\n"
            "[Point to the highlighted policy block.]\n\n"
            "The bandit computes a UCB score for each of the four arms — "
            "STANDARD, RATED, DECLINE, REFER — and selects the argmax. "
            "This is the step where the exploration-exploitation trade-off "
            "meets the actuarial judgment."
        ),
    },
    # ── Slide 19: Bandit Build-Up — Context (Sophea beat MANDATORY) ────────
    {
        "num": 19,
        "title": "BANDIT IN ACTION: SOPHEA'S CONTEXT & ARM SCORES",
        "timing": "~1.5 min",
        "script": (
            "Step one: Sophea's vector enters the bandit.\n\n"
            "[Point to the left feature list.]\n\n"
            "`age_std=0.3, bmi_std=−0.1, smoker=0, hypertension=1, "
            "kampong_cham=1, agriculture=1` — and twenty-eight more standardised "
            "features. This 34-dimensional vector is the bandit's complete and "
            "only view of Sophea. No underwriter notes. No prior history.\n\n"
            "[Point to the LinUCB formula on the right.]\n\n"
            "The LinUCB arm score formula: theta-hat transposed Sophea's vector, "
            "plus alpha times the square root of her vector transposed A-inverse "
            "her vector. The second term is the exploration bonus — large early "
            "in training when A is sparse, shrinking as the gram matrix fills in.\n\n"
            "The bandit computes this score for each of the four arms — RATED, "
            "STANDARD, DECLINE, REFER — and takes the argmax."
        ),
    },
    # ── Slide 20: Bandit Build-Up — Selection (Sophea beat MANDATORY) ──────
    {
        "num": 20,
        "title": "POLICY LADDER: CUMULATIVE REWARD OVER 5,000 ROUNDS",
        "timing": "~2 min",
        "script": (
            "[Point to the argmax banner at the top.]\n\n"
            "ArgMax = STANDARD (0.52). The bandit gives Sophea the right answer.\n\n"
            "After sufficient training, the computed arm values for Sophea are: "
            "RATED 0.31, STANDARD 0.52, DECLINE 0.10, REFER 0.28. The STANDARD "
            "arm wins by a clear margin. The system issues coverage at the correct "
            "actuarial price.\n\n"
            "[Point to the policy ladder table.]\n\n"
            "Here is the full policy ladder across 5,000 rounds. Oracle — the "
            "theoretically perfect policy — earns $126,804. That is the ceiling.\n\n"
            "LinTS earns $93,723 at plus 29.8 percent over Static XGB. LinUCB "
            "earns $91,864 at plus 27.2 percent. Epsilon-Greedy earns $76,441. "
            "Static XGB — the system that declined Sophea — earns $72,206.\n\n"
            "[Point to the note at the bottom.]\n\n"
            "AlwaysRATED earns $122,287 — between Oracle and LinTS. This is "
            "reported honestly in the note: commercially and regulatorily "
            "inadmissible. It cannot be deployed. The admissible comparison "
            "is LinUCB versus Static XGB."
        ),
    },
    # ── Slide 21: ZOOM-IN — Fairness Guardrail & HITL ─────────────────────
    {
        "num": 21,
        "title": "ZOOM-IN: FAIRNESS GUARDRAIL & HITL",
        "timing": "~15 sec",
        "script": (
            "We have seen how the bandit selects actions and receives rewards. "
            "We now zoom in to the guardrails.\n\n"
            "[Point to the highlighted PSI and HITL blocks.]\n\n"
            "The PSI monitor checks demographic parity on a 500-round sliding "
            "window. The HITL wrapper catches decisions where the bandit is "
            "uncertain. Together these two layers ensure the system remains "
            "fair, auditable, and safe to deploy."
        ),
    },
    # ── Slide 22: PSI Guardrail ────────────────────────────────────────────
    {
        "num": 22,
        "title": "PSI FAIRNESS GUARDRAIL",
        "timing": "~1.5 min",
        "script": (
            "[Point to the traffic-light zones.]\n\n"
            "The PSI guardrail monitors the approved-portfolio distribution against "
            "the applicant population on a rolling 500-round window — separately "
            "for region and occupation.\n\n"
            "PSI equals the sum over each segment of: actual approval percentage "
            "minus expected percentage, times the natural log of actual over expected. "
            "This follows Siddiqi 2006, validated by Yurdakul and Naranjo 2020.\n\n"
            "GREEN below 0.10 — no significant shift, policy is stable.\n\n"
            "AMBER 0.10 to 0.25 — moderate shift, monitor closely, flag for review.\n\n"
            "RED above 0.25 — major shift, halt or recalibrate the bandit, escalate "
            "to compliance.\n\n"
            "The EXP-006 result: LinUCB sits GREEN on all 8 regions and 7 occupations "
            "across 20 seeds. Mean PSI 0.042 for region and 0.037 for occupation. "
            "Sophea's Kampong Cham region PSI: 0.082 — GREEN. Her occupation "
            "category PSI max: 0.123 — AMBER, in the monitor zone, below RED."
        ),
    },
    # ── Slide 23: HITL Wrapper ─────────────────────────────────────────────
    {
        "num": 23,
        "title": "HUMAN-IN-THE-LOOP (HITL) WRAPPER",
        "timing": "~1.5 min",
        "script": (
            "[Point to the four-step loop on the left.]\n\n"
            "The HITL wrapper adds a safety layer on top of the bandit.\n\n"
            "Step 1: the bandit selects an arm as usual. Step 2: if the margin "
            "between the best and second-best arm score is below threshold kappa "
            "of 0.7 — the system is genuinely uncertain — the case is escalated "
            "to REFER. Step 3: a human actuary reviews the full context and makes "
            "the final call. Step 4: the system performs a dual update — updating "
            "both the selected arm on the human label, and penalising the REFER "
            "arm to prevent over-selection.\n\n"
            "[Point to the gotcha card on the right.]\n\n"
            "The dual update is critical. Without it, REFER accumulates reward "
            "without cost, creating an over-selection spiral. This was an "
            "implementation gotcha discovered during EXP-008 development.\n\n"
            "The headline result: plus 6.5 percent reward gain over vanilla bandit, "
            "at a review rate of only 1.5 percent. 75 applications reviewed out "
            "of 5,000. That is the value of targeted human judgment."
        ),
    },
    # ── Slide 24: Experimental Design ─────────────────────────────────────
    {
        "num": 24,
        "title": "EXPERIMENTAL DESIGN",
        "timing": "~1.5 min",
        "script": (
            "[Point to the statistics protocol banner.]\n\n"
            "Every experiment follows the same rigorous protocol: 20 independent "
            "seeds, bootstrap 95 percent confidence intervals, paired Wilcoxon "
            "signed-rank tests, Bonferroni correction for multiple comparisons, "
            "and Cohen's d effect sizes.\n\n"
            "[Point to the experiment table.]\n\n"
            "Nine experiments in total.\n\n"
            "EXP-005 is the primary pre-registered test — LinUCB versus Static XGB "
            "over 5,000 rounds, 20 seeds. This is the experiment that answers RQ1.\n\n"
            "EXP-006 runs the six fairness criteria — PSI plus EEOC four-fifths "
            "rule — answering RQ2.\n\n"
            "EXP-007 is the full benchmark ladder using Common Random Numbers for "
            "variance reduction.\n\n"
            "EXP-008 to EXP-015 cover HITL, drift adaptation, cold start, "
            "ablation, regret bound validation, and drift rescue — progressively "
            "interrogating the system's boundaries."
        ),
    },
    # ── Slide 25: Results Section Divider ──────────────────────────────────
    {
        "num": 25,
        "title": "SECTION DIVIDER — Results & Evaluation",
        "timing": "~5 sec",
        "script": (
            "Let me now tell you what the system actually did — including what it "
            "got right, what it got wrong, and what I reported honestly either way."
        ),
    },
    # ── Slide 26: Baseline Ladder (Sophea beat MANDATORY + AlwaysRATED honesty) ─
    {
        "num": 26,
        "title": "THE BASELINE LADDER",
        "timing": "~2 min",
        "script": (
            "[Point to the full ladder table.]\n\n"
            "This is the complete baseline ladder across 20 seeds. Oracle sits at "
            "$126,804 — the theoretical ceiling. LinTS at $93,723. LinUCB at "
            "$91,864. Both are highlighted in green as our proposed admissible "
            "policies.\n\n"
            "[Point to the AlwaysRATED row.]\n\n"
            "I want to be direct about this number — $122,287. AlwaysRATED beats "
            "both bandits. I report this honestly. AlwaysRATED is inadmissible: "
            "no Cambodian insurer can apply a blanket 25% surcharge to every "
            "applicant regardless of risk. Our claim is scoped to admissible "
            "policies. Among those, bandits rank first and second.\n\n"
            "That +25.2% is the gap between 2023 Sophea and 2026 Sophea — between "
            "the static system that declined her and the bandit that learned to "
            "see her correctly.\n\n"
            "Two additional points of transparency:\n\n"
            "LinTS versus LinUCB: p equals 0.87. They are statistically tied at "
            "the top of the admissible set. I do not claim one beats the other.\n\n"
            "AlwaysSTANDARD earns only $34,684 — well below Static XGB. A naive "
            "all-approve policy is not the answer."
        ),
    },
    # ── Slide 27: EXP-005 Convergence (25.2% mention MANDATORY) ─────────────
    {
        "num": 27,
        "title": "EXP-005: CONVERGENCE VALIDATION",
        "timing": "~1.5 min",
        "script": (
            "[Point to the metrics on the left.]\n\n"
            "EXP-005 is the pre-registered primary experiment. Paired Wilcoxon "
            "test across 20 independent seeds, LinUCB versus Static XGB.\n\n"
            "LinUCB cumulative reward: $90,540 plus-or-minus $5,382, 95 percent CI "
            "[88,287 – 92,886]. Static XGB: $72,292 plus-or-minus $4,120, CI "
            "[70,646 – 74,136].\n\n"
            "Improvement: plus $18,248 — that is +25.2%. Cohen's d equals 2.98. "
            "P less than 0.001.\n\n"
            "[Point to the bottom banner.]\n\n"
            "+25.2% is the gap between 2023 Sophea and 2026 Sophea — between the "
            "system that declined her and the bandit that learned to price her correctly.\n\n"
            "[Point to the convergence panel on the right.]\n\n"
            "The convergence indicators confirm the learning is genuine. Action "
            "entropy drops from 1.314 to 1.105 nats — exploration giving way to "
            "exploitation. Oracle-agreement in the last 500 rounds reaches 37.8 "
            "percent. And the regret curve follows O of root-T — log-log slope "
            "0.572, R-squared 0.9915. All five EXP-005 criteria: PASSED."
        ),
    },
    # ── Slide 28: EXP-006 Fairness Audit ──────────────────────────────────
    {
        "num": 28,
        "title": "EXP-006: FAIRNESS AUDIT",
        "timing": "~2 min",
        "script": (
            "The fairness audit evaluates six pre-registered criteria. Five passed. "
            "One failed — and I want to address that failure directly.\n\n"
            "[Point to the six criterion cards.]\n\n"
            "Region PSI: 0.082 — GREEN. Occupation PSI: 0.123 — AMBER, in the "
            "monitor zone but below RED. Region parity at 85.72 percent — above "
            "the 80 percent four-fifths threshold. Occupation parity at 90.12 "
            "percent — also above 80 percent. Region permutation test: p equals "
            "0.132 — no significant association.\n\n"
            "[Point to the amber Criterion 6 card.]\n\n"
            "Criterion 6 — occupation-to-action independence — FAILED, p less "
            "than 0.001. The system's decisions are statistically associated "
            "with occupation.\n\n"
            "My interpretation: occupation is an actuarially valid risk factor. "
            "Rice farmers, garment workers, and office workers carry genuinely "
            "different health risk profiles. The association is statistically "
            "significant but practically small — no regulatory threshold is "
            "breached. I call this FAILED-with-interpretation. I stand by that "
            "verdict. PSI is a monitor, not an enforcer — constrained-action "
            "guardrails are future work."
        ),
    },
    # ── Slide 29: EXP-007 Benchmark ────────────────────────────────────────
    {
        "num": 29,
        "title": "EXP-007: BENCHMARK COMPARISON (CRN)",
        "timing": "~1.5 min",
        "script": (
            "EXP-007 uses the CRN — Common Random Numbers — harness for variance "
            "reduction. All policies run on the same sequence of applicant draws, "
            "making comparisons sharper.\n\n"
            "[Point to the left table.]\n\n"
            "AlwaysRATED leads at $122,287 — as expected and reported honestly. "
            "LinTS at $93,723. LinUCB at $91,864. Epsilon-Greedy at $76,441. "
            "Static XGB at $72,206.\n\n"
            "[Point to the pairwise comparison cards on the right.]\n\n"
            "LinTS versus LinUCB: p equals 0.87, d equals 0.26 — TIED. They are "
            "statistically indistinguishable at the top of the admissible set.\n\n"
            "LinUCB versus Static XGB: minus $19,774 regret, p less than 0.001, "
            "d equals negative 3.41 — WIN.\n\n"
            "LinTS versus Static XGB: minus $21,400 regret, p less than 0.001, "
            "d equals negative 3.89 — WIN.\n\n"
            "Two coexisting findings: adaptive bandits decisively beat the frozen "
            "static rule. And the trivial constant AlwaysRATED still beats all "
            "bandits — honestly reported."
        ),
    },
    # ── Slide 30: EXP-008 HITL ────────────────────────────────────────────
    {
        "num": 30,
        "title": "EXP-008: HUMAN-IN-THE-LOOP",
        "timing": "~1.5 min",
        "script": (
            "[Point to the key metrics.]\n\n"
            "EXP-008 evaluates the HITL wrapper with kappa of 0.7 — the headline "
            "setting.\n\n"
            "HITL reward: $102,100. Vanilla bandit: $95,872. Improvement: plus "
            "$6,228 — that is plus 6.5 percent. Review cost: $2,625 — about 2.6 "
            "percent of reward. Human overrides: 75 out of 5,000 applications. "
            "A review rate of 1.5 percent. Alignment score between human expert "
            "and bandit: 60 percent.\n\n"
            "[Point to the note at the bottom.]\n\n"
            "Important scope note: plus 6.5 percent is versus the vanilla bandit "
            "— not versus AlwaysRATED, not versus Static XGB. This measures the "
            "incremental value of targeted human oversight on top of the bandit "
            "baseline.\n\n"
            "Thirteen applicants reviewed per thousand. The actuary's judgment "
            "on those thirteen cases is worth a 6.5 percent gain on the whole "
            "portfolio. That is the value of the HITL layer."
        ),
    },
    # ── Slide 31: EXP-011+EXP-015 — What Drives the Value? ────────────────
    {
        "num": 31,
        "title": "WHAT DRIVES THE VALUE? (EXP-011 + EXP-015)",
        "timing": "~2 min",
        "script": (
            "[Point to the left ablation panel.]\n\n"
            "EXP-011 tells us the exploration bonus is not what drives the value "
            "— Greedy-only ties full LinUCB. The value comes from online ridge "
            "updating. EXP-015 tells us that even under drift, the constant beats "
            "us. These two findings together define the boundary of what this "
            "thesis can and cannot claim.\n\n"
            "On the left: EXP-011. Full LinUCB versus Greedy-only with alpha "
            "equals zero. p equals 0.580, d equals 0.13 — statistically tied. "
            "Exploration is not load-bearing.\n\n"
            "But Greedy-only versus Static XGB: plus $18,969, p less than 0.001, "
            "d equals 3.01. Online ridge updating IS the mechanism. The bandit "
            "beats Static XGB not because of its UCB exploration bonus but because "
            "it updates its ridge estimator from every new applicant.\n\n"
            "[Point to the right drift panel.]\n\n"
            "On the right: EXP-015. Under a realistic drift shock, AlwaysRATED "
            "earns $99,321. LinTS earns $71,429 — minus 39 percent. LinUCB earns "
            "$71,373 — minus 39.2 percent. The discounted LinUCB with gamma of "
            "0.999 earns $70,995 — no meaningful improvement.\n\n"
            "Non-stationarity does not rescue the bandit. We honestly report this "
            "as a boundary of the current framework."
        ),
    },
    # ── Slide 32: EXP-010+013 — Cold Start & Regret Bound ─────────────────
    {
        "num": 32,
        "title": "COLD START & REGRET BOUND (EXP-010 + EXP-013)",
        "timing": "~1.5 min",
        "script": (
            "[Point to the cold start table on the left.]\n\n"
            "EXP-010 asks: at what horizon does the bandit certify its superiority? "
            "This matters because a real insurer cannot wait 5,000 applicants "
            "before trusting the system.\n\n"
            "At T equals 200, FreshXGB leads bandits by 2.1 times. At T equals "
            "500, still 1.26 times. At T equals 1,000, the systems tie. At T "
            "equals 2,000, bandits cross over and take the lead.\n\n"
            "Operational implication: warm-start required for the first 1,000 to "
            "2,000 applications. A hybrid deployment — XGBoost until crossover, "
            "bandit thereafter — is the practical path.\n\n"
            "LinTS passes the T equals 2,000 Wilcoxon test with p equals 0.0039. "
            "LinUCB draws level but is not certified — p equals 0.0840. I report "
            "LinUCB honestly as draws-level, not a proven win at 2,000.\n\n"
            "[Point to the regret bound panel on the right.]\n\n"
            "EXP-013: log-log slope 0.572, theory 0.5 — near-optimal. R-squared "
            "0.9915. Sublinear regret confirmed empirically."
        ),
    },
    # ── Slide 33: Live Demo (Sophea beat MANDATORY) ─────────────────────────
    {
        "num": 33,
        "title": "LIVE DEMONSTRATION",
        "timing": "~3 min",
        "script": (
            "[Open browser at localhost:8000 before this slide.]\n\n"
            "I will now show you Sophea's application — not as a number in a "
            "table, but as a live interaction with the prototype dashboard.\n\n"
            "[Enter Sophea's profile: age 42, female, BMI 24.1, smoker: no, "
            "hypertension: yes, Kampong Cham, agriculture.]\n\n"
            "Enter Sophea's profile live — show STANDARD decision. Age 42, female, "
            "BMI 24.1, non-smoker, hypertension managed, Kampong Cham, agriculture. "
            "The bandit sees her 34 features, computes the arm scores, and issues "
            "its decision.\n\n"
            "[Show the STANDARD decision.]\n\n"
            "STANDARD premium. The correct actuarial answer. The one she was denied "
            "in 2023.\n\n"
            "[Submit a high-risk applicant — older, smoker, high BMI, multiple flags.]\n\n"
            "Now a higher-risk applicant. The system selects REFER — escalating "
            "to the HITL queue. Switch to the HITL tab to show the running referral "
            "rate and cumulative review cost.\n\n"
            "[This is the FastAPI prototype deployed on Render — not a mockup.]\n\n"
            "This is not a simulation. This is the same FastAPI stack described "
            "in the thesis, deployed on Render, running in real time."
        ),
    },
    # ── Slide 34: Conclusion Section Divider ───────────────────────────────
    {
        "num": 34,
        "title": "SECTION DIVIDER — Conclusion & Future Work",
        "timing": "~5 sec",
        "script": "Let me bring this back to Sophea — and to the four key findings.",
    },
    # ── Slide 35: 4 Key Findings — Sophea Resolution (MANDATORY) ──────────
    {
        "num": 35,
        "title": "4 KEY FINDINGS",
        "timing": "~2.5 min",
        "script": (
            "[Point to Finding 1.]\n\n"
            "Finding 1 — EXP-005: Online adaptation beats static rules. Plus 25.2 "
            "percent, p less than 0.001, d equals 2.98. LinUCB earns plus $18,248 "
            "over Static XGB across 20 seeds.\n\n"
            "[Point to Finding 2.]\n\n"
            "Finding 2 — EXP-006: No demographic bias introduced. 85.72 and 90.12 "
            "percent parity for region and occupation. PSI GREEN-AMBER throughout. "
            "Criterion 6 FAILED-with-interpretation — occupation is an actuarially "
            "valid signal, not a bias.\n\n"
            "[Point to Finding 3.]\n\n"
            "Finding 3 — EXP-011: The mechanism is online ridge updating, not "
            "exploration. Greedy-only ties full LinUCB. The value comes from "
            "learning, not from exploration bonuses.\n\n"
            "[Point to Finding 4.]\n\n"
            "Finding 4 — EXP-008: HITL adds value at low cost. Plus 6.5 percent "
            "at 1.5 percent review rate. Alignment score 60 percent — human "
            "oversight is meaningful.\n\n"
            "In 2023, the static system issued DECLINE. Sophea left without "
            "coverage. In 2026, the bandit issues STANDARD premium — the correct "
            "actuarial answer. That is the 25.2%. It is not everything "
            "— a trivial constant earns more. But it is a principled, fair, "
            "auditable step forward for an insurance market that needs one."
        ),
    },
    # ── Slide 36: Limitations ──────────────────────────────────────────────
    {
        "num": 36,
        "title": "LIMITATIONS",
        "timing": "~1.5 min",
        "script": (
            "I want to be transparent about the boundaries of this work.\n\n"
            "[Point to the four limitation cards.]\n\n"
            "First: synthetic data. 2,000 records cannot capture rare comorbidities, "
            "fraud patterns, or the full complexity of real Cambodian claims. The "
            "dataset is CDHS-anchored but not real insurance claims.\n\n"
            "Second: single-period rewards. The reward function is a one-shot "
            "proxy for profitability. It does not capture multi-year claims, "
            "customer retention, or renewal cycles.\n\n"
            "Third: stationarity assumption. EXP-009 and EXP-015 partially address "
            "this, but DiscountedLinUCB helps only marginally under a shock. "
            "Non-stationarity remains a meaningful limit of the current design.\n\n"
            "Fourth: the constant-policy ceiling. AlwaysRATED beats bandits by "
            "roughly 30 percent. Bandits lead every admissible deployable alternative "
            "— but the headroom to Oracle remains large. This is honestly reported "
            "and defines the next phase of work."
        ),
    },
    # ── Slide 37: Future Work ──────────────────────────────────────────────
    {
        "num": 37,
        "title": "FUTURE WORK",
        "timing": "~1 min",
        "script": (
            "Four directions for future work.\n\n"
            "First: non-stationary drift. DiscountedLinUCB plus PSI early-warning "
            "pipeline, with threshold-adaptive forgetting factors. The current "
            "gamma of 0.999 helped only marginally — better discount schedules "
            "need investigation.\n\n"
            "Second: neural bandit extensions. NeuralUCB and Neural-Linear hybrids "
            "would relax the linear reward assumption. Viable once dataset size "
            "scales beyond 2,000 records.\n\n"
            "Third: live A/B deployment. Delayed reward via survival proxy — "
            "real claims lag 6 to 24 months. The thesis uses a simulator; a live "
            "trial with real Cambodian insurers is the natural next step.\n\n"
            "Fourth: multi-period customer value. Customer lifetime value, "
            "retention, and cross-selling would move the system beyond the "
            "single-decision reward framing."
        ),
    },
    # ── Slide 38: Thank You / Q&A ──────────────────────────────────────────
    {
        "num": 38,
        "title": "THANK YOU / Q&A",
        "timing": "~30 sec",
        "script": (
            "[The slide reads: 2023: DECLINE. 2026: STANDARD.]\n\n"
            "That is the story of this thesis.\n\n"
            "In 2023, the static system declined Sophea. In 2026, the bandit "
            "issues STANDARD premium. Cambodia has hundreds of thousands of "
            "applicants like her — people whose risk profiles are nuanced, whose "
            "context matters, and who deserve a decision system capable of seeing "
            "them fully.\n\n"
            "Thank you, Distinguished Committee, for your time and attention.\n\n"
            "I am now ready for your questions. If it would be helpful, I have "
            "five appendix slides available: A1 covers the complete baseline "
            "ladder with all nine policies; A2 reconciles the three reward-lift "
            "numbers — plus 25.2, plus 29.8, and plus 6.5 percent; A3 shows all "
            "six fairness criteria verdicts; A4 has the full mathematical details "
            "for LinUCB, PSI, and the HITL dual update; and A5 has the full "
            "sensitivity parameter tables."
        ),
    },
    # ── Appendix A1: Complete Baseline Ladder ─────────────────────────────
    {
        "num": "A1",
        "title": "A1: COMPLETE BASELINE LADDER",
        "timing": "if asked",
        "script": (
            "[Show if Committee asks about AlwaysRATED or the full ranking.]\n\n"
            "The complete ladder across all nine policies — 20 seeds, CRN harness.\n\n"
            "Oracle: $126,804 — theoretical ceiling, not deployable. "
            "LogisticOracle: $123,977 — fit in-sample on oracle labels, not "
            "deployable, diagnostic only.\n\n"
            "AlwaysRATED: $122,287. This is the trivial constant that applies a "
            "blanket 25% loading to every applicant regardless of risk. No "
            "Cambodian insurer can commercially or regulatorily apply this "
            "uniformly. It would create severe adverse selection, drive healthy "
            "applicants out of the pool, and face regulatory challenge. "
            "Our pre-registered expectation was that bandits would outperform "
            "AlwaysRATED. That expectation was falsified. We report it as the "
            "scientifically informative outcome it is.\n\n"
            "LinTS: $93,723. LinUCB: $91,864. Both proposed admissible policies.\n\n"
            "Epsilon-Greedy: $76,441. Static XGB (the system that declined Sophea): "
            "$72,206. AlwaysSTANDARD: $34,684. Random: $1,980.\n\n"
            "The headline claim stands: bandits rank first and second among every "
            "admissible policy a real insurer could deploy."
        ),
    },
    # ── Appendix A2: Number Reconciliation ────────────────────────────────
    {
        "num": "A2",
        "title": "A2: NUMBER RECONCILIATION",
        "timing": "if asked",
        "script": (
            "[Show if Committee asks why there are multiple reward-lift numbers.]\n\n"
            "Three different reward-lift numbers appear across the thesis. They "
            "answer three different questions and are mutually consistent.\n\n"
            "Plus 25.2 percent: EXP-005. LinUCB versus Static XGB. Pre-registered "
            "primary metric. Paired design, 20 seeds, standardised evaluation. "
            "LinUCB mean $90,540 versus Static XGB mean $72,292. This is the "
            "headline figure cited throughout the thesis.\n\n"
            "Plus 29.8 percent: EXP-007. LinTS versus Static XGB. CRN benchmark "
            "harness — common random numbers for variance reduction. Different "
            "experimental setup from EXP-005, which is why the number is slightly "
            "higher. Reported for completeness; the pre-registered comparison "
            "is EXP-005.\n\n"
            "Plus 6.5 percent: EXP-008. HITL reward versus vanilla bandit. "
            "HITL $102,100 versus vanilla $95,872 on seed 42. Completely different "
            "baseline — this measures the incremental value of human oversight "
            "on top of the bandit, not versus Static XGB.\n\n"
            "When I cite the headline result, I cite 25.2 percent — the "
            "conservative pre-registered figure."
        ),
    },
    # ── Appendix A3: All 6 Fairness Criteria ──────────────────────────────
    {
        "num": "A3",
        "title": "A3: ALL 6 FAIRNESS CRITERIA",
        "timing": "if asked",
        "script": (
            "[Show if Committee asks about the fairness methodology or Criterion 6.]\n\n"
            "The six pre-registered fairness criteria.\n\n"
            "Criterion 1: Region PSI must be at or below 0.25. Result: PSI equals "
            "0.082 — GREEN. PASSED.\n\n"
            "Criterion 2: Occupation PSI must be at or below 0.25. Result: "
            "PSI equals 0.123 — AMBER, below RED. PASSED.\n\n"
            "Criterion 3: EEOC four-fifths rule for region — approval rates across "
            "all regions must be at least 80 percent of the highest. Result: "
            "85.72 percent. PASSED.\n\n"
            "Criterion 4: EEOC four-fifths rule for occupation. Result: 90.12 "
            "percent. PASSED.\n\n"
            "Criterion 5: Permutation test for region-to-action independence. "
            "p equals 0.132. PASSED.\n\n"
            "Criterion 6: Permutation test for occupation-to-action independence. "
            "p less than 0.001. FAILED-with-interpretation.\n\n"
            "My interpretation of Criterion 6: occupation predicts the underwriting "
            "action because occupation is a genuine actuarial risk signal. Sophea's "
            "agricultural occupation is correctly associated with a different risk "
            "profile than an office worker's — that is actuarially sound. The "
            "association is statistically significant but practically small. "
            "No regulatory threshold is breached. I call this "
            "FAILED-with-interpretation, and I stand by that verdict."
        ),
    },
    # ── Appendix A4: Math Details ──────────────────────────────────────────
    {
        "num": "A4",
        "title": "A4: MATHEMATICAL DETAILS",
        "timing": "if asked",
        "script": (
            "[Show if Committee asks about the LinUCB update rule, PSI formula, "
            "or HITL dual-update mechanics.]\n\n"
            "Three mathematical components — using Sophea's application as the "
            "concrete example.\n\n"
            "LinUCB update rule:\n"
            "Design matrix update: A receives Sophea's vector x transposed times "
            "x. Reward vector update: b receives reward times x. Ridge estimate: "
            "theta-hat equals A-inverse times b. UCB score for arm a: theta-hat "
            "transposed x, plus alpha times the square root of x-transposed "
            "A-inverse x — where x is Sophea's 34-dimensional vector.\n\n"
            "PSI formula:\n"
            "PSI equals the sum over each segment of: P-new minus P-old, times the "
            "natural log of P-new over P-old. For Sophea's Kampong Cham region: "
            "PSI 0.082 — GREEN. For her occupation category: PSI max 0.123 — AMBER.\n\n"
            "HITL dual-update:\n"
            "When the human overrides the bandit: update the selected arm on the "
            "human label, and apply a penalty to the REFER arm reward to prevent "
            "the over-selection spiral. Without the penalty, REFER accumulates "
            "reward without cost — the dual update corrects that incentive."
        ),
    },
    # ── Appendix A5: Full Sensitivity Tables ──────────────────────────────
    {
        "num": "A5",
        "title": "A5: FULL SENSITIVITY TABLES",
        "timing": "if asked",
        "script": (
            "[Show if Committee asks about parameter sensitivity or robustness.]\n\n"
            "The headline results are robust across the full parameter grid.\n\n"
            "LinUCB exploration parameter alpha: tested from 0.5 to 2.0. Alpha "
            "equals 1.0 selected in EXP-012 as the regret-minimising setting.\n\n"
            "LinTS posterior width v: 0.1. Ridge penalty lambda: 1.0.\n\n"
            "HITL conservatism kappa: headline result at kappa equals 0.7. Kappa "
            "of 0.3 and 0.5 also tested; the ranking of HITL above vanilla bandit "
            "is stable across all kappa values.\n\n"
            "Price elasticity slope: base at 3.5, stressed at 2.5 and 4.5.\n\n"
            "Adverse-selection factor: 1.35 is the DAC actuarial prior.\n\n"
            "Across the EXP-011 ablation and EXP-012 sensitivity grid, the ranking "
            "of LinUCB and LinTS above all other admissible policies is stable. "
            "Sophea receives STANDARD across all parameter combinations tested."
        ),
    },
]


# ---------------------------------------------------------------------------
# Helper: resolve thumbnail PNG path
# ---------------------------------------------------------------------------
def _slide_png(num):
    if isinstance(num, str) and num.startswith("A"):
        idx = _APPENDIX_OFFSET + int(num[1:])
    else:
        idx = int(num)
    return os.path.join(SLIDES_DIR, f"slide_{idx:03d}.png")


# ---------------------------------------------------------------------------
# Build docx
# ---------------------------------------------------------------------------
def build_doc():
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin  = Cm(2.5)
    sec.right_margin = Cm(2.5)
    sec.top_margin   = Cm(2.0)
    sec.bottom_margin = Cm(2.0)

    # ── Cover ──────────────────────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title_p.add_run("THESIS DEFENSE PRESENTATION SCRIPT")
    tr.bold = True
    tr.font.size = Pt(16)
    tr.font.color.rgb = DRGBColor(0x1F, 0x3A, 0x6E)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sub_p.add_run(
        "Adaptive Health Insurance Underwriting via Contextual Bandits:\n"
        "A Reinforcement Learning Approach for Cambodia\n\n"
        "LUN CHANPOLY  ·  ITC-AMS  ·  July 2026"
    )
    sr.font.size = Pt(11)
    sr.font.color.rgb = DRGBColor(0x40, 0x40, 0x40)

    doc.add_paragraph()

    how_p = doc.add_paragraph()
    hr = how_p.add_run(
        "HOW TO USE THIS SCRIPT\n"
        "Read aloud naturally — do not recite word-for-word if it feels unnatural. "
        "Bracketed notes [like this] are stage directions, not spoken text. "
        "The Sophea narrative beats are highlighted throughout — these are the "
        "emotional anchors of the presentation. "
        "Appendix slides A1–A5 are on standby; only advance to them if the "
        "Committee asks a question that slide addresses."
    )
    hr.font.size = Pt(10)
    hr.italic = True

    doc.add_page_break()

    # ── Per-slide sections ─────────────────────────────────────────────────
    for slide in SLIDES:
        num = slide["num"]
        is_appendix = isinstance(num, str) and num.startswith("A")
        label = f"APPENDIX {num}" if is_appendix else f"SLIDE {num}"

        # Heading
        h = doc.add_heading(f"{label}  ·  {slide['title']}", level=2)
        for run in h.runs:
            run.font.color.rgb = DRGBColor(0x2E, 0x74, 0xB5)

        # Timing
        tp = doc.add_paragraph()
        tp.paragraph_format.space_before = Pt(0)
        tp.paragraph_format.space_after  = Pt(4)
        tr2 = tp.add_run(f"Timing: {slide['timing']}")
        tr2.italic = True
        tr2.font.size = Pt(9)
        tr2.font.color.rgb = DRGBColor(0x70, 0x70, 0x70)

        # Thumbnail (if available)
        png = _slide_png(num)
        if os.path.isfile(png):
            ip = doc.add_paragraph()
            ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ip.add_run().add_picture(png, width=Cm(14))

        # Script text (split on double newline → paragraphs)
        for block in slide["script"].split("\n\n"):
            block = block.strip()
            if not block:
                continue
            sp = doc.add_paragraph(block)
            sp.paragraph_format.space_before = Pt(4)
            sp.paragraph_format.space_after  = Pt(4)
            for run in sp.runs:
                run.font.size = Pt(11)

        doc.add_paragraph()  # spacer between slides

    doc.save(DOCX_OUT)
    print(f"Saved docx: {DOCX_OUT}")


# ---------------------------------------------------------------------------
# Inject speaker notes into pptx
# ---------------------------------------------------------------------------
def inject_speaker_notes():
    prs = Presentation(PPTX_PATH)
    total = len(prs.slides)

    for slide_data in SLIDES:
        num = slide_data["num"]
        if isinstance(num, str) and num.startswith("A"):
            idx = _APPENDIX_OFFSET + int(num[1:]) - 1   # 0-based
        else:
            idx = int(num) - 1                           # 0-based

        if idx >= total:
            print(f"WARNING: slide index {idx} out of range ({total} slides)")
            continue

        tf = prs.slides[idx].notes_slide.notes_text_frame
        tf.clear()
        tf.text = slide_data["script"]

    prs.save(PPTX_PATH)
    print(f"Speaker notes injected: {PPTX_PATH}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    build_doc()
    inject_speaker_notes()
