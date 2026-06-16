# Defense PPTX — SDG-aligned Introduction + Dataset Overview slide

**Date:** 2026-06-16
**Deck:** `thesis/health_rl/build_burgundy_presentation.py` (v3 blue, currently 33 slides)
**Status:** design approved (user confirmed all four decisions on 2026-06-16)

## Goal

Two content changes to the defense deck:

1. Reframe the **Introduction** slide so its right panel speaks to how the project
   advances **Cambodia's UN Sustainable Development Goals**, instead of the current
   blank captioned panel.
2. Add a **dataset-overview** slide that actually shows what the 2,000-applicant
   synthetic dataset looks like (distribution montage + a short description).

## Locked decisions (from brainstorming, 2026-06-16)

| # | Decision | Choice |
|---|----------|--------|
| 1 | SDG framing | SDG 3 (Good Health & Well-being) + SDG 1 (No Poverty) + SDG 10 (Reduced Inequalities) |
| 2 | Intro layout | Keep `<10%` stat + problem bullets on the left; **replace the right panel** with an SDG-alignment block |
| 3 | Dataset overview | **New slide**, a 2×2 distribution montage (age · region · occupation · BMI) + description |
| 4 | Placement | **Main flow**, inserted right after `slide_zoom_dataset` (current idx 11 → new slide becomes idx 12) |

## Part 1 — Introduction reframe (`slide_introduction`, idx 4)

- **Left column unchanged:** the `< 10%` penetration figure, its letterspaced caption, and
  the four problem bullets. The opening hook stays intact.
- **Right panel** (currently `_add_placeholder_image(..., show_label=False)` at
  `Inches(7.1), CONTENT_TOP, Inches(5.7), Inches(4.6)`) → **replaced** with an
  "ALIGNMENT WITH CAMBODIA'S SDGs" block:
  - A panel container (filled box, `PANEL` fill, `BLUE_TINT` outline) + a letterspaced header.
  - Three stacked rows, each = a small "SDG n" chip (filled box, white bold text on `BLUE_DEEP`)
    plus name + one-line tie to the method:
    - **SDG 3 · Good Health & Well-being** — widen voluntary health-insurance access beyond the ~16% NSSF formal sector.
    - **SDG 1 · No Poverty** — shield households from catastrophic out-of-pocket health costs.
    - **SDG 10 · Reduced Inequalities** — PSI guardrail keeps underwriting demographically fair.
  - Built only from `_add_filled_box` + `_add_text_box` → **no images** (no picture-count or
    index impact) and **no slide added** here.
- **Speaker notes** rewritten to narrate the SDG alignment. Framed as *motivation / contribution*
  ("this work contributes to…"), NOT as a cited thesis section — the thesis body names no SDGs,
  so the wording must not imply otherwise.

## Part 2 — Dataset overview

### 2a. Montage figure
- New asset `thesis/health_rl/figures/slides/slide_dataset_montage.png`.
- A single composited **2×2 matplotlib montage** generated from `data/cambodia/cambodia_dataset.parquet`:
  age histogram · region bar · occupation bar · BMI histogram. Styled to the blue slide palette
  (`figures/_slide_style.py` `SLIDE_PALETTE`), consistent with the existing `slide_*.png` figures.
- **One** image → embedded as **1 picture** (stays under the `test_logos_only_on_title_and_thanks`
  ≤3-picture guard; four separate images would trip it). Output > 30 KB so it passes the
  figure-existence pattern.
- Generator lives in the slide-figure pipeline (extend the existing slide-figure generator, or a
  small standalone `generate_dataset_montage.py`); run once and commit the PNG (slide figures are
  git-tracked).

### 2b. New slide `slide_dataset_overview`
- `_content_slide(prs, "The Dataset at a Glance", _pg(10))`.
- **Left:** short description + stat callouts — 2,000 synthetic applicants · 5 features ·
  anchored on CDHS/STEPS/ILO/WHO · fully synthetic (no PII).
- **Right / lower:** the montage via `_add_picture_fit`.
- `_add_notes(...)` (>40 chars — it sits in `NOTED_IDX`).
- Inserted in `main()` immediately after `slide_zoom_dataset(prs)`.

## Cross-cutting: index + page-number churn (main-flow cost)

Inserting one main-flow slide at idx 12 shifts every later slide +1. Required updates:

**Builder (`build_burgundy_presentation.py`):**
- `_pg` denominator `"{n} / 28"` → `"{n} / 29"`.
- New slide uses `_pg(10)`; **increment every existing `_pg(n)` with n ≥ 10 by +1**
  (reward 10→11, zoom_bandit 11→12, build-ups 12→13…16→17, zoom_fairness 17→18,
  divider IV 18→19, results 19→20…21→22, references 22→23, divider V 24→25).
  `_pg(9)` (divider III + dataset) is unchanged.
- `assert len(prs.slides) == 33` → `== 34`.
- Bump any "32/33 slides" docstrings to 34 (cosmetic).

**Tests (`tests/test_build_presentation.py`):** bump every index ≥ 12 by +1, specifically:
- `test_generates_33_slides`: `== 33` → `== 34` (rename optional).
- `test_appendix_slides_have_page_numbers`: `28 + i` → `29 + i`; docstring "28-32" → "29-33".
- `test_headline_numbers_match_json`: slide 20→21, 21→22, 28→29 (and comments).
- `NOTED_IDX`: every value ≥12 +1, **and add the new slide's idx 12**.
  New list: `[3,4,5,6,8,10,11,12,13,14,15,16,17,18,20,21,22,23,24,26,27,29,30,31,32,33]`.
- `test_claim_armor_strings_present`: (16→17),(19→20),(20→21),(21→22),(22→23),(25→26),(28→29);
  the `(6, …)` objective checks are unchanged.
- `test_logos_only_on_title_and_thanks`: thanks 27→28; exclusion list `[0,27]`→`[0,28]`.
- `test_references_slide_present`: idx 26 → 27.
- `test_divider_slides_present`: `(18,"IV")`→`(19,"IV")`, `(24,"V")`→`(25,"V")`; I/II/III unchanged.
- `test_methodology_overview_and_three_zooms`: 10,11 unchanged; 13→14, 17→18.
- `test_demo_slide_has_visual`: idx 23 → 24.

> All other tests (helper unit tests, palette, footer, no-burgundy, talking-points rule) are
> index-independent and need no change.

## Verification

1. (figure) run the montage generator → `slide_dataset_montage.png` exists, > 30 KB, blue palette.
2. `python thesis/health_rl/build_burgundy_presentation.py` → "Saved 34 slides".
3. `python -m pytest tests/test_build_presentation.py -q` → all pass.
4. Programmatic content check: SDG 3/1/10 strings on intro (idx 4); "Dataset at a Glance" +
   1 picture on idx 12; footer denominators read "/ 29"; armor needles intact at new indices.
5. This change **stacks on top of** the in-flight 4-edits work (Edit 1/2/2b/3/4) — the pending
   HITL screenshot re-capture + final build + PNG eyeball still gate the single commit.

## Out of scope
- No change to the existing `slide_zoom_dataset` (idx 11) — it keeps its pipeline/role framing.
- No official UN SDG colour swatches (stay on the defense-safe blue template); SDG numbers carry the cue.
- No thesis-body edits (the GREEN/locked LaTeX is untouched).
