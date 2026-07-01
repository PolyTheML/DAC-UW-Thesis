# Defense PPTX — deck-wide font-size bump

**Date:** 2026-07-01
**Deck:** `thesis/health_rl/build_defense_v3.py` (all 44 slides) + `thesis/health_rl/defense_draw.py` (`card()` helper defaults)
**Status:** design approved (user confirmed 2026-07-01)

## Goal

Most body text in the deck (cards, tables, bullet rows) sits at 8-14pt, which
will be hard for the committee to read from the back of a defense room.
Increase it modestly — a proportionate bump, not a full redesign — without
touching already-large elements (titles, big stat numbers, section dividers)
and without introducing text overflow, given none of these textboxes have
PowerPoint autofit configured.

## Locked decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | Scope | Whole 44-slide deck, not just the About-DAC slide |
| 2 | Bump size | Modest tiered floor increase (~2-3pt), not a jump to presentation-standard ~18pt+ |
| 3 | Footer ribbon | Left unchanged at 9pt — peripheral chrome (page number, section name, org label), not committee-facing content |
| 4 | Titles / big numbers / section dividers (≥15pt) | Left unchanged — already prominent; bumping them risks disproportion |
| 5 | Mechanism | Scripted, rule-based transform (not ~100 manual edits) for auditability and consistency |

## Tiered size mapping

Applied to every explicit font-size literal found via two call-site patterns
in `thesis/health_rl/build_defense_v3.py`, plus the `card()` function's own
default parameter values in `thesis/health_rl/defense_draw.py`:

1. **Helper calls:** `para()`, `new_para()`, `add_run()` (the `size`
   parameter, always the 3rd positional argument per `defense_draw.py`'s
   signatures), and `card(..., header_size=N, body_size=N)` keyword
   arguments.
2. **Raw python-pptx run assignments:** `<run>.font.size = Pt(N)` —
   used directly (not via the helpers) in every table-rendering block in
   the deck (~30 sites: header rows, body cells, Appendix tables/ladders).
   A few of these use a ternary, e.g. `Pt(9 if col_i == 0 else 10)` — both
   branch constants get mapped independently, the condition is untouched.
   *(Found during plan-writing, 2026-07-01 — the original draft of this
   spec only described pattern 1; tables use pattern 2 exclusively and are
   exactly the dense, high-risk content called out below, so they were
   always intended to be in scope.)*

| Current size | New size |
|---|---|
| 8pt | 11pt |
| 9pt | 12pt |
| 10pt | 13pt |
| 11pt | 13pt |
| 12pt | 14pt |
| 13pt | 15pt |
| 14pt | 16pt |
| ≥15pt | unchanged |

**Explicitly excluded from the sweep** (must remain untouched):
- `defense_draw.py`'s `footer()` helper (all 9pt calls) and `section_divider()`'s
  footer block (also 9pt) — per locked decision 3.
- `defense_draw.py`'s `title_block()` (26pt) — already prominent.
- `section_divider()`'s numeral (48pt) and section-name (28pt) text — already ≥15pt, unchanged by the mapping anyway, but called out explicitly since it lives in the helper file, not the sweep target.
- Any literal ≥15pt anywhere in `build_defense_v3.py` (big stat numbers, DECLINE banner, etc.) — unchanged by the mapping's own rule.

**`card()` default parameters** (`defense_draw.py:131`): `header_size=14` → `16`,
`body_size=11` → `13`. This matters because 9 of the deck's 10 `card()` call
sites omit `body_size` and rely on the default — only bumping explicit
literals in `build_defense_v3.py` would miss 90% of card-based content.

## Overflow-risk verification

None of these textboxes have PowerPoint autofit configured (`textbox()` in
`defense_draw.py` only sets `word_wrap`), so oversized text will visually
overflow its box rather than shrink to fit. This environment has no
PowerPoint/LibreOffice installed, so the deck cannot be rendered to images
for direct visual inspection.

Mitigation:
1. **Heuristic fit checker** (one-off script, not committed): for every
   touched textbox call site, estimate wrapped line count from the box's
   width (EMU → pt) and the new font size using a conservative average
   character-width heuristic (~0.5× font size for the deck's sans-serif
   fonts), then compare estimated total text height (line count × font
   size × ~1.2 line-spacing factor) against the box's actual height (EMU →
   pt). Flag any site where estimated height exceeds box height.
2. **Manual arithmetic spot-check** on the deck's densest fixed-height,
   multi-row regions — the Appendix tables/ladders (`LADDER_A1`, `FAIR_A3`,
   `ELASTICITY_ROWS`, `ADVERS_ROWS`, `HYPER_A4`, `EXP_ROWS`, `ALG_ROWS`,
   `FEAT_CATS`) and the About-DAC service rows just built — the same kind
   of row-height arithmetic already used to verify the About-DAC slide.
3. **Disclosed limitation:** flagged sites (if any) get a best-effort fix
   (e.g., growing a box into existing slide whitespace) where straightforward;
   anything that can't be confidently resolved via arithmetic alone is called
   out to the user as needing a manual visual check in PowerPoint before the
   defense. This spec does not claim zero-overflow certainty — only that the
   sweep is proportionate and the highest-risk spots are checked.

## Commit hygiene

`build_defense_v3.py` has substantial unrelated pending work already
uncommitted in the working tree (from before this task). As with the
About-DAC slide task, this change must land as its own isolated commit —
extract just this task's hunks (or use a scoped diff/patch), not
`git add` the whole file.

## Out of scope

- No layout/positioning changes beyond what's needed to avoid a flagged
  overflow (no general redesign of any slide).
- No change to footer, title, or already-≥15pt text.
- No change to fonts/colors — size only.
- No new PowerPoint-rendering tooling installed in this environment.
