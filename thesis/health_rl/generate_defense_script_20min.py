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
            "Good morning, Distinguished Committee. My name is Lun Chanpoly, and "
            "I'm here to defend Adaptive Health Insurance Underwriting via "
            "Contextual Bandits — a reinforcement learning approach for Cambodia. "
            "This grew out of my internship at Decent Actuarial Consultants, under "
            "Dr. Has Sothea and Mr. ON Radet.\n\n"
            "I've kept this to seven short sections, in plain language — the math "
            "lives in the appendix if you want it. But I'd rather start with a "
            "person. Her name is Sophea."
        ),
    },
    {
        "num": 2, "title": "TABLE OF CONTENTS", "timing": "8 sec",
        "script": "Quick roadmap: the problem, what's been tried before, how I "
                  "built this, what it found, and then I'll show it to you live. "
                  "[Advance.]",
    },
    {
        "num": 3, "title": "A MARKET THE SYSTEM WAS NOT BUILT FOR", "timing": "25 sec",
        "script": (
            "This is the market Sophea lives in. In Cambodia, fewer than two "
            "percent of people carry any health insurance at all. The state scheme "
            "only reaches formal-sector workers — roughly sixteen percent of the "
            "workforce. Everyone else? Underwritten by hand, one judgment call at "
            "a time. Sophea is part of that other ninety-eight percent — the "
            "market this system was never built for."
        ),
    },
    {
        "num": 4, "title": "MEET SOPHEA", "timing": "40 sec",
        "script": (
            "[Point to the profile, then the flags, then the red box.]\n\n"
            "Meet Sophea. She's forty-two, a rice farmer in Kampong Cham. Active, "
            "doesn't smoke, BMI of 24.1 — and one flag on her chart: managed "
            "hypertension.\n\n"
            "In 2023, she applies for cover. The static system looks at exactly "
            "two fields — occupation is agriculture, condition is hypertension — "
            "and both cross a hard-coded threshold. The decision comes back: "
            "DECLINE.\n\n"
            "Was that the right call?"
        ),
    },
    {
        "num": 5, "title": "WHY STATIC RULES FAIL", "timing": "25 sec",
        "script": (
            "Here's the problem — the rule couldn't have known better. It only "
            "sees two fields, not her whole picture, and it never learns from what "
            "actually happens afterward. Three things are broken here: the "
            "cutoffs are fixed and ignore context, the model never updates itself "
            "from real claims, and nobody's checking whether whole groups are "
            "quietly getting shut out."
        ),
    },
    {
        "num": 6, "title": "GOAL & OBJECTIVES", "timing": "30 sec",
        "script": (
            "So here's the goal, in one sentence: can a system that learns from "
            "every decision underwrite better — and stay fairer — than today's "
            "fixed rules? That breaks into three questions I set out to answer: "
            "does it earn more money, does it stay fair without anyone telling it "
            "to, and which learning method actually wins. And underneath all of "
            "that, this touches three of Cambodia's Sustainable Development "
            "Goals — health, poverty, and inequality."
        ),
    },
    {
        "num": 7, "title": "ABOUT DECENT ACTUARIAL CONSULTANTS", "timing": "20 sec",
        "script": (
            "I did this work at Decent Actuarial Consultants — a regional "
            "actuarial firm operating across Taiwan, Vietnam, and Cambodia. Their "
            "clients face applicants like Sophea every single day. My task was to "
            "design, validate, and prototype an adaptive underwriting system for "
            "exactly that problem."
        ),
    },
    {
        "num": 8, "title": "PROJECT TIMELINE", "timing": "12 sec",
        "script": "Three months, roughly three phases: research and modelling "
                  "first, then the experiments, then building the demo and "
                  "writing it all up. [Advance.]",
    },
    {
        "num": 9, "title": "THE LITERATURE, IN ONE TABLE", "timing": "35 sec",
        "script": (
            "I pulled together four bodies of work into one table. Emerging-"
            "market health insurance. Contextual bandits — the method at the core "
            "of this thesis, going back to Li in 2010 and Agrawal and Goyal in "
            "2013. Fairness and drift monitoring. And human-in-the-loop review. "
            "Put them side by side, and one gap jumps out: nobody had applied "
            "online-learning underwriting to Cambodia before."
        ),
    },
    {
        "num": 10, "title": "HOW THE SYSTEM WORKS", "timing": "25 sec",
        "script": (
            "The whole system, in one line: it decides, watches what happens, and "
            "gets a little smarter every round. Concretely — it reads a short "
            "applicant profile, picks one of four actions, earns a reward based "
            "on the outcome, checks itself for fairness, and hands off the "
            "uncertain cases to a human."
        ),
    },
    {
        "num": 11, "title": "HOW THE SYSTEM DECIDES FOR SOPHEA", "timing": "35 sec",
        "script": (
            "Let's watch it actually decide, for Sophea specifically. On the left "
            "is everything it knows about her — that short profile. It scores all "
            "four options: Standard comes out highest at 0.52, then Rated, then "
            "Refer, then Decline. Highest score wins, so Sophea gets Standard. In "
            "plain words, it's estimating how each option would pay off — plus a "
            "small bonus for options it hasn't tried very often yet."
        ),
    },
    {
        "num": 12, "title": "WHAT THE SYSTEM EARNS", "timing": "25 sec",
        "script": (
            "The reward function is deliberately simple: premiums collected, "
            "minus claims paid. Insure someone healthy, and you earn. Insure a "
            "frequent claimer, and you lose. Decline everyone, and you earn "
            "nothing at all. So the incentive is exactly what you'd want — "
            "insure the right people, at the right price."
        ),
    },
    {
        "num": 13, "title": "THE FAIRNESS GUARDRAIL", "timing": "30 sec",
        "script": (
            "The fairness guardrail is called PSI, and it asks one question: are "
            "the people we're approving today drifting away from the people we "
            "originally trained on? Think of it as a traffic light — green below "
            "0.10, amber up to 0.25, red above that. And whenever the system's "
            "uncertain, it hands the case to a human — that's about one in every "
            "seventy applicants."
        ),
    },
    {
        "num": 14, "title": "THE DATA", "timing": "25 sec",
        "script": (
            "The dataset is two thousand synthetic applicants, thirty-four facts "
            "each, across four possible decisions. Synthetic, because no insurer "
            "was going to share real records with me — but shaped carefully to "
            "match published Cambodia statistics: the CDHS, STEPS, ILO, and WHO "
            "surveys."
        ),
    },
    {
        "num": 15, "title": "HOW WE TESTED IT", "timing": "25 sec",
        "script": (
            "I ran five thousand applicants through, one at a time, twenty "
            "independent repeats — head-to-head against the static rules. The "
            "learning system won every single time. Now, a bandit doesn't have a "
            "train/test split the way a normal model does, so instead I judge it "
            "by how much reward it loses compared to a perfect Oracle, averaged "
            "across those twenty repeats."
        ),
    },
    {
        "num": 16, "title": "THE HEADLINE RESULT", "timing": "40 sec",
        "script": (
            "So here's the headline number: twenty-five point two percent more "
            "reward than the static rules — $90,540 against $72,292, averaged "
            "over twenty seeds. Put plainly, for every hundred dollars the old "
            "rules earned, the learning system earned a hundred and twenty-five. "
            "And this wasn't a lucky run — the gap held across all twenty "
            "repeats, p below 0.001, effect size d of 2.98."
        ),
    },
    {
        "num": 17, "title": "THE BASELINE LADDER", "timing": "30 sec",
        "script": (
            "I didn't just compare against one baseline — I built a full ladder "
            "of them. And every realistic alternative lands below the bandit. "
            "Only two things sit above it: the Oracle, which cheats by seeing "
            "the future, and AlwaysRATED, which just rates every single "
            "applicant at a flat loading — something no regulator would ever "
            "actually allow. Among the policies you could actually deploy, the "
            "bandit leads."
        ),
    },
    {
        "num": 18, "title": "SOPHEA, THREE WAYS", "timing": "25 sec",
        "script": (
            "Same applicant, three systems, three answers. The static rules say "
            "DECLINE. Our LinUCB bandit says STANDARD. And the Oracle — the one "
            "with perfect, all-knowing information — also says STANDARD. So the "
            "bandit lands on the same answer as the all-knowing benchmark. The "
            "static rule never gets there."
        ),
    },
    {
        "num": 19, "title": "FAIRNESS & HUMAN OVERSIGHT — RESULTS", "timing": "40 sec",
        "script": (
            "Two questions here: is it fair, and does human oversight actually "
            "help? On fairness — region drift is green at 0.082, occupation is "
            "amber at 0.123, and approval parity sits at 85.7 and 90.1 percent, "
            "both clearing the eighty-percent rule. One of six checks came in "
            "narrowly on occupation — I report that honestly, though no "
            "threshold was actually breached. And on oversight — adding a human "
            "reviewer lifts reward by fourteen point eight percent, for a cost "
            "of just 2.2 percent of cases, about one in seventy."
        ),
    },
    {
        "num": 20, "title": "FINDINGS & LIMITATIONS", "timing": "35 sec",
        "script": (
            "So, what does this actually add up to? Four findings. Learning "
            "beats static rules by twenty-five percent. It doesn't introduce new "
            "bias while doing it. It's the learning itself doing the work, not "
            "just lucky exploration — I checked. And human oversight adds real "
            "value, cheaply. Now, the honest limits, because there are some: "
            "this is synthetic data, a single-period reward, one country — and "
            "a constant policy still tops the full ladder."
        ),
    },
    {
        "num": 21, "title": "FUTURE WORK", "timing": "25 sec",
        "script": (
            "Looking ahead, four directions feel worth chasing: handling change "
            "over time, using forgetting alongside PSI as an early-warning "
            "system; richer neural models; an actual shadow-mode trial with a "
            "Cambodian insurer; and thinking about lifetime customer value, not "
            "just a single decision."
        ),
    },
    {
        "num": 22, "title": "THE TAKEAWAY", "timing": "20 sec",
        "script": (
            "So, to close where I started. In 2023, the static system declined "
            "Sophea. Run the same profile through the learning system today, "
            "and it offers her Standard cover. Same woman — but finally, a "
            "system that sees her whole picture. And Cambodia has hundreds of "
            "thousands more like her."
        ),
    },
    {
        "num": 23, "title": "LIVE DEMONSTRATION", "timing": "75 sec",
        "script": (
            "[Switch to the browser — a live FastAPI app, not a mockup.]\n\n"
            "Let me show you this actually running. First, I'll score Sophea "
            "live, right here, with the fairness guardrail visible on screen. "
            "Then I'll run a higher-risk applicant through, so you can see the "
            "decision and the reward change. And finally, 'Watch it Learn' — a "
            "live animation of cumulative reward, watching the learning system "
            "pull ahead of the static rules in real time."
        ),
    },
    {
        "num": 24, "title": "IF LIVE DEMO FAILS — A SCORED APPLICANT", "timing": "skip if live demo worked",
        "script": "[Backup only.] If the live demo didn't cooperate — here's a "
                  "captured screenshot from the Underwriting Desk, a sample "
                  "applicant already scored, decision and fairness guardrail "
                  "both visible.",
    },
    {
        "num": 25, "title": "IF LIVE DEMO FAILS — WATCH IT LEARN", "timing": "skip if live demo worked",
        "script": "[Backup only.] And here's the cumulative-reward curve itself "
                  "— learning system against static rules — exactly as the live "
                  "animation would have rendered it.",
    },
    {
        "num": 26, "title": "THANK YOU / Q&A", "timing": "15 sec",
        "script": (
            "That's my thesis. Thank you for your attention — I'd welcome your "
            "questions. And if a question needs a specific number, I've got "
            "eight appendix slides standing by."
        ),
    },
    {
        "num": 28, "title": "APPENDIX A2: NUMBER RECONCILIATION", "timing": "if asked (Q&A)",
        "script": (
            "Let's untangle the three percentages you might have seen. Plus "
            "25.2 percent is the headline — LinUCB against Static XGB, "
            "pre-registered before I ran it. Plus 29.8 percent is LinTS, "
            "measured on a different harness. And plus 14.8 percent is the "
            "human-in-the-loop gain over the vanilla bandit, across twenty "
            "seeds. If you only look at seed 42 alone, that same HITL "
            "comparison reads plus 6.5 percent — but that's one seed, not "
            "twenty, and the number I actually quote and stand behind is the "
            "twenty-seed 14.8 percent."
        ),
    },
    {
        "num": 32, "title": "APPENDIX A6: WHY A BANDIT HAS NO TRAIN/TEST SPLIT", "timing": "if asked (Q&A)",
        "script": (
            "Good question, and it's a fair one. A supervised model splits its "
            "data, fits once, and freezes. A bandit doesn't work that way — it "
            "meets applicants one at a time, so every single round is both "
            "training and testing at once, regularised online by a ridge prior, "
            "which means there's no static fit sitting around to overfit. So "
            "instead, I measure generalisation as cumulative regret against the "
            "Oracle, averaged over twenty seeds. And the Static XGB baseline, by "
            "contrast, is fit offline and frozen — so the comparison between "
            "them is still fair."
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
