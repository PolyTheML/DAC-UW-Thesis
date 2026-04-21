"""Tests for the defense presentation generator."""
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

SCRIPT = Path("thesis/auto/build_presentation.py")
OUTPUT = Path("thesis/auto/auto_defense_presentation.pptx")


def _run_build():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"


def test_generates_20_slides():
    OUTPUT.unlink(missing_ok=True)
    _run_build()
    assert OUTPUT.exists()
    prs = Presentation(str(OUTPUT))
    assert len(prs.slides) == 20, f"Expected 20 slides, got {len(prs.slides)}"


def test_title_slide_has_presenter_name():
    prs = Presentation(str(OUTPUT))
    texts = [
        shape.text_frame.text
        for shape in prs.slides[0].shapes
        if shape.has_text_frame
    ]
    combined = " ".join(texts)
    assert "LUN CHANPOLY" in combined, f"Presenter name missing. Got: {combined}"


def test_slide_titles_present():
    prs = Presentation(str(OUTPUT))
    expected = [
        ("Population Stability", 0),
        ("Agenda",               1),
        ("Cambodia",             2),
        ("Research Claim",       3),
        ("PSI",                  4),
        ("Telematics",           5),
        ("Baseline",             9),
        ("Responsiveness",      10),
        ("Failure Modes",       11),
        ("Temporal",            14),
        ("Thank You",           19),
    ]
    for keyword, idx in expected:
        texts = [
            shape.text_frame.text
            for shape in prs.slides[idx].shapes
            if shape.has_text_frame
        ]
        combined = " ".join(texts)
        assert keyword in combined, (
            f"Slide {idx + 1}: '{keyword}' not found. Got: {combined[:200]}"
        )
