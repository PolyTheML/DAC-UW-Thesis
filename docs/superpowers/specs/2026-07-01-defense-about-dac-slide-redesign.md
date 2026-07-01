# Defense PPTX — "About DAC" slide redesign (logo + overview)

**Date:** 2026-07-01
**Deck:** `thesis/health_rl/build_defense_v3.py` (Slide 4, "ABOUT DECENT ACTUARIAL CONSULTANTS")
**Status:** design approved (user confirmed 2026-07-01, via brainstorming + visual companion)

## Goal

The existing "About DAC" slide (Slide 4) has 6 service cards in a 2×3 grid plus a
one-line credentials footer, but no company logo and no overview/identity blurb.
Add both, without disrupting the deck's slide count, section labels, or footer
numbering.

## Locked decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | Overview content | Both identity/scale AND thesis relevance, in 2 sentences (see draft copy below) |
| 2 | Layout | Two-column split — chosen over a top corner-logo banner and a hero-band+chip-row alternative (compared via visual companion mockups) |
| 3 | Credentials line | Dropped entirely — redundant with the overview blurb and with Slide 1's metadata grid (Organization/Advisor/Duration) |
| 4 | Logo asset | Reuse existing `thesis/DAC.jpg` (already used on Slide 1's title-slide logo row) |

## Layout

Left column (~34% of `CONTENT_W`) and right column (~62%), matching the existing
"Meet Sophea" (Slide 3) card+column visual pattern already used in this deck.

**Left column — "org profile card":**
- One light-bg card (`LIGHT_BG` fill + `NAVY` left accent, same visual language as
  `card()`/the Sophea profile card), spanning the full content height
  (`START_T` → `CONTENT_BOT`).
- DAC logo (`DAC.jpg`) centered near the top of the card, width-constrained with
  aspect ratio preserved (python-pptx auto-scales height from width).
- Overview blurb below the logo, plain paragraph text (not bulleted), ~12–13pt:

  > "Decent Actuarial Consultants (DAC) is a Taipei-headquartered actuarial
  > consultancy serving insurers across Taiwan, Vietnam, Cambodia, and the wider
  > Southeast Asian region. This thesis was completed during a 3-month internship
  > (Mar–Jun 2026) at DAC's Phnom Penh office, applying DAC's actuarial expertise
  > to Cambodia's underserved health-insurance underwriting problem."

**Right column — services list:**
- The same 6 services currently in `SERVICES` (unchanged text), each rendered as
  its own full-width one-line row via the existing `card()` helper (light bg +
  navy/blue left accent), stacked vertically with a small gap between rows —
  replacing the current 2×3 card grid.

**Removed:** the bottom italic credentials line (`HQ: Taipei ... Advisor: Mr. ON Radet`).

**Unchanged:** title block, footer ribbon, section label ("Introduction & Problem
Background"), slide number/ordering, all other slides.

## Implementation

- Single-file change: `thesis/health_rl/build_defense_v3.py`, Slide 4 block
  (currently lines ~211-239). No new helper functions needed — reuses `card()`,
  `textbox()`, `para()`, and the existing `LOGO_DAC` path constant (already
  defined at line 71, currently only used on Slide 1).
- Rebuild: rerun the script to regenerate
  `thesis/health_rl/Poly_defense_presentation_v3.pptx`.
- Verify: existing `tests/test_build_presentation.py` suite still passes (slide
  count and ordering are unchanged, so no test updates expected — confirm by
  running the suite, not by assumption).

## Out of scope

- No changes to any other slide.
- No changes to the DAC logo asset itself.
- No changes to the credentials data itself (still present on Slide 1's metadata grid).
