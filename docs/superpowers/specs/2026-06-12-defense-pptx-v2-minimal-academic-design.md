# Defense PPTX v2 — Minimal Academic Restyle

**Date**: 2026-06-12
**Status**: DESIGN APPROVED by user
**Decided via**: visual-companion session — user reviewed all 32 rendered slides of build 1,
flagged problems by click, picked style direction from three side-by-side mockups, chose
density mode via terminal question.
**Supersedes**: the *visual execution* of `2026-06-12-defense-pptx-sreynich-format-design.md`
(build 1). The **structure from that spec survives unchanged** — slide inventory, section
map, decimal titles, corner numbers, JSON-driven numbers discipline all stay.

---

## 1. Evidence — what the user rejected in build 1

Categories flagged (browser multi-select): **look & feel**, **text density**, **layout &
polish**, **figures**. NOT flagged: structure/flow, content emphasis → skeleton is approved.

Slides flagged: 8 (4.1 Pipeline), 10–18 (4.3 → 5.6, all Methodology detail + all Results),
20 (6.2 Ladder limitation) — i.e. every figure-heavy/content-heavy slide.

Concrete diagnosis (from rendered-slide review):
- Beveled, drop-shadowed pills/boxes + heavy burgundy fills + serif display titles = dated.
- Thesis-scale matplotlib PNGs pasted in: ~9 pt axis text, document captions
  ("Figure 4.1 —"), dead white margins; illegible at projection distance.
- Full sentences and triple-layer fine print (body + footnote row + admissibility box).
- ITC/AMS/DAC logo cluster floating bottom-right on every content slide.

## 2. Style decision

**B — Minimal Academic, plus the thin burgundy bottom bar** (user: "B but keep the bottom
bar"). Density mode: **talking points only** (user-confirmed, recommended option).

## 3. Visual system (applies to all 32 slides)

- **Background**: white everywhere. No cream/`LIGHT_GRAY` panels.
- **Content-slide chrome** (complete list — nothing else):
  1. Section tag: plain text, no chip — `V · RESULTS & DISCUSSION` style, ~10 pt, bold,
     BURGUNDY `#5D2A42`, letter-spaced uppercase, top-left.
  2. Title row: burgundy decimal (`5.1`) + charcoal title text, single line.
  3. Short burgundy underline accent (~0.5 in × 3 pt) under the title row.
  4. Bottom bar: full-width burgundy strip ~0.22 in with white page number, right-aligned
     (content slides `01`–`19`, appendix `A1`–`A8`; title, ToC, demonstration, thanks and
     appendix-divider slides keep the bar but carry no number — same convention as build 1).
- **Typography**: Calibri only (safe on any defense machine). No serif anywhere.
  Title ~28 pt bold; talking points 16–18 pt; stat numbers 30–40 pt bold; labels/footnotes
  10–11 pt gray (`#777777`) uppercase for labels, sentence case for footnotes.
- **Color discipline**: charcoal `#1A1A1A` body text on white. BURGUNDY `#5D2A42` reserved
  for: decimal numbers, section tag, underline accent, bottom bar, ONE highlighted stat per
  slide, hero line in charts. BURGUNDY_DARK `#471F33` only if a darker shade is needed.
  Semantic accents strictly for meaning: green `#2E8B57` pass, amber `#E6A62E` warning,
  red `#D93B3B` fail/inadmissible, blue `#3B6EA5` only if a fourth series is unavoidable.
- **No rounded corners, no shadows, no bevels, no gradients — anywhere.** Grouping via
  hairline rules (1 px `#DDDDDD`) and whitespace; if a panel is unavoidable (tables), flat
  `#F7F5F6` fill, square corners.
- **KPI stats**: flat big-number typography rows — number over small gray caps label,
  hairline separators between stats. No pills/boxes.
- **Logos**: title slide + thanks slide only. Removed from all content slides.

## 4. Density rules

- ≤ 4 talking points per slide, ≤ 8 words each; sentence case, no terminal periods.
- **Presenter notes**: every detail cut from a slide is rewritten into that slide's notes
  pane (`notes_slide.notes_text_frame`) as the rehearsal script — full numbers, caveats,
  and the sentence the speaker should say.
- **Claim-critical footnotes stay on-slide** (10–11 pt gray) — non-negotiable examiner
  armor:
  - admissible-scope line (§5.0.1) on convergence/benchmark slides,
  - criterion-6 FAILED-with-interpretation on the fairness slide,
  - LinUCB cold-start softened (p = 0.0840) next to the LinTS pass (p = 0.0039),
  - AlwaysRATED inadmissibility on the ladder slide.
- Tables (literature summary 3.1, reconciliation A1): ≤ 5 rows, short cells, 12–14 pt.

## 5. Figures

- New slide-figure style (matplotlib rcParams in a regeneration script): axis labels ≥ 18 pt,
  ticks ≥ 14 pt, legend ≥ 16 pt, line width 3.5–4, white background, no chart title (the
  slide title does that job), no document captions, 16:9-friendly aspect, tight crop.
- Palette: burgundy hero series, warm-gray comparison series; semantic colors only for
  status meaning (PSI bands etc.).
- Regenerate slide variants for every chart on flagged slides: convergence (5.1), benchmark
  (5.2), cold-start (5.3), HITL (5.4), fairness/PSI (5.5), drift (5.6), ladder (6.2), plus
  any methodology charts in 4.3–4.5. Source the same frozen result data the existing
  thesis figures use.
- Output to `thesis/health_rl/figures/slides/` — **thesis-report figures are not touched**.
- **Architecture diagram (4.1): rebuilt as native PowerPoint shapes** in the deck palette
  inside the builder. The blue/green/orange matplotlib PNG is dropped.

## 6. Slide-type templates

- **Title**: white, flat; charcoal + burgundy type, Calibri; ITC/AMS/DAC logos kept;
  supervisor block and "July 2026" placeholder unchanged.
- **ToC**: two-column roman-numeral list, burgundy numerals; 🎓 emoji removed.
- **Demonstration / Thanks / Appendix divider**: same minimal language; divider = large
  burgundy "APPENDIX" wordmark on white.
- **Appendix content slides**: standard chrome with `A1`–`A8` corner numbers; re-use the
  section tag of the material they extend (unchanged from build 1).

## 7. Engineering

- Evolve `thesis/health_rl/build_burgundy_presentation.py` **in place** (same filename,
  same output path `thesis/health_rl/burgundy_defense_presentation.pptx`). Build 1
  recoverable via git.
- Helper rewrite: `_add_section_tag` → plain text (no chip); keep `_add_bottom_bar`;
  remove rounded/shadowed box styling; add `_add_stat_row`, `_add_talking_points`,
  `_add_notes` helpers.
- Numbers stay loaded from `demo/static/thesis_results.json` at build time, KeyError on
  missing key (drift discipline unchanged).
- **Tests** (`tests/test_build_presentation.py`): keep slide-count / section-tag /
  decimal-title / JSON-number assertions; add — presenter notes present on all content
  slides, talking-point count ≤ 4 enforced, claim-critical footnote text present on the
  four armor slides, no shadowed shapes (style regression guard if cheaply assertable).

## 8. Out of scope

- Structural changes (slide inventory, section order) — approved as-is.
- Claim/content changes — wording already aligned with r13 thesis claims.
- Real A6–A8 demo screenshots (placeholders remain; separate task).
- Defense date (placeholder "July 2026" until scheduled).

## 9. Open items carried forward

- [ ] Defense date placeholder — replace when scheduled.
- [ ] A6–A8: capture real demo screenshots before defense day.
- [ ] Rehearse Q1/Q2 against slide 6.2 and appendix A1 (now easier: presenter notes
      double as the rehearsal script).
