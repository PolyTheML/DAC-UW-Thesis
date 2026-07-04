"""Generate Poly_defense_script.docx — thesis defense presentation script."""

import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUT_PATH = r"thesis\health_rl\Poly_defense_script.docx"
SLIDES_DIR = r"thesis\health_rl\slide_thumbnails"

# Appendix slides A1-A5 are pptx slides 30-34
_APPENDIX_OFFSET = 29


def _slide_png(num):
    """Return PNG path for a slide number (int) or appendix label ('A1'-'A5')."""
    if isinstance(num, str) and num.startswith("A"):
        idx = _APPENDIX_OFFSET + int(num[1:])
    else:
        idx = int(num)
    return os.path.join(SLIDES_DIR, f"slide_{idx:03d}.png")

SLIDES = [
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
        "transition": None,
    },
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
        "transition": None,
    },
    {
        "num": 3,
        "title": "SECTION DIVIDER — Introduction & Problem Background",
        "timing": "~1.5 min",
        "script": (
            "Imagine Sophea. She is forty-three years old, a garment worker. Her "
            "BMI is 25.7. She does not smoke. Her only medical flag is a managed "
            "case of hypertension, picked up two years ago.\n\n"
            "In 2023, Sophea applies for voluntary health insurance — perhaps the "
            "first time anyone in her family has ever done so.\n\n"
            "The underwriter runs her profile through the company's static "
            "rule-based system. It predicts her mortality risk from her full "
            "profile — 1.83 times normal, close to her true risk — and that "
            "estimate falls into a fixed premium band. The answer comes back: "
            "RATED.\n\n"
            "Sophea gets covered — but at a loaded premium she may not need.\n\n"
            "This research begins with the question: was that the right price? "
            "And if not — what would a better system look like?"
        ),
        "transition": None,
    },
    {
        "num": 4,
        "title": "ABOUT DECENT ACTUARIAL CONSULTANTS",
        "timing": "~1 min",
        "script": (
            "To answer that question, I joined Decent Actuarial Consultants — DAC "
            "— as a research intern in March 2026.\n\n"
            "DAC is a Phnom Penh-based actuarial consultancy whose clients span "
            "life, non-life, and general insurance companies across Cambodia. They "
            "are the practitioners who live with the underwriting problem every day.\n\n"
            "Supervised by Mr. ON Radet, my task was to design and validate an "
            "adaptive underwriting system — and then build a working prototype. "
            "The thesis you have in your hands, and the demonstration I will show "
            "you today, are the outputs of that internship."
        ),
        "transition": None,
    },
    {
        "num": 5,
        "title": "INTRODUCTION",
        "timing": "~1 min",
        "script": (
            "Sophea's situation is not an isolated edge case. It sits inside a "
            "much larger problem.\n\n"
            "As of 2023, health insurance penetration in Cambodia is estimated at "
            "under 10 percent — the large number you see on the left. The NSSF "
            "provides mandatory coverage, but only to formal-sector workers — "
            "roughly 16 percent of the population. Private underwriting is manual "
            "and rule-based, static rules never learn from claims outcomes, and "
            "there is no demographic-parity monitoring in practice.\n\n"
            "This research connects directly to three of Cambodia's SDGs, shown "
            "on the right. SDG 3 — Good Health and Well-being — by widening "
            "voluntary insurance access beyond the formal sector. SDG 1 — No "
            "Poverty — by shielding households from catastrophic out-of-pocket "
            "health costs. And SDG 10 — Reduced Inequalities — through the PSI "
            "fairness guardrail I will describe shortly.\n\n"
            "Sophea represents the 84 percent the current system was not built for."
        ),
        "transition": None,
    },
    {
        "num": 6,
        "title": "PROBLEM STATEMENT",
        "timing": "~1 min",
        "script": (
            "The static system that rated Sophea has four specific failure modes "
            "— and each one is visible in her case.\n\n"
            "First: fixed thresholds. Its risk estimate for Sophea is actually "
            "accurate — but a fixed premium band has no mechanism to weigh whether "
            "a loaded premium is still worth offering once you account for her "
            "likelihood of accepting it. Context is priced, but not optimised.\n\n"
            "Second: no online adaptation. The system was trained once, on historical "
            "data that may not reflect current Cambodia. It could not update its "
            "beliefs from new claims outcomes. Every applicant — including Sophea "
            "— was assessed against stale weights.\n\n"
            "Third: demographic blindspot. No parity metric was tracked. If the "
            "system systematically rated certain occupations higher at rates "
            "inconsistent with their actual risk, that pattern would be invisible "
            "to the insurer.\n\n"
            "Fourth: no intelligent triage. Cases like Sophea's — borderline, "
            "nuanced — were either mechanically rated or sent to a senior underwriter "
            "with no supporting analysis.\n\n"
            "Each of these failures costs Sophea. Together, they are the problem "
            "I set out to solve."
        ),
        "transition": None,
    },
    {
        "num": 7,
        "title": "PROJECT OBJECTIVE",
        "timing": "~2 min",
        "script": (
            "My primary research goal was to design, implement, and empirically "
            "validate a contextual bandit framework that outperforms static "
            "rule-based underwriting on cumulative profitability — while maintaining "
            "regional and occupational fairness — on a synthetic Cambodia dataset.\n\n"
            "In Sophea's terms: could a learning system weigh the price trade-off "
            "a fixed rule can't — and make a more profitable decision, even when "
            "the risk estimate itself is already accurate?\n\n"
            "I broke this into five measurable secondary objectives.\n\n"
            "O1: Build a reproducible 2,000-record synthetic dataset anchored on "
            "real Cambodia survey data — CDHS 2021-22, STEPS, ILO, WHO — so that "
            "Sophea is a statistically realistic applicant, not a cartoon.\n\n"
            "O2: Implement and compare three bandit algorithms — LinUCB, LinTS, "
            "and Epsilon-Greedy — against a Static XGBoost baseline over 5,000 "
            "underwriting rounds.\n\n"
            "O3: Design PSI-based fairness guardrails so that the approved portfolio "
            "does not drift demographically from the applicant population — "
            "protecting applicants in categories like Sophea's.\n\n"
            "O4: Conduct an EEOC four-fifths parity audit — verifying that no "
            "segment faces approval rates below 80% of the highest-approved group.\n\n"
            "O5: Design a human-in-the-loop wrapper that escalates only the most "
            "uncertain cases — quantifying reward gain against actuary review cost.\n\n"
            "I will address each of these directly in the results section."
        ),
        "transition": None,
    },
    {
        "num": 8,
        "title": "SECTION DIVIDER — Literature Review",
        "timing": "~5 sec",
        "script": (
            "Before I show you the system I built, let me briefly survey what "
            "the research literature told me about building it."
        ),
        "transition": None,
    },
    {
        "num": 9,
        "title": "LITERATURE REVIEW",
        "timing": "~2 min",
        "script": (
            "Five research areas shaped the design of this system — and each one "
            "left a mark on how I handled Sophea's case.\n\n"
            "First, emerging-market underwriting. Reports from CDHS, ILO, and ADB "
            "established Cambodia's context and gave us the data anchors that make "
            "Sophea a realistic synthetic applicant. Under 10% health insurance "
            "penetration. A formal-sector NSSF that covers only 16% of the "
            "population. Private insurers working with manual, rule-based systems.\n\n"
            "Second, linear contextual bandits. The two algorithms at the heart of "
            "this work — LinUCB from Li et al. 2010, and LinTS from Agrawal and "
            "Goyal 2013 — both achieve sub-linear regret of order square-root of T, "
            "times d, times log T. This theoretical guarantee is why I chose them: "
            "they are provably efficient at learning from experience.\n\n"
            "Third, neural bandits. NeuralUCB, NeuralTS, and EE-Net relax the "
            "linear-reward assumption. They are natural candidates for a future "
            "version of this system — one that might model Sophea's risk "
            "non-linearly.\n\n"
            "Fourth, fairness in insurance machine learning. Barocas et al. and "
            "Ensign et al. established the basis for protected-attribute constraints "
            "and warned specifically about feedback loops in automated decision "
            "systems. Sophea's category — female, garment-sector — is exactly "
            "the kind of group that feedback loops can harm.\n\n"
            "Fifth, Population Stability Index. PSI, grounded in Jensen-Shannon "
            "divergence, gives us three interpretable zones: GREEN below 0.10, "
            "AMBER 0.10 to 0.25, RED at or above 0.25. It tells us whether the "
            "system is drifting away from applicants like Sophea.\n\n"
            "The full review is in Chapter III, citing 25 sources in APA format."
        ),
        "transition": None,
    },
    {
        "num": 10,
        "title": "SECTION DIVIDER — Methodology & Model Design",
        "timing": "~5 sec",
        "script": "Let me now show you the system I built to give Sophea a better answer.",
        "transition": None,
    },
    {
        "num": 11,
        "title": "METHODOLOGY OVERVIEW",
        "timing": "~1 min",
        "script": (
            "The system is a closed-loop pipeline — shown here left to right.\n\n"
            "Sophea's application enters as a 34-dimensional context vector. A bandit "
            "policy selects one of four underwriting actions. An actuarial simulator "
            "returns a reward — revenue minus expected claims — that updates the "
            "policy's parameters. In parallel, a PSI guardrail monitors portfolio "
            "drift, and a human-in-the-loop wrapper catches the cases the bandit "
            "is genuinely uncertain about.\n\n"
            "Every decision the system makes on every applicant — including Sophea "
            "— feeds back into making the next decision sharper. This is the "
            "fundamental difference from the static system."
        ),
        "transition": None,
    },
    {
        "num": 12,
        "title": "ZOOM-IN: DATASET & CONTEXT",
        "timing": "~1 min",
        "script": (
            "Starting with the first component: who Sophea is to the system.\n\n"
            "The bandit sees 2,000 synthetic applications. Each is a 34-dimensional "
            "standardised vector. The dataset is anchored on four real-world sources "
            "— CDHS, STEPS, ILO, WHO — and contains no real personal data.\n\n"
            "Sophea is one of those 2,000. The system must choose among four arms "
            "for each applicant: RATED — accept with a 25% premium loading. "
            "STANDARD — accept at standard premium. DECLINE — reject. "
            "REFER — escalate to a human underwriter.\n\n"
            "In 2023, the static system chose RATED for Sophea — loading her "
            "premium even though its own risk estimate was close to the truth. "
            "The bandit will need to do better."
        ),
        "transition": None,
    },
    {
        "num": 13,
        "title": "THE DATASET AT A GLANCE",
        "timing": "~1.5 min",
        "script": (
            "Sophea's 34-dimensional vector is built from seven feature categories.\n\n"
            "Demographics and vitals: age 43, female, BMI 25.7. Lifestyle: "
            "non-smoker, sedentary factory work, no alcohol. Social determinants: "
            "secondary education, middle wealth index, good self-rated health. "
            "Economic features. One clinical flag — managed hypertension. Region: "
            "Other Provinces — one of eight one-hot encoded regions. Occupation: "
            "garment work — one of seven one-hot encoded categories.\n\n"
            "Standardised, her key dimensions look like this: age at 1.2 standard "
            "deviations above the mean, BMI at 0.8 — mildly elevated, smoker "
            "flag zero, hypertension flag one, Other Provinces indicator one, "
            "garment-work indicator one.\n\n"
            "She is not a high-risk profile — her true mortality multiplier is "
            "1.84, and the static model predicts 1.83, essentially spot on. But "
            "even an accurate estimate lands in a fixed band, and the band, not "
            "the estimate, decides."
        ),
        "transition": None,
    },
    {
        "num": 14,
        "title": "REWARD SIMULATOR",
        "timing": "~1.5 min",
        "script": (
            "The reward simulator is the actuarial core that would have judged "
            "Sophea correctly — if asked.\n\n"
            "For each applicant with context x, the bandit selects an action, and "
            "the simulator returns reward: premium revenue minus expected claims.\n\n"
            "For Sophea specifically: if the system selects RATED — a 25% loading "
            "— it is overcharging a borderline-healthy applicant, creating adverse "
            "selection and a poor customer experience. The reward is penalised.\n\n"
            "If it selects STANDARD — it correctly prices her risk. The actuarial "
            "margin is healthy. The reward is positive.\n\n"
            "If it selects DECLINE — it loses the premium revenue entirely, and "
            "Sophea leaves without coverage, for a small fixed processing cost — "
            "not zero, but close to it.\n\n"
            "The bandit's objective over 5,000 rounds is to learn which action "
            "maximises cumulative reward — and for applicants like Sophea, that "
            "means learning that an accurate risk estimate doesn't automatically "
            "justify a loaded premium."
        ),
        "transition": None,
    },
    {
        "num": 15,
        "title": "ZOOM-IN: BANDIT POLICY",
        "timing": "~30 sec",
        "script": (
            "Now I will show you exactly how the bandit processes Sophea's "
            "application — building up the policy step by step."
        ),
        "transition": None,
    },
    {
        "num": 16,
        "title": "BANDIT BUILD-UP: CONTEXT",
        "timing": "~1 min",
        "script": (
            "Step one: the context vector.\n\n"
            "The bandit's complete and only view of Sophea is her 34-dimensional "
            "vector. No underwriter notes. No prior history.\n\n"
            "Her key dimensions: age 1.2, BMI 0.8, smoker zero, "
            "hypertension one, Other Provinces one, garment-work one — and twenty-eight "
            "more standardised features capturing the full picture the static "
            "system's own risk estimate happens to get right, even though its "
            "pricing rule doesn't.\n\n"
            "This vector is what the bandit must learn from. The question is "
            "what it does with it."
        ),
        "transition": None,
    },
    {
        "num": 17,
        "title": "BANDIT BUILD-UP: VALUE ESTIMATES",
        "timing": "~1.5 min",
        "script": (
            "Step two: computing per-arm value estimates for Sophea.\n\n"
            "For each of the four arms — RATED, STANDARD, DECLINE, REFER — the "
            "algorithm estimates the expected reward given her specific vector.\n\n"
            "LinUCB computes an optimistic estimate: theta-hat transposed Sophea's "
            "vector, plus an exploration bonus alpha times the square root of her "
            "vector transposed A-inverse her vector. Early in training, that bonus "
            "is large — LinUCB tries arms it has not seen much. Over time, the "
            "bonus shrinks as the gram matrix A fills in with more applicants.\n\n"
            "LinTS takes a different path: it draws a sample from the posterior "
            "over theta and evaluates each arm under that sample. Uncertainty is "
            "expressed probabilistically, not as a deterministic bonus.\n\n"
            "For Sophea specifically, after sufficient training, the computed arm "
            "values are: STANDARD 0.66, DECLINE 0.20, REFER 0.13, RATED 0.00. "
            "The standard arm is highest — by a clear margin."
        ),
        "transition": None,
    },
    {
        "num": 18,
        "title": "BANDIT BUILD-UP: SELECTION & ACTION",
        "timing": "~2 min",
        "script": (
            "Step three: action selection.\n\n"
            "The algorithm takes the argmax — 0.66 — and issues STANDARD. The "
            "reward is returned. Sophea gets coverage at the correct actuarial "
            "price. The gram matrix A is updated with her context vector, so the "
            "next similar applicant is decided with more confidence.\n\n"
            "We compare five policies in total.\n\n"
            "LinUCB and LinTS are our two proposed admissible policies.\n\n"
            "Epsilon-Greedy is a naive explorer — achieving only O of T to the "
            "two-thirds regret in the worst case. It would eventually learn "
            "Sophea's correct arm, but slowly.\n\n"
            "Static XGB is the train-once incumbent baseline — the one that "
            "rated Sophea in 2023, even though its own risk estimate for her "
            "was close to the truth.\n\n"
            "AlwaysRATED is a constant policy that applies a 25% loading to every "
            "single applicant regardless of risk. It is the inadmissible ceiling.\n\n"
            "I want to be precise about admissibility — a term I will return to "
            "in the results. A policy is admissible only if it is both commercially "
            "and regulatorily viable for real deployment. AlwaysRATED fails this "
            "test: no Cambodian insurer can legally or commercially apply a blanket "
            "surcharge to every applicant — including healthy ones like Sophea "
            "— regardless of risk. Our headline performance claim is therefore "
            "scoped to admissible policies only, and the comparison that matters "
            "is LinUCB versus Static XGB, not versus AlwaysRATED."
        ),
        "transition": None,
    },
    {
        "num": 19,
        "title": "ZOOM-IN: FAIRNESS GUARDRAIL & HITL",
        "timing": "~1.5 min",
        "script": (
            "Two safety layers protect applicants like Sophea.\n\n"
            "The PSI demographic guardrail monitors the approved-portfolio "
            "distribution against the applicant population on a rolling 500-round "
            "window, separately for region and occupation. If the system began "
            "systematically declining Other Provinces applicants or garment "
            "workers at rates inconsistent with the population, PSI would catch "
            "it. GREEN below 0.10 — stable. AMBER 0.10 to 0.25 — monitor. "
            "RED at or above 0.25 — mandatory review.\n\n"
            "The human-in-the-loop wrapper escalates cases where the bandit's "
            "decision uncertainty exceeds threshold kappa. If the system is "
            "genuinely unsure about Sophea — perhaps early in training, before it "
            "has seen enough garment workers from Other Provinces — it refers her "
            "to an actuary rather than guessing. The actuary's decision is then "
            "fed back to train the bandit. Design target: keep review cost below "
            "2% of total reward."
        ),
        "transition": None,
    },
    {
        "num": 20,
        "title": "SECTION DIVIDER — Results & Evaluation",
        "timing": "~5 sec",
        "script": (
            "Let me now tell you what the system actually did — including what it "
            "got right, what it got wrong, and what I reported honestly either way."
        ),
        "transition": None,
    },
    {
        "num": 21,
        "title": "HEADLINE BENCHMARK",
        "timing": "~2 min",
        "script": (
            "The headline result: among all admissible policies, LinTS and LinUCB "
            "rank first and second.\n\n"
            "Over 5,000 rounds, LinTS earns $93,723 in cumulative reward. LinUCB "
            "earns $91,864. Epsilon-Greedy earns $76,441. Static XGB — the system "
            "that rated Sophea — earns $72,206.\n\n"
            "The log-log regret slope is 0.572, with R-squared of 0.992. This "
            "confirms sub-linear regret — consistent with the theoretical bound.\n\n"
            "Two things I want to be transparent about.\n\n"
            "First: LinTS versus LinUCB is not statistically significant — p equals "
            "0.87 across 20 seeds. They are effectively tied at the top of the "
            "admissible set. I do not claim one outperforms the other.\n\n"
            "Second: AlwaysRATED earns $122,287 — higher than both. I report this "
            "honestly. But AlwaysRATED would have loaded a blanket 25% surcharge "
            "on Sophea, on every healthy young applicant, on everyone — regardless "
            "of risk. It is inadmissible. The comparison that answers the research "
            "question is LinUCB versus Static XGB."
        ),
        "transition": None,
    },
    {
        "num": 22,
        "title": "CONVERGENCE & REGRET",
        "timing": "~1.5 min",
        "script": (
            "The primary pre-registered metric: paired Wilcoxon test across 20 "
            "independent seeds, LinUCB versus Static XGB.\n\n"
            "Result: plus 25.2% cumulative reward lift. Cohen's d effect size 2.98. "
            "P less than 0.001.\n\n"
            "This is the gap between 2023 Sophea and 2026 Sophea.\n\n"
            "The static system, over 5,000 rounds, earns $72,206. The bandit earns "
            "$91,864 — by learning, over time, that applicants like Sophea are "
            "better assessed at standard premium than mechanically rated.\n\n"
            "For context: Oracle — the theoretically perfect policy with full "
            "knowledge of true risk — earns $126,804. LinUCB recovers 72% of the "
            "gap between Static XGB and Oracle. That is a strong empirical result "
            "for a policy that starts with no prior knowledge of any applicant."
        ),
        "transition": None,
    },
    {
        "num": 23,
        "title": "COLD-START & HUMAN-IN-THE-LOOP",
        "timing": "~1.5 min",
        "script": (
            "Two additional experiments speak to the system's practical readiness.\n\n"
            "The cold-start analysis asks: could the bandit certify its superiority "
            "at T equals 2,000 — halfway through the horizon? This matters because "
            "a real insurer cannot wait 5,000 applicants before trusting the system.\n\n"
            "LinTS passes with p equals 0.0039. LinUCB draws level but is not "
            "certified — p equals 0.0840. I report LinUCB honestly as 'draws level' "
            "in the thesis, not as a proven win at 2,000.\n\n"
            "The human-in-the-loop experiment: when the bandit is uncertain about "
            "an applicant — say, early encounters with Sophea's profile before it "
            "has seen enough Other Provinces garment workers — it escalates to a "
            "human actuary. "
            "The result: plus 14.8% reward lift over the vanilla bandit, at a "
            "referral rate of only 1.3%. Thirteen applicants reviewed per thousand. "
            "The actuary's judgment on those thirteen cases is worth a 14.8% gain "
            "on the whole portfolio."
        ),
        "transition": None,
    },
    {
        "num": 24,
        "title": "FAIRNESS AUDIT & DRIFT",
        "timing": "~2 min",
        "script": (
            "The fairness audit evaluates six pre-registered criteria. Five passed. "
            "One failed — and I want to address that failure directly.\n\n"
            "For region: PSI 0.0821 — GREEN. EEOC four-fifths parity 85.72% — "
            "above the 80% threshold. Both pass cleanly.\n\n"
            "For occupation — Sophea's category: PSI 0.1225 — AMBER, in the monitor "
            "zone but below RED. EEOC parity 90.12% — above 80%. That passes too.\n\n"
            "But Criterion 6 — occupation-to-action statistical independence — "
            "failed, with p less than 0.001. The system's decisions are statistically "
            "associated with occupation.\n\n"
            "Here is my interpretation: occupation is an actuarially valid risk "
            "factor. Rice farmers, garment workers, and office workers carry "
            "objectively different health risk profiles — different exposures, "
            "different injury patterns, different chronic disease rates. The "
            "association is statistically significant but practically small, and "
            "no regulatory threshold is breached. Sophea is correctly rated at "
            "STANDARD premium. I call this a FAILED-with-interpretation verdict "
            "— honest about the statistical finding, honest about why it does not "
            "constitute harmful discrimination.\n\n"
            "On drift resilience: after a shock at round 1,500 simulating sudden "
            "claims inflation, the bandits achieve a post-to-pre regret ratio of "
            "0.29. Static XGB shows 0.85. The bandits adapt. The static system "
            "barely moves."
        ),
        "transition": None,
    },
    {
        "num": 25,
        "title": "LIVE DEMONSTRATION",
        "timing": "~3 min",
        "script": (
            "[Open browser at localhost:8000 before this slide.]\n\n"
            "I will now show you Sophea's application — not as a number, but as "
            "a live interaction with the prototype dashboard.\n\n"
            "[Click the \"Sophea\" preset button — do not hand-type her fields live.]\n\n"
            "Here is Sophea's profile loaded into the underwriting desk. The "
            "bandit sees her 34 features, computes the arm scores, and issues "
            "its decision.\n\n"
            "[Show the decision: STANDARD, and the static-XGB comparison card "
            "showing RATED.]\n\n"
            "STANDARD premium from the bandit — even though the static system, "
            "sitting right next to it, still loads her at RATED.\n\n"
            "[Submit a high-risk applicant — older, smoker, high BMI, multiple "
            "clinical flags.]\n\n"
            "Now a higher-risk applicant. The bandit selects REFER — escalating "
            "to the human-in-the-loop queue. The HITL tab tracks the running "
            "referral rate.\n\n"
            "This is the same FastAPI stack described in the thesis — deployed "
            "on Render, available live — not a mockup, not a simulation. It is "
            "the prototype I built at DAC, running in real time."
        ),
        "transition": None,
    },
    {
        "num": 26,
        "title": "SECTION DIVIDER — Conclusion & Future Work",
        "timing": "~5 sec",
        "script": "Let me bring this back to Sophea.",
        "transition": None,
    },
    {
        "num": 27,
        "title": "CONCLUSION",
        "timing": "~2 min",
        "script": (
            "In 2023, Sophea applied for health insurance and was rated. The "
            "static system's risk estimate for her was accurate — but its fixed "
            "premium band still loaded her, without weighing whether that "
            "premium was still worth offering.\n\n"
            "In 2026, the bandit sees her complete 34-dimensional profile, has "
            "learned from thousands of prior decisions, and issues STANDARD premium "
            "outright — the more profitable answer. That difference is part of "
            "the 25.2%.\n\n"
            "Reviewing the five secondary objectives:\n"
            "O1 — 2,000-record CDHS-anchored dataset: ACHIEVED.\n"
            "O2 — LinUCB, LinTS, and Epsilon-Greedy benchmarked against Static XGB: ACHIEVED.\n"
            "O3 — PSI fairness guardrails designed and validated: ACHIEVED.\n"
            "O4 — EEOC four-fifths parity audit: ACHIEVED.\n"
            "O5 — Human-in-the-loop wrapper evaluated: ACHIEVED.\n\n"
            "The overarching conclusion: contextual bandits provide a principled, "
            "adaptive, and auditable alternative to static rule-based underwriting "
            "in the Cambodian health insurance context.\n\n"
            "Sophea's case is not unique. Cambodia has hundreds of thousands of "
            "applicants like her — people whose risk profiles are nuanced, whose "
            "context matters, and who deserve a decision system capable of seeing "
            "them fully."
        ),
        "transition": None,
    },
    {
        "num": 28,
        "title": "REFERENCES",
        "timing": "~20 sec",
        "script": (
            "The key methodological references are listed here. The full bibliography "
            "— 25 sources in APA format — is in Chapter III of the thesis. "
            "I am happy to discuss any specific citation if the Committee wishes."
        ),
        "transition": None,
    },
    {
        "num": 29,
        "title": "THANK YOU / Q&A",
        "timing": "~15 sec",
        "script": (
            "Thank you, Distinguished Committee, for your time and attention.\n\n"
            "I am now ready for your questions. If it would be helpful, I have five "
            "appendix slides available: A1 covers the baseline ladder and admissibility "
            "discussion; A2 reconciles the three reward-lift numbers across experiments; "
            "A3 details the six fairness criteria verdicts; A4 covers sensitivity and "
            "ablation results; and A5 has the full bandit mathematics and PSI mechanics."
        ),
        "transition": None,
    },
    {
        "num": "A1",
        "title": "APPENDIX A1 — BASELINE LADDER (EXP-014)",
        "timing": "if asked",
        "script": (
            "Committee members may notice that AlwaysRATED earns $122,287 — higher "
            "than both LinTS and LinUCB.\n\n"
            "This is true, and I report it honestly.\n\n"
            "AlwaysRATED is a policy that charges a flat 25% loading to every "
            "applicant — including Sophea, including every healthy young non-smoker "
            "in the dataset. No Cambodian insurer can commercially or regulatorily "
            "apply that uniformly. It would create severe adverse selection, drive "
            "healthy applicants out of the pool, and face regulatory challenge.\n\n"
            "Our pre-registered expectation was that bandits would outperform "
            "AlwaysRATED. That expectation was falsified. We report it as the "
            "scientifically informative outcome it is. The headline claim is "
            "correctly scoped: bandits rank first and second among the admissible "
            "set — policies a real insurer could actually deploy."
        ),
        "transition": None,
    },
    {
        "num": "A2",
        "title": "APPENDIX A2 — NUMBER RECONCILIATION",
        "timing": "if asked",
        "script": (
            "Three different reward-lift numbers appear across the thesis. "
            "Let me address them directly.\n\n"
            "Plus 25.2%: LinUCB versus Static XGB in EXP-005. Pre-registered "
            "primary metric. Paired design, 20 seeds, standardised evaluation. "
            "This is our headline number — the one that answers the research question.\n\n"
            "Plus 27.2%: LinUCB versus Static XGB in EXP-014. This uses the CRN "
            "harness and a reward-maximising policy configuration — a different "
            "experimental setup, which is why the number is slightly higher.\n\n"
            "Plus 29.8%: LinTS versus Static XGB in EXP-014. Same CRN harness.\n\n"
            "Plus 14.8%: HITL versus vanilla LinUCB in EXP-008. This compares "
            "the HITL wrapper against the vanilla bandit — a completely different "
            "baseline. It does not compare against Static XGB.\n\n"
            "These three numbers answer three different questions and are mutually "
            "consistent. When I cite the headline result, I cite 25.2% — the "
            "conservative pre-registered figure."
        ),
        "transition": None,
    },
    {
        "num": "A3",
        "title": "APPENDIX A3 — FAIRNESS CRITERIA VERDICTS",
        "timing": "if asked",
        "script": (
            "The six pre-registered fairness criteria, shown with their verdicts.\n\n"
            "Criteria 1 through 5 passed.\n\n"
            "Criterion 1: region PSI within GREEN threshold — PASSED at 0.0821. "
            "Criterion 2: occupation PSI within AMBER threshold — PASSED at 0.1225. "
            "Criteria 3 and 4: EEOC four-fifths parity for region and occupation "
            "— PASSED at 85.72% and 90.12%. Criterion 5: region-to-action "
            "independence — PASSED.\n\n"
            "Criterion 6: occupation-to-action independence — FAILED, p less "
            "than 0.001.\n\n"
            "The interpretation: occupation predicts the underwriting action because "
            "occupation is a genuine actuarial risk signal. Sophea's garment-sector "
            "occupation is correctly associated with a different risk profile than "
            "an office worker's — that is actuarially sound, not discriminatory. "
            "The association is statistically significant but practically small. "
            "No regulatory threshold is breached. I call this FAILED-with-"
            "interpretation, and I stand by that verdict."
        ),
        "transition": None,
    },
    {
        "num": "A4",
        "title": "APPENDIX A4 — SENSITIVITY & ABLATION",
        "timing": "if asked",
        "script": (
            "The headline results are robust across the full parameter grid.\n\n"
            "LinUCB: exploration parameter alpha equals 1.0, selected in EXP-012 "
            "as the regret-minimising setting across the range 0.5 to 2.0. "
            "LinTS: posterior width v equals 0.1, ridge penalty lambda equals 1.0. "
            "HITL wrapper: conservatism kappa equals 0.7 for the headline result; "
            "0.3 and 0.5 also tested.\n\n"
            "Price elasticity stress-tested at 2.5 and 4.5, with the base at 3.5. "
            "Adverse-selection factor 1.35 is the DAC actuarial prior.\n\n"
            "Across the EXP-011 ablation and EXP-012 sensitivity grid, the ranking "
            "of LinUCB and LinTS above all other admissible policies is stable. "
            "Sophea gets STANDARD across all parameter combinations tested."
        ),
        "transition": None,
    },
    {
        "num": "A5",
        "title": "APPENDIX A5 — BANDIT MATH & PSI MECHANICS",
        "timing": "if asked",
        "script": (
            "For reference, the full update rules — using Sophea's application "
            "as the concrete example.\n\n"
            "LinUCB: we update the gram matrix A by adding Sophea's vector x "
            "transposed times itself, and the reward vector b by adding the "
            "realized reward times x. The parameter estimate theta-hat equals "
            "A-inverse times b. The arm selected is the argmax of theta-hat "
            "transposed x plus alpha times the square root of x-transposed "
            "A-inverse x — where x is Sophea's 34-dimensional vector.\n\n"
            "LinTS: the prior is theta distributed as Normal with mean mu and "
            "precision lambda times identity. The posterior precision is lambda "
            "identity plus A. We draw a sample theta-tilde from Normal mu, "
            "v-squared Sigma, and select the arm with highest expected reward "
            "under the sample.\n\n"
            "PSI for Sophea's region category: sum over each province segment "
            "of: actual approval percentage minus expected percentage, times the "
            "log ratio of actual to expected. Region PSI across all segments, "
            "including Other Provinces: 0.0821 — GREEN. Occupation max PSI across "
            "all categories, including garment work: 0.1225 — AMBER. Both within "
            "threshold."
        ),
        "transition": None,
    },
]


def add_heading(doc, text, level):
    p = doc.add_heading(text, level=level)
    run = p.runs[0] if p.runs else p.add_run(text)
    if level == 1:
        run.font.color.rgb = RGBColor(0x1F, 0x3A, 0x6E)  # dark blue
    elif level == 2:
        run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)  # medium blue


def add_meta(doc, timing):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(f"Timing: {timing}")
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x70, 0x70, 0x70)


def add_script(doc, text):
    for block in text.split("\n\n"):
        p = doc.add_paragraph(block.strip())
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.font.size = Pt(11)


def build_doc():
    doc = Document()

    # Page margins
    section = doc.sections[0]
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    # Cover heading
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("THESIS DEFENSE PRESENTATION SCRIPT")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x1F, 0x3A, 0x6E)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run(
        "Adaptive Health Insurance Underwriting via Contextual Bandits:\n"
        "A Reinforcement Learning Approach for Cambodia\n\n"
        "LUN CHANPOLY  ·  ITC-AMS  ·  July 2026"
    )
    sub_run.font.size = Pt(11)
    sub_run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    doc.add_paragraph()

    note_p = doc.add_paragraph()
    note_run = note_p.add_run(
        "HOW TO USE THIS SCRIPT\n"
        "Read aloud naturally — do not recite word-for-word if it feels unnatural. "
        "Bracketed notes [like this] are stage directions, not spoken text. "
        "Appendix slides A1–A5 are on standby; only advance to them if the "
        "Committee asks a question that slide addresses."
    )
    note_run.font.size = Pt(10)
    note_run.italic = True

    doc.add_page_break()

    # Main content
    for slide in SLIDES:
        num = slide["num"]
        is_appendix = isinstance(num, str) and num.startswith("A")
        label = f"APPENDIX {num}" if is_appendix else f"SLIDE {num}"

        add_heading(doc, f"{label}  ·  {slide['title']}", level=2)
        add_meta(doc, slide["timing"])

        # Embed slide thumbnail
        png = _slide_png(num)
        if os.path.isfile(png):
            img_p = doc.add_paragraph()
            img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            img_run = img_p.add_run()
            img_run.add_picture(png, width=Cm(14))

        add_script(doc, slide["script"])

        doc.add_paragraph()  # spacer

    doc.save(OUT_PATH)
    print(f"Saved: {OUT_PATH}")


PPTX_PATH = r"thesis\health_rl\Poly_defense_presentation.pptx"


def inject_speaker_notes():
    """Write each slide's script as the PowerPoint speaker note."""
    from pptx import Presentation
    from pptx.util import Pt
    import lxml.etree as etree

    prs = Presentation(PPTX_PATH)
    slide_count = len(prs.slides)

    for slide_data in SLIDES:
        num = slide_data["num"]
        if isinstance(num, str) and num.startswith("A"):
            idx = _APPENDIX_OFFSET + int(num[1:]) - 1  # 0-based
        else:
            idx = int(num) - 1

        if idx >= slide_count:
            print(f"  WARNING: slide index {idx} out of range ({slide_count} slides)")
            continue

        slide = prs.slides[idx]
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.clear()
        tf.text = slide_data["script"]

    prs.save(PPTX_PATH)
    print(f"Speaker notes injected: {PPTX_PATH}")


if __name__ == "__main__":
    build_doc()
    inject_speaker_notes()
