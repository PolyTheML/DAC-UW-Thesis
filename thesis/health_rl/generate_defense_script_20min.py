"""
Generate Poly_defense_script_20min.docx — the STRICT 20-MINUTE delivery cut.

Companion to generate_defense_script_v2.py, NOT a replacement.
Poly_defense_script_v2.docx is the deep-study version — full sentences per slide.
Poly_defense_script_20min.docx (this file) is the tight cut you rehearse against
the real clock, leaving buffer inside the 20-minute slot for pacing, gestures,
and the live demo running long.

SYNCED 2026-07-02 to the 34-slide "Sreynich-flow" deck
(Poly_defense_presentation_v3.pptx, built by build_defense_v3.py): every
presented slide (1-26) is narrated tersely; the 8 appendix slides A1-A8 stay
on standby for Q&A. num is the PHYSICAL slide number, so embedded thumbnails
line up 1:1 with the deck. HITL headline is the canonical 20-seed +14.8%
($103,951 vs $90,540, p<0.001, d=2.65); the stale +6.5% survives only as the
seed-42 illustrative reading inside the A2 reconciliation note.

Run from C:\\DAC-UW-Thesis\\:
    python thesis/health_rl/generate_defense_script_20min.py
"""

import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.dml.color import RGBColor as DRGBColor

DOCX_OUT = r"thesis\health_rl\Poly_defense_script_20min.docx"
SLIDES_DIR = r"thesis\health_rl\slide_thumbnails_v3"

# ---------------------------------------------------------------------------
# SLIDES — presented slides 1-26 (terse) + appendix A2/A6 on standby.
# num = physical slide number; timings are hard budgets summing well inside
# 20 min so the live demo can run long.
# ---------------------------------------------------------------------------
SLIDES = [
    {
        "num": 1, "title": "TITLE SLIDE", "timing": "30 sec",
        "script": (
            "Good morning, Distinguished Committee. I am Lun Chanpoly, defending "
            "Adaptive Health Insurance Underwriting via Contextual Bandits — a "
            "Reinforcement Learning approach for Cambodia, from my internship at "
            "Decent Actuarial Consultants under Dr. Has Sothea and Mr. ON Radet.\n\n"
            "Seven short sections, plain language, maths in the appendix. Let me "
            "start with a person named Sophea."
        ),
    },
    {
        "num": 2, "title": "TABLE OF CONTENTS", "timing": "8 sec",
        "script": "Here's the roadmap — problem, literature, design, results, "
                  "conclusion, and a live demo. [Advance.]",
    },
    {
        "num": 3, "title": "A MARKET THE SYSTEM WAS NOT BUILT FOR", "timing": "25 sec",
        "script": (
            "This is Sophea's market. In Cambodia, fewer than two percent have any "
            "health insurance. The state scheme reaches only formal workers — about "
            "sixteen percent. Everyone else is underwritten by hand. Sophea "
            "represents the ninety-eight percent the system was not built for."
        ),
    },
    {
        "num": 4, "title": "MEET SOPHEA", "timing": "40 sec",
        "script": (
            "[Point to the profile, then the flags, then the red box.]\n\n"
            "Sophea: 42, a rice farmer from Kampong Cham. Active, non-smoker, BMI "
            "24.1, one flag — managed hypertension.\n\n"
            "In 2023 she applies for cover. The static system checks two fields — "
            "occupation agriculture, condition hypertension — both cross a "
            "threshold. Decision: DECLINE. Was that the right answer?"
        ),
    },
    {
        "num": 5, "title": "WHY STATIC RULES FAIL", "timing": "25 sec",
        "script": (
            "The rule couldn't have known. It can't see her full picture, and it "
            "never learns. Three problems: fixed cutoffs that ignore context, a "
            "model that never updates from claims, and no one checking whether "
            "whole groups get shut out."
        ),
    },
    {
        "num": 6, "title": "GOAL & OBJECTIVES", "timing": "30 sec",
        "script": (
            "The goal in one sentence: can a system that learns from every decision "
            "underwrite better — and stay fair — than today's fixed rules? Three "
            "questions: does it earn more, does it stay fair without being told to, "
            "and which method wins. And it touches three of Cambodia's SDGs — "
            "health, poverty, and inequality."
        ),
    },
    {
        "num": 7, "title": "ABOUT DECENT ACTUARIAL CONSULTANTS", "timing": "20 sec",
        "script": (
            "I did this at Decent Actuarial Consultants — a regional actuarial "
            "firm across Taiwan, Vietnam and Cambodia, whose clients face "
            "applicants like Sophea daily. My task: design, validate, and "
            "prototype an adaptive underwriting system."
        ),
    },
    {
        "num": 8, "title": "PROJECT TIMELINE", "timing": "12 sec",
        "script": "A three-month internship: research and modelling, then "
                  "experiments, then engineering the demo and writing up. [Advance.]",
    },
    {
        "num": 9, "title": "THE LITERATURE, IN ONE TABLE", "timing": "35 sec",
        "script": (
            "Four bodies of work, in one table: emerging-market health insurance, "
            "contextual bandits — the method at the core of this, from Li 2010 and "
            "Agrawal and Goyal 2013 — fairness and drift monitoring, and "
            "human-in-the-loop review. The gap: no prior work applies "
            "online-learning underwriting to Cambodia."
        ),
    },
    {
        "num": 10, "title": "HOW THE SYSTEM WORKS", "timing": "25 sec",
        "script": (
            "The whole system on one line: it decides, sees what happens, and gets "
            "a little smarter each round. It reads a short profile, picks one of "
            "four actions, earns a reward, checks fairness, and refers the "
            "uncertain cases to a human."
        ),
    },
    {
        "num": 11, "title": "HOW THE SYSTEM DECIDES FOR SOPHEA", "timing": "35 sec",
        "script": (
            "Watch it decide for Sophea. On the left, what it knows — a short "
            "profile. It scores the four options: Standard highest at 0.52, then "
            "Rated, Refer, Decline. Highest wins, so Sophea gets Standard. In plain "
            "words: it estimates how each option pays off, plus a small bonus for "
            "options it hasn't tried much."
        ),
    },
    {
        "num": 12, "title": "WHAT THE SYSTEM EARNS", "timing": "25 sec",
        "script": (
            "Reward is simple: premiums collected minus claims paid. Insure someone "
            "healthy, you earn; a frequent claimer, you lose; decline everyone, you "
            "earn nothing. So it's rewarded for insuring the right people at the "
            "right price."
        ),
    },
    {
        "num": 13, "title": "THE FAIRNESS GUARDRAIL", "timing": "30 sec",
        "script": (
            "The fairness guardrail, PSI, asks one question: are the people we "
            "approve today drifting away from the people we trained on? A traffic "
            "light — green below 0.10, amber to 0.25, red above. And uncertain "
            "cases go to a human, about one in seventy."
        ),
    },
    {
        "num": 14, "title": "THE DATA", "timing": "25 sec",
        "script": (
            "Two thousand synthetic applicants, thirty-four facts each, four "
            "decisions. Synthetic because no insurer shares real records — but "
            "shaped to match published Cambodia statistics: CDHS, STEPS, ILO, WHO."
        ),
    },
    {
        "num": 15, "title": "HOW WE TESTED IT", "timing": "25 sec",
        "script": (
            "Five thousand applicants one at a time, twenty independent repeats — "
            "the learning system won every time — head-to-head against the static "
            "rules. A bandit has no train/test split, so I judge it by reward lost "
            "versus a perfect Oracle, averaged over the twenty repeats."
        ),
    },
    {
        "num": 16, "title": "THE HEADLINE RESULT", "timing": "40 sec",
        "script": (
            "The headline: twenty-five point two percent more reward than the "
            "static rules — $90,540 versus $72,292, over twenty seeds. In plain "
            "words, for every hundred dollars the old rules earned, the learning "
            "system earned a hundred and twenty-five — and the gap held across all "
            "twenty repeats. p below 0.001, d of 2.98."
        ),
    },
    {
        "num": 17, "title": "THE BASELINE LADDER", "timing": "30 sec",
        "script": (
            "Against a full ladder, every realistic alternative lands below the "
            "bandits. Two things sit above them — the Oracle, which sees the "
            "future, and AlwaysRATED, which rates everyone at a flat loading and no "
            "regulator would allow. Among deployable policies, the bandit leads."
        ),
    },
    {
        "num": 18, "title": "SOPHEA, THREE WAYS", "timing": "25 sec",
        "script": (
            "The same applicant, three systems. Static rules say DECLINE. Our "
            "LinUCB bandit says STANDARD. And the perfect-knowledge Oracle also "
            "says STANDARD. The bandit reaches the answer the all-knowing benchmark "
            "picks — the static rule never can."
        ),
    },
    {
        "num": 19, "title": "FAIRNESS & HUMAN OVERSIGHT — RESULTS", "timing": "40 sec",
        "script": (
            "Is it fair, and does oversight help? Region drift green at 0.082, "
            "occupation amber at 0.123, approval parity 85.7 and 90.1 percent — "
            "above the eighty-percent rule. One of six checks failed narrowly on "
            "occupation; I report it, no threshold breached. And a human review "
            "lifts reward by fourteen point eight percent for a 2.2 percent cost — "
            "one case in seventy."
        ),
    },
    {
        "num": 20, "title": "FINDINGS & LIMITATIONS", "timing": "35 sec",
        "script": (
            "Four findings: learning beats static rules by twenty-five percent; no "
            "bias introduced; it's the learning, not the exploration, that does the "
            "work; and human oversight adds value cheaply. And the honest limits: "
            "synthetic data, single-period reward, one country — a constant policy "
            "still tops the ladder."
        ),
    },
    {
        "num": 21, "title": "FUTURE WORK", "timing": "25 sec",
        "script": (
            "Four directions: handle change over time with forgetting plus PSI "
            "early warning; richer neural models; a real shadow-mode trial with a "
            "Cambodian insurer; and lifetime customer value beyond a single "
            "decision."
        ),
    },
    {
        "num": 22, "title": "THE TAKEAWAY", "timing": "20 sec",
        "script": (
            "So, to close: in 2023 the static system declined Sophea; in 2026 the "
            "learning system offers her Standard cover. The same woman — a system "
            "that finally sees her whole picture. And Cambodia has hundreds of "
            "thousands like her."
        ),
    },
    {
        "num": 23, "title": "LIVE DEMONSTRATION", "timing": "75 sec",
        "script": (
            "[Switch to the browser — a live FastAPI app, not a mockup.]\n\n"
            "First I score Sophea live with the fairness guardrail on screen. Then "
            "a higher-risk applicant, to show the decision and reward change. Then "
            "'Watch it Learn' — the cumulative-reward animation, the learning "
            "system pulling ahead of the static rules."
        ),
    },
    {
        "num": 24, "title": "IF LIVE DEMO FAILS — A SCORED APPLICANT", "timing": "skip if live demo worked",
        "script": "[Backup only.] A captured Underwriting Desk screenshot — a "
                  "sample applicant scored, decision and fairness guardrail shown.",
    },
    {
        "num": 25, "title": "IF LIVE DEMO FAILS — WATCH IT LEARN", "timing": "skip if live demo worked",
        "script": "[Backup only.] The cumulative-reward curve — learning system "
                  "versus static rules — as the live animation renders it.",
    },
    {
        "num": 26, "title": "THANK YOU / Q&A", "timing": "15 sec",
        "script": (
            "That is my thesis. Thank you for your attention — I welcome your "
            "questions. If a question targets a number, I have eight appendix "
            "slides on standby."
        ),
    },
    {
        "num": 28, "title": "APPENDIX A2: NUMBER RECONCILIATION", "timing": "if asked (Q&A)",
        "script": (
            "The three percentages. Plus 25.2 percent is the headline — LinUCB vs "
            "Static XGB, pre-registered. Plus 29.8 percent is LinTS on a different "
            "harness. Plus 14.8 percent is the human-in-the-loop gain over the "
            "vanilla bandit across twenty seeds. At the single seed 42 that same "
            "HITL comparison reads plus 6.5 percent — one seed, not twenty; I quote "
            "the twenty-seed 14.8 percent."
        ),
    },
    {
        "num": 32, "title": "APPENDIX A6: WHY A BANDIT HAS NO TRAIN/TEST SPLIT", "timing": "if asked (Q&A)",
        "script": (
            "A supervised model splits data, fits once, freezes. A bandit meets "
            "applicants one at a time — every round is both train and test, "
            "regularised online by a ridge prior, so there's no static fit to "
            "overfit. I measure generalisation as cumulative regret versus the "
            "Oracle over twenty seeds; the Static XGB baseline is fit offline and "
            "frozen, so the comparison is fair."
        ),
    },
]


def _slide_png(num):
    return os.path.join(SLIDES_DIR, f"slide_{int(num):03d}.png")


def build_doc():
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title_p.add_run("THESIS DEFENSE — 20-MINUTE DELIVERY SCRIPT")
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
        "This is the STRICT 20-minute cut, synced to the 34-slide deck "
        "(Poly_defense_presentation_v3.pptx) — see the budgeted total below, "
        "which leaves buffer for pacing and the live demo. Rehearse from THIS "
        "script against a clock; use Poly_defense_script_v2.docx only for deeper "
        "background study. Bracketed notes [like this] are stage directions. The "
        "eight appendix slides A1-A8 are not part of the timed 20 minutes; A2 and "
        "A6 are transcribed here as the two most likely Q&A follow-ups."
    )
    hr.font.size = Pt(10)
    hr.italic = True

    doc.add_page_break()

    total_seconds = 0
    for slide in SLIDES:
        parts = slide["timing"].split()
        if parts and parts[0].isdigit():
            total_seconds += int(parts[0])

    tot_p = doc.add_paragraph()
    tot_r = tot_p.add_run(
        f"Budgeted talk-time (excluding 'skip if live demo worked' and Q&A "
        f"slides): ~{total_seconds // 60} min {total_seconds % 60} sec"
    )
    tot_r.bold = True
    tot_r.font.size = Pt(10)
    doc.add_paragraph()

    for slide in SLIDES:
        num = slide["num"]
        h = doc.add_heading(f"SLIDE {num}  ·  {slide['title']}", level=2)
        for run in h.runs:
            run.font.color.rgb = DRGBColor(0x1F, 0x6F, 0xC4)

        tp = doc.add_paragraph()
        tp.paragraph_format.space_before = Pt(0)
        tp.paragraph_format.space_after = Pt(4)
        tr2 = tp.add_run(f"Timing budget: {slide['timing']}")
        tr2.italic = True
        tr2.font.size = Pt(9)
        tr2.font.color.rgb = DRGBColor(0x70, 0x70, 0x70)

        png = _slide_png(num)
        if os.path.isfile(png):
            ip = doc.add_paragraph()
            ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ip.add_run().add_picture(png, width=Cm(14))

        for block in slide["script"].split("\n\n"):
            block = block.strip()
            if not block:
                continue
            sp = doc.add_paragraph(block)
            sp.paragraph_format.space_before = Pt(4)
            sp.paragraph_format.space_after = Pt(4)
            for run in sp.runs:
                run.font.size = Pt(11)

        doc.add_paragraph()

    doc.save(DOCX_OUT)
    print(f"Saved docx: {DOCX_OUT}")
    print(f"Budgeted talk-time: ~{total_seconds // 60} min {total_seconds % 60} sec")


if __name__ == "__main__":
    build_doc()
