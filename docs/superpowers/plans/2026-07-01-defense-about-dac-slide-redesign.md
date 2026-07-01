# About-DAC Slide Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign Slide 4 ("ABOUT DECENT ACTUARIAL CONSULTANTS") in the defense deck to add the DAC logo and a short company-overview blurb, in a two-column layout that reuses the existing "Meet Sophea" (Slide 3) profile-card visual pattern.

**Architecture:** Single-file edit inside `thesis/health_rl/build_defense_v3.py`. The current Slide 4 block (2×3 service-card grid + a bottom credentials line) is replaced with a two-column layout: a left "org profile" panel (logo + overview paragraph) and a right column of 6 compact single-line service rows. No new drawing helpers are needed — the change reuses `rect()`, `textbox()`, `para()`, and `card()` from `defense_draw.py`, and the `LOGO_DAC` path constant already defined at the top of the file.

**Tech Stack:** Python, `python-pptx`. No test framework covers this file today (the only defense-deck pytest suite, `tests/test_build_presentation.py`, targets a *different* script — `build_burgundy_presentation.py` — and is unaffected by this change). Verification here is a one-off `python-pptx` introspection script, run before and after the edit (red → green), not a permanent pytest addition.

## Global Constraints

- Reuse existing drawing helpers only (`rect`, `textbox`, `para`, `card` from `thesis/health_rl/defense_draw.py`) — no new drawing primitives.
- Colors/fonts must come from `thesis/health_rl/defense_tokens.py` constants only (`NAVY`, `LIGHT_BG`, `DARK_TXT`, etc.) — no new hex literals.
- Reuse the existing `thesis/DAC.jpg` asset unmodified — do not replace or edit the logo file.
- Slide count, slide order, footer section label ("Introduction & Problem Background"), and footer numbering ("2" / total 44) must remain unchanged.
- The 6 service descriptions (`SERVICES` list text) must remain byte-identical — only their visual arrangement changes (2×3 grid → single column of rows).
- The bottom credentials line (`HQ: Taipei ... Advisor: Mr. ON Radet`) is removed entirely, per the approved spec (`docs/superpowers/specs/2026-07-01-defense-about-dac-slide-redesign.md`).

---

### Task 1: Redesign Slide 4 — logo + overview panel, compact services column

**Files:**
- Modify: `thesis/health_rl/build_defense_v3.py:211-239` (the `# ── Slide 4: About DAC` block)
- Verify (one-off, not committed): `C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\verify_about_dac_slide.py`

**Interfaces:**
- Consumes: `LOGO_DAC` (path constant, already defined at `build_defense_v3.py:71`), `MARGIN_L`, `CONTENT_W`, `CONTENT_BOT`, `LIGHT_BG`, `NAVY`, `DARK_TXT` (from `defense_tokens.py`, already imported via `from defense_tokens import *`), `rect()`, `textbox()`, `para()`, `card()`, `title_block()`, `footer()` (from `defense_draw.py`, already imported at the top of the file).
- Produces: no new names consumed by later code — this is a self-contained slide block. `SERVICES` remains a locally-scoped list (already the case today).

- [ ] **Step 1: Write the one-off verification script**

Create `C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\verify_about_dac_slide.py`:

```python
"""One-off check for the About-DAC slide redesign. Not part of the pytest suite."""
import sys
from pathlib import Path
from pptx import Presentation

ROOT = Path(r"C:\dac-uw-thesis")
PPTX = ROOT / "thesis" / "health_rl" / "Poly_defense_presentation_v3.pptx"

prs = Presentation(str(PPTX))
slide = prs.slides[3]  # Slide 4: About DAC (0-indexed)

n_pics = sum(1 for sh in slide.shapes if sh.shape_type == 13)
text = " ".join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)

checks = [
    (n_pics == 1, f"expected 1 picture (the DAC logo) on slide 4, got {n_pics}"),
    ("Taipei-headquartered" in text, "overview blurb missing"),
    ("Phnom Penh" in text, "thesis-relevance sentence missing"),
    ("Appointed Actuary Services" in text, "service 1 missing"),
    ("IFRS 17 Implementation" in text, "service 2 missing"),
    ("Product Development" in text, "service 3 missing"),
    ("Asset" in text and "ERM" in text, "service 4 (ALM/ERM) missing"),
    ("Mergers & Acquisitions" in text, "service 5 missing"),
    ("Education & Cooperation" in text, "service 6 missing"),
    ("ON Radet" not in text, "stale credentials line (advisor) should be removed from this slide"),
]

failed = [msg for ok, msg in checks if not ok]
if failed:
    print("FAIL:")
    for msg in failed:
        print(f"  - {msg}")
    sys.exit(1)
print(f"PASS: slide 4 has {n_pics} picture, overview + all 6 services present, "
      f"stale credentials line removed.")
```

- [ ] **Step 2: Run the verification script against the current (unmodified) deck and confirm it fails**

Run (from repo root `C:\dac-uw-thesis`):
```bash
python thesis/health_rl/build_defense_v3.py
python "C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\verify_about_dac_slide.py"
```
Expected: exits 1, `FAIL:` printed with at least `expected 1 picture (the DAC logo) on slide 4, got 0` and `overview blurb missing`.

- [ ] **Step 3: Replace the Slide 4 block in `build_defense_v3.py`**

Replace the current block (`build_defense_v3.py:211-239`, from `# ── Slide 4: About DAC` through the `footer(...)` call that ends it) with:

```python
# ── Slide 4: About DAC ────────────────────────────────────────────────
s = new_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
title_block(s, "ABOUT DECENT ACTUARIAL CONSULTANTS")

SERVICES = [
    "Appointed Actuary Services — Life & General Insurance, Southeast Asia",
    "IFRS 17 Implementation",
    "Product Development — Life & General Insurance",
    "Asset–Liability Management & Enterprise Risk Management (ALM/ERM)",
    "Mergers & Acquisitions Advisory",
    "Education & Cooperation — University partnerships, government-academia-industry",
]

OVERVIEW_TEXT = (
    "Decent Actuarial Consultants (DAC) is a Taipei-headquartered actuarial "
    "consultancy serving insurers across Taiwan, Vietnam, Cambodia, and the "
    "wider Southeast Asian region. This thesis was completed during a "
    "3-month internship (Mar–Jun 2026) at DAC's Phnom Penh office, applying "
    "DAC's actuarial expertise to Cambodia's underserved health-insurance "
    "underwriting problem."
)

# Left column: org-profile panel (logo + overview), mirrors the Slide 3
# "Meet Sophea" profile-card pattern.
PANEL_L = MARGIN_L
PANEL_T = 1200000
PANEL_W = 3900000
PANEL_H = CONTENT_BOT - PANEL_T
rect(s, PANEL_L, PANEL_T, PANEL_W, PANEL_H, fill=LIGHT_BG)
rect(s, PANEL_L, PANEL_T, 91440, PANEL_H, fill=NAVY)

LOGO_W = 3200000
LOGO_H = 1800000   # DAC.jpg is ~16:9; add_picture(width=...) preserves true aspect ratio
LOGO_T = PANEL_T + 280000
LOGO_L = PANEL_L + (PANEL_W - LOGO_W) // 2
if os.path.exists(LOGO_DAC):
    s.shapes.add_picture(LOGO_DAC, LOGO_L, LOGO_T, width=LOGO_W)

OVERVIEW_T = LOGO_T + LOGO_H + 250000
OVERVIEW_L = PANEL_L + 180000
OVERVIEW_W = PANEL_W - 360000
OVERVIEW_H = (PANEL_T + PANEL_H) - 100000 - OVERVIEW_T
tf = textbox(s, OVERVIEW_L, OVERVIEW_T, OVERVIEW_W, OVERVIEW_H)
para(tf, OVERVIEW_TEXT, 12, color=DARK_TXT)

# Right column: 6 services as compact single-line rows.
ROW_L = PANEL_L + PANEL_W + 280000
ROW_W = (MARGIN_L + CONTENT_W) - ROW_L
ROW_H = 784000
ROW_GAP = 90000
for i, svc in enumerate(SERVICES):
    row_t = PANEL_T + i * (ROW_H + ROW_GAP)
    card(s, ROW_L, row_t, ROW_W, ROW_H, body_lines=[svc], body_size=13)

footer(s, "Introduction & Problem Background", "2", 44)
```

- [ ] **Step 4: Rebuild the deck and rerun the verification script, confirm it passes**

Run (from repo root `C:\dac-uw-thesis`):
```bash
python thesis/health_rl/build_defense_v3.py
python "C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\verify_about_dac_slide.py"
```
Expected: exits 0, prints `PASS: slide 4 has 1 picture, overview + all 6 services present, stale credentials line removed.`

- [ ] **Step 5: Sanity-check the rest of the deck didn't regress**

Run (from repo root `C:\dac-uw-thesis`):
```bash
python -c "
from pptx import Presentation
prs = Presentation(r'thesis/health_rl/Poly_defense_presentation_v3.pptx')
print('total slides:', len(prs.slides))
n_pics_0 = sum(1 for sh in prs.slides[0].shapes if sh.shape_type == 13)
print('slide 1 (title) pictures:', n_pics_0)
"
```
Expected: `total slides:` matches the count before this change (unchanged — this task only edits Slide 4's contents, not slide count/order), and `slide 1 (title) pictures:` is unchanged (still >=2, since Slide 4's new picture doesn't touch Slide 1).

- [ ] **Step 6: Commit**

```bash
git add thesis/health_rl/build_defense_v3.py thesis/health_rl/Poly_defense_presentation_v3.pptx docs/superpowers/specs/2026-07-01-defense-about-dac-slide-redesign.md docs/superpowers/plans/2026-07-01-defense-about-dac-slide-redesign.md
git commit -m "$(cat <<'EOF'
feat(defense): About-DAC slide gets company logo + overview blurb

Redesigns Slide 4 from a 2x3 service-card grid into a two-column
layout: a Sophea-style profile panel (DAC.jpg logo + short overview
blurb) on the left, and the same 6 services as compact single-line
rows on the right. Drops the now-redundant bottom credentials line.

EOF
)"
```

---

## Self-Review Notes

- **Spec coverage:** all 4 locked decisions from the spec are implemented — overview content (identity/scale + thesis relevance), two-column layout, dropped credentials line, reused `DAC.jpg` asset. ✅
- **Placeholder scan:** no TBD/TODO; all code is complete and copy-pasteable. ✅
- **Type/name consistency:** `LOGO_DAC`, `MARGIN_L`, `CONTENT_W`, `CONTENT_BOT`, `LIGHT_BG`, `NAVY`, `DARK_TXT`, `WHITE`, `SW`, `SH` all match names already defined/imported earlier in `build_defense_v3.py` / `defense_tokens.py` — verified by reading the file directly, not assumed. `card()`'s signature (`slide, l, t, w, h, header=None, body_lines=None, ..., body_size=11`) matches the call in Step 3. ✅
- **Scope:** single file, single slide, one task — no decomposition needed. ✅
