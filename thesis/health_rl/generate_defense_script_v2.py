"""
Generate Poly_defense_script_v2.docx and inject speaker notes
into Poly_defense_presentation_v3.pptx.

Run from C:\\DAC-UW-Thesis\\:
    python thesis/health_rl/generate_defense_script_v2.py

IMPORTANT run order: build_defense_v3.py FIRST, then this script. The builder
creates a fresh Presentation() every run and silently wipes injected notes, so
this generator must always run afterwards to restore them.

2026-07-02 (Sreynich-flow redesign): re-synced to the 34-slide deck
(1 Title · 2 ToC · 3 Map · 4-8 Introduction · 9 Literature · 10-13 System
Design · 14-15 Implementation · 16-19 Results · 20-22 Conclusion · 23-25
Demonstration · 26 Thanks · 27-34 Appendix A1-A8). Plain-language-first;
formulas exiled to the appendix. HITL headline is the canonical 20-seed
figure: +14.8% ($103,951 vs $90,540, p<0.001, d=2.65, review rate 1.3% =
65/5,000, cost 2.2% of reward). The stale "+6.5%" figure survives ONLY as the
single-seed-42 illustrative reading inside the A2 reconciliation.
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

# Appendix labels -> real 1-based pptx slide index (physical position).
_APPENDIX_SLIDE_MAP = {
    "A1": 27, "A2": 28, "A3": 29, "A4": 30,
    "A5": 31, "A6": 32, "A7": 33, "A8": 34,
}

# Nav-tab labels (drawn before the title on every content slide) — skipped
# when resolving a slide's on-screen title for alignment verification.
_NAV_LABELS = {
    "i. Introduction", "ii. Literature", "iii. System Design",
    "iv. Implementation", "v. Results", "vi. Conclusion", "vii. Demo",
}

# Thumbnails regenerated 2026-07-02 against the 34-slide deck (3-digit
# slide_NNN.png in SLIDES_DIR) — safe to embed.
_THUMBNAILS_CURRENT = True


# ---------------------------------------------------------------------------
# SLIDES — 34 entries: main 1-26 + appendix A1-A8
# ---------------------------------------------------------------------------
SLIDES = [
    {
        "num": 1,
        "title": "TITLE SLIDE",
        "timing": "~1 min",
        "script": (
            "Good morning, Distinguished Committee. I am Lun Chanpoly, and I am "
            "here to defend my master's thesis — Adaptive Health Insurance "
            "Underwriting via Contextual Bandits: A Reinforcement Learning "
            "Approach for Cambodia. This project grew out of my internship at "
            "Decent Actuarial Consultants in Phnom Penh, from March to June 2026, "
            "under the supervision of Dr. Has Sothea and the guidance of Mr. ON "
            "Radet at DAC.\n\n"
            "The talk has seven short sections — I'll keep the language plain and "
            "keep the maths for the appendix, which is on standby if you want to "
            "go deeper on any number.\n\n"
            "But first, let me tell you about a person named Sophea."
        ),
    },
    {
        "num": 2,
        "title": "TABLE OF CONTENTS",
        "timing": "~0.5 min",
        "script": (
            "Here is the shape of the talk. I'll start with the problem and the "
            "market, review the literature in a single table, walk through how the "
            "system is designed and built, show the results, draw the conclusions, "
            "and finish with a live demonstration.\n\n"
            "[Advance to the map.]"
        ),
    },
    {
        "num": 3,
        "title": "A MARKET THE SYSTEM WAS NOT BUILT FOR",
        "timing": "~1 min",
        "script": (
            "[Point to the map and the numbers around it.]\n\n"
            "This is the market Sophea lives in. In Cambodia, fewer than two "
            "percent of people have any health insurance. The state scheme, NSSF, "
            "reaches only formal-sector workers — roughly sixteen percent of the "
            "population. Everyone else is underwritten by hand: fixed rules, no "
            "learning, and no check on fairness.\n\n"
            "So Sophea is not an exception. She represents the ninety-eight percent "
            "the current system was simply not built for."
        ),
    },
    {
        "num": 4,
        "title": "MEET SOPHEA",
        "timing": "~1.5 min",
        "script": (
            "[Point to the profile card on the left.]\n\n"
            "This is Sophea — forty-two years old, a rice farmer from Kampong Cham. "
            "She is active from field farming, a non-smoker, with a BMI of 24.1, "
            "well within the normal range. Her only health flag is managed "
            "hypertension.\n\n"
            "[Point to the two amber flags on the right.]\n\n"
            "In 2023 she applies for voluntary health insurance in Phnom Penh. The "
            "static system checks just two fields: occupation — agriculture; and "
            "condition — hypertension. Both thresholds are crossed.\n\n"
            "[Point to the red box.]\n\n"
            "The decision: DECLINE. Sophea leaves without coverage. And I have to "
            "ask — was that the right answer?"
        ),
    },
    {
        "num": 5,
        "title": "WHY STATIC RULES FAIL",
        "timing": "~1 min",
        "script": (
            "The honest answer is that the rule couldn't have known. A fixed rule "
            "can't see Sophea's full picture — and it never learns from its "
            "mistakes.\n\n"
            "Three problems, in plain words. First, fixed cutoffs: it checks two "
            "fields and stops, so her normal BMI and active lifestyle are invisible. "
            "Second, it never updates: claims come back over the years but the rule "
            "stays frozen, repeating the same mistake. And third, nobody checks "
            "fairness: no one is watching whether whole regions or occupations are "
            "quietly shut out.\n\n"
            "My thesis asks whether a system that learns can do better on all three."
        ),
    },
    {
        "num": 6,
        "title": "GOAL & OBJECTIVES",
        "timing": "~1.5 min",
        "script": (
            "So here is the goal, in one sentence: can a system that learns from "
            "every decision underwrite better — and stay fair — than today's fixed "
            "rules?\n\n"
            "That breaks into three research questions. One: does the learning "
            "system earn more and make fewer mistakes than the fixed-rule baseline? "
            "Two: does it stay fair across regions and occupations, without being "
            "explicitly told to? And three: which learning method works best?\n\n"
            "[Point to the SDG strip.]\n\n"
            "And why it matters: this touches three of Cambodia's Sustainable "
            "Development Goals — good health, no poverty, and reduced inequality."
        ),
    },
    {
        "num": 7,
        "title": "ABOUT DECENT ACTUARIAL CONSULTANTS",
        "timing": "~1 min",
        "script": (
            "I pursued this at Decent Actuarial Consultants — DAC — as a research "
            "intern from March 2026.\n\n"
            "DAC is a regional actuarial consultancy headquartered in Taipei, with "
            "offices across Taiwan, Vietnam and Cambodia. Their work spans life and "
            "general insurance — appointed-actuary services, IFRS 17, product "
            "development, ALM and ERM, M&A advisory, and university partnerships.\n\n"
            "Their clients include insurers who face applicants like Sophea every "
            "day. Under Mr. ON Radet, my task was to design, validate, and prototype "
            "an adaptive underwriting system. This thesis and the demo are the "
            "outputs of that internship."
        ),
    },
    {
        "num": 8,
        "title": "PROJECT TIMELINE",
        "timing": "~0.5 min",
        "script": (
            "The work ran over a three-month internship. The first month was "
            "research and modelling — literature, the dataset, and the baselines. "
            "The second was experiments. The third was engineering the demo and "
            "writing up. Four milestones, from baselines ready to thesis complete."
        ),
    },
    {
        "num": 9,
        "title": "THE LITERATURE, IN ONE TABLE",
        "timing": "~1.5 min",
        "script": (
            "Four bodies of work meet in this thesis, and I've put them in one "
            "table.\n\n"
            "First, health insurance in emerging markets — the surveys that tell us "
            "Cambodia is barely insured. Second, contextual bandits — the machine-"
            "learning method at the heart of this work, from Li and colleagues in "
            "2010 and Agrawal and Goyal in 2013; these learn which action pays off "
            "one decision at a time, without a big offline dataset. Third, fairness "
            "and drift monitoring — the Population Stability Index. And fourth, "
            "human-in-the-loop review.\n\n"
            "[Point to the green bar.]\n\n"
            "The gap is clear: no prior work applies online-learning underwriting "
            "to Cambodia. That is where this thesis sits."
        ),
    },
    {
        "num": 10,
        "title": "HOW THE SYSTEM WORKS",
        "timing": "~1 min",
        "script": (
            "Here's the whole system on one line. In plain words: it decides, sees "
            "what happens, and gets a little smarter each round.\n\n"
            "It reads a short profile of the applicant. It picks one of four "
            "actions — Standard, Rated, Decline, or Refer to a human. It earns a "
            "reward: the premiums it collects minus the claims that follow. A "
            "fairness guardrail watches for drift, and the genuinely uncertain "
            "cases are handed to a human expert. Then it updates and moves to the "
            "next applicant."
        ),
    },
    {
        "num": 11,
        "title": "HOW THE SYSTEM DECIDES FOR SOPHEA",
        "timing": "~1.5 min",
        "script": (
            "Let's watch it decide for Sophea.\n\n"
            "[Point to the left panel.]\n\n"
            "On the left is what it knows about her — a short profile: age, "
            "non-smoker, managed blood pressure, active, rice farmer, low wealth. "
            "Thirty-four facts in all.\n\n"
            "[Point to the bars.]\n\n"
            "It scores each of the four options. Standard scores highest, at 0.52; "
            "Rated 0.31; Refer 0.28; Decline just 0.10. The highest score wins, so "
            "Sophea gets Standard coverage.\n\n"
            "In plain words: it estimates how each option would pay off for someone "
            "like her, then adds a small bonus for options it hasn't tried often — "
            "so it keeps learning. The exact formula is in Appendix A7 if you'd "
            "like it."
        ),
    },
    {
        "num": 12,
        "title": "WHAT THE SYSTEM EARNS",
        "timing": "~1 min",
        "script": (
            "What does 'reward' actually mean? It's simple: reward equals premiums "
            "collected minus claims paid.\n\n"
            "Insure someone who stays healthy and you collect premiums and pay few "
            "claims — you earn. Insure a frequent claimer and the claims outrun the "
            "premiums — you lose. Decline everyone and you collect nothing.\n\n"
            "So the system is rewarded for insuring the right people at the right "
            "price — not for saying yes to everyone, and not for saying no to "
            "everyone. The full actuarial detail — risk loadings, adverse "
            "selection, price elasticity — is in the reward simulator, Table 8, "
            "and Appendix A5."
        ),
    },
    {
        "num": 13,
        "title": "THE FAIRNESS GUARDRAIL",
        "timing": "~1 min",
        "script": (
            "Learning fast is not enough — it also has to stay fair. That's the "
            "job of the Population Stability Index, or PSI.\n\n"
            "PSI asks one question: are the people we approve today drifting away "
            "from the people we trained on? It's a simple traffic light. Green, "
            "below 0.10, means all clear. Amber, between 0.10 and 0.25, means watch "
            "closely. Red, above 0.25, means stop and recalibrate.\n\n"
            "And when the system isn't sure about a case, it hands it to a human "
            "expert — about one in seventy. The exact formula is in Appendix A8."
        ),
    },
    {
        "num": 14,
        "title": "THE DATA",
        "timing": "~1 min",
        "script": (
            "Now, the data. Two thousand synthetic applicants, thirty-four facts "
            "about each person, four possible decisions, anchored to four real "
            "Cambodian surveys.\n\n"
            "[Gesture at the table.]\n\n"
            "The features span demographics and vitals, lifestyle, social "
            "determinants, economics, clinical flags, and one-hot region and "
            "occupation.\n\n"
            "Why synthetic? Because no insurer would share real records. But the "
            "data is shaped to match published Cambodia statistics — the CDHS "
            "survey, STEPS, ILO, and WHO — so it behaves realistically even though "
            "no real person is in it."
        ),
    },
    {
        "num": 15,
        "title": "HOW WE TESTED IT",
        "timing": "~1 min",
        "script": (
            "How did I test it? Three things, in plain words.\n\n"
            "Five thousand applicants, seen one at a time in order — exactly how it "
            "would run in production. Twenty independent repeats, each with a "
            "different random draw; the learning system won every single time. And "
            "a head-to-head comparison against the incumbent static-rules approach "
            "on the same applicants.\n\n"
            "One subtlety: a learning system has no train/test split — it learns as "
            "it goes. So I judge it by how much reward it loses versus a "
            "perfect-knowledge Oracle, averaged over the twenty repeats. Appendix "
            "A6 explains that in full, and the statistics underneath are all "
            "standard — bootstrap intervals, Wilcoxon tests, Bonferroni, and "
            "effect sizes."
        ),
    },
    {
        "num": 16,
        "title": "THE HEADLINE RESULT",
        "timing": "~1.5 min",
        "script": (
            "This is the headline result. The learning system earned twenty-five "
            "point two percent more cumulative reward than the static rules — "
            "$90,540 versus $72,292, over twenty seeds.\n\n"
            "In plain words: for every hundred dollars the old rules earned, the "
            "learning system earned a hundred and twenty-five — and the gap held "
            "across all twenty repeats. Statistically it's about as clean as it "
            "gets: p below 0.001, Cohen's d of 2.98.\n\n"
            "[Point to the curve.]\n\n"
            "You can see it on the right: the two lines track together early, then "
            "the learning system pulls steadily ahead as it learns."
        ),
    },
    {
        "num": 17,
        "title": "THE BASELINE LADDER",
        "timing": "~1.5 min",
        "script": (
            "I want to be honest about where the bandit sits, so I tested it "
            "against a whole ladder of alternatives.\n\n"
            "Every realistic alternative lands below the bandits — the static "
            "incumbent, epsilon-greedy, always-standard, random. The two learning "
            "methods, LinTS and LinUCB, are the best deployable policies on the "
            "board.\n\n"
            "[Point to the top rows.]\n\n"
            "Now, two things sit above them. The Oracle, which sees the future — "
            "not deployable. And AlwaysRATED, a trivial constant that rates "
            "everyone at a flat loading. It scores higher, but it approves nobody "
            "cheaply and everybody expensively — no regulator would allow it. So "
            "among policies you could actually deploy, the bandit leads."
        ),
    },
    {
        "num": 18,
        "title": "SOPHEA, THREE WAYS",
        "timing": "~1 min",
        "script": (
            "Let me bring it back to Sophea. Here is the same applicant, decided by "
            "three different systems.\n\n"
            "The static rules — today's incumbent — see two fields and say DECLINE. "
            "Our LinUCB bandit weighs her whole profile and offers STANDARD cover. "
            "And the Oracle, the perfect-knowledge benchmark that knows her true "
            "risk, also says STANDARD.\n\n"
            "That's the whole story in one line: the bandit reaches the answer the "
            "all-knowing benchmark picks — the static rule never can."
        ),
    },
    {
        "num": 19,
        "title": "FAIRNESS & HUMAN OVERSIGHT — RESULTS",
        "timing": "~1.5 min",
        "script": (
            "So it earns more. Is it fair — and does human oversight help? Yes to "
            "both.\n\n"
            "On fairness, across twenty seeds: region drift is green at 0.082, "
            "occupation drift is amber at 0.123, and approval parity is 85.7 and "
            "90.1 percent — both comfortably above the eighty-percent rule. I'll be "
            "transparent: one of six fairness checks failed narrowly on occupation. "
            "I report it and explain it — no regulatory threshold is breached.\n\n"
            "On oversight: adding a human review lifts reward by fourteen point "
            "eight percent — to $103,951 — for a cost of just 2.2 percent, by "
            "sending only about one in seventy cases to an expert. A real gain for "
            "a small cost."
        ),
    },
    {
        "num": 20,
        "title": "FINDINGS & LIMITATIONS",
        "timing": "~1.5 min",
        "script": (
            "Let me gather the findings — and be honest about the limits.\n\n"
            "Four findings. Learning beats static rules, by twenty-five percent. No "
            "demographic bias was introduced. It's the learning-as-it-goes, not the "
            "exploration, that does the work — the greedy version ties the full one. "
            "And human oversight adds value cheaply.\n\n"
            "And the limits. The data is synthetic — anchored to real surveys, but "
            "not real claims. The reward is single-period, so no multi-year "
            "renewals yet. And it's calibrated to one country; a constant policy "
            "still tops the ladder. These are real, and they point straight at the "
            "future work."
        ),
    },
    {
        "num": 21,
        "title": "FUTURE WORK",
        "timing": "~1 min",
        "script": (
            "So where next? Four directions.\n\n"
            "First, handle change over time — forgetting-factor updates paired with "
            "the PSI early warning, so it adapts faster when the population shifts. "
            "Second, richer models — neural bandits that go beyond thirty-four "
            "simple features. Third, real-world deployment — a shadow-mode trial "
            "with a Cambodian insurer, using a claims-lag proxy for delayed reward. "
            "And fourth, lifetime customer value — retention and renewals, beyond a "
            "single decision."
        ),
    },
    {
        "num": 22,
        "title": "THE TAKEAWAY",
        "timing": "~0.5 min",
        "script": (
            "So let me close where I began.\n\n"
            "In 2023, the static system issued Sophea a DECLINE. In 2026, the "
            "learning system issues STANDARD. The same woman — but a system that "
            "finally sees her whole picture, and keeps learning.\n\n"
            "And Cambodia has hundreds of thousands of applicants like her."
        ),
    },
    {
        "num": 23,
        "title": "LIVE DEMONSTRATION",
        "timing": "~2 min",
        "script": (
            "Let me show you it working — this is a live FastAPI app, not a "
            "mockup.\n\n"
            "[Switch to the browser: uvicorn demo.desk.app:app --port 8000.]\n\n"
            "First, I'll score Sophea live and you'll see the decision and the "
            "fairness guardrail on screen. Then I'll score a higher-risk applicant "
            "so you can see the decision and the reward change. And finally, on the "
            "'Watch it Learn' tab, I'll play the cumulative-reward animation — the "
            "learning system pulling ahead of the static rules, round by round."
        ),
    },
    {
        "num": 24,
        "title": "IF LIVE DEMO FAILS — A SCORED APPLICANT",
        "timing": "contingency",
        "script": (
            "[Use only if the live app fails — wifi, server, or port.]\n\n"
            "This is a captured screenshot of the Underwriting Desk: a sample "
            "applicant scored, with the decision and the inline fairness guardrail "
            "shown just as they appear live."
        ),
    },
    {
        "num": 25,
        "title": "IF LIVE DEMO FAILS — WATCH IT LEARN",
        "timing": "contingency",
        "script": (
            "[Use only if the live app fails.]\n\n"
            "And this is the 'Watch it Learn' view: the cumulative-reward curve, "
            "the learning system versus the static rules, exactly as the live "
            "animation renders it."
        ),
    },
    {
        "num": 26,
        "title": "THANK YOU",
        "timing": "~0.5 min",
        "script": (
            "That is my thesis. Thank you very much for your attention — I welcome "
            "your questions.\n\n"
            "[If a question targets a specific number, advance to the matching "
            "appendix: A1 the full ladder, A2 the number reconciliation, A3 all six "
            "fairness checks, A4 the maths, A5 the sensitivity analysis, A6 the "
            "no-split point, A7 the exploration bonus, or A8 the PSI walkthrough.]"
        ),
    },
    # ── Appendix (on standby; only walked if asked) ────────────────────────
    {
        "num": "A1",
        "title": "A1: COMPLETE BASELINE LADDER",
        "timing": "on standby",
        "script": (
            "This is the complete ladder, with 95% confidence intervals. From the "
            "Oracle at the top down to Random at the bottom. The point to make: the "
            "only policies above LinTS and LinUCB are the non-deployable Oracle, an "
            "in-sample logistic ceiling, and the inadmissible AlwaysRATED constant. "
            "Among everything you could deploy, the bandits lead."
        ),
    },
    {
        "num": "A2",
        "title": "A2: NUMBER RECONCILIATION",
        "timing": "on standby",
        "script": (
            "This slide reconciles the three percentages in the talk. The headline "
            "is plus 25.2 percent — LinUCB versus Static XGB, the primary "
            "pre-registered result. Plus 29.8 percent is LinTS on a different "
            "benchmark harness. And plus 14.8 percent is the human-in-the-loop "
            "gain over the vanilla bandit across twenty seeds. Note that at the "
            "single illustrative seed 42 the HITL figure reads plus 6.5 percent — "
            "same comparison, one seed instead of twenty; the twenty-seed 14.8 "
            "percent is the number I quote."
        ),
    },
    {
        "num": "A3",
        "title": "A3: ALL 6 FAIRNESS CRITERIA (EXP-006)",
        "timing": "on standby",
        "script": (
            "All six fairness criteria. PSI on region and occupation, the "
            "four-fifths approval-parity rule on both, and permutation tests on "
            "both. Five pass. Criterion six — the occupation permutation test — is "
            "marked FAILED, in the interest of honesty: the dependence is "
            "statistically significant but practically small. PSI stays amber, "
            "parity is 90 percent, and no regulatory threshold is crossed."
        ),
    },
    {
        "num": "A4",
        "title": "A4: MATHEMATICAL DETAILS",
        "timing": "on standby",
        "script": (
            "The maths, for completeness. On the left, the LinUCB update rule — the "
            "design matrix, the reward vector, the ridge estimate, and the UCB "
            "score — plus the PSI formula and the human-in-the-loop dual update. On "
            "the right, every hyperparameter: alpha 1.0, LinTS v-squared 1.0, ridge "
            "lambda 1.0, horizon 5,000, twenty seeds, and the PSI thresholds."
        ),
    },
    {
        "num": "A5",
        "title": "A5: SENSITIVITY ANALYSIS (EXP-012, 10 SEEDS)",
        "timing": "on standby",
        "script": (
            "The sensitivity analysis. On the left, the alpha sweep over ten seeds "
            "— alpha 1.0 gives $91,378 and the lowest regret; the reward barely "
            "moves across the whole range. On the right, LinUCB's advantage over "
            "Static XGB holds at every adverse-selection factor and every "
            "elasticity slope tested. One reconciliation note: the alpha-1.0 figure "
            "here is $91,378 over ten seeds, while the headline $90,540 is the "
            "twenty-seed number — both real, just different seed counts."
        ),
    },
    {
        "num": "A6",
        "title": "A6: WHY A BANDIT HAS NO TRAIN/TEST SPLIT",
        "timing": "on standby",
        "script": (
            "Why there's no train/test split. A supervised model splits the data, "
            "fits once, and freezes. A bandit meets applicants one at a time — every "
            "round is both train and test, and the ridge prior regularises online, "
            "so there is no static fit to overfit. I measure generalisation as "
            "cumulative regret versus the Oracle, averaged over twenty independent "
            "seeds — the seeds play the role of the held-out set. And the Static "
            "XGB baseline is fit offline and frozen, so the comparison is fair."
        ),
    },
    {
        "num": "A7",
        "title": "A7: THE EXPLORATION BONUS (α), IN PLAIN WORDS",
        "timing": "on standby",
        "script": (
            "The exploration bonus, alpha, in plain words. An arm's score is its "
            "expected payoff plus alpha times how-unsure-we-still-are. In the "
            "formula, x-bar is the best guess of the payoff, the square-root term is "
            "how uncertain we still are, and alpha — which we set to 1.0 — controls "
            "how adventurous to be. For Sophea's Standard arm, the 0.52 is a payoff "
            "guess plus a small curiosity bonus. Too high wastes decisions "
            "exploring; too low and it never learns. I swept alpha from 0.1 to 5 — "
            "the reward barely moves, and 1.0 is best."
        ),
    },
    {
        "num": "A8",
        "title": "A8: THE FAIRNESS INDEX (PSI), STEP BY STEP",
        "timing": "on standby",
        "script": (
            "The PSI, step by step. It sums, over each group, the difference "
            "between the share we approve now and the share in the training data, "
            "times the log of their ratio. The worked example with two regions "
            "comes out to about 0.010 — comfortably green. Green is below 0.10, "
            "amber to 0.25, red above. Our own result: region 0.082, green; "
            "occupation 0.123, amber. And PSI is a monitor, not an enforcer — it "
            "detects drift but does not change the policy."
        ),
    },
]


# ---------------------------------------------------------------------------
# Helper: resolve thumbnail PNG path
# ---------------------------------------------------------------------------
def _slide_png(num):
    if not _THUMBNAILS_CURRENT:
        return None
    idx = _APPENDIX_SLIDE_MAP[num] if isinstance(num, str) and num.startswith("A") else int(num)
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

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title_p.add_run("THESIS DEFENSE PRESENTATION SCRIPT")
    tr.bold = True
    tr.font.size = Pt(16)
    tr.font.color.rgb = DRGBColor(0x1B, 0x56, 0x97)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sub_p.add_run(
        "Adaptive Health Insurance Underwriting via Contextual Bandits:\n"
        "A Reinforcement Learning Approach for Cambodia\n\n"
        "LUN CHANPOLY  ·  ITC-AMS  ·  8 July 2026"
    )
    sr.font.size = Pt(11)
    sr.font.color.rgb = DRGBColor(0x40, 0x40, 0x40)

    doc.add_paragraph()

    how_p = doc.add_paragraph()
    hr = how_p.add_run(
        "HOW TO USE THIS SCRIPT\n"
        "Read aloud naturally — do not recite word-for-word if it feels unnatural. "
        "Bracketed notes [like this] are stage directions, not spoken text. The "
        "Sophea narrative is the emotional thread — carry it slides 4, 11, 18 and "
        "22. The eight appendix slides A1-A8 are on standby; only advance to them "
        "if the Committee asks a question that slide addresses."
    )
    hr.font.size = Pt(10)
    hr.italic = True

    doc.add_page_break()

    for slide in SLIDES:
        num = slide["num"]
        is_appendix = isinstance(num, str) and num.startswith("A")
        label = f"APPENDIX {num}" if is_appendix else f"SLIDE {num}"

        h = doc.add_heading(f"{label}  ·  {slide['title']}", level=2)
        for run in h.runs:
            run.font.color.rgb = DRGBColor(0x1F, 0x6F, 0xC4)

        tp = doc.add_paragraph()
        tp.paragraph_format.space_before = Pt(0)
        tp.paragraph_format.space_after  = Pt(4)
        tr2 = tp.add_run(f"Timing: {slide['timing']}")
        tr2.italic = True
        tr2.font.size = Pt(9)
        tr2.font.color.rgb = DRGBColor(0x70, 0x70, 0x70)

        png = _slide_png(num)
        if png and os.path.isfile(png):
            ip = doc.add_paragraph()
            ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ip.add_run().add_picture(png, width=Cm(14))

        for block in slide["script"].split("\n\n"):
            block = block.strip()
            if not block:
                continue
            sp = doc.add_paragraph(block)
            sp.paragraph_format.space_before = Pt(4)
            sp.paragraph_format.space_after  = Pt(4)
            for run in sp.runs:
                run.font.size = Pt(11)

        doc.add_paragraph()

    doc.save(DOCX_OUT)
    print(f"Saved docx: {DOCX_OUT}")


# ---------------------------------------------------------------------------
# Alignment verification — must pass before speaker notes get written to pptx
# ---------------------------------------------------------------------------
def _norm(s):
    return "".join(ch.lower() for ch in s if ch.isalnum())


# Hero/cover slides have no standard title_block, so their first text-frame text
# does not match slide["title"] verbatim; give them explicit expected substrings.
_TITLE_OVERRIDE = {
    1: "institute of technology",
    26: "thank you",
}


def _first_text(slide):
    """First on-screen text — skipping the persistent nav-tab labels, which are
    drawn before the title on every content slide."""
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip():
            txt = shape.text_frame.text.strip()
            if txt in _NAV_LABELS:
                continue
            return txt.split("\n")[0]
    return ""


def verify_alignment(prs):
    """Cross-check SLIDES order against the live pptx. Returns (ok, problems)."""
    total = len(prs.slides)
    problems = []
    if total != 34:
        problems.append(f"expected 34 slides in pptx, found {total}")

    for slide_data in SLIDES:
        num = slide_data["num"]
        if isinstance(num, str) and num.startswith("A"):
            if num not in _APPENDIX_SLIDE_MAP:
                problems.append(f"slide {num}: no entry in _APPENDIX_SLIDE_MAP")
                continue
            idx = _APPENDIX_SLIDE_MAP[num] - 1
        else:
            idx = int(num) - 1

        if idx < 0 or idx >= total:
            problems.append(f"slide {num}: index {idx} out of range ({total} slides)")
            continue

        actual = _first_text(prs.slides[idx])
        expected = _TITLE_OVERRIDE.get(num, slide_data["title"])
        e, a = _norm(expected), _norm(actual)
        if not e or not a or not (e in a or a in e or e[:15] in a or a[:15] in e):
            problems.append(
                f"slide {num} (pptx slide {idx + 1}): expected title-ish "
                f"'{expected}' but pptx slide starts with '{actual}'"
            )

    return (len(problems) == 0, problems)


# ---------------------------------------------------------------------------
# Inject speaker notes into pptx
# ---------------------------------------------------------------------------
def inject_speaker_notes():
    prs = Presentation(PPTX_PATH)

    ok, problems = verify_alignment(prs)
    if not ok:
        print("ABORTING speaker-notes injection — SLIDES order does not "
              "verifiably line up 1:1 with the live pptx:")
        for p in problems:
            print(f"  - {p}")
        print(f"Nothing was written to {PPTX_PATH}.")
        return False

    for slide_data in SLIDES:
        num = slide_data["num"]
        if isinstance(num, str) and num.startswith("A"):
            idx = _APPENDIX_SLIDE_MAP[num] - 1
        else:
            idx = int(num) - 1
        tf = prs.slides[idx].notes_slide.notes_text_frame
        tf.clear()
        tf.text = slide_data["script"]

    prs.save(PPTX_PATH)
    print(f"Speaker notes injected: {PPTX_PATH}")
    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    build_doc()
    inject_speaker_notes()
