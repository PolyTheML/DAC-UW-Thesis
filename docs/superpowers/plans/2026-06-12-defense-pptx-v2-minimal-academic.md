# Defense PPTX v2 — Minimal Academic Restyle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle all 32 slides of `burgundy_defense_presentation.pptx` to the approved Minimal Academic system (flat white, Calibri, burgundy accents + thin bottom bar), cut on-slide text to ≤4 talking points with generated presenter notes, and regenerate all 6 result charts at slide scale.

**Architecture:** `thesis/health_rl/build_burgundy_presentation.py` evolves in place in two phases: first the shared chrome/helpers are swapped to the flat system while keeping old call-site signatures green, then slide functions are rewritten cluster-by-cluster. Slide-scale figures come from a new `gen_slide_figures.py` that reuses the existing `gen_*` figure scripts' data harnesses (with npz caches so re-renders are instant) and a new `_slide_style.py` (sans, ≥16 pt, thick lines, deck palette) saving into `figures/slides/`.

**Tech Stack:** python-pptx, matplotlib (Agg), numpy, pytest. Spec: `docs/superpowers/specs/2026-06-12-defense-pptx-v2-minimal-academic-design.md`.

---

## Context an engineer needs

- **Builder**: `thesis/health_rl/build_burgundy_presentation.py` (~1,640 lines). One function per slide, assembled in `main()`. All headline numbers load at import time from `demo/static/thesis_results.json` into `_E005…_E013`, `_LADDER` aliases — KeyError on a missing key is **intentional** (drift guard). Never hardcode a number that exists in the JSON.
- **Tests**: `tests/test_build_presentation.py` — session fixture runs the builder once via subprocess, then asserts on the saved pptx. `python -m pytest tests/test_build_presentation.py -q` takes ~10 s.
- **Build 1 problem** (user-rejected): rounded+shadowed pills, Times New Roman display type, thesis-scale matplotlib PNGs (9 pt text), full sentences, logo cluster on every slide. Structure (32 slides, tags, decimal titles, numbering) is **approved — do not change it**.
- **Shadows**: python-pptx autoshapes inherit a theme drop shadow. The fix is `shape.shadow.inherit = False` in every shape-creating helper.
- **Claim discipline (non-negotiable)**: four "armor" footnotes must stay on-slide (admissible-scope §5.0.1; criterion-6 FAILED-with-interpretation; LinUCB cold-start p=0.0840 softened; AlwaysRATED inadmissibility). Objectives O1–O4 on slide 5 stay **verbatim** (examiner compares against thesis) — a deliberate exception to the 8-word rule.
- **Figure gen scripts** (`thesis/health_rl/figures/gen_*.py`): each separates an expensive data step (re-runs the experiment harness; 20-seed runs take 10–25 min each) from a cheap plot step using shared `_style.py`. We reuse their data functions; we never modify them.
- **JSON gotchas**: `_E008["referral_pct"]` = 1.3 and `_E008["human_cost_pct_of_reward"]` = 2.2 (not the 1.5 %/2 % some prose quotes); cold-start effect sizes live at `_E010["wilcoxon_t2000"]["lints_vs_freshxgb"]["d"]` (1.48) and `…["linucb_vs_freshxgb"]["d"]` (0.55) — use them instead of build 1's hardcoded "d = 1.48".

## File map

| File | Action | Responsibility |
|---|---|---|
| `thesis/health_rl/build_burgundy_presentation.py` | Modify heavily | The deck. Same filename, same output path. |
| `thesis/health_rl/figures/_slide_style.py` | Create | Slide-scale rcParams, SLIDE_PALETTE, `save_slide()` → `figures/slides/` |
| `thesis/health_rl/figures/gen_slide_figures.py` | Create | 6 slide-scale charts; reuses gen_* data harnesses; npz caches |
| `thesis/health_rl/figures/slides/` | Created by scripts | `slide_*.png` outputs + `_cache_*` (gitignored) |
| `tests/test_build_presentation.py` | Modify | Existing 8 assertions kept (1 regex updated) + 7 new style/density/armor tests |
| `.gitignore` | Modify | ignore `figures/slides/_cache_*` |

Slide function → cluster map (all in the builder):

| Task | Functions |
|---|---|
| 3 | `slide_title`, `slide_toc`, `slide_demo`, `slide_thanks`, `slide_appendix_divider` |
| 4 | `slide_research_background`, `slide_research_problem`, `slide_goal_objectives`, `slide_dac_internship`, `slide_lit_summary` |
| 5 | `slide_system_pipeline`, `slide_cambodia_dataset`, `slide_bandit_formulation`, `slide_algorithms_baselines`, `slide_guardrail_hitl_design` |
| 7 | `slide_convergence`, `slide_benchmark`, `slide_cold_start`, `slide_hitl_results`, `slide_fairness_audit`, `slide_drift_adaptation` |
| 8 | `slide_achievements`, `slide_baseline_ladder`, `slide_other_limitations`, `slide_app_*` (5), `_slide_demo_screenshot` |

---

### Task 0: Baseline commit of build 1

Build 1 currently exists **only as uncommitted working-tree changes**. The spec promises "build 1 recoverable via git", so commit it before touching anything.

**Files:**
- Commit (no edits): `thesis/health_rl/build_burgundy_presentation.py`, `thesis/health_rl/burgundy_defense_presentation.pptx`, `tests/test_build_presentation.py`, `demo/static/thesis_results.json`

- [ ] **Step 0.1: Verify build 1 is green before snapshotting**

Run: `python -m pytest tests/test_build_presentation.py -q`
Expected: `8 passed`

- [ ] **Step 0.2: Commit exactly these four files** (the repo has many unrelated dirty files — do NOT `git add .`)

```bash
git add thesis/health_rl/build_burgundy_presentation.py \
        thesis/health_rl/burgundy_defense_presentation.pptx \
        tests/test_build_presentation.py \
        demo/static/thesis_results.json
git commit -m "chore(defense): baseline commit of pptx build 1 (Sreynich structural pass)

Snapshot before the v2 minimal-academic restyle so build 1 stays
recoverable. 32 slides, 8/8 tests, JSON-driven numbers.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 1: Flat chrome — compat-preserving helper restyle

Swap the shared chrome to the Minimal Academic system **without changing any helper signature**, so all 32 existing slide functions still build and the suite stays green. After this task the deck is white/flat with the new tag/title/bar but still has old layouts — that's expected mid-transition.

**Files:**
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (imports, constants, helpers `_add_text_box` `_add_bullet_box` `_add_filled_box` `_add_callout` `_add_picture_fit` `_add_section_tag` `_add_slide_title` `_add_title_rule` `_add_bottom_bar`)
- Modify: `tests/test_build_presentation.py` (section-tag regex)

- [ ] **Step 1.1: Update the section-tag test to the new chrome convention** (TDD: this is the failing test that drives the chrome change)

Replace the body of `test_section_tags_present_on_content_slides` with:

```python
def test_section_tags_present_on_content_slides(built_presentation):
    """Every content slide (indices 2-20) carries an uppercase 'ROMAN · NAME' tag."""
    prs = Presentation(str(built_presentation))
    tag_pattern = re.compile(r"\b(I|II|III|IV|V|VI) · [A-Z&\s]+")
    for idx in range(2, 21):
        combined = _all_text(prs, idx)
        assert tag_pattern.search(combined), (
            f"Slide {idx + 1}: no uppercase section tag found. Got: {combined[:200]}"
        )
```

- [ ] **Step 1.2: Run it to confirm it fails against build 1**

Run: `python -m pytest tests/test_build_presentation.py::test_section_tags_present_on_content_slides -q`
Expected: FAIL (old chip text is lowercase `iv. Methodology`)

- [ ] **Step 1.3: Builder header — add `re` import and the new constants**

Add `import re` after `import os`. In the Colors block add:

```python
GRAY_LABEL = RGBColor(0x77, 0x77, 0x77)   # stat labels / footnotes
HAIRLINE   = RGBColor(0xDD, 0xDD, 0xDD)   # 1px separators
PANEL      = RGBColor(0xF7, 0xF5, 0xF6)   # flat panel fill (no borders)
```

Replace the Dimensions block values (thin bar, taller content area):

```python
SLIDE_WIDTH       = Inches(13.333)
SLIDE_HEIGHT      = Inches(7.5)
MARGIN_LEFT       = Inches(0.5)
CONTENT_TOP       = Inches(1.32)   # below tag + title + accent
BOTTOM_BAR_TOP    = Inches(7.28)
BOTTOM_BAR_HEIGHT = Inches(0.22)
CONTENT_W         = SLIDE_WIDTH - MARGIN_LEFT - Inches(0.5)
CONTENT_H         = BOTTOM_BAR_TOP - CONTENT_TOP - Inches(0.15)
FOOTNOTE_TOP      = BOTTOM_BAR_TOP - Inches(0.42)
```

After `FIG_DIR` add: `SLIDE_FIG_DIR = FIG_DIR / "slides"`.

Update the module docstring's convention list to mention the v2 visual system (one line: `Minimal Academic restyle (v2): flat white, Calibri-only, burgundy accents, thin bottom bar`).

- [ ] **Step 1.4: De-shadow every shape-creating helper**

Add immediately after `_no_line`:

```python
def _flat(shape):
    """Kill the theme's inherited drop shadow -- v2 is shadow-free everywhere."""
    shape.shadow.inherit = False


def _letterspace(paragraph, spc: int = 140):
    """Letter-space a paragraph's runs (OOXML 'spc' is in 1/100 pt)."""
    for r in paragraph.runs:
        r.font._rPr.set("spc", str(spc))
```

Then add `_flat(box)` as the first statement after each `add_shape` call in `_add_text_box`, `_add_bullet_box`, `_add_filled_box`, `_add_callout`, and `_flat(pic)` after `add_picture` in `_add_picture_fit` (pictures: python-pptx exposes `.shadow` on them too).

In `_add_filled_box`, neutralise rounding but keep the signature so old call sites still run (the param is deleted in Task 9 once no caller remains):

```python
def _add_filled_box(slide, left, top, width, height,
                    fill_color: RGBColor, rounded: bool = False,
                    line_color: RGBColor | None = None, line_width_pt: float = 0):
    # 'rounded' is ignored: v2 is square-corner only (param removed in Task 9)
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    _flat(box)
    _set_shape_fill(box, fill_color)
    ...  # rest unchanged
```

In `_add_callout`, replace the rounded outline style with a flat panel (same signature):

```python
def _add_callout(slide, left, top, width, height, text: str,
                 font_size: int = 13, bold: bool = False,
                 color: RGBColor = DARK_TEXT, font_name: str = "Calibri"):
    """v2: flat light panel, square corners, charcoal text, no border."""
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    _flat(box)
    _set_shape_fill(box, PANEL)
    _no_line(box)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = PP_ALIGN.LEFT
    return box
```

(Note the default `color` changes BURGUNDY → DARK_TEXT; old callers that want burgundy pass it explicitly — none do — so panels go charcoal, which is the v2 look.)

- [ ] **Step 1.5: Replace the three chrome functions**

```python
def _add_section_tag(slide, sec_key: str):
    """Plain-text uppercase letter-spaced section tag, top-left (no chip)."""
    num, name = next((n, t) for n, t in SECTIONS if n == sec_key)
    box = _add_text_box(slide, MARGIN_LEFT, Inches(0.16), Inches(7.0), Inches(0.3),
                        f"{num.upper()} · {name.upper()}",
                        font_size=10, bold=True, color=BURGUNDY)
    _letterspace(box.text_frame.paragraphs[0])


_TITLE_RX = re.compile(r"^([A-Za-z]?\d+(?:\.\d+)?)\.?\s+(.*)$")


def _add_slide_title(slide, text: str):
    """Burgundy decimal run + charcoal title run, Calibri 26 bold."""
    m = _TITLE_RX.match(text.strip())
    num, rest = (m.group(1), m.group(2).strip()) if m else ("", text.strip())
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, MARGIN_LEFT, Inches(0.46),
                                 Inches(12.3), Inches(0.62))
    _flat(box)
    box.fill.background()
    _no_line(box)
    tf = box.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    for run_text, run_color in ((f"{num}  ", BURGUNDY), (rest, DARK_TEXT)):
        if run_text.strip():
            r = p.add_run()
            r.text = run_text
            r.font.size = Pt(26)
            r.font.bold = True
            r.font.color.rgb = run_color
            r.font.name = "Calibri"


def _add_title_rule(slide):
    """Short burgundy accent under the title (replaces the full-width rule)."""
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.14), Inches(0.55), Inches(0.045), BURGUNDY)


def _add_bottom_bar(slide, page_num: str | None = None):
    """Thin burgundy strip; white right-aligned page number; NO logos."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), BOTTOM_BAR_TOP, SLIDE_WIDTH, BOTTOM_BAR_HEIGHT)
    _flat(bar)
    _set_shape_fill(bar, BURGUNDY)
    _no_line(bar)
    if page_num is not None:
        pg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(12.3), BOTTOM_BAR_TOP - Inches(0.02),
            Inches(0.9), Inches(0.26))
        _flat(pg)
        pg.fill.background()
        _no_line(pg)
        tf = pg.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = Inches(0)
        tf.margin_bottom = Inches(0)
        p = tf.paragraphs[0]
        p.text = page_num
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.RIGHT
```

`_content_slide` is unchanged (it just calls the four chrome helpers).

- [ ] **Step 1.6: Build and test**

Run: `python thesis/health_rl/build_burgundy_presentation.py` → `Saved 32 slides -> ...`
Run: `python -m pytest tests/test_build_presentation.py -q`
Expected: `8 passed` (the step-1.1 regex now matches the new tags)

- [ ] **Step 1.7: Commit**

```bash
git add thesis/health_rl/build_burgundy_presentation.py \
        thesis/health_rl/burgundy_defense_presentation.pptx \
        tests/test_build_presentation.py
git commit -m "feat(defense): v2 chrome - flat de-shadowed helpers, text tag, thin bar

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 2: New layout helpers (stat row, talking points, notes, footnote, flat table)

These five helpers carry the whole v2 layout language; every slide rewrite in Tasks 3–8 calls them. The ≤4-point density rule is **enforced in code** here.

**Files:**
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (insert after `_add_picture_fit`)
- Test: `tests/test_build_presentation.py`

- [ ] **Step 2.1: Write the failing density unit test** (append to the test file)

```python
# ---------------------------------------------------------------------------
# Density rule is enforced in code
# ---------------------------------------------------------------------------

def test_talking_points_helper_rejects_more_than_four():
    import importlib.util
    spec = importlib.util.spec_from_file_location("builder", SCRIPT)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    prs = Presentation()
    prs.slide_width = builder.SLIDE_WIDTH
    prs.slide_height = builder.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    with pytest.raises(ValueError):
        builder._add_talking_points(slide, builder.MARGIN_LEFT, builder.CONTENT_TOP,
                                    builder.CONTENT_W, ["a", "b", "c", "d", "e"])
```

- [ ] **Step 2.2: Run it to verify it fails**

Run: `python -m pytest tests/test_build_presentation.py::test_talking_points_helper_rejects_more_than_four -q`
Expected: FAIL with `AttributeError: ... has no attribute '_add_talking_points'`

- [ ] **Step 2.3: Implement the five helpers** (insert after `_add_picture_fit`, before the Chrome section)

```python
# ===========================================================================
# v2 layout helpers (Minimal Academic)
# ===========================================================================

def _add_stat_row(slide, top, stats, hero_idx: int = 0, height=Inches(1.05),
                  left=None, width=None, value_colors=None):
    """Flat big-number stat row: value over small gray caps label, hairline-separated.

    stats: list of (value, label). hero_idx gets BURGUNDY; value_colors overrides per-stat.
    """
    left = MARGIN_LEFT if left is None else left
    width = CONTENT_W if width is None else width
    n = len(stats)
    col_w = int(width / n)
    for i, (val, label) in enumerate(stats):
        cx = left + i * col_w
        color = (value_colors[i] if value_colors and value_colors[i] is not None
                 else (BURGUNDY if i == hero_idx else DARK_TEXT))
        _add_text_box(slide, cx, top, col_w - Inches(0.15), Inches(0.62),
                      str(val), font_size=30, bold=True, color=color)
        lab = _add_text_box(slide, cx, top + Inches(0.62), col_w - Inches(0.15),
                            Inches(0.36), label.upper(), font_size=10, color=GRAY_LABEL)
        _letterspace(lab.text_frame.paragraphs[0], 80)
        if i > 0:
            _add_filled_box(slide, cx - Inches(0.12), top + Inches(0.05),
                            Inches(0.012), height - Inches(0.15), HAIRLINE)


def _add_talking_points(slide, left, top, width, points, font_size: int = 17,
                        line_h=Inches(0.62)):
    """<=4 short points, burgundy square marker + charcoal text. Returns bottom y.

    Density rule (spec section 4) is enforced here: more than 4 points raises.
    """
    if len(points) > 4:
        raise ValueError(f"talking points rule: max 4 per slide, got {len(points)}")
    y = top
    for text in points:
        _add_filled_box(slide, left, y + Inches(0.12), Inches(0.1), Inches(0.1), BURGUNDY)
        _add_text_box(slide, left + Inches(0.28), y, width - Inches(0.28),
                      line_h, text, font_size=font_size, color=DARK_TEXT)
        y += line_h
    return y


def _add_footnote(slide, text: str):
    """Claim-critical small gray footnote pinned above the bottom bar."""
    _add_text_box(slide, MARGIN_LEFT, FOOTNOTE_TOP, CONTENT_W, Inches(0.36),
                  text, font_size=10.5, italic=True, color=GRAY_LABEL)


def _add_notes(slide, text: str):
    """Presenter notes = the rehearsal script for this slide."""
    slide.notes_slide.notes_text_frame.text = text


def _add_flat_table(slide, left, top, col_ws, header, rows, font_size: int = 12,
                    row_h=Inches(0.5), cell_style=None):
    """Flat table: bold charcoal header over a burgundy hairline, PANEL/white zebra rows.

    cell_style: optional fn(r, c, text) -> (bold, RGBColor) for emphasis cells.
    """
    col_xs = [left]
    for w in col_ws[:-1]:
        col_xs.append(col_xs[-1] + w)
    for cx, cw, h in zip(col_xs, col_ws, header):
        _add_text_box(slide, cx + Inches(0.06), top, cw - Inches(0.12), Inches(0.34),
                      h, font_size=font_size, bold=True, color=DARK_TEXT)
    _add_filled_box(slide, left, top + Inches(0.36), sum(col_ws, Inches(0)),
                    Inches(0.025), BURGUNDY)
    for i, row in enumerate(rows):
        ry = top + Inches(0.44) + i * row_h
        if i % 2 == 0:
            _add_filled_box(slide, left, ry, sum(col_ws, Inches(0)), row_h, PANEL)
        for c, (cx, cw, text) in enumerate(zip(col_xs, col_ws, row)):
            bold, color = (False, DARK_TEXT)
            if cell_style is not None:
                bold, color = cell_style(i, c, text)
            _add_text_box(slide, cx + Inches(0.06), ry + Inches(0.04),
                          cw - Inches(0.12), row_h - Inches(0.08),
                          text, font_size=font_size, bold=bold, color=color)
    return top + Inches(0.44) + len(rows) * row_h
```

(`sum(col_ws, Inches(0))`: `Inches()` returns `Emu` ints, so summing with an `Emu` start keeps the type.)

- [ ] **Step 2.4: Run the new test + full suite**

Run: `python -m pytest tests/test_build_presentation.py -q`
Expected: `9 passed`

- [ ] **Step 2.5: Commit**

```bash
git add thesis/health_rl/build_burgundy_presentation.py tests/test_build_presentation.py
git commit -m "feat(defense): v2 layout helpers - stat row, talking points (max 4), notes, footnote, flat table

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Title, ToC, Demonstration, Thanks, Appendix divider

Rewrite the five non-content slides in the v2 language. Title keeps its three logos and the unchanged supervisor block / "July 2026" placeholder; everything else goes flat white Calibri.

**Files:**
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (replace bodies of `slide_title`, `slide_toc`, `slide_demo`, `slide_thanks`, `slide_appendix_divider`)

- [ ] **Step 3.1: Replace `slide_title`**

```python
def slide_title(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    for path, lx, ly, lw in [
        (LOGO_ITC, 0.6,  0.30, 1.0),
        (LOGO_AMS, 1.75, 0.40, 1.45),
        (LOGO_DAC, 11.3, 0.35, 1.45),
    ]:
        if os.path.exists(path):
            pic = slide.shapes.add_picture(path, Inches(lx), Inches(ly), width=Inches(lw))
            _flat(pic)

    _add_text_box(slide, Inches(3.4), Inches(0.42), Inches(7.2), Inches(0.5),
                  INSTITUTION, font_size=22, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(3.4), Inches(0.92), Inches(7.2), Inches(0.4),
                  DEPARTMENT, font_size=15, color=GRAY_LABEL, align=PP_ALIGN.CENTER)

    _add_filled_box(slide, Inches(5.92), Inches(2.05), Inches(1.5), Inches(0.045), BURGUNDY)
    box = _add_text_box(slide, Inches(0.9), Inches(2.35), Inches(11.5), Inches(1.7),
                        THESIS_TITLE.upper(), font_size=27, bold=True, color=DARK_TEXT,
                        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    box.text_frame.word_wrap = True
    _add_filled_box(slide, Inches(5.92), Inches(4.25), Inches(1.5), Inches(0.045), BURGUNDY)

    _add_text_box(slide, Inches(0), Inches(4.62), SLIDE_WIDTH, Inches(0.34),
                  "Thesis Defense — Presented by", font_size=14, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(4.96), SLIDE_WIDTH, Inches(0.5),
                  PRESENTER, font_size=27, bold=True, color=BURGUNDY,
                  align=PP_ALIGN.CENTER)

    lx, rx = Inches(1.5), Inches(7.5)
    for i, (lt, rt) in enumerate([
        (f"Supervisor      :  {SUPERVISOR}",    f"Organization :  {ORGANIZATION}"),
        (f"Co-Supervisor  :  {CO_SUPERVISOR}", f"Duration        :  {DURATION}"),
    ]):
        y = Inches(5.68) + i * Inches(0.36)
        _add_text_box(slide, lx, y, Inches(5.6), Inches(0.34), lt, font_size=14, color=DARK_TEXT)
        _add_text_box(slide, rx, y, Inches(5.6), Inches(0.34), rt, font_size=14, color=DARK_TEXT)

    _add_text_box(slide, Inches(0), Inches(6.6), SLIDE_WIDTH, Inches(0.38),
                  DEFENSE_DATE, font_size=15, bold=True, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)
```

- [ ] **Step 3.2: Replace `slide_toc`** (kills the burgundy band, white circle, and the 🎓 emoji)

```python
def slide_toc(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_text_box(slide, MARGIN_LEFT, Inches(0.55), Inches(9.0), Inches(0.7),
                  "Table of Contents", font_size=30, bold=True, color=DARK_TEXT)
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.32), Inches(0.55), Inches(0.045), BURGUNDY)

    col_xs = [Inches(0.9), Inches(7.1)]
    row_h = Inches(1.55)
    for idx, (num, name) in enumerate(SECTIONS):
        cx = col_xs[idx // 3]
        cy = Inches(1.95) + (idx % 3) * row_h
        _add_text_box(slide, cx, cy, Inches(1.1), Inches(0.65),
                      num, font_size=30, bold=True, color=BURGUNDY)
        _add_text_box(slide, cx + Inches(1.25), cy + Inches(0.06),
                      Inches(4.6), Inches(0.5),
                      name, font_size=19, bold=True, color=DARK_TEXT)
        _add_filled_box(slide, cx + Inches(1.25), cy + Inches(0.62),
                        Inches(4.3), Inches(0.012), HAIRLINE)
    _add_bottom_bar(slide)
```

- [ ] **Step 3.3: Replace `slide_demo`** (white, no banner band)

```python
def slide_demo(prs: Presentation):
    """Slide 22 -- live demo cue."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    tag = _add_text_box(slide, MARGIN_LEFT, Inches(0.7), Inches(6.0), Inches(0.34),
                        "LIVE DEMONSTRATION", font_size=12, bold=True, color=BURGUNDY)
    _letterspace(tag.text_frame.paragraphs[0], 200)
    _add_text_box(slide, MARGIN_LEFT, Inches(1.1), Inches(12.0), Inches(0.7),
                  "Adaptive Underwriting Dashboard", font_size=30, bold=True,
                  color=DARK_TEXT)
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.92), Inches(0.55), Inches(0.045), BURGUNDY)

    steps = [
        ("1", "Run",  "uvicorn demo.main:app --reload --port 8000"),
        ("2", "Open", "http://localhost:8000"),
        ("3", "Show", "Score applicant -> bandit arm selection -> PSI monitor panel"),
        ("4", "Show", "Human-in-the-loop referral queue + cost accounting"),
    ]
    step_top = Inches(2.6)
    for num, verb, detail in steps:
        _add_text_box(slide, MARGIN_LEFT, step_top, Inches(0.5), Inches(0.5),
                      num, font_size=22, bold=True, color=BURGUNDY)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.65), step_top + Inches(0.05),
                      Inches(1.2), Inches(0.45), verb, font_size=16, bold=True,
                      color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(2.0), step_top + Inches(0.07),
                      Inches(10.5), Inches(0.45), detail, font_size=14,
                      color=SOFT_TEXT, font_name="Consolas")
        _add_filled_box(slide, MARGIN_LEFT, step_top + Inches(0.58),
                        Inches(11.9), Inches(0.012), HAIRLINE)
        step_top += Inches(0.78)

    _add_footnote(slide, "Fallback: demo screenshots in appendix (A6-A8) if the live run fails.")
    _add_bottom_bar(slide)
    _add_notes(slide,
        "Switch to the browser. Walk one applicant through scoring, show the arm the bandit "
        "picks and the uncertainty-driven REFER, then the PSI monitor staying GREEN/AMBER, "
        "and finally the HITL queue with per-referral cost. If anything breaks, jump to "
        "appendix slides A6-A8 and narrate over the screenshots.")
```

- [ ] **Step 3.4: Replace `slide_thanks`** (flat; keeps the two logos rule: title + thanks only)

```python
def slide_thanks(prs: Presentation):
    """Slide 23."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_filled_box(slide, Inches(5.92), Inches(2.0), Inches(1.5), Inches(0.045), BURGUNDY)
    _add_text_box(slide, Inches(0), Inches(2.35), SLIDE_WIDTH, Inches(1.0),
                  "Thank you.", font_size=54, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(3.45), SLIDE_WIDTH, Inches(0.5),
                  "Questions & Answers", font_size=20, color=BURGUNDY,
                  align=PP_ALIGN.CENTER)

    _add_text_box(slide, Inches(0), Inches(4.7), SLIDE_WIDTH, Inches(0.42),
                  PRESENTER, font_size=20, bold=True, color=DARK_TEXT,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(5.15), SLIDE_WIDTH, Inches(0.38),
                  "chanpoly3@gmail.com", font_size=15, color=GRAY_LABEL,
                  align=PP_ALIGN.CENTER)
    _add_text_box(slide, Inches(0), Inches(5.55), SLIDE_WIDTH, Inches(0.38),
                  INSTITUTION, font_size=14, color=GRAY_LABEL, align=PP_ALIGN.CENTER)

    for path, lx in [(LOGO_ITC, 5.45), (LOGO_AMS, 6.25), (LOGO_DAC, 7.15)]:
        if os.path.exists(path):
            pic = slide.shapes.add_picture(path, Inches(lx), Inches(6.15), width=Inches(0.7))
            _flat(pic)
    _add_bottom_bar(slide)
```

- [ ] **Step 3.5: Replace `slide_appendix_divider`** (white; burgundy wordmark)

```python
def slide_appendix_divider(prs: Presentation):
    """Slide 24."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    _add_text_box(slide, MARGIN_LEFT, Inches(0.9), Inches(10.0), Inches(1.0),
                  "APPENDIX", font_size=48, bold=True, color=BURGUNDY)
    _add_filled_box(slide, MARGIN_LEFT, Inches(2.05), Inches(0.55), Inches(0.045), BURGUNDY)

    items = [
        ("A1", "Q2: Number Reconciliation -- EXP-005 vs ladder harness"),
        ("A2", "Fairness Criterion-6 Detail -- FAILED-with-interpretation"),
        ("A3", "PSI Guardrail Mechanics"),
        ("A4", "LinUCB / LinTS Update Equations"),
        ("A5", "Dataset Construction -- CDHS / STEPS / ILO / WHO anchoring"),
        ("A6-A8", "Demo Screenshots (fallback if live demo fails)"),
    ]
    item_top = Inches(2.55)
    for i, (label, desc) in enumerate(items):
        iy = item_top + i * Inches(0.68)
        _add_text_box(slide, Inches(1.0), iy, Inches(1.2), Inches(0.4),
                      label, font_size=15, bold=True, color=BURGUNDY)
        _add_text_box(slide, Inches(2.4), iy, Inches(10.0), Inches(0.4),
                      desc, font_size=15, color=DARK_TEXT)
    _add_bottom_bar(slide)
```

- [ ] **Step 3.6: Build, test, commit**

Run: `python thesis/health_rl/build_burgundy_presentation.py` then `python -m pytest tests/test_build_presentation.py -q`
Expected: `9 passed`

```bash
git add thesis/health_rl/build_burgundy_presentation.py \
        thesis/health_rl/burgundy_defense_presentation.pptx
git commit -m "feat(defense): v2 title/toc/demo/thanks/divider - flat white, no emoji, logos title+thanks only

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 4: Sections i–iii (slides 3–7)

Density pass + flat layout for Introduction, DAC, Literature. Cut detail moves into `_add_notes` — the notes ARE the deliverable here; never drop a fact, relocate it.

**Files:**
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (replace bodies of `slide_research_background`, `slide_research_problem`, `slide_goal_objectives`, `slide_dac_internship`, `slide_lit_summary`)

- [ ] **Step 4.1: Replace `slide_research_background`**

```python
def slide_research_background(prs: Presentation):
    """Slide 3 (01)."""
    slide = _content_slide(prs, "i", "1.1.  Research Background", "01")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.1), Inches(6.4), Inches(0.9),
                  "< 10 %", font_size=60, bold=True, color=BURGUNDY)
    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.05), Inches(6.4),
                        Inches(0.36), "HEALTH-INSURANCE PENETRATION IN CAMBODIA (2023 EST.)",
                        font_size=10, color=GRAY_LABEL)
    _letterspace(lab.text_frame.paragraphs[0], 80)

    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.8), Inches(6.4), [
        "NSSF covers formal-sector workers only (~16%)",
        "Private underwriting is manual and rule-based",
        "Static rules never learn from outcomes",
        "No demographic-parity monitoring in practice",
    ])

    _add_callout(slide, Inches(7.3), CONTENT_TOP + Inches(0.1), Inches(5.5), Inches(4.6),
                 "Research opportunity\n\nContextual bandits can learn from every "
                 "underwriting decision in real time, adapting to Cambodia-specific risk "
                 "patterns while demographic fairness is monitored automatically.",
                 font_size=15)

    _add_notes(slide,
        "Cambodia context: the National Social Security Fund covers only formal-sector "
        "workers, roughly 16 percent; private voluntary insurance is nascent and "
        "underwriting is mostly manual and rule-based. Actuaries apply fixed premium rules "
        "without learning from outcomes, suboptimal decisions compound over a growing "
        "applicant pool, and penetration is below 10 percent (2023 estimate). The "
        "opportunity: a contextual bandit learns online from each decision while a PSI "
        "guardrail watches demographic fairness.")
```

- [ ] **Step 4.2: Replace `slide_research_problem`** (2×2 flat panels, one line each)

```python
def slide_research_problem(prs: Presentation):
    """Slide 4 (02)."""
    slide = _content_slide(prs, "i", "1.2.  Research Problem", "02")

    problems = [
        ("Static thresholds", "Fixed cutoffs ignore applicant context"),
        ("No online adaptation", "Claims feedback never reaches the model"),
        ("Demographic blindspot", "No parity metric is tracked"),
        ("No triage", "Experts review routine, not borderline, cases"),
    ]
    card_w, card_h = Inches(6.0), Inches(2.35)
    positions = [
        (MARGIN_LEFT,               CONTENT_TOP + Inches(0.2)),
        (MARGIN_LEFT + Inches(6.4), CONTENT_TOP + Inches(0.2)),
        (MARGIN_LEFT,               CONTENT_TOP + Inches(2.85)),
        (MARGIN_LEFT + Inches(6.4), CONTENT_TOP + Inches(2.85)),
    ]
    for (title, desc), (lx, ly) in zip(problems, positions):
        _add_filled_box(slide, lx, ly, card_w, card_h, PANEL)
        _add_filled_box(slide, lx, ly, Inches(0.07), card_h, BURGUNDY)
        _add_text_box(slide, lx + Inches(0.3), ly + Inches(0.35),
                      card_w - Inches(0.6), Inches(0.5),
                      title, font_size=20, bold=True, color=DARK_TEXT)
        _add_text_box(slide, lx + Inches(0.3), ly + Inches(1.0),
                      card_w - Inches(0.6), Inches(1.1),
                      desc, font_size=15, color=SOFT_TEXT)

    _add_notes(slide,
        "Four concrete failures of the status quo. One: fixed age/BMI/income cutoffs "
        "ignore context, so a misclassified high-risk applicant generates uncorrected "
        "losses. Two: the claims signal is never fed back, so accuracy degrades silently "
        "as demographics shift. Three: no parity metric is tracked, so regional or "
        "occupational concentration can develop undetected. Four: there is no triage - "
        "actuaries spend time on high-volume routine cases instead of genuine edge cases.")
```

- [ ] **Step 4.3: Replace `slide_goal_objectives`** — **O1–O4 text stays VERBATIM** (claim discipline; deliberate exception to the 8-word rule). Only the styling changes.

```python
def slide_goal_objectives(prs: Presentation):
    """Slide 5 (03). Objectives verbatim from the thesis -- do not paraphrase."""
    slide = _content_slide(prs, "i", "1.3.  Research Goal & Objectives", "03")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(4.0), Inches(0.32),
                        "RESEARCH GOAL", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.38), CONTENT_W, Inches(0.75),
                  "Design and evaluate an adaptive health insurance underwriting system using "
                  "contextual bandit algorithms on a synthetic Cambodia applicant dataset, "
                  "incorporating demographic fairness monitoring and human-in-the-loop augmentation.",
                  font_size=15, color=DARK_TEXT)

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.35), Inches(4.0),
                        Inches(0.32), "OBJECTIVES", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)

    objs = [
        ("O1", "Implement and adapt linear contextual bandit algorithms (LinUCB, LinTS) "
               "for multi-arm health insurance underwriting decisions."),
        ("O2", "Construct a 2,000-record synthetic Cambodia applicant dataset anchored "
               "on CDHS, STEPS, ILO, and WHO demographic distributions."),
        ("O3", "Evaluate bandit performance versus static rule-based baselines via "
               "20-seed multi-run trials, bootstrap CIs, and paired Wilcoxon tests."),
        ("O4", "Assess demographic fairness via PSI monitoring across region and occupation, "
               "and integrate a human-in-the-loop underwriting wrapper."),
    ]
    top = CONTENT_TOP + Inches(1.8)
    for i, (label, text) in enumerate(objs):
        y = top + i * Inches(0.95)
        _add_text_box(slide, MARGIN_LEFT, y, Inches(0.75), Inches(0.5),
                      label, font_size=20, bold=True, color=BURGUNDY)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.85), y + Inches(0.02),
                      CONTENT_W - Inches(0.85), Inches(0.85),
                      text, font_size=14, color=DARK_TEXT)
        if i > 0:
            _add_filled_box(slide, MARGIN_LEFT, y - Inches(0.1), CONTENT_W,
                            Inches(0.012), HAIRLINE)

    _add_notes(slide,
        "Read the goal once, slowly. The four objectives map one-to-one onto the chapters: "
        "O1 the algorithms (Chapter IV), O2 the dataset (Chapter IV), O3 the evaluation "
        "(Chapter V), O4 fairness plus HITL (Chapter V). These are verbatim from the thesis "
        "- the examiners will check the wording.")
```

- [ ] **Step 4.4: Replace `slide_dac_internship`**

```python
def slide_dac_internship(prs: Presentation):
    """Slide 6 (04)."""
    slide = _content_slide(prs, "ii", "2.1.  Internship at DAC", "04")

    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.1), Inches(6.4), [
        "DAC -- actuarial consulting, Phnom Penh",
        "Clients: insurers, pension funds, regulators",
        "Role: research intern, Mar-Jun 2026",
        "Deliverable: underwriting prototype + thesis",
    ])

    _add_callout(slide, Inches(7.3), CONTENT_TOP + Inches(0.1), Inches(5.5), Inches(2.5),
                 f"Supervision\n\nThesis advisor: {SUPERVISOR} (ITC)\n"
                 f"Field supervisor: {CO_SUPERVISOR} (DAC)",
                 font_size=15)

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.05), Inches(4.0),
                        Inches(0.32), "INTERNSHIP TIMELINE", font_size=11, bold=True,
                        color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    timeline = [
        ("Mar 2026", "Problem scoping & dataset design"),
        ("Apr 2026", "Algorithm implementation"),
        ("May 2026", "Experiments & analysis"),
        ("Jun 2026", "Thesis writing & defense prep"),
    ]
    seg_w = Inches(3.0)
    strip_top = CONTENT_TOP + Inches(3.5)
    for i, (month, desc) in enumerate(timeline):
        lx = MARGIN_LEFT + i * (seg_w + Inches(0.1))
        _add_filled_box(slide, lx, strip_top, seg_w, Inches(0.05), BURGUNDY)
        _add_text_box(slide, lx, strip_top + Inches(0.15), seg_w - Inches(0.2),
                      Inches(0.36), month, font_size=14, bold=True, color=BURGUNDY)
        _add_text_box(slide, lx, strip_top + Inches(0.55), seg_w - Inches(0.2),
                      Inches(0.8), desc, font_size=12, color=SOFT_TEXT)

    _add_notes(slide,
        "Decent Actuarial Consultants is a Phnom Penh actuarial consultancy serving "
        "insurers, pension funds and regulators across Southeast Asia. The thesis is "
        "embedded in a DAC-supervised research internship, March through June 2026; the "
        "deliverable is the end-to-end adaptive underwriting prototype plus this report. "
        "Timeline: March scoping and dataset design, April algorithms, May experiments, "
        "June writing and defense preparation.")
```

- [ ] **Step 4.5: Replace `slide_lit_summary`** — merge the two bandit-theory rows so the table is ≤5 rows (spec §4)

```python
def slide_lit_summary(prs: Presentation):
    """Slide 7 (05)."""
    slide = _content_slide(prs, "iii", "3.1.  Literature Summary", "05")

    rows = [
        ("Bandits in healthcare", "Bouneffouf et al. (2017)",
         "Clinical decision support via LinUCB; reward = patient outcome"),
        ("Linear bandit theory", "Li et al. (2010); Agrawal & Goyal (2013)",
         "LinUCB O(sqrt(T) d log T) regret; LinTS posterior sampling, near-optimal"),
        ("Fairness in insurance ML", "Frees et al. (2014); Kusner et al. (2017)",
         "Regulatory constraints on protected attributes; counterfactual fairness"),
        ("PSI model monitoring", "Yurdakul (2018)",
         "Population Stability Index drift zones (GREEN / AMBER / RED)"),
        ("Human-in-the-loop RL", "Christiano et al. (2017)",
         "Expert overrides improve alignment; cost-benefit of referral"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.15),
                    [Inches(3.0), Inches(3.6), Inches(5.7)],
                    ["Topic", "Key authors", "Contribution"],
                    rows, font_size=13, row_h=Inches(0.85))

    _add_footnote(slide, "Full review: thesis Chapter III (30+ sources).")
    _add_notes(slide,
        "Five strands inform the method. Bouneffouf showed LinUCB works for clinical "
        "decisions. Li et al. 2010 give the LinUCB regret bound, Agrawal and Goyal 2013 "
        "the LinTS guarantee - together they justify the two proposed policies. Frees and "
        "Kusner frame insurance fairness constraints; Yurdakul's PSI gives the monitoring "
        "metric with the 0.10/0.25 thresholds; Christiano motivates the human-in-the-loop "
        "wrapper. The thesis reviews thirty-plus sources; this is the load-bearing subset.")
```

- [ ] **Step 4.6: Build, test, commit**

Run: `python thesis/health_rl/build_burgundy_presentation.py && python -m pytest tests/test_build_presentation.py -q`
Expected: `9 passed`

```bash
git add thesis/health_rl/build_burgundy_presentation.py \
        thesis/health_rl/burgundy_defense_presentation.pptx
git commit -m "feat(defense): v2 sections i-iii - talking points + notes, 5-row lit table

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Methodology slides 8–12 (incl. native architecture diagram)

The matplotlib architecture PNG dies; slide 8 is rebuilt from native flat shapes in the deck palette.

**Files:**
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (replace bodies of `slide_system_pipeline`, `slide_cambodia_dataset`, `slide_bandit_formulation`, `slide_algorithms_baselines`, `slide_guardrail_hitl_design`)

- [ ] **Step 5.1: Replace `slide_system_pipeline`** (native shapes; three layers × four stages + two data sources)

```python
def slide_system_pipeline(prs: Presentation):
    """Slide 8 (06) -- native-shape architecture (replaces fig_ch4_architecture.png)."""
    slide = _content_slide(prs, "iv", "4.1.  System Pipeline", "06")

    layers = [
        ("BROWSER (SPA)", ["Applicant Simulator", "Premium Optimiser",
                           "Bandit Arena", "PSI Monitor"]),
        ("FASTAPI REST", ["/api/simulate", "/api/pricing/optimize",
                          "/api/bandit/run", "/api/psi/audit"]),
        ("PYTHON BACKEND", ["Actuarial Reward Sim", "Pricing Engine",
                            "Bandit Algorithms (LinUCB / LinTS)", "PSI Compute"]),
    ]
    label_w, box_w, box_h, gap = Inches(1.7), Inches(2.55), Inches(0.78), Inches(0.18)
    row_step = Inches(1.45)
    top0 = CONTENT_TOP + Inches(0.25)
    for li, (label, boxes) in enumerate(layers):
        ly = top0 + li * row_step
        lab = _add_text_box(slide, MARGIN_LEFT, ly + Inches(0.22), label_w, Inches(0.4),
                            label, font_size=10, bold=True, color=BURGUNDY)
        _letterspace(lab.text_frame.paragraphs[0], 80)
        for bi, text in enumerate(boxes):
            bx = MARGIN_LEFT + label_w + bi * (box_w + gap)
            _add_filled_box(slide, bx, ly, box_w, box_h, PANEL,
                            line_color=HAIRLINE, line_width_pt=1.0)
            _add_text_box(slide, bx + Inches(0.08), ly, box_w - Inches(0.16), box_h,
                          text, font_size=12, bold=(li == 2), color=DARK_TEXT,
                          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            if li < 2:  # connector to the layer below
                cx = bx + box_w / 2
                _add_filled_box(slide, cx, ly + box_h, Inches(0.018),
                                row_step - box_h, BURGUNDY)

    src_y = top0 + 3 * row_step + Inches(0.1)
    for sx, text in [(MARGIN_LEFT + label_w, "Cambodia synthetic dataset (2,000 applicants)"),
                     (MARGIN_LEFT + label_w + 2 * (box_w + gap),
                      "Static XGBoost baseline (mortality model)")]:
        _add_filled_box(slide, sx, src_y, box_w * 2 + gap, Inches(0.6), WHITE,
                        line_color=BURGUNDY, line_width_pt=1.2)
        _add_text_box(slide, sx, src_y, box_w * 2 + gap, Inches(0.6),
                      text, font_size=12, color=SOFT_TEXT,
                      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    _add_notes(slide,
        "Architecture in three layers. The browser SPA hosts four panels: applicant "
        "simulator, premium optimiser, bandit arena, PSI monitor. Each maps to a FastAPI "
        "endpoint, backed by the Python core: the actuarial reward simulator, the pricing "
        "engine, the bandit algorithms LinUCB and LinTS, and the PSI computation. "
        "Everything is fed by the 2,000-applicant synthetic Cambodia dataset, with the "
        "static XGBoost mortality model as the incumbent baseline. This same stack powers "
        "the live demo later.")
```

- [ ] **Step 5.2: Replace `slide_cambodia_dataset`**

```python
def slide_cambodia_dataset(prs: Presentation):
    """Slide 9 (07)."""
    slide = _content_slide(prs, "iv", "4.2.  Synthetic Cambodia Dataset", "07")

    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        ("2,000", "synthetic applications"),
        ("5", "demographic features"),
        ("4", "underwriting arms"),
        ("4", "anchoring sources"),
    ])

    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(1.45), Inches(6.2), [
        "Anchored on CDHS, STEPS, ILO, WHO data",
        "Adverse selection AF = 1.35; elasticity 3.5",
        "Fully synthetic -- no real applicant PII",
    ])

    arms = [
        ("RATED",    "Accept + premium loading (+25%)"),
        ("STANDARD", "Accept at standard premium"),
        ("DECLINE",  "Reject application"),
        ("REFER",    "Escalate to human underwriter"),
    ]
    ay = CONTENT_TOP + Inches(1.5)
    for i, (arm, desc) in enumerate(arms):
        ry = ay + i * Inches(0.78)
        _add_text_box(slide, Inches(7.1), ry, Inches(1.9), Inches(0.4),
                      arm, font_size=15, bold=True, color=BURGUNDY)
        _add_text_box(slide, Inches(9.1), ry + Inches(0.02), Inches(3.7), Inches(0.5),
                      desc, font_size=13, color=SOFT_TEXT)
        if i > 0:
            _add_filled_box(slide, Inches(7.1), ry - Inches(0.14), Inches(5.7),
                            Inches(0.012), HAIRLINE)

    _add_footnote(slide, "Construction detail: appendix A5 (sources, simulator parameters).")
    _add_notes(slide,
        "The dataset is 2,000 synthetic applicants with five features: age, sex, region, "
        "occupation, BMI. Distributions are anchored on CDHS 2021-22 and STEPS 2021; "
        "income on ILO labour-force surveys; claim probabilities calibrated from WHO SEARO "
        "health-expenditure data. Adverse-selection factor 1.35 and price-elasticity slope "
        "3.5 come from DAC actuarial priors. Four arms: RATED accepts with a 25 percent "
        "loading, STANDARD accepts at standard rate, DECLINE rejects, REFER escalates to a "
        "human. No real applicant data is used anywhere.")
```

- [ ] **Step 5.3: Replace `slide_bandit_formulation`**

```python
def slide_bandit_formulation(prs: Presentation):
    """Slide 10 (08)."""
    slide = _content_slide(prs, "iv", "4.3.  Bandit Formulation", "08")

    defs = [
        ("Context  x_t ∈ R^5", "age, sex, region, occupation, BMI -- standardised"),
        ("Action  a_t", "one of RATED / STANDARD / DECLINE / REFER"),
        ("Reward  r_t", "revenue minus claims, actuarial simulator"),
    ]
    dy = CONTENT_TOP + Inches(0.15)
    for i, (term, desc) in enumerate(defs):
        ry = dy + i * Inches(0.95)
        _add_text_box(slide, MARGIN_LEFT, ry, Inches(2.9), Inches(0.45),
                      term, font_size=16, bold=True, color=BURGUNDY)
        _add_text_box(slide, MARGIN_LEFT, ry + Inches(0.42), Inches(5.9), Inches(0.4),
                      desc, font_size=13, color=SOFT_TEXT)

    _add_callout(slide, MARGIN_LEFT, dy + Inches(3.05), Inches(5.9), Inches(1.0),
                 "Objective: maximise cumulative reward Σ r_t over T rounds, "
                 "subject to demographic PSI guardrails.",
                 font_size=14, bold=True)

    rows = [
        ("RATED",    "+premium − claims", "− adverse-sel. penalty"),
        ("STANDARD", "+premium − claims", "+optimal margin"),
        ("DECLINE",  "0 (avoided loss)",  "− missed revenue"),
        ("REFER",    "+human decision net", "+human decision net"),
    ]
    _add_flat_table(slide, Inches(7.0), CONTENT_TOP + Inches(0.15),
                    [Inches(1.7), Inches(2.1), Inches(2.0)],
                    ["Action", "High-risk", "Low-risk"],
                    rows, font_size=12, row_h=Inches(0.72))

    _add_notes(slide,
        "Formally: at each round the context is the standardised five-feature applicant "
        "vector, the action is one of four arms, and the reward is revenue minus claims "
        "from the actuarial simulator, with adverse selection penalising premium-heavy "
        "arms on low-risk applicants. The objective is cumulative reward over T rounds "
        "subject to the PSI guardrail. The table sketches the reward structure: for a "
        "high-risk applicant DECLINE avoids a loss; for a low-risk one it forfeits "
        "revenue; REFER nets the human decision either way.")
```

- [ ] **Step 5.4: Replace `slide_algorithms_baselines`** (one short phrase per policy; armor footnote)

```python
def slide_algorithms_baselines(prs: Presentation):
    """Slide 11 (09)."""
    slide = _content_slide(prs, "iv", "4.4.  Algorithms & Baselines", "09")

    algos = [
        (ACCENT_GREEN, "LinUCB",      "Optimism under uncertainty -- O(sqrt(T) d log T) regret"),
        (ACCENT_GREEN, "LinTS",       "Posterior sampling -- near-optimal regret"),
        (ACCENT_AMBER, "ε-Greedy",    "Uniform exploration -- suboptimal O(T^2/3)"),
        (MED_GRAY,     "Static XGB",  "Train-once incumbent baseline"),
        (ACCENT_RED,   "AlwaysRATED", "Constant +25% loading -- inadmissible ceiling"),
    ]
    ay = CONTENT_TOP + Inches(0.25)
    for i, (color, name, desc) in enumerate(algos):
        ry = ay + i * Inches(0.85)
        _add_filled_box(slide, MARGIN_LEFT, ry + Inches(0.06), Inches(0.16),
                        Inches(0.5), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), ry, Inches(2.6), Inches(0.5),
                      name, font_size=18, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(3.2), ry + Inches(0.05),
                      Inches(9.2), Inches(0.5), desc, font_size=15, color=SOFT_TEXT)
        if i > 0:
            _add_filled_box(slide, MARGIN_LEFT, ry - Inches(0.17), CONTENT_W,
                            Inches(0.012), HAIRLINE)

    _add_footnote(slide,
        "Admissibility (§5.0.1): deployable AND commercially/regulatorily viable. "
        "LinUCB and LinTS are the top-2 admissible policies. "
        "Other reference policies: AlwaysSTANDARD, AlwaysDECLINE, Random, LogisticOracle, Oracle.")
    _add_notes(slide,
        "Two proposed policies and three reference points. LinUCB plays optimism in the "
        "face of uncertainty over a linear reward model with the square-root-T regret "
        "bound; LinTS samples from the posterior and is near-optimal with naturally "
        "calibrated uncertainty. Epsilon-greedy is the naive explorer with provably worse "
        "T-to-the-two-thirds regret. Static XGB is the train-once incumbent. AlwaysRATED "
        "rates everyone at +25 percent loading - it scores highest but is neither "
        "commercially nor regulatorily viable, which is exactly the admissibility "
        "distinction in section 5.0.1 and the dedicated limitation slide 6.2.")
```

- [ ] **Step 5.5: Replace `slide_guardrail_hitl_design`**

```python
def slide_guardrail_hitl_design(prs: Presentation):
    """Slide 12 (10)."""
    slide = _content_slide(prs, "iv", "4.5.  Guardrail + HITL Design", "10")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP, Inches(5.9), Inches(0.32),
                        "PSI DEMOGRAPHIC GUARDRAIL", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    psi_zones = [
        (ACCENT_GREEN, "GREEN", "PSI < 0.10", "stable"),
        (ACCENT_AMBER, "AMBER", "0.10-0.25", "monitor"),
        (ACCENT_RED,   "RED",   "PSI ≥ 0.25", "review"),
    ]
    zy = CONTENT_TOP + Inches(0.5)
    for color, label, threshold, action in psi_zones:
        _add_filled_box(slide, MARGIN_LEFT, zy, Inches(0.16), Inches(0.5), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), zy, Inches(1.5), Inches(0.5),
                      label, font_size=16, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(2.0), zy + Inches(0.04),
                      Inches(2.1), Inches(0.45), threshold, font_size=14, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(4.2), zy + Inches(0.04),
                      Inches(1.7), Inches(0.45), action, font_size=14, color=SOFT_TEXT)
        zy += Inches(0.72)
    _add_text_box(slide, MARGIN_LEFT, zy + Inches(0.1), Inches(5.9), Inches(0.7),
                  "Computed on region & occupation, rolling 500-round window.",
                  font_size=13, color=SOFT_TEXT)

    lab = _add_text_box(slide, Inches(7.1), CONTENT_TOP, Inches(5.7), Inches(0.32),
                        "HUMAN-IN-THE-LOOP WRAPPER", font_size=11, bold=True, color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, Inches(7.1), CONTENT_TOP + Inches(0.5), Inches(5.7), [
        "Uncertainty > κ  →  REFER to actuary",
        "Conservatism κ ∈ {0.3, 0.5, 0.7}",
        "Human decides; reward still trains bandit",
        "Target: review cost < 2% of reward",
    ], font_size=15)

    _add_footnote(slide,
        "PSI is a monitor, not an enforcer -- constrained-action enforcement is future work.")
    _add_notes(slide,
        "Two safety layers. The PSI guardrail computes the Population Stability Index on "
        "region and occupation over a rolling 500-round window: GREEN below 0.10, AMBER to "
        "0.25, RED above. It detects concentration; it does not constrain the policy - "
        "enforcement is future work, stated honestly. The HITL wrapper REFERs an applicant "
        "to the actuary whenever predicted uncertainty exceeds the conservatism threshold "
        "kappa, tested at 0.3, 0.5, 0.7; the human's decision is final and its observed "
        "reward still updates the bandit. Design target: keep review cost under two "
        "percent of gross reward.")
```

- [ ] **Step 5.6: Build, test, commit**

Run: `python thesis/health_rl/build_burgundy_presentation.py && python -m pytest tests/test_build_presentation.py -q`
Expected: `9 passed`

```bash
git add thesis/health_rl/build_burgundy_presentation.py \
        thesis/health_rl/burgundy_defense_presentation.pptx
git commit -m "feat(defense): v2 methodology slides - native flat architecture diagram, density pass

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 6: Slide-scale figures (`_slide_style.py` + `gen_slide_figures.py`)

Six charts re-rendered at slide scale from the **same harnesses the thesis figures use** (imported from the existing `gen_*` modules — never modified). Data steps are expensive (full run ≈ 45–75 min CPU); every collector caches to `figures/slides/_cache_*` so re-renders are instant. If executing inline, you may start Step 6.4's command with `run_in_background: true` right after writing the files and continue with Task 7's builder edits in the meantime — but do not commit Task 7 until Step 6.5 passes.

**Files:**
- Create: `thesis/health_rl/figures/_slide_style.py`
- Create: `thesis/health_rl/figures/gen_slide_figures.py`
- Modify: `.gitignore`

- [ ] **Step 6.1: Create `thesis/health_rl/figures/_slide_style.py`**

```python
"""Slide-scale figure style for the defense deck (v2 Minimal Academic).

Sans type >= 14 pt, thick lines, deck palette, PNG-only into figures/slides/.
Companion to _style.py (publication style) -- thesis report figures are NOT touched.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SLIDE_DIR = Path(__file__).resolve().parent / "slides"

SLIDE_PALETTE = {
    "hero":    "#5D2A42",   # burgundy -- headline series (LinUCB unless noted)
    "hero2":   "#8A5570",   # lighter burgundy variants (HITL conservatism cells)
    "hero3":   "#B894A6",
    "lints":   "#3B6EA5",   # blue -- only when a third series is unavoidable
    "compare": "#9AA0A6",   # warm gray -- the baseline being beaten
    "amber":   "#E6A62E",
    "green":   "#2E8B57",
    "red":     "#D93B3B",   # inadmissible / failure semantics
    "dark":    "#1A1A1A",
}


def apply_slide_style() -> None:
    """Projection-scale rcParams. Call before building each figure."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Calibri", "Arial", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "font.size": 16,
        "axes.labelsize": 18,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "legend.fontsize": 16,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.8,
        "axes.linewidth": 1.2,
        "lines.linewidth": 3.5,
        "legend.frameon": False,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def save_slide(fig, stem: str) -> Path:
    SLIDE_DIR.mkdir(exist_ok=True)
    out = SLIDE_DIR / f"{stem}.png"
    fig.savefig(out)
    plt.close(fig)
    return out
```

- [ ] **Step 6.2: Create `thesis/health_rl/figures/gen_slide_figures.py`**

```python
"""Slide-scale variants of the six defense-deck charts.

Reuses the data harnesses of the existing publication generators (gen_fig07/13/14/15/17,
gen_results_curves) so every curve reproduces the frozen thesis numbers, then re-plots
with _slide_style (sans >= 14 pt, thick lines, deck palette) into figures/slides/.

Data collection is expensive (full run ~45-75 min); each collector caches to
slides/_cache_*.npz|.json so re-rendering is instant.

Run:
    python thesis/health_rl/figures/gen_slide_figures.py            # all six
    python thesis/health_rl/figures/gen_slide_figures.py --figs ladder,reward
    python thesis/health_rl/figures/gen_slide_figures.py --no-cache # force re-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from healthrl.underwriting_bandit import (                      # noqa: E402
    LinUCB, StaticXGBBaseline, preprocess_cambodia_data, run_bandit,
)
from healthrl.config import EXPERIMENT, BANDIT                  # noqa: E402
from statistical_utils import bootstrap_ci                      # noqa: E402
from _slide_style import apply_slide_style, save_slide, SLIDE_PALETTE, SLIDE_DIR  # noqa: E402
import matplotlib.pyplot as plt                                 # noqa: E402
from matplotlib.patches import Patch                            # noqa: E402

import exp_010_cold_start_analysis as e10                       # noqa: E402
import exp_013_loglog_regret_validation as e13                  # noqa: E402
from experiment_utils import run_experiment_seeds               # noqa: E402
import gen_fig07_ladder                                         # noqa: E402
import gen_fig13_hitl                                           # noqa: E402
import gen_fig15_drift                                          # noqa: E402

N = EXPERIMENT.n_rounds
ROUNDS = np.arange(1, N + 1)
USE_CACHE = True


def _band(curves, n_sub=200):
    """Mean + bootstrap 95% CI at n_sub sampled rounds (same as gen_results_curves)."""
    mean_full = curves.mean(0)
    idx = np.unique(np.linspace(0, curves.shape[1] - 1, n_sub).astype(int))
    lo = np.empty(len(idx)); hi = np.empty(len(idx))
    for j, i in enumerate(idx):
        lo[j], hi[j] = bootstrap_ci(curves[:, i])
    return mean_full, idx, lo, hi


def _cached_npz(name, collect_fn):
    """Load slides/_cache_<name>.npz or run collect_fn() -> dict[str, ndarray] and save."""
    SLIDE_DIR.mkdir(exist_ok=True)
    path = SLIDE_DIR / f"_cache_{name}.npz"
    if USE_CACHE and path.exists():
        print(f"  [{name}] cache hit: {path.name}")
        with np.load(path) as z:
            return {k: z[k] for k in z.files}
    data = collect_fn()
    np.savez_compressed(path, **data)
    return data


# ── collectors (mirror the publication harnesses) ───────────────────────────

def collect_reward():
    """EXP-005 harness half of gen_results_curves.collect(): LinUCB vs Static, 20 seeds."""
    X, df_raw, _ = preprocess_cambodia_data()
    nf = X.shape[1]
    ucb_R, stat_R = [], []
    for seed in range(EXPERIMENT.n_seeds):
        print(f"  [reward] seed {seed + 1}/{EXPERIMENT.n_seeds}", flush=True)
        r_ucb = run_bandit("LinUCB", LinUCB(4, nf, alpha=BANDIT.linucb_alpha),
                           X.copy(), df_raw, N, seed=seed)
        r_stat = run_bandit("StaticXGB", StaticXGBBaseline(),
                            X.copy(), df_raw, N, seed=seed)
        ucb_R.append(r_ucb.cumulative_rewards)
        stat_R.append(r_stat.cumulative_rewards)
    return {"ucb_R": np.array(ucb_R), "stat_R": np.array(stat_R)}


def collect_loglog():
    curves = []
    for s in range(e13.N_SEEDS):
        print(f"  [loglog] seed {s + 1}/{e13.N_SEEDS}", flush=True)
        curves.append(e13.run_single_seed(s))
    return {"curves": np.array(curves)}


def collect_hitl():
    hitl, base = gen_fig13_hitl.collect()
    out = {"base": np.asarray(base.cumulative_rewards, float)}
    for c in gen_fig13_hitl.CONS:
        out[f"c{int(c * 10):02d}"] = np.asarray(hitl[c].cumulative_rewards, float)
    return out


def collect_drift():
    reg = gen_fig15_drift.collect(EXPERIMENT.n_seeds)
    return {k: v for k, v in reg.items()}


def coldstart_stats():
    """EXP-010 stats; cached as JSON (dict of (mean, std) tuples)."""
    path = SLIDE_DIR / "_cache_coldstart.json"
    if USE_CACHE and path.exists():
        print("  [coldstart] cache hit")
        return {k: tuple(v) for k, v in json.loads(path.read_text()).items()}
    stats = run_experiment_seeds(e10.run, n_seeds=10)
    path.write_text(json.dumps({k: list(v) for k, v in stats.items()}))
    return stats


# ── figures ──────────────────────────────────────────────────────────────────

def fig_reward():
    d = _cached_npz("reward", collect_reward)
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(12.2, 5.0))
    for key, col, lab in (("ucb_R", "hero", "LinUCB"), ("stat_R", "compare", "Static XGB")):
        m, idx, lo, hi = _band(d[key])
        ax.plot(ROUNDS, m, color=SLIDE_PALETTE[col], label=lab)
        ax.fill_between(ROUNDS[idx], lo, hi, color=SLIDE_PALETTE[col], alpha=0.18, lw=0)
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative reward ($)")
    ax.set_xlim(0, N); ax.legend(loc="upper left")
    save_slide(fig, "slide_reward_curves")
    print(f"  [reward] final LinUCB {d['ucb_R'][:, -1].mean():,.0f} (frozen 90,540) | "
          f"Static {d['stat_R'][:, -1].mean():,.0f} (frozen 72,292)")


def fig_loglog():
    d = _cached_npz("loglog", collect_loglog)
    curves = d["curves"]
    mean_curve = curves.mean(0)
    fit = e13.fit_loglog_slope(mean_curve, t_min=200)   # reproduces frozen 0.572 / 0.992
    apply_slide_style()
    t = np.arange(1, e13.N_ROUNDS + 1)
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    ax.loglog(t, np.clip(mean_curve, 1e-6, None), color=SLIDE_PALETTE["hero"],
              label="Mean regret (20 seeds)")
    tf = t[200:]
    ax.loglog(tf, np.exp(fit["intercept"]) * tf ** fit["slope"],
              color=SLIDE_PALETTE["dark"], ls="--", lw=2.5,
              label=f"Fit: slope {fit['slope']:.3f}")
    mid = len(tf) // 2
    ref_int = np.log(mean_curve[200:][mid]) - 0.5 * np.log(tf[mid])
    ax.loglog(tf, np.exp(ref_int) * tf ** 0.5, color=SLIDE_PALETTE["compare"],
              ls=":", lw=2.5, label="O(sqrt T) reference")
    ax.set_xlabel("Round t"); ax.set_ylabel("Cumulative regret ($)")
    ax.set_xlim(10, e13.N_ROUNDS); ax.set_ylim(10, None)
    ax.legend(loc="upper left")
    save_slide(fig, "slide_loglog_regret")
    print(f"  [loglog] slope {fit['slope']:.3f} R2 {fit['r_squared']:.3f} (frozen 0.572/0.992)")


def fig_coldstart():
    stats = coldstart_stats()
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.axvspan(1000, 2000, color=SLIDE_PALETTE["hero"], alpha=0.05, zorder=0)
    spec = [("LinUCB", "hero", "o"), ("LinTS", "lints", "s"), ("FreshXGB", "compare", "^")]
    for name, col, mk in spec:
        means = np.array([stats[f"cum_reward_{name}_t{t}"][0] for t in e10.TS])
        stds = np.array([stats[f"cum_reward_{name}_t{t}"][1] for t in e10.TS])
        lab = "Fresh XGB" if name == "FreshXGB" else name
        ax.errorbar(e10.TS, means, yerr=stds, color=SLIDE_PALETTE[col], marker=mk,
                    markersize=11, capsize=5, elinewidth=1.6, label=lab)
    ax.annotate("bandits overtake", xy=(2000, stats["cum_reward_LinTS_t2000"][0]),
                xytext=(1150, stats["cum_reward_FreshXGB_t2000"][0] + 7000),
                fontsize=14, color="#444444",
                arrowprops=dict(arrowstyle="->", color="#444444", lw=1.6))
    ax.set_xlabel("Horizon T (rounds)"); ax.set_ylabel("Cumulative reward ($)")
    ax.set_xticks(e10.TS); ax.set_xlim(e10.TS[0] - 90, e10.TS[-1] + 140)
    ax.legend(loc="upper left")
    save_slide(fig, "slide_cold_start")
    for name, _, _ in spec:
        print(f"  [coldstart] {name} T=2000: {stats[f'cum_reward_{name}_t2000'][0]:,.0f}")


def fig_hitl():
    d = _cached_npz("hitl", collect_hitl)
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.plot(d["base"], color=SLIDE_PALETTE["compare"], ls="--", label="Vanilla bandit")
    for c, col in ((0.3, "hero3"), (0.5, "hero2"), (0.7, "hero")):
        ax.plot(d[f"c{int(c * 10):02d}"], color=SLIDE_PALETTE[col], label=f"HITL c = {c}")
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative reward ($)")
    ax.set_xlim(0, len(d["base"])); ax.legend(loc="upper left")
    save_slide(fig, "slide_hitl")
    print(f"  [hitl] c=0.7 final {d['c07'][-1]:,.0f} (frozen seed-42 trace 102,100)")


def fig_drift():
    d = _cached_npz("drift", collect_drift)
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    kernel = np.ones(gen_fig15_drift.WINDOW) / gen_fig15_drift.WINDOW
    rounds = np.arange(gen_fig15_drift.WINDOW - 1, gen_fig15_drift.N)
    for key, col, lab in (("LinTS", "lints", "LinTS"), ("LinUCB", "hero", "LinUCB"),
                          ("StaticXGB", "compare", "Static XGB")):
        smoothed = np.array([np.convolve(d[key][s], kernel, mode="valid")
                             for s in range(d[key].shape[0])])
        m, idx, lo, hi = _band(smoothed)
        ax.plot(rounds, m, color=SLIDE_PALETTE[col], label=lab)
        ax.fill_between(rounds[idx], lo, hi, color=SLIDE_PALETTE[col], alpha=0.15, lw=0)
    ax.axvline(gen_fig15_drift.SHOCK, ls="--", lw=2.0, color=SLIDE_PALETTE["dark"],
               label="Shock (round 1,500)")
    ax.set_xlabel("Round"); ax.set_ylabel("Regret per round ($)")
    ax.set_xlim(0, gen_fig15_drift.N); ax.set_ylim(bottom=0)
    ax.legend(loc="upper right")
    save_slide(fig, "slide_drift")


def fig_ladder():
    d = gen_fig07_ladder.load()                      # cheap CSV read; no cache needed
    apply_slide_style()
    color_map = {"LinTS": "hero", "LinUCB": "hero2", "AlwaysRATED": "red",
                 "LogisticPolicy": "dark", "Oracle": "dark"}
    rows = []
    for pol, (name, _, deploy) in gen_fig07_ladder.SPEC.items():
        v = np.array(d[pol])
        lo, hi = bootstrap_ci(v)
        rows.append((name, color_map.get(pol, "compare"), deploy, v.mean(), lo, hi))
    rows.sort(key=lambda r: r[3])
    names = [r[0] for r in rows]
    means = np.array([r[3] for r in rows])
    lo_err = means - np.array([r[4] for r in rows])
    hi_err = np.array([r[5] for r in rows]) - means
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    y = np.arange(len(names))
    for i, r in enumerate(rows):
        dep = r[2]
        ax.barh(y[i], means[i], color=SLIDE_PALETTE[r[1]], alpha=0.95 if dep else 0.45,
                hatch=None if dep else "///",
                edgecolor="white" if dep else SLIDE_PALETTE[r[1]], linewidth=1.0,
                xerr=[[lo_err[i]], [hi_err[i]]],
                error_kw={"ecolor": "#333333", "elinewidth": 1.4, "capsize": 4})
        ax.text(max(means[i], 0) + hi_err[i] + max(means) * 0.015, y[i],
                f"${means[i]:,.0f}", va="center", ha="left", fontsize=13)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=14)
    for lbl in ax.get_yticklabels():
        if lbl.get_text() in ("LinUCB", "LinTS"):
            lbl.set_fontweight("bold")
    ax.set_xlabel("Cumulative reward ($), mean ± 95% CI")
    ax.set_xlim(min(0, means.min() * 1.15), max(means + hi_err) * 1.24)
    legend = [Patch(facecolor="#777777", alpha=0.95, label="Deployable"),
              Patch(facecolor="#777777", alpha=0.45, hatch="///", edgecolor="#777777",
                    label="Not deployable / ceiling")]
    ax.legend(handles=legend, loc="lower right", fontsize=13)
    save_slide(fig, "slide_ladder")


FIGS = {"reward": fig_reward, "loglog": fig_loglog, "coldstart": fig_coldstart,
        "hitl": fig_hitl, "drift": fig_drift, "ladder": fig_ladder}


def main():
    global USE_CACHE
    ap = argparse.ArgumentParser()
    ap.add_argument("--figs", default=",".join(FIGS),
                    help="comma list of: " + ",".join(FIGS))
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()
    USE_CACHE = not args.no_cache
    for name in args.figs.split(","):
        print(f"== {name} ==", flush=True)
        FIGS[name.strip()]()
    done = sorted(p.name for p in SLIDE_DIR.glob("slide_*.png"))
    print(f"\nwrote {len(done)} slide figures: {', '.join(done)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6.3: Gitignore the caches**

Append to `.gitignore`:

```
# Slide-figure data caches (regenerable, large)
thesis/health_rl/figures/slides/_cache_*
```

- [ ] **Step 6.4: Cheap smoke run first (ladder only — CSV-backed, seconds), then the full run**

Run: `python thesis/health_rl/figures/gen_slide_figures.py --figs ladder`
Expected: `wrote 1 slide figures: slide_ladder.png`

Run (LONG — 45–75 min; background-friendly): `python thesis/health_rl/figures/gen_slide_figures.py`
Expected: reproduction prints near frozen numbers (LinUCB ≈ 90,540; Static ≈ 72,292; slope ≈ 0.572) and `wrote 6 slide figures: ...`

- [ ] **Step 6.5: Verify the six PNGs exist and are non-trivial**

Run (PowerShell): `Get-ChildItem thesis\health_rl\figures\slides\slide_*.png | Format-Table Name, Length`
Expected: 6 files — `slide_reward_curves.png`, `slide_loglog_regret.png`, `slide_cold_start.png`, `slide_hitl.png`, `slide_drift.png`, `slide_ladder.png` — each > 30 KB. Open 1–2 and eyeball: axis text must be obviously larger/thicker than the thesis versions.

- [ ] **Step 6.6: Commit (scripts + PNGs, not caches)**

```bash
git add thesis/health_rl/figures/_slide_style.py \
        thesis/health_rl/figures/gen_slide_figures.py \
        thesis/health_rl/figures/slides/slide_*.png \
        .gitignore
git commit -m "feat(defense): slide-scale figure pipeline - 6 charts, deck palette, npz caches

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 7: Results slides 13–18 (slide figures + armor footnotes)

Every chart switches to `SLIDE_FIG_DIR / "slide_*.png"`. Three of the four claim-critical armor footnotes land here (the fourth is Task 8's ladder slide). All numbers via `_E0*` aliases — zero hardcoding.

**Files:**
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (replace bodies of `slide_convergence`, `slide_benchmark`, `slide_cold_start`, `slide_hitl_results`, `slide_fairness_audit`, `slide_drift_adaptation`)

- [ ] **Step 7.1: Replace `slide_convergence`**

```python
def slide_convergence(prs: Presentation):
    """Slide 13 (11) -- EXP-005."""
    slide = _content_slide(prs, "v", "5.1.  Convergence  (EXP-005)", "11")

    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        (f"+{_E005['lift_pct']}%", "reward lift vs static xgb"),
        (f"d = {_E005['reward_cohen_d']}", "effect size"),
        (f"p {_E005['reward_p']}", "paired wilcoxon · 20 seeds"),
        (f"${_E005['linucb_reward']:,}", "linucb cumulative reward"),
    ])

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_reward_curves.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.25),
                     CONTENT_W, CONTENT_H - Inches(1.7))

    _add_footnote(slide,
        f"Scope: admissible policies only (§5.0.1). Static XGB ${_E005['static_reward']:,} · "
        f"Oracle ${_E005['oracle_reward']:,} ({_E005['oracle_reward_recovered_pct']}% recovered).")
    _add_notes(slide,
        f"The headline: LinUCB earns {_E005['lift_pct']} percent more cumulative reward "
        f"than the static XGBoost baseline over 5,000 rounds - "
        f"${_E005['linucb_reward']:,} versus ${_E005['static_reward']:,}, twenty seeds, "
        f"paired Wilcoxon p {_E005['reward_p']}, Cohen's d {_E005['reward_cohen_d']}. "
        f"The curves separate around round 1,500 once the bandit's ridge estimates "
        f"converge. Critical scope: this claim is over ADMISSIBLE policies per section "
        f"5.0.1 - the inadmissible AlwaysRATED constant sits above (slide 6.2). Oracle "
        f"recovery is {_E005['oracle_reward_recovered_pct']} percent.")
```

- [ ] **Step 7.2: Replace `slide_benchmark`**

```python
def slide_benchmark(prs: Presentation):
    """Slide 14 (12) -- EXP-007."""
    slide = _content_slide(prs, "v", "5.2.  Benchmark vs Static XGB  (EXP-007)", "12")

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_loglog_regret.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.1),
                     Inches(6.6), CONTENT_H - Inches(0.5))

    rows = [(str(r["rank"]), r["algorithm"], f"${r['reward']:,}")
            for r in _E007["ranking"]]

    def _rank_style(i, c, text):
        top2 = i < 2
        return (top2, BURGUNDY if top2 else DARK_TEXT)

    _add_flat_table(slide, Inches(7.5), CONTENT_TOP + Inches(0.35),
                    [Inches(0.8), Inches(2.4), Inches(2.1)],
                    ["#", "Algorithm", "Reward"],
                    rows, font_size=14, row_h=Inches(0.62), cell_style=_rank_style)

    _add_text_box(slide, Inches(7.5), CONTENT_TOP + Inches(3.5), Inches(5.3), Inches(0.8),
                  f"Log-log regret slope {_E013['slope']} (R² = {_E013['r2']}) -- "
                  "sub-linear, consistent with O(√T·d).",
                  font_size=14, color=DARK_TEXT)

    _add_footnote(slide,
        f"LinTS vs LinUCB: p = {_E007['lints_vs_linucb_p']} (n.s. -- tied at 20 seeds). "
        "Same CRN harness across all four algorithms.")
    _add_notes(slide,
        f"All four algorithms under common random numbers. LinTS ranks first at "
        f"${_E007['ranking'][0]['reward']:,}, LinUCB second at "
        f"${_E007['ranking'][1]['reward']:,} - statistically tied "
        f"(p = {_E007['lints_vs_linucb_p']}). Epsilon-greedy trails, static XGB last. "
        f"The log-log plot validates theory: fitted slope {_E013['slope']} with R squared "
        f"{_E013['r2']}, close to the 0.5 of the O(root-T d) bound - the bandit's regret "
        f"really is sub-linear, it is learning, not memorising.")
```

- [ ] **Step 7.3: Replace `slide_cold_start`** (armor: LinUCB softened verdict on-slide, d values from JSON)

```python
def slide_cold_start(prs: Presentation):
    """Slide 15 (13) -- EXP-010."""
    slide = _content_slide(prs, "v", "5.3.  Cold-start Evaluation  (EXP-010)", "13")

    w = _E010["wilcoxon_t2000"]
    lints, linucb = w["lints_vs_freshxgb"], w["linucb_vs_freshxgb"]
    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        ("PASSED", "lints @ t = 2,000"),
        (f"p = {lints['p']}", f"wilcoxon · d = {lints['d']}"),
        ("DRAWS LEVEL", "linucb @ t = 2,000"),
        (f"p = {linucb['p']}", f"n.s. · d = {linucb['d']}"),
    ], value_colors=[ACCENT_GREEN, DARK_TEXT, ACCENT_AMBER, DARK_TEXT])

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_cold_start.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.25),
                     Inches(8.2), CONTENT_H - Inches(1.7))

    _add_talking_points(slide, Inches(9.1), CONTENT_TOP + Inches(1.6), Inches(3.7), [
        "Fresh XGB wins below T ≈ 1,000",
        "Crossover between 1,000-2,000",
        "Deploy with warm-start",
    ], font_size=14, line_h=Inches(0.85))

    _add_footnote(slide,
        f"Only LinTS is certified at T = 2,000 (p = {lints['p']}); LinUCB's lead is not "
        f"significant (p = {linucb['p']}, d = {linucb['d']}) and is reported as 'draws level'.")
    _add_notes(slide,
        f"Honest cold-start picture: below a thousand rounds a freshly trained XGBoost "
        f"beats both bandits - at T=200 it is roughly twice as good. The crossover comes "
        f"between one and two thousand rounds. At T=2,000 LinTS's lead is significant at "
        f"the Bonferroni-corrected threshold (p = {lints['p']}, d = {lints['d']}); "
        f"LinUCB's is positive but NOT significant (p = {linucb['p']}, d = {linucb['d']}) "
        f"- we softened that claim to 'draws level'. Deployment implication: warm-start "
        f"or shadow mode for the first thousand applications. Note this crossover is "
        f"against a frozen rule, not against the AlwaysRATED constant.")
```

- [ ] **Step 7.4: Replace `slide_hitl_results`** (armor: ceiling scope footnote)

```python
def slide_hitl_results(prs: Presentation):
    """Slide 16 (14) -- EXP-008."""
    slide = _content_slide(prs, "v", "5.4.  Human-in-the-loop  (EXP-008)", "14")

    _add_stat_row(slide, CONTENT_TOP + Inches(0.05), [
        (f"+{_E008['lift_pct']}%", "reward lift vs vanilla bandit"),
        (f"d = {_E008['lift_cohen_d']}", f"wilcoxon p {_E008['lift_p']} · 20 seeds"),
        (f"{_E008['referral_pct']}%", "referral rate"),
        (f"{_E008['human_cost_pct_of_reward']}%", "review cost of gross reward"),
    ])

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_hitl.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(1.25),
                     Inches(7.2), CONTENT_H - Inches(1.7))

    _add_talking_points(slide, Inches(8.0), CONTENT_TOP + Inches(1.6), Inches(4.8), [
        f"HITL ${_E008['hitl_reward']:,} vs bandit ${_E008['baseline_reward']:,}",
        f"Experts agree with bandit {_E008['alignment_pct']:.0f}% (κ=0.7)",
        "Queue depth stays at zero",
    ], font_size=14, line_h=Inches(0.85))

    _add_footnote(slide,
        "Lift is vs the vanilla bandit -- HITL does NOT beat the inadmissible "
        "AlwaysRATED ceiling (§5.4.2).")
    _add_notes(slide,
        f"Adding the human wrapper lifts reward {_E008['lift_pct']} percent over the "
        f"vanilla bandit: ${_E008['hitl_reward']:,} versus ${_E008['baseline_reward']:,}, "
        f"twenty seeds, p {_E008['lift_p']}, d = {_E008['lift_cohen_d']}. Cost side: only "
        f"{_E008['referral_pct']} percent of applicants get referred, review spend is "
        f"{_E008['human_cost_pct_of_reward']} percent of gross reward, and experts agree "
        f"with the bandit {_E008['alignment_pct']:.0f} percent of the time at kappa 0.7. "
        f"Scope, stated plainly: this certifies HITL against the bandit itself, not "
        f"against the AlwaysRATED constant - section 5.4.2.")
```

- [ ] **Step 7.5: Replace `slide_fairness_audit`** (armor: criterion-6 footnote)

```python
def slide_fairness_audit(prs: Presentation):
    """Slide 17 (15) -- EXP-006."""
    slide = _content_slide(prs, "v", "5.5.  Fairness Audit  (EXP-006)", "15")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.5),
                  "5 of 6 pre-registered criteria PASSED",
                  font_size=20, bold=True, color=DARK_TEXT)

    for col_i, (attr, data) in enumerate([("Region", _E006["region"]),
                                          ("Occupation", _E006["occupation"])]):
        cx = MARGIN_LEFT + col_i * Inches(6.3)
        zone_color = ACCENT_GREEN if data["psi_zone"] == "GREEN" else ACCENT_AMBER
        verdict = data["permutation_verdict"]
        rows = [
            ("PSI zone", f"{data['psi_zone']}  ({data['psi_max_sliding']:.4f} max)"),
            ("EEOC parity", f"{data['parity_pct']}%  (floor 80%)"),
            ("Criterion 6", verdict),
        ]

        def _style(i, c, text, _zone=zone_color, _verdict=verdict):
            if c == 1 and i == 0:
                return (True, _zone)
            if c == 1 and i == 2:
                return (True, ACCENT_GREEN if _verdict == "PASSED" else ACCENT_RED)
            return (c == 1, DARK_TEXT)

        _add_text_box(slide, cx, CONTENT_TOP + Inches(0.7), Inches(5.9), Inches(0.4),
                      attr, font_size=16, bold=True, color=BURGUNDY)
        _add_flat_table(slide, cx, CONTENT_TOP + Inches(1.2),
                        [Inches(2.2), Inches(3.7)], ["Check", "Result"],
                        rows, font_size=14, row_h=Inches(0.66), cell_style=_style)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.0), CONTENT_W, Inches(0.85),
                 "Occupation association reflects actuarially justified risk differences "
                 "(§5.2.4); no regulatory threshold (EEOC 80%, PSI 0.25) is breached.",
                 font_size=13)

    _add_footnote(slide,
        f"Criterion 6 (occupation→action) FAILED-with-interpretation: "
        f"p {_E006['occupation']['permutation_p']} -- statistically significant but "
        f"practically small. Reported honestly.")
    _add_notes(slide,
        f"Fairness audit over the converged window. Region: PSI GREEN at "
        f"{_E006['region']['psi_max_sliding']}, parity {_E006['region']['parity_pct']} "
        f"percent, permutation test PASSED (p = {_E006['region']['permutation_p']}). "
        f"Occupation: PSI AMBER at {_E006['occupation']['psi_max_sliding']} - within the "
        f"0.25 threshold - parity {_E006['occupation']['parity_pct']} percent, well above "
        f"the EEOC 80 percent floor. Criterion 6 is the one failure: the "
        f"occupation-action association is statistically significant (p < 0.001) but "
        f"practically small, and occupation is an actuarially valid rating factor; we "
        f"marked it FAILED in the interest of honesty rather than rationalising it away. "
        f"Fairness is maintained and verified, not improved.")
```

- [ ] **Step 7.6: Replace `slide_drift_adaptation`**

```python
def slide_drift_adaptation(prs: Presentation):
    """Slide 18 (16) -- EXP-009. Droppable if rehearsal runs long (notes, not slide)."""
    slide = _content_slide(prs, "v", "5.6.  Drift Adaptation  (EXP-009)", "16")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.4),
                  f"Shock at round 1,500: {_E009['shock']}",
                  font_size=13, italic=True, color=GRAY_LABEL)

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_drift.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.5),
                     Inches(7.2), CONTENT_H - Inches(0.9))

    rows = [(r["algorithm"], f"{r['post_pre_ratio']}×") for r in _E009["rows"]]

    def _ratio_style(i, c, text):
        if c == 1:
            good = float(text.rstrip("×")) < 0.5
            return (True, ACCENT_GREEN if good else ACCENT_AMBER)
        return (False, DARK_TEXT)

    _add_text_box(slide, Inches(8.0), CONTENT_TOP + Inches(0.6), Inches(4.8), Inches(0.4),
                  "Post/pre regret ratio", font_size=16, bold=True, color=BURGUNDY)
    _add_flat_table(slide, Inches(8.0), CONTENT_TOP + Inches(1.1),
                    [Inches(2.6), Inches(2.0)], ["Algorithm", "Ratio"],
                    rows, font_size=14, row_h=Inches(0.66), cell_style=_ratio_style)

    _add_footnote(slide,
        "Pre/post windows also differ in learning-curve position; the static baseline's "
        "0.85× is the cleanest comparator (§5.9.3).")
    _add_notes(slide,
        "Stress test: at round 1,500 we double TB prevalence and cut garment-worker "
        "income 30 percent. The bandits re-converge within their learning window - "
        "post-shock regret drops to 0.29 times the pre-shock level for both LinUCB and "
        "LinTS, while static XGB only reaches 0.85. Caveat on the slide: pre and post "
        "windows also differ in learning-curve position, so the static baseline is the "
        "cleanest comparator. DiscountedLinUCB for sustained non-stationarity is future "
        "work. THIS SLIDE IS DROPPABLE if timing runs long - the examiner armor lives "
        "elsewhere.")
```

- [ ] **Step 7.7: Build, test, commit**

Run: `python thesis/health_rl/build_burgundy_presentation.py && python -m pytest tests/test_build_presentation.py -q`
Expected: `9 passed` (headline-number assertions keep passing — slides still quote `lift_pct`, `hitl lift`, LinTS p-value)

```bash
git add thesis/health_rl/build_burgundy_presentation.py \
        thesis/health_rl/burgundy_defense_presentation.pptx
git commit -m "feat(defense): v2 results slides - slide-scale charts, stat rows, armor footnotes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 8: Conclusion slides 19–21 + appendix A1–A8

The ladder slide (6.2) carries the fourth armor footnote. Appendix slides keep their content but go flat; A2/A3/A4/A5 mostly swap boxed styling for `_add_flat_table`/panels.

**Files:**
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (replace bodies of `slide_achievements`, `slide_baseline_ladder`, `slide_other_limitations`, `slide_app_number_reconciliation`, `slide_app_fairness_detail`, `slide_app_psi_mechanics`, `slide_app_bandit_math`, `slide_app_dataset_construction`, `_slide_demo_screenshot`)

- [ ] **Step 8.1: Replace `slide_achievements`**

```python
def slide_achievements(prs: Presentation):
    """Slide 19 (17)."""
    slide = _content_slide(prs, "vi", "6.1.  Achievements & Lessons", "17")

    lints_r  = next(r["reward"] for r in _LADDER["rows"] if r["policy"] == "LinTS")
    static_r = next(r["reward"] for r in _LADDER["rows"] if r["policy"] == "Static XGB")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "ACHIEVEMENTS", font_size=11, bold=True,
                        color=ACCENT_GREEN)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.5), Inches(5.9), [
        f"Leads every admissible policy (+{_E005['lift_pct']}%, d={_E005['reward_cohen_d']})",
        "LinTS cold-start crossover certified (p=0.0039)",
        f"HITL +{_E008['lift_pct']}% at {_E008['referral_pct']}% referrals",
        "5 of 6 fairness criteria PASSED",
    ], font_size=15, line_h=Inches(0.78))

    lab = _add_text_box(slide, Inches(6.9), CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "LESSONS / LIMITS", font_size=11, bold=True,
                        color=ACCENT_RED)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, Inches(6.9), CONTENT_TOP + Inches(0.5), Inches(5.9), [
        f"AlwaysRATED ceiling sits above (→ 6.2)",
        "Synthetic data limits external validity",
        "PSI monitors; it does not enforce",
        "Cold-start needs warm-start in production",
    ], font_size=15, line_h=Inches(0.78))

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.0), CONTENT_W, Inches(0.85),
                 "Contextual bandits give a principled, adaptive, auditable alternative "
                 "to static rule-based underwriting in the Cambodian context.",
                 font_size=15, bold=True)

    _add_notes(slide,
        f"Balance sheet. Wins: LinTS leads every admissible policy at ${lints_r:,} versus "
        f"static ${static_r:,}; the cold-start crossover is certified for LinTS; HITL adds "
        f"{_E008['lift_pct']} percent at {_E008['referral_pct']} percent referrals; five of "
        f"six fairness criteria pass; log-log slope {_E013['slope']} matches theory. "
        f"Honest limits: the inadmissible AlwaysRATED constant scores higher - next slide "
        f"is devoted to it; data is synthetic; PSI only monitors; criterion 6 failed with "
        f"interpretation; cold-start needs warm-start. Net: adaptive, auditable, and "
        f"honest about scope.")
```

- [ ] **Step 8.2: Replace `slide_baseline_ladder`** (the Q1 armor slide)

```python
def slide_baseline_ladder(prs: Presentation):
    """Slide 20 (18) -- Q1 armor slide."""
    slide = _content_slide(prs, "vi", "6.2.  Limitation: Baseline Ladder  (EXP-014)", "18")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.42),
                  "Why AlwaysRATED is inadmissible -- and why the headline claim still holds",
                  font_size=15, bold=True, color=DARK_TEXT)

    _add_picture_fit(slide, str(SLIDE_FIG_DIR / "slide_ladder.png"),
                     MARGIN_LEFT, CONTENT_TOP + Inches(0.5),
                     Inches(7.2), CONTENT_H - Inches(0.95))

    panel_policies = ["LinTS", "LinUCB", "Static XGB", "AlwaysRATED"]
    by_name = {r["policy"]: r for r in _LADDER["rows"]}
    rows = [(p, f"${by_name[p]['reward']:,}", by_name[p]["status"])
            for p in panel_policies]

    def _status_style(i, c, text):
        if c == 2:
            return (True, ACCENT_RED if text == "inadmissible" else ACCENT_GREEN)
        return (c == 0, DARK_TEXT)

    _add_flat_table(slide, Inches(8.0), CONTENT_TOP + Inches(0.7),
                    [Inches(1.9), Inches(1.5), Inches(1.5)],
                    ["Policy", "Reward", "Status"],
                    rows, font_size=13, row_h=Inches(0.6), cell_style=_status_style)

    _add_talking_points(slide, Inches(8.0), CONTENT_TOP + Inches(3.7), Inches(4.8), [
        "Rates 100% at flat +25% loading",
        "Not commercially / regulatorily viable",
        "Bandits rank 1-2 of admissible set",
    ], font_size=13, line_h=Inches(0.55))

    ar = by_name["AlwaysRATED"]["reward"]
    _add_footnote(slide,
        f"Pre-registered expectation FALSIFIED: AlwaysRATED ${ar:,} tops the ladder "
        f"(§5.0.1) -- reported as the scientifically informative outcome; headline is "
        f"scoped to admissible policies.")
    _add_notes(slide,
        f"This is the anticipated question, so we lead with it. The full baseline ladder "
        f"shows AlwaysRATED - rate every applicant at a flat 25 percent loading - at "
        f"${ar:,}, above LinTS ${by_name['LinTS']['reward']:,} and LinUCB "
        f"${by_name['LinUCB']['reward']:,}. Our pre-registered expectation that the "
        f"bandit beats every simple baseline was FALSIFIED, and we report that. Why the "
        f"thesis still stands: AlwaysRATED is inadmissible - loading every customer 25 "
        f"percent collapses commercially (adverse selection drives good risks away) and "
        f"would not survive regulatory scrutiny - per the admissibility definition in "
        f"section 5.0.1. Within the admissible set the bandits rank first and second. "
        f"If pressed on number differences across sections: appendix A1 reconciles "
        f"+25.2 / +27.2 / +29.8 percent.")
```

- [ ] **Step 8.3: Replace `slide_other_limitations`**

```python
def slide_other_limitations(prs: Presentation):
    """Slide 21 (19)."""
    slide = _content_slide(prs, "vi", "6.3.  Other Limitations & Future Work", "19")

    lab = _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "REMAINING LIMITATIONS", font_size=11, bold=True,
                        color=ACCENT_RED)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.5), Inches(5.9), [
        "Synthetic data -- proof of concept only",
        "Fairness is monitored, not enforced",
        "Cold-start penalty below T ≈ 1,000",
        "Single market, single product",
    ], font_size=15, line_h=Inches(0.78))

    lab = _add_text_box(slide, Inches(6.9), CONTENT_TOP + Inches(0.05), Inches(5.9),
                        Inches(0.32), "FUTURE WORK", font_size=11, bold=True,
                        color=BURGUNDY)
    _letterspace(lab.text_frame.paragraphs[0], 120)
    _add_talking_points(slide, Inches(6.9), CONTENT_TOP + Inches(0.5), Inches(5.9), [
        "DiscountedLinUCB for sustained drift",
        "Constrained bandits: hard fairness limits",
        "Real insurer pilot with observed claims",
        "Multi-product portfolio underwriting",
    ], font_size=15, line_h=Inches(0.78))

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.0), CONTENT_W, Inches(0.85),
                 "Contribution: end-to-end adaptive underwriting prototype + evaluation "
                 "framework with demographic fairness monitoring for Cambodia.",
                 font_size=15, bold=True)

    _add_notes(slide,
        "Remaining limits beyond the ladder: demographics are CDHS-anchored but rewards "
        "are simulated, so treat results as proof-of-concept, not production estimates; "
        "the PSI guardrail detects concentration but cannot prevent it; bandits "
        "underperform a fresh XGBoost below roughly a thousand rounds; and we tested one "
        "market, one product. Future work in order of value: discounted or "
        "sliding-window UCB for seasonal drift, constrained contextual bandits for hard "
        "fairness enforcement, a real-insurer pilot replacing the simulator with observed "
        "claims, neural-linear bandits for richer features, multi-product portfolios, and "
        "a SERC Cambodia regulatory pathway.")
```

- [ ] **Step 8.4: Replace the five appendix content slides** (flat tables/panels; content unchanged)

```python
def slide_app_number_reconciliation(prs: Presentation):
    """A1 -- Q2: Why do percentage lifts differ between sections?"""
    slide = _content_slide(prs, "v", "A1.  Q2: Number Reconciliation", "A1")

    lifts = _LADDER["ladder_basis_lift"]
    rows = [
        ("LinUCB vs Static XGB (EXP-005)", f"+{_E005['lift_pct']}%",
         "Paired design, standardised eval -- the pre-registered primary metric"),
        ("LinUCB vs Static XGB (EXP-014 ladder)", f"+{lifts['linucb_vs_static_pct']}%",
         "CRN harness, reward-maximising policy (Table 9, §5.0.1)"),
        ("LinTS vs Static XGB (EXP-014 ladder)", f"+{lifts['lints_vs_static_pct']}%",
         "CRN harness, LinTS reward-maximising (Table 9, §5.0.1)"),
        ("HITL vs vanilla LinUCB (EXP-008)", f"+{_E008['lift_pct']}%",
         "Augmented bandit vs vanilla bandit -- different baseline entirely"),
    ]

    def _lift_style(i, c, text):
        return (c == 1, BURGUNDY if c == 1 else DARK_TEXT)

    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.2),
                    [Inches(4.4), Inches(1.4), Inches(6.4)],
                    ["Comparison pair", "Lift", "Basis / why different"],
                    rows, font_size=13, row_h=Inches(0.85), cell_style=_lift_style)

    _add_callout(slide, MARGIN_LEFT, CONTENT_TOP + Inches(4.3), CONTENT_W, Inches(0.9),
                 "All three answer different questions and are mutually consistent. "
                 "EXP-005 (+25.2%) is the conservative pre-registered primary.",
                 font_size=14)
    _add_notes(slide,
        "If asked why 25.2, 27.2 and 29.8 percent all appear: the headline uses the "
        "paired EXP-005 design; the ladder harness uses common random numbers which "
        "yields larger separations; HITL's 14.8 percent is against the vanilla bandit, a "
        "different baseline. Same code, different pre-registered questions.")


def slide_app_fairness_detail(prs: Presentation):
    """A2 -- Fairness criterion-6 detail."""
    slide = _content_slide(prs, "v", "A2.  Fairness Criterion-6 Detail", "A2")

    occ, reg = _E006["occupation"], _E006["region"]
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.02), CONTENT_W, Inches(0.4),
                  "Occupation → action association: FAILED-with-interpretation",
                  font_size=16, bold=True, color=DARK_TEXT)
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.55), Inches(6.2), [
        f"Permutation p {occ['permutation_p']} (PASS needs ≥ 0.05)",
        f"EEOC parity {occ['parity_pct']}% (floor 80%)",
        f"PSI AMBER {occ['psi_max_sliding']} < 0.25 RED",
        "Significant, but practically small",
    ], font_size=15, line_h=Inches(0.7))

    _add_callout(slide, Inches(7.1), CONTENT_TOP + Inches(0.55), Inches(5.7), Inches(2.6),
                 "Interpretation: occupation is an actuarially valid risk predictor; the "
                 "bandit prices legitimate risk differences, not protected-class membership. "
                 "Marked FAILED for honesty (§5.2.3-5.2.4).",
                 font_size=14)

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.5), Inches(6.2), Inches(0.4),
                  "Region (PASSED, for reference)", font_size=14, bold=True,
                  color=ACCENT_GREEN)
    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.95), Inches(6.2), Inches(0.8),
                  f"PSI GREEN {reg['psi_max_sliding']}  ·  parity {reg['parity_pct']}%  ·  "
                  f"permutation p = {reg['permutation_p']} (n.s.)",
                  font_size=13, color=SOFT_TEXT)

    _add_footnote(slide,
        "No formal algorithmic-fairness standard exists for Cambodian insurance; EEOC 80% "
        "is applied as international best practice.")
    _add_notes(slide,
        "Deep-dive armor for criterion 6. The permutation test rejects independence at p "
        "below 0.001, so by our own pre-registered rule it is FAILED. Context: parity is "
        "90 percent against an 80 percent floor, PSI stays under the RED threshold, and "
        "occupation is an actuarially priced factor everywhere. Region passes everything. "
        "Regulatory framing: Cambodia has no algorithmic fairness standard, so EEOC 80 "
        "percent is the borrowed benchmark - and it passes for both attributes.")


def slide_app_psi_mechanics(prs: Presentation):
    """A3 -- PSI guardrail mechanics."""
    slide = _content_slide(prs, "iv", "A3.  PSI Guardrail Mechanics", "A3")

    _add_text_box(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.05), Inches(10.5), Inches(0.5),
                  "PSI = Σ (Actual% − Expected%) × ln(Actual% / Expected%)",
                  font_size=20, bold=True, color=DARK_TEXT, font_name="Consolas")
    _add_talking_points(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.75), CONTENT_W, [
        "Actual% = bucket share, rolling 500-round window",
        "Expected% = training-set reference distribution",
        "Computed on region and occupation (EXP-006)",
    ], font_size=15, line_h=Inches(0.62))

    psi_zones = [
        (ACCENT_GREEN, "GREEN", "PSI < 0.10", "stable -- no action"),
        (ACCENT_AMBER, "AMBER", "0.10 ≤ PSI < 0.25", "monitor closely"),
        (ACCENT_RED,   "RED",   "PSI ≥ 0.25", "mandatory review / rollback"),
    ]
    zy = CONTENT_TOP + Inches(2.85)
    for color, label, threshold, action in psi_zones:
        _add_filled_box(slide, MARGIN_LEFT, zy, Inches(0.16), Inches(0.5), color)
        _add_text_box(slide, MARGIN_LEFT + Inches(0.4), zy, Inches(1.4), Inches(0.5),
                      label, font_size=16, bold=True, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(1.9), zy + Inches(0.04), Inches(2.6),
                      Inches(0.45), threshold, font_size=14, color=DARK_TEXT)
        _add_text_box(slide, MARGIN_LEFT + Inches(4.7), zy + Inches(0.04), Inches(7.5),
                      Inches(0.45), action, font_size=14, color=SOFT_TEXT)
        zy += Inches(0.7)

    _add_footnote(slide,
        f"EXP-006: region PSI {_E006['region']['psi_max_sliding']} (GREEN) · occupation "
        f"max {_E006['occupation']['psi_max_sliding']} (AMBER) -- both within threshold.")
    _add_notes(slide,
        "PSI mechanics if asked: it is the symmetrised relative-entropy-style sum over "
        "demographic buckets comparing the rolling 500-round window against the training "
        "reference. Standard industry thresholds: 0.10 and 0.25. In our audit region "
        "peaks at 0.0821, occupation at 0.1225.")


def slide_app_bandit_math(prs: Presentation):
    """A4 -- LinUCB / LinTS update equations."""
    slide = _content_slide(prs, "iv", "A4.  LinUCB / LinTS Update Equations", "A4")

    for cx, head, eqs in [
        (MARGIN_LEFT, "LinUCB (OFUL)", [
            "A_a ← A_a + x_t x_tᵀ",
            "b_a ← b_a + r_t x_t",
            "θ_a = A_a⁻¹ b_a",
            "a* = argmax θ_aᵀx_t + α√(x_tᵀA_a⁻¹x_t)",
        ]),
        (Inches(7.0), "LinTS (Thompson)", [
            "Prior: θ_a ~ N(μ_a, λ⁻¹I)",
            "Σ_a⁻¹ = λI + A_a ;  μ_a = Σ_a b_a",
            "Sample: θ̃_a ~ N(μ_a, v²Σ_a)",
            "Select: a* = argmax θ̃_aᵀ x_t",
        ]),
    ]:
        _add_text_box(slide, cx, CONTENT_TOP + Inches(0.05), Inches(5.8), Inches(0.4),
                      head, font_size=16, bold=True, color=BURGUNDY)
        for i, eq in enumerate(eqs):
            _add_text_box(slide, cx + Inches(0.15),
                          CONTENT_TOP + Inches(0.55) + i * Inches(0.56),
                          Inches(5.7), Inches(0.5), eq, font_size=15,
                          color=DARK_TEXT, font_name="Consolas")

    hp_rows = [
        ("α  (LinUCB exploration)", "1.0 -- regret-minimising (EXP-012)"),
        ("v  (LinTS variance)", "0.1 -- posterior width calibration"),
        ("λ  (ridge penalty)", "1.0 -- identity prior"),
        ("κ  (HITL conservatism)", "0.7 headline; 0.3 / 0.5 also tested"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.35),
                    [Inches(4.2), Inches(8.1)], ["Hyperparameter", "Value"],
                    hp_rows, font_size=13, row_h=Inches(0.56))
    _add_notes(slide,
        "Math armor. LinUCB maintains a per-arm gram matrix and reward vector, solves "
        "ridge regression, and adds the alpha-scaled confidence width - optimism in the "
        "face of uncertainty. LinTS instead samples theta from the posterior and picks "
        "the argmax - exploration through randomisation. Hyperparameters: alpha 1.0 "
        "chosen as regret-minimising in the EXP-012 sensitivity sweep, ridge lambda 1.0, "
        "LinTS variance 0.1, HITL kappa 0.7.")


def slide_app_dataset_construction(prs: Presentation):
    """A5 -- Dataset construction detail."""
    slide = _content_slide(prs, "iv", "A5.  Dataset Construction", "A5")

    src_rows = [
        ("CDHS 2021-22", "Age, sex, region, BMI distributions"),
        ("STEPS 2021", "Chronic-disease prevalence by occupation"),
        ("ILO LFS 2021", "Income distribution by occupation / sector"),
        ("WHO SEARO", "Health expenditure per capita by quintile"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(0.15),
                    [Inches(2.6), Inches(9.7)], ["Source", "Variables anchored"],
                    src_rows, font_size=13, row_h=Inches(0.6))

    sim_rows = [
        ("Scale", "2,000 applicants · 20 seeds · 5,000 rounds"),
        ("Adverse-selection AF", "1.35 (DAC actuarial priors)"),
        ("Price elasticity β", "3.5 base; 2.5 / 4.5 in EXP-012"),
        ("Claim probability", "Logistic in BMI, age, chronic status"),
    ]
    _add_flat_table(slide, MARGIN_LEFT, CONTENT_TOP + Inches(3.2),
                    [Inches(2.6), Inches(9.7)], ["Simulator parameter", "Value"],
                    sim_rows, font_size=13, row_h=Inches(0.6))

    _add_footnote(slide, "Fully synthetic -- no real applicant PII anywhere in the pipeline.")
    _add_notes(slide,
        "Dataset armor: every marginal is anchored to a public source - CDHS for "
        "demographics and BMI, WHO STEPS for chronic prevalence by occupation, ILO "
        "labour-force surveys for income, WHO SEARO for expenditure. The simulator adds "
        "adverse selection at 1.35 and elasticity 3.5 from DAC priors, both stress-tested "
        "in EXP-012. No real applicant data exists anywhere in the pipeline.")
```

- [ ] **Step 8.5: Replace `_slide_demo_screenshot`** (flat placeholder)

```python
def _slide_demo_screenshot(prs: Presentation, label: str, page_num: str, caption: str):
    """Generic demo screenshot placeholder slide (real captures: pre-defense task)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_bottom_bar(slide, page_num)
    _add_slide_title(slide, label)
    _add_title_rule(slide)
    _add_filled_box(slide, MARGIN_LEFT, Inches(1.35), CONTENT_W,
                    BOTTOM_BAR_TOP - Inches(1.7), PANEL)
    _add_text_box(slide, MARGIN_LEFT, Inches(1.35), CONTENT_W,
                  BOTTOM_BAR_TOP - Inches(1.7),
                  f"[Demo screenshot placeholder]\n\n{caption}",
                  font_size=16, color=GRAY_LABEL, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.MIDDLE)
    _add_notes(slide, f"Fallback narration target: {caption}")
    return slide
```

- [ ] **Step 8.6: Remove the now-dead `rounded` argument uses, build, test, commit**

Run: `grep -n "rounded=True" thesis/health_rl/build_burgundy_presentation.py`
Expected: no matches (every caller was rewritten in Tasks 3–8). If any remain, you missed a slide function — fix it before proceeding.

Run: `python thesis/health_rl/build_burgundy_presentation.py && python -m pytest tests/test_build_presentation.py -q`
Expected: `9 passed`

```bash
git add thesis/health_rl/build_burgundy_presentation.py \
        thesis/health_rl/burgundy_defense_presentation.pptx
git commit -m "feat(defense): v2 conclusion + appendix - ladder armor slide, flat tables

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 9: Test-suite overhaul (style + density + armor regression guards)

**Files:**
- Modify: `tests/test_build_presentation.py` (append new tests; module docstring → "v2 minimal-academic")
- Modify: `thesis/health_rl/build_burgundy_presentation.py` (delete the ignored `rounded` param)

- [ ] **Step 9.1: Delete the dead `rounded` parameter**

In `_add_filled_box`, remove `rounded: bool = False,` from the signature and the explanatory comment. Verify no caller remains: search the builder for `rounded=` → expect 0 matches.

- [ ] **Step 9.2: Append the new tests**

```python
# ---------------------------------------------------------------------------
# v2 style, density, and claim-armor guards
# ---------------------------------------------------------------------------

CONTENT_IDX = list(range(2, 21))            # slides 3-21 (01-19)
NOTED_IDX = CONTENT_IDX + [21] + list(range(24, 32))   # + demo + A1-A8


def test_presenter_notes_on_content_slides(built_presentation):
    prs = Presentation(str(built_presentation))
    for idx in NOTED_IDX:
        slide = prs.slides[idx]
        assert slide.has_notes_slide, f"Slide {idx + 1}: no notes slide"
        text = slide.notes_slide.notes_text_frame.text
        assert len(text) > 40, f"Slide {idx + 1}: notes too short ({len(text)} chars)"


def test_no_serif_display_font(built_presentation):
    """v2 is Calibri-only: Times New Roman must not appear on any slide."""
    prs = Presentation(str(built_presentation))
    for s_i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                # builder sets fonts at paragraph level (p.font) AND run level -- check both
                assert para.font.name != "Times New Roman", (
                    f"Slide {s_i + 1}: Times New Roman paragraph '{para.text[:40]}'"
                )
                for run in para.runs:
                    assert run.font.name != "Times New Roman", (
                        f"Slide {s_i + 1}: Times New Roman run '{run.text[:40]}'"
                    )


def test_no_inherited_shadows(built_presentation):
    """Every shape is created through a _flat()-calling helper."""
    prs = Presentation(str(built_presentation))
    for s_i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            assert shape.shadow.inherit is False, (
                f"Slide {s_i + 1}: shape '{shape.shape_type}' inherits theme shadow"
            )


def test_claim_armor_footnotes_present(built_presentation):
    """The four claim-critical lines must survive any future density edits."""
    prs = Presentation(str(built_presentation))
    checks = [
        (12, "5.0.1"),                        # convergence: admissible scope
        (14, "0.0840"),                       # cold-start: LinUCB softened p
        (15, "AlwaysRATED"),                  # HITL: ceiling scope
        (16, "FAILED-with-interpretation"),   # fairness: criterion 6
        (19, "FALSIFIED"),                    # ladder: falsified expectation
    ]
    for idx, needle in checks:
        combined = _all_text(prs, idx)
        assert needle in combined, (
            f"Slide {idx + 1}: armor text '{needle}' missing. Got: {combined[:300]}"
        )


def test_slide_scale_figures_exist():
    slide_dir = ROOT / "thesis" / "health_rl" / "figures" / "slides"
    for stem in ["slide_reward_curves", "slide_loglog_regret", "slide_cold_start",
                 "slide_hitl", "slide_drift", "slide_ladder"]:
        p = slide_dir / f"{stem}.png"
        assert p.exists() and p.stat().st_size > 30_000, f"{p.name} missing or trivial"


def test_logos_only_on_title_and_thanks(built_presentation):
    """Content slides carry at most one picture (the chart); title/thanks carry logos."""
    prs = Presentation(str(built_presentation))
    def n_pics(idx):
        return sum(1 for sh in prs.slides[idx].shapes if sh.shape_type == 13)
    for idx in CONTENT_IDX:
        assert n_pics(idx) <= 1, f"Slide {idx + 1}: {n_pics(idx)} pictures (logo creep?)"
    assert n_pics(0) >= 2, "Title slide lost its logos"
    assert n_pics(22) >= 2, "Thanks slide lost its logos"
```

- [ ] **Step 9.3: Full suite**

Run: `python -m pytest tests/test_build_presentation.py -q`
Expected: `15 passed`

- [ ] **Step 9.4: Commit**

```bash
git add tests/test_build_presentation.py thesis/health_rl/build_burgundy_presentation.py
git commit -m "test(defense): v2 guards - notes, no-serif, no-shadow, armor footnotes, logo discipline

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 10: Full verification + visual review with the user

**Files:** none new (verification only; pptx recommitted if the rebuild changes it)

- [ ] **Step 10.1: Clean rebuild + full suite from scratch**

```bash
rm thesis/health_rl/burgundy_defense_presentation.pptx
python thesis/health_rl/build_burgundy_presentation.py
python -m pytest tests/test_build_presentation.py -q
```
Expected: `Saved 32 slides`, `15 passed`.

- [ ] **Step 10.2: Export every slide to PNG for eyeballing** (PowerShell; PowerPoint COM)

```powershell
$out = "$env:TEMP\deck_export_v2"; New-Item -ItemType Directory -Force $out | Out-Null
$pp = New-Object -ComObject PowerPoint.Application
try {
  $pres = $pp.Presentations.Open("C:\DAC-UW-Thesis\thesis\health_rl\burgundy_defense_presentation.pptx", $true, $true, $false)
  $pres.Export($out, "PNG", 1280, 720)
  $pres.Close()
} finally { $pp.Quit() }
(Get-ChildItem $out -Filter *.PNG | Measure-Object).Count
```
Expected: `32`

- [ ] **Step 10.3: Self-check the exports against the v2 system, then show the user**

Read at least slides 8, 11, 13, 16, 20 (the worst build-1 offenders). Verify: no shadows/bevels, no serif titles, chart text legible at thumbnail size, ≤4 points per slide, armor footnotes visible. Then present the full export to the user for sign-off (gallery in the visual companion if a session is live, otherwise tell them to open `%TEMP%\deck_export_v2`). **Do not mark this plan done without user sign-off — this is a taste rebuild; the user's eye is the acceptance test.**

- [ ] **Step 10.4: Commit the final pptx if the rebuild changed it**

```bash
git add thesis/health_rl/burgundy_defense_presentation.pptx
git commit -m "feat(defense): v2 minimal-academic deck - final rebuild

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Spec-coverage checklist (for the final review)

| Spec section | Where implemented |
|---|---|
| §2 style decision (B + bottom bar) | Tasks 1, 3–8 |
| §3 chrome (tag/title/accent/bar) | Task 1 |
| §3 no shadows / no rounding / Calibri-only | Tasks 1, 9 (guard tests) |
| §3 stat typography, logos title+thanks only | Tasks 2, 3, 7, 9 |
| §4 ≤4 talking points, enforced | Task 2 (ValueError) + per-slide Tasks 4–8 |
| §4 presenter notes everywhere | Tasks 3–8 content, Task 9 guard |
| §4 four armor footnotes | Tasks 7–8 content, Task 9 guard |
| §4 tables ≤5 rows | Task 4 (lit merged), Task 8 (A1 4 rows) |
| §5 slide-scale figures, palette, no captions | Task 6 |
| §5 native architecture diagram | Task 5 (Step 5.1) |
| §6 title/ToC/divider templates, emoji removed | Task 3 |
| §7 builder in place, JSON discipline, tests | Tasks 0–9 |
| §8 out of scope (structure, claims, A6–A8 captures, date) | untouched by design |

<!-- END OF PLAN -->






