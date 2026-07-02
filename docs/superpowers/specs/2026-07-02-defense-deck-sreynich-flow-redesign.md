# Defense Deck Redesign — Nang Sreynich Flow (spec)

**Date**: 2026-07-02 · **Status**: APPROVED via /grill-me interview, ready to build
**Builds on**: 25-slide working-tree deck (uncommitted) · **Defense**: 2026-07-08 (6 days)
**Deliverable owner**: next session (user chose "spec only, build next session")

---

## 1. Goal

Restructure `Poly_defense_presentation_v3.pptx` (built by `thesis/health_rl/build_defense_v3.py`)
to follow the flow of the reference deck **`thesis/sample/Doc2_Slide - Nang Sreynich.pptx`**
(repo copy; same file as the Telegram download the user supplied; 47 slides, ITC thesis
defense, 09-Jul-2025). User requirements, verbatim intent:

1. **Follow the reference flow** (7 numbered sections, demo last, appendices after thanks).
2. **Cambodia map on the "< 2% penetration" slide**, like the reference's 25.6% map slide.
3. **Low jargon** — "easy for me to present as I'm not quite the expert in my topic".
   User has said "I don't know" to α questions; slides must carry plain language, armor
   stays in appendix.
4. **Proportionate layout, no text overlap** — automated layout lint + PNG eyeball required.

## 2. Decisions locked in the /grill-me interview (2026-07-02)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Baseline | **25-slide working tree** (NOT the committed 44-slide deck; the 47-slide Ballister state was never committed and is gone) |
| 2 | Flow | **Full reference order**, Demonstration section LAST (after Conclusion), then Thanks, then Appendices |
| 3 | Nav chrome | **Persistent top section tabs** (current section highlighted) + dedicated ToC slide + page number bottom-right |
| 4 | Palette | **Keep current tokens** (`defense_tokens.py` — cobalt values under NAVY/BLUE names, user-approved 2026-06-22). Do NOT restyle to reference navy. |
| 5 | Map slide | **Map center + stat callout chips around it** (user picked this over reference-faithful two-column). SDG chips MOVE to Objectives slide. |
| 6 | Jargon | **Plain-first**: formulas exiled to appendix; any technical term that stays gets a one-line "in plain words" translation beneath (reference style); stats phrased "20 independent repeats — consistent every time" with exact values in small print |
| 7 | Appendix | **Full armor A1–A6 restored** from `git show 1a75d25:thesis/health_rl/build_defense_v3.py` + 2 new plain-language walkthrough slides (A7 UCB, A8 PSI). Fix A5 overflow. |
| 8 | New beats | Timeline Gantt ✓ · Side-by-side validation exhibit ✓ · Lit review as one plain table ✓ |
| 9 | Scripts | **Both** `Poly_defense_script_v2.docx` and 20-min script regenerated after rebuild; stale +6.5 % HITL → +14.8 % fixed everywhere |

Additional locked details:
- Sophea remains the narrative thread (equivalent of the reference's tuition-fee worked example).
- Slide size stays 16:9 (`SW=12191695`, `SH=6858000` EMU) — do not adopt the reference's 11×8.5 in canvas.
- Section labels (tabs + ToC), 7 sections: `i. Introduction · ii. Literature Review · iii. System Design · iv. Implementation · v. Results & Discussion · vi. Conclusion & Future Work · vii. Demonstration`.

## 3. Reference-deck patterns being adopted (from PPTX analysis)

- **Top nav bar** on every content slide: section tabs across the full width, active section
  visually distinct; small section label text; page number bottom-right (plain text, 2 digits).
- **Big-stat-on-map** background slide (reference slide 3: Cambodia map image-filled freeform,
  "25.6%" overlaid, finding line, source footnote).
- **Plain-language interpretation under every result** (reference slides 23–24: "It means the
  chatbot often gives part of the right answer, but sometimes it's not complete").
- **One-table literature review** (reference slide 8: Topic | Authors | Methodology, 4 rows).
- **Concrete worked example threaded through** (their tuition question ↔ our Sophea).
- **Side-by-side validation** (reference slides 25/46/47: ChatGPT vs DeepSeek vs their chatbot
  vs the true answer ↔ our Static XGB vs LinUCB vs Oracle on Sophea).
- **Demonstration as final section** (reference: video slide 31; ours: live demo + fallbacks).

## 4. Slide map (34 physical slides)

Page numbers = physical position; footer page number printed from slide 3 onward.

| Phys | Sect | Slide | Content notes |
|------|------|-------|---------------|
| 1 | — | Title | Keep current slide 1 as-is (logos, 8 July 2026, ON Radet cell) |
| 2 | — | Table of Contents | i–vii list, reference slide-2 style; recover/adapt TOC code from `1a75d25` slide 2 (fix its "six appendix" count if reused) |
| 3 | i | **Cambodia map + < 2 %** | NEW ASSET `thesis/health_rl/figures/cambodia_map_silhouette.png` (extracted from reference; recolor to NAVY #1B5697, white→transparent — PIL snippet §6). Map centered ~4.5 in wide; callout chips with connector lines: "< 2 % have health insurance (2023 est.)", "NSSF covers formal workers only (~16 %)", "Underwriting today: manual, rule-based". Kicker bottom: "Sophea represents the 98 % the current system was not built for." Source footnote small print: ILO 2023 · CDHS 2021-22. |
| 4 | i | Meet Sophea | Current slide 2, unchanged content; add "declined 2023" beat clearly (verdict_2023 DECLINE from `SOPHEA` dict) |
| 5 | i | Why static rules fail | Current slide 5 (Problem Statement) rewritten plain: "A fixed rule can't see Sophea's full picture — and it never learns from its mistakes." Three chips: Fixed cutoffs · Never updates · Nobody checks fairness |
| 6 | i | Goal & Objectives | Current slide 6 (RQ&O) in plain words; RQ1–3 one line each + **SDG strip relocated here** (SDG 3 / 1 / 10 compact chips, from current slide 4 right panel) |
| 7 | i | About DAC | Current slide 3, unchanged |
| 8 | i | Project Timeline | NEW: `figures/fig_project_timeline_3month.png` (Mar–Jun 2026 Gantt) full-width; one caption line |
| 9 | ii | Literature in one table | Compress current slide 7 to reference format: Topic \| Authors \| One-line takeaway (plain), 4–5 rows max: emerging-market health insurance (CDHS/ILO/ADB) · contextual bandits (Li et al. 2010 LinUCB; Agrawal & Goyal 2013 LinTS) · fairness/PSI monitoring · HITL underwriting. Gap line at bottom: "No prior work applies online-learning underwriting to Cambodia." |
| 10 | iii | System architecture | Current slide 8 diagram, plain caption: "The system decides, sees what happens, and gets a little smarter each round." |
| 11 | iii | How the bandit decides | MERGE current slides 11+12: Sophea's context (a few key dims, not 34-dim vector talk) → 4 arm scores as horizontal bars (0.31/0.52/0.10/0.28 from `SOPHEA`) → "Highest score wins: STANDARD. In plain words: it estimates how each option would pay off for someone like her, then adds a curiosity bonus for options it hasn't tried often." NO UCB formula (→ A7). |
| 12 | iii | What the system earns | Current slide 10 (Reward Simulator) plain rewrite: "Reward = premium collected − claims paid. Issue policies to people who stay healthy → earn; issue to people who claim a lot → lose; decline everyone → earn nothing." Adverse-selection/elasticity internals → small print or A4/A5. Keep "(Table 8)" pointer in small print for thesis cross-ref. |
| 13 | iii | Fairness guardrail | Current slide 13 plain rewrite: traffic light GREEN < 0.10 / AMBER 0.10–0.25 / RED > 0.25; "PSI asks one question: are the people we approve today drifting away from the people we trained on?" Formula → A4/A8. Include HITL one-liner (uncertain cases go to a human). |
| 14 | iv | Dataset | Current slide 9: 2,000 synthetic applicants, 34 features → say "34 facts about each applicant"; anchored to real Cambodia surveys (CDHS 2021-22, STEPS, ILO, WHO) — name them in small print; "synthetic because no insurer would share records — but shaped to match published Cambodia statistics" |
| 15 | iv | How we tested it | Current slide 14 plain rewrite: "5,000 applicants, one at a time · 20 independent repeats with different random draws — same winner every time · compared against the incumbent static-rules approach". Small print: bootstrap 95 % CI, paired Wilcoxon, Bonferroni, Cohen's d. Online-learning/no-split note stays (one plain line + "details: Appendix A6"). |
| 16 | v | Headline result | +25.2 %: LinUCB $90,540 vs Static XGB $72,292, 20 seeds. Plain line under number: "For every $100 the old rules earned, the learning system earned $125 — and the gap held across all 20 repeats." Small print: p < 0.001, d = 2.98. Use `figures/slides/slide_reward_curves.png` if a figure is wanted. |
| 17 | v | Baseline ladder | Current slide 15 (`slide_ladder.png` / fig_exp_014): plain caption "Every realistic alternative we tried lands below the bandits." Keep AlwaysRATED-inadmissible footnote (plain: "the only thing that beat it approves nobody cheaply and everybody expensively — no regulator would allow it"). |
| 18 | v | Side-by-side validation (NEW) | Reference slides 46/47 pattern, 3 panels: **Static rules** → Sophea: DECLINE · **LinUCB bandit** → Sophea: STANDARD · **Oracle (knows true risk)** → STANDARD. One line: "The bandit reaches the answer the all-knowing benchmark picks — the static rule never can." |
| 19 | v | Fairness + HITL results | Current slide 17: PSI GREEN both dims (region max ≈0.023, occupation ≈0.062 — verify vs `thesis_results.json`); criterion-6 honesty line kept ("1 of 6 pre-registered checks failed narrowly; we report it and explain why" — plain); HITL: "+14.8 % more reward when 1.5 % of cases go to a human (20 seeds)". |
| 20 | vi | Findings & limitations | Current slide 19: 4 findings, each with plain-words line; limitations panel kept two-sided (synthetic data, linear-reward assumption, single-country calibration) |
| 21 | vi | Future work | Current slide 20 unchanged content, plain labels |
| 22 | vi | Takeaway | Current slide 21 close: "2023: DECLINE. 2026: STANDARD." + "Cambodia has hundreds of thousands of applicants like her." (Thank-you line REMOVED — moves to slide 26) |
| 23 | vii | Demonstration intro | Current slide 18 (Live Demo): what the committee will see (Sophea scored live, learning animation, PSI guardrail). Demo runs from `demo/desk/` app. |
| 24 | vii | Fallback: scored applicant | Current fallback slide (desk_underwriting.png) — used only if live demo fails |
| 25 | vii | Fallback: learning animation | Current fallback slide (desk_learning.png) |
| 26 | — | Thanks | "Thank you for your attention — questions welcome." Reference slide-32 tone, current chrome |
| 27–32 | App | A1–A6 restored | Recover from `git show 1a75d25:thesis/health_rl/build_defense_v3.py` (search `Appendix A`). **A5 overflow MUST be fixed**: its tables extend below SH 6,858,000 EMU — split into two stacked half-width tables or cut rows to the α-sweep essentials (EXP-012 10-seed, best $91,378; keep the $91,378-vs-$90,540 10-seed/20-seed nuance line from memory). A2 keeps +25.2 %/+29.8 %/+6.5 % reconciliation but must present +14.8 % (20-seed) as the HITL headline and +6.5 % as seed-42 illustrative. |
| 33 | App | A7: UCB in plain words (NEW) | For PHOK Ponna's α question: score = "expected payoff + α × how-unsure-we-are". Walk Sophea's STANDARD arm: estimate 0.52 = payoff guess + curiosity bonus; α controls curiosity; "we tested α values — results barely move (Appendix A5)". One small formula allowed HERE: UCB = x̄ + α·√(xᵀA⁻¹x), each term labeled in plain words. |
| 34 | App | A8: PSI walkthrough (NEW) | For OL Say: PSI = Σ (Aᵢ−Eᵢ)·ln(Aᵢ/Eᵢ) with each symbol labeled ("share approved now" vs "share in training data"); worked mini-example with 2 buckets; thresholds GREEN/AMBER/RED; real numbers from EXP-006. |

Timing estimate: 24 story slides ≈ 18–19 min (3 added beats are fast; two bandit slides merged).

## 5. Top-nav tab component (new, in `defense_draw.py` or builder)

- Bar of 7 tabs, full slide width, top of every content slide (slides 3–25; NOT title/ToC/Thanks/appendix — appendix may keep simple title chrome).
- Geometry: bar height ≈ 0.42 in; each tab ≈ SW/7 wide; y = 0. Title block moves DOWN: set
  title top ≈ 0.55 in (current `TITLE_T` 310896 EMU will collide — adjust or add per-slide offset).
- Active tab: `NAVY` fill, white bold 10–11 pt text. Inactive: `LIGHT_BG` fill, `GRAY` 10 pt.
  Hairline `DIVIDER` under the bar.
- Tab labels are the roman-numeral section names (short forms fit: "i. Introduction",
  "ii. Literature", "iii. System Design", "iv. Implementation", "v. Results", "vi. Conclusion",
  "vii. Demo").
- Page number: plain text bottom-right (reference style, e.g. "03"), replacing or coexisting
  with the existing `footer()` — if keeping `footer()`, print the PHYSICAL page number, and
  drop the old conceptual-number scheme (the old zoom-in shared-number complexity is gone
  with the zoom-ins).

## 6. Map asset

- File: `thesis/health_rl/figures/cambodia_map_silhouette.png` (86,843 bytes, ~1489×1122,
  dark-navy fill on white, extracted 2026-07-02 from reference slide 3's image-filled freeform).
- Recolor before embedding (white → transparent, navy → NAVY #1B5697):

```python
from PIL import Image
img = Image.open("thesis/health_rl/figures/cambodia_map_silhouette.png").convert("RGBA")
px = img.load()
for y in range(img.height):
    for x in range(img.width):
        r, g, b, a = px[x, y]
        if r > 230 and g > 230 and b > 230:
            px[x, y] = (255, 255, 255, 0)          # white bg -> transparent
        else:
            px[x, y] = (0x1B, 0x56, 0x97, a)       # any fill -> NAVY
img.save("thesis/health_rl/figures/cambodia_map_navy.png")
```

- Embed `cambodia_map_navy.png`; chips overlap the map edges are ALLOWED (whitelist in lint).

## 7. Execution order & gotchas (do not rediscover)

1. Edit `build_defense_v3.py` → run it → THEN run script generators.
   **`build_defense_v3.py` creates a fresh `Presentation()` and silently wipes injected
   speaker notes** — script-gen must always run after the builder, never before.
2. `generate_defense_script_v2.py` and `generate_defense_script_20min.py` are keyed to the OLD
   slide order — their per-slide entries must be rewritten to the §4 map (thumbnails, timing,
   talk-track). Fix stale **+6.5 % HITL → +14.8 % (20-seed, p<0.001, d=2.65)** in v2 entries
   and any pptx `notes_slide` text (the 2 new 2026-07-01 docs already carry the correct number).
3. A1–A6 source: `git show 1a75d25:thesis/health_rl/build_defense_v3.py` (HEAD). The Ballister
   47-slide state was never committed — do not go looking for it.
4. Numbers canon: `demo/static/thesis_results.json` (re-canonicalized vs ch5-Results.tex) and
   ch5 Results chapter. Do not invent; copy.
5. Committee (2026-06-30 roster): LIN Mongkolsery (general) · OL Say (PSI/features) ·
   PHOK Ponna (α/hyperparameters/methodology) · HAS Sothea (supervisor). Deck must survive
   their known probing patterns via appendix, not body jargon.
6. Defense-safe fonts only: Segoe UI (headings) / Calibri (body) — already in tokens.
7. Do NOT touch `defense_tokens.py` palette values.

## 8. Layout QA (user requirement: "everything proportionate, text not overlap")

Build a lint script (suggest `thesis/health_rl/lint_deck_layout.py`) that opens the built pptx
and reports, per slide:

1. **Off-canvas**: any shape with `left < 0`, `top < 0`, `left+width > SW`, or `top+height > SH`
   (tolerance 10,000 EMU). This is exactly the A5 bug class.
2. **Text-box pair overlap**: bounding-box intersection between two TEXT-bearing shapes where
   intersection area > 15 % of the smaller box — excluding whitelisted pairs (background
   rects, the map+chips composite, stat text deliberately on filled rects: whitelist by
   shape-name prefix, e.g. name chips `chip_*`, backgrounds `bg_*`).
3. **Probable text overflow**: estimate rendered height (chars/line from width & font size ×
   line count × 1.2 line height) vs frame height; flag > 105 %.
4. Exit non-zero on any finding; print slide number + shape names.

Acceptance: lint clean, then PNG-export all 34 slides (LibreOffice headless or PowerPoint COM,
as done 2026-07-01) and eyeball at minimum: 1, 2, 3 (map), 9 (table), 11, 16, 18, 27–34.

## 9. Verification checklist (before commit)

- [ ] `python thesis/health_rl/build_defense_v3.py` → 34 slides exactly
- [ ] Layout lint clean (§8)
- [ ] PNG eyeball of the 12 key slides listed above
- [ ] Every body slide: zero formulas, every kept technical term has a plain-words line
- [ ] Numbers audit vs `thesis_results.json`: +25.2 %, $90,540/$72,292, +14.8 % HITL, PSI
      GREEN values, $91,378 A5 nuance, AlwaysRATED 122,287
- [ ] `generate_defense_script_v2.py` then 20-min generator rerun; grep both docx outputs:
      zero occurrences of "+6.5" outside the A2 reconciliation context
- [ ] Speaker notes present on all 24 story slides (spot-check 3)
- [ ] Commit builder + pptx + scripts + lint together (branch `thesis/ch5-structural-pass`,
      still NOT pushed; ~50 ahead of origin/main)

## 10. Out of scope

- No thesis (LaTeX) changes. No demo-app changes. No push.
- No restyle of palette/fonts. No 4:3 canvas.
- Rehearsal schedule (2026-07-04 first timed run) is downstream of this build.
