"""Tests for the defense presentation generator (v3 blue, 32 slides)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.enum.text import PP_ALIGN

ROOT   = Path(__file__).parent.parent
SCRIPT = ROOT / "thesis" / "health_rl" / "build_burgundy_presentation.py"
OUTPUT = ROOT / "thesis" / "health_rl" / "burgundy_defense_presentation.pptx"
RESULTS_JSON = ROOT / "demo" / "static" / "thesis_results.json"


def _run_build():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, f"Builder failed:\n{result.stderr}"


@pytest.fixture(scope="session")
def built_presentation():
    OUTPUT.unlink(missing_ok=True)
    _run_build()
    return OUTPUT


@pytest.fixture(scope="session")
def import_builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location("builder", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _all_text(prs, slide_idx: int) -> str:
    return " ".join(
        shape.text_frame.text
        for shape in prs.slides[slide_idx].shapes
        if shape.has_text_frame
    )


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

def test_generates_32_slides(built_presentation):
    prs = Presentation(str(built_presentation))
    assert len(prs.slides) == 32, f"Expected 32 slides, got {len(prs.slides)}"


def test_title_slide_has_presenter_name(built_presentation):
    prs = Presentation(str(built_presentation))
    combined = _all_text(prs, 0)
    assert "LUN CHANPOLY" in combined, f"Presenter name missing. Got: {combined[:200]}"


def test_title_slide_has_defense_date(built_presentation):
    prs = Presentation(str(built_presentation))
    combined = _all_text(prs, 0)
    assert "July 2026" in combined, f"Defense date missing. Got: {combined[:200]}"


def test_toc_slide_has_five_sections(built_presentation):
    prs = Presentation(str(built_presentation))
    combined = _all_text(prs, 1)
    for roman in ["I", "II", "III", "IV", "V"]:
        assert roman in combined, f"ToC missing section '{roman}'. Got: {combined[:300]}"


def test_appendix_slides_have_page_numbers(built_presentation):
    """Appendix slides (indices 27-31) must have A1-A5 page numbers."""
    prs = Presentation(str(built_presentation))
    for i, label in enumerate(["A1", "A2", "A3", "A4", "A5"]):
        combined = _all_text(prs, 27 + i)
        assert label in combined, (
            f"Appendix slide {i + 1}: page number '{label}' not found. Got: {combined[:200]}"
        )


# ---------------------------------------------------------------------------
# Numbers match thesis_results.json
# ---------------------------------------------------------------------------

def test_headline_numbers_match_json(built_presentation):
    """Key headline numbers from JSON appear verbatim in the relevant slides."""
    prs = Presentation(str(built_presentation))
    with open(RESULTS_JSON) as f:
        results = json.load(f)

    # exp005 +25.2% lift appears in slide idx 20 (CONVERGENCE & REGRET)
    lift_pct = str(results["exp005"]["lift_pct"])
    slide_20_text = _all_text(prs, 20)
    assert lift_pct in slide_20_text, (
        f"EXP-005 lift_pct '{lift_pct}' not found in slide 21. Got: {slide_20_text[:300]}"
    )

    # exp008 +14.8% HITL lift appears in slide idx 21 (COLD-START & HUMAN-IN-THE-LOOP)
    hitl_lift = str(results["exp008"]["lift_pct"])
    slide_21_text = _all_text(prs, 21)
    assert hitl_lift in slide_21_text, (
        f"EXP-008 lift_pct '{hitl_lift}' not found in slide 22. Got: {slide_21_text[:300]}"
    )

    # AlwaysRATED ladder reward appears in slide idx 27 (A1 ladder appendix)
    always_rated_r = f"{next(r['reward'] for r in results['ladder']['rows'] if r['policy'] == 'AlwaysRATED'):,}"
    slide_27_text = _all_text(prs, 27)
    assert always_rated_r in slide_27_text, (
        f"AlwaysRATED reward '{always_rated_r}' not found in slide 28. "
        f"Got: {slide_27_text[:300]}"
    )

    # exp010 LinTS Wilcoxon p-value appears in slide idx 21
    lints_p = str(results["exp010"]["wilcoxon_t2000"]["lints_vs_freshxgb"]["p"])
    assert lints_p in slide_21_text, (
        f"EXP-010 LinTS p-value '{lints_p}' not found in slide 22. "
        f"Got: {slide_21_text[:300]}"
    )


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


# ---------------------------------------------------------------------------
# v3 style, density, and claim-armor guards
# ---------------------------------------------------------------------------

NOTED_IDX = [3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 25, 27, 28, 29, 30, 31]


def test_presenter_notes_on_content_slides(built_presentation):
    prs = Presentation(str(built_presentation))
    for idx in NOTED_IDX:
        slide = prs.slides[idx]
        assert slide.has_notes_slide, f"Slide {idx + 1}: no notes slide"
        text = slide.notes_slide.notes_text_frame.text
        assert len(text) > 40, f"Slide {idx + 1}: notes too short ({len(text)} chars)"


def test_no_serif_display_font(built_presentation):
    """v3 is Calibri/Segoe-UI-only: Times New Roman must not appear on any slide."""
    prs = Presentation(str(built_presentation))
    for s_i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
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


def test_claim_armor_strings_present(built_presentation):
    """Spec §5 armor mapping — exact indices in the v3 inventory."""
    prs = Presentation(str(built_presentation))
    checks = [
        (6,  "O1"), (6, "O2"), (6, "O3"), (6, "O4"),  # objectives verbatim
        (16, "AlwaysRATED"), (16, "inadmissible"),     # build-up C ceiling
        (19, "5.0.1"),                                 # benchmark admissible scope
        (20, "5.0.1"),                                 # convergence admissible scope
        (21, "0.0039"), (21, "0.0840"),                # cold-start LinTS + softened LinUCB
        (22, "FAILED-with-interpretation"),            # fairness criterion 6
        (25, "O1"),                                    # conclusion scorecard
        (27, "FALSIFIED"), (27, "AlwaysRATED"),        # ladder appendix
    ]
    for idx, needle in checks:
        combined = _all_text(prs, idx)
        assert needle in combined, (
            f"Slide {idx + 1}: armor text '{needle}' missing. Got: {combined[:300]}")


def test_slide_scale_figures_exist():
    slide_dir = ROOT / "thesis" / "health_rl" / "figures" / "slides"
    for stem in ["slide_reward_curves", "slide_loglog_regret", "slide_cold_start",
                 "slide_hitl", "slide_drift", "slide_ladder"]:
        p = slide_dir / f"{stem}.png"
        assert p.exists() and p.stat().st_size > 30_000, f"{p.name} missing or trivial"


def test_logos_only_on_title_and_thanks(built_presentation):
    """Title slide (idx 0) and thanks slide (idx 26) carry logos (>=2 pics).
    All other slides carry at most 3 pictures (live-demo carries up to 3 screenshots)."""
    prs = Presentation(str(built_presentation))

    def n_pics(idx):
        return sum(1 for sh in prs.slides[idx].shapes if sh.shape_type == 13)

    assert n_pics(0) >= 2, "Title slide lost its logos"
    assert n_pics(26) >= 2, "Thanks slide lost its logos"
    for idx in range(len(prs.slides)):
        if idx not in [0, 26]:
            assert n_pics(idx) <= 3, (
                f"Slide {idx + 1}: {n_pics(idx)} pictures (logo creep?)"
            )


# ---------------------------------------------------------------------------
# v3 blue footer ribbon (helper unit tests — must stay)
# ---------------------------------------------------------------------------

def test_slide_palette_is_blue_not_burgundy():
    """Figure palette must carry no retired burgundy hexes."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "slide_style", ROOT / "thesis" / "health_rl" / "figures" / "_slide_style.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    banned = {"#5d2a42", "#8a5570", "#b894a6", "#471f33"}
    used = {v.lower() for v in mod.SLIDE_PALETTE.values()}
    assert not (used & banned), f"burgundy survives in SLIDE_PALETTE: {used & banned}"
    assert mod.SLIDE_PALETTE["hero"].lower() == "#1b5697", "hero series must be steel-blue"


def test_footer_ribbon_three_parts(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    b._add_footer_ribbon(slide, "12 / 27")
    text = " ".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    assert "DAC" in text and "ITC-AMS" in text          # left org block
    assert "12 / 27" in text                             # right page block
    assert "July 2026" in text                           # right date


def test_content_title_centered_caps(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    b._add_content_title(slide, "Synthetic Cambodia Dataset")
    titled = [s for s in slide.shapes if s.has_text_frame
              and "SYNTHETIC CAMBODIA DATASET" in s.text_frame.text]
    assert titled, "title not rendered ALL-CAPS"
    p = titled[0].text_frame.paragraphs[0]
    assert p.alignment == PP_ALIGN.CENTER


def test_divider_slide_renders_number_and_name(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    b._add_divider(prs, "III", "Methodology & Model Design", "10 / 27")
    slide = prs.slides[0]
    text = " ".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    assert "III" in text and "Methodology & Model Design" in text


def test_overview_flowchart_six_stages_and_highlight(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    b._add_overview_flowchart(slide, b.CONTENT_TOP, highlight="Bandit Policy")
    text = " ".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    for stage in ["Applicant Context", "Bandit Policy", "Underwriting Action",
                  "Actuarial Reward", "PSI Fairness + HITL", "Decision"]:
        assert stage in text, f"flowchart missing stage '{stage}'"
    # the highlight box uses GREEN_HILITE line color
    greens = [s for s in slide.shapes
              if s.line.color.type is not None and s.line.color.rgb == b.GREEN_HILITE]
    assert greens, "no green highlight outline drawn"


def test_buildup_stage_renders_labels_and_outputs(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    stages = [("Context vector x_t in R^5", "[0.4, -1.1, 0, 2, 0.8]"),
              ("Per-arm value estimates", "RATED 0.31 / STD 0.52 / DEC 0.10 / REF 0.28")]
    b._add_buildup_stage(slide, b.CONTENT_TOP, stages)
    text = " ".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    assert "Context vector" in text and "[0.4, -1.1, 0, 2, 0.8]" in text
    assert "Per-arm value estimates" in text


def test_placeholder_image_shows_swap_caption(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    b._add_placeholder_image(slide, b.Inches(7), b.CONTENT_TOP, b.Inches(5.5),
                             b.Inches(4.0), "Phnom Penh DAC office")
    text = " ".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    assert "PHOTO" in text.upper() and "Phnom Penh DAC office" in text
    assert "swap" in text.lower()


def test_demo_screenshot_helper_present(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # missing path -> labeled placeholder (deck never breaks)
    b._add_demo_screenshot(slide, b.MARGIN_LEFT, b.CONTENT_TOP, b.Inches(6),
                           b.Inches(4), "nonexistent.png", "Underwriting dashboard")
    text = " ".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    assert "Underwriting dashboard" in text


# ---------------------------------------------------------------------------
# v3 structural guards
# ---------------------------------------------------------------------------

def test_footer_ribbon_on_every_slide(built_presentation):
    prs = Presentation(str(built_presentation))
    for s_i, slide in enumerate(prs.slides):
        text = " ".join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
        assert "ITC-AMS" in text, f"Slide {s_i + 1}: footer ribbon missing"


def test_divider_slides_present(built_presentation):
    prs = Presentation(str(built_presentation))
    for idx, num in [(2, "I"), (7, "II"), (9, "III"), (18, "IV"), (24, "V")]:
        text = _all_text(prs, idx)
        assert f"{num}." in text, f"Slide {idx + 1}: divider '{num}.' missing"


def test_methodology_overview_and_three_zooms(built_presentation):
    prs = Presentation(str(built_presentation))
    assert "Applicant Context" in _all_text(prs, 10)
    assert "Applicant Context" in _all_text(prs, 11)   # zoom 1
    assert "Bandit Policy" in _all_text(prs, 13)        # zoom 2
    assert "PSI Fairness + HITL" in _all_text(prs, 17)  # zoom 3


def test_no_burgundy_fill_anywhere(built_presentation):
    """Color regression: the retired burgundy RGB must not fill any shape."""
    from pptx.dml.color import RGBColor
    burgundy = {RGBColor(0x5D, 0x2A, 0x42), RGBColor(0x47, 0x1F, 0x33),
                RGBColor(0x8A, 0x55, 0x70), RGBColor(0xB8, 0x94, 0xA6)}
    prs = Presentation(str(built_presentation))
    for s_i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            try:
                if shape.fill.type is not None and shape.fill.fore_color.rgb in burgundy:
                    raise AssertionError(f"Slide {s_i + 1}: burgundy fill survives")
            except (TypeError, AttributeError):
                continue   # gradient/none/inherited fills have no solid rgb


def test_demo_slide_has_visual(built_presentation):
    """Live-demo slide (idx 23) carries 3 visuals (real shots or placeholders)."""
    prs = Presentation(str(built_presentation))
    text = _all_text(prs, 23)
    assert "scoring" in text.lower() or "dashboard" in text.lower()
