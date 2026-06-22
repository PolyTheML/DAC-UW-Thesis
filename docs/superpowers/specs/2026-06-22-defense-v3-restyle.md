# Spec: Defense v3 — Burgundy-Chrome Restyle (pure skin)

**Date:** 2026-06-22
**Branch:** `thesis/ch5-structural-pass`
**Status:** AWAITING SIGN-OFF (no code until approved)

---

## Goal

Restyle `Poly_defense_presentation_v3.pptx` (39 slides, content-verified) to **match the
chrome of `burgundy_defense_presentation.pptx` exactly**, changing **only the visual skin**
— palette, fonts, title slide, section dividers, card/footer styling. **No content changes.**

## Decisions locked (grill 2026-06-22)

1. **Match burgundy chrome exactly** — adopt burgundy's cobalt palette, logo'd classic title
   slide, and cobalt divider style wholesale.
2. **Pure skin only — content untouched.** All 39 slides keep their text, tables, stat
   blocks, SDG cards, canonical numbers, and the Sophea arc beat positions verbatim. Tables
   stay tables (NOT converted to chart images). Slide count stays 39.

## Premise correction (important)

The handoff (`handoff_defense_v3_restyle_2026-06-22.md`) describes burgundy as having a
roman-numeral chip, decimal titles ("1.1."), and no divider slides. **That describes the
old, rejected v2 burgundy.** The file on disk (`build_burgundy_presentation.py` docstring)
is **already the full-blue Yuth-reference design** WITH cobalt divider slides I–V, plain
ALL-CAPS underlined titles, and NO chip/decimals. Verified by rendering all 34 slides. The
real v3↔burgundy gap is only: **title slide, palette brightness, divider color, fonts.**

---

## Architecture (why this is surgical)

- v3 content slides call shared primitives in `defense_draw.py`
  (`title_block`, `footer`, `section_divider`, `card`) and reference palette **tokens** from
  `defense_tokens.py` directly — **66** `fill=NAVY/BLUE/AMBER/...` usages across
  `build_defense_v3.py`.
- Therefore: **changing token VALUES auto-propagates the palette to all 66 content usages**
  with zero edits to content code.
- Only the 4 chrome functions + the inline title slide need hand edits.

---

## Changes

### C1 — `defense_tokens.py`: palette values + fonts

Remap existing token **values** to burgundy's palette (keep token NAMES so content code is
untouched). Source values from `build_burgundy_presentation.py` lines 61–82.

| Token | v3 now | → burgundy value | Drives |
|---|---|---|---|
| `NAVY` | `#1F3A6E` | `#1B5697` (BLUE_TITLE) | titles, underline, card accent, stat blocks, table headers (all auto) |
| `BLUE` | `#2E74B5` | `#1F6FC4` (ACCENT_BLUE) | secondary accents |
| `LIGHT_BG` | `#EFF3F8` | `#F3F6FB` (PANEL) | card fill |
| `DIVIDER` | `#CBDCEF` | `#DDDDDD` (HAIRLINE) | thin separators |
| `AMBER_ACC` | `#F4A11D` | `#E6A62E` | ladder/PSI amber band |
| `RED_ACC` | `#C02020` | `#D93B3B` | decline/red band |
| `GREEN_ACC` | `#218238` | `#2E8B57` | proposed/green band |

Add new tokens:
- `BLUE_DEEP = #143D6B` (footer org panels)
- `BLUE_DIVIDER = #1F6FC4` (divider-slide background)
- `BLUE_TINT = #AFC4E4` (footer center panel)
- `HEAD_FONT = "Segoe UI"`, `BODY_FONT = "Calibri"`

`AMBER_BG`/`RED_BG`/`GREEN_BG` tints left as-is (already light, read fine on white).

### C2 — `defense_draw.py`: font support

- `add_run(...)`: add `font_name=BODY_FONT` param; set `run.font.name = font_name`.
- `para(...)` / `new_para(...)`: add `font_name=BODY_FONT` passthrough.
- v3 currently sets NO font (falls back to Calibri). Burgundy headings = Segoe UI.

### C3 — `title_block()`

- Title run + underline: color `NAVY` (now `#1B5697`), title `font_name=HEAD_FONT`.
- Geometry unchanged (centered ALL-CAPS + short underline already matches burgundy).

### C4 — `footer()`

- Left/right panels: fill `BLUE_DEEP` (was `NAVY`).
- Center panel: fill `BLUE_TINT` `#AFC4E4` (was `#BDCEE4` hardcoded).
- Center text color → `NAVY` (now cobalt). Right/left text stays white.
- `total` default → `39` (v3 already passes 39 explicitly everywhere; align default too).

### C5 — `section_divider()`

- Full-slide background: `BLUE_DIVIDER` `#1F6FC4` (was `NAVY` dark).
- Match burgundy numeral treatment: large white roman numeral **with trailing dot** (e.g.
  `I.`), white underline bar beneath, white section name below. `font_name=HEAD_FONT`.
- Footer org block on divider: `BLUE_DEEP`.

### C6 — `card()`

- `bg` default → `LIGHT_BG` (now `#F3F6FB`), `accent` default `NAVY` (now cobalt).
- Header `font_name=HEAD_FONT`, body `font_name=BODY_FONT`.

### C7 — Title slide (build_defense_v3.py lines 25–51) — REPLACE

Replace the navy-banner/no-logo title with a port of burgundy `slide_title()`
(`build_burgundy_presentation.py` 520–567):
- Logos top: `thesis/ITC.jpg` (L), `thesis/AMS.png`, `thesis/DAC.jpg` (R) — files confirmed present.
- `INSTITUTION` + `DEPARTMENT` centered top.
- Short `BLUE_TITLE` underline accent above + below the title.
- Full thesis title, ALL-CAPS, `HEAD_FONT`, centered.
- "Thesis Defense — Presented by" + `LUN CHANPOLY` in `BLUE_TITLE`.
- Metadata grid: `Supervisor : Dr. HAS Sothea` | `Organization : DAC (Decent Actuarial Consultants)`;
  `Duration : Mar 2026 – Jun 2026` | **`DAC Advisor : Mr. ON Radet`** ← preserved from v3 (burgundy lacks it).
- `July 2026` centered; footer ribbon `"1 / 39"`.

**Default to veto at sign-off:** ON Radet is folded into the metadata grid (4th cell). If you
prefer it omitted to match burgundy 1:1, say so.

---

## Out of scope (NOT changing)

- Any slide body content, tables, numbers, bullet text, speaker notes, Sophea arc.
- Slide count (stays 39). Divider count (stays 5: I–V).
- Data tables → chart images (explicitly rejected in grill).
- `build_burgundy_presentation.py` (reference only; untouched).

---

## Verification

1. `python thesis/health_rl/build_defense_v3.py` builds without error.
2. Re-export 39 PNGs via PowerPoint COM → `slide_thumbnails_v3/`.
3. Visual spot-check (title, a divider, a card slide, the Baseline Ladder) side-by-side vs
   burgundy renders. **User visual sign-off BEFORE committing the .pptx.**
4. Confirm canonical numbers unchanged on the ladder/HITL/EXP slides (content must be byte-identical
   text; only colors/fonts differ).

## Risk

Low. Token-value swap is mechanical; 4 small function edits; 1 title-slide replacement.
No content logic touched. Prior rejections were content/bar-guessing — this bar is now
pinned to a rendered reference deck.
