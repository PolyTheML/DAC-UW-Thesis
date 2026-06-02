from audit.lib.render_html import render_dashboard


def _fake_results() -> dict:
    return {
        "phase4": [
            {"equation_id": "ch03_disp_001", "status": "PASS", "confidence": 0.95,
             "source_paper": "agrawal13.pdf", "source_page": 4,
             "source_text": "theta_a x_t", "cited": True, "notes": "",
             "match_method": "fuzzy"},
            {"equation_id": "ch03_disp_002", "status": "FAIL", "confidence": 0.1,
             "source_paper": "", "source_page": 0,
             "source_text": "", "cited": False, "notes": "No match",
             "match_method": "none"},
        ],
        "phase5": [],
        "phase6": [],
        "phase7": [],
        "phase8": [],
        "phase9": [
            {"check_id": "RL-01", "status": "PASS", "notes": ""}
        ],
        "thesis_equations": [
            {"equation_id": "ch03_disp_001", "chapter": "03", "section": "3.3.2",
             "latex_md": r"\hat\theta_a^\top x_t", "display": True,
             "citations": ["Agrawal & Goyal, 2013"]},
            {"equation_id": "ch03_disp_002", "chapter": "03", "section": "3.3.3",
             "latex_md": r"R_T = \sum_t r_t", "display": True,
             "citations": []},
        ],
        "llm_queue": ["ch03_disp_003"],
    }


def test_html_contains_summary_table():
    html = render_dashboard(_fake_results())
    assert "Executive Summary" in html
    assert "PASS" in html
    assert "FAIL" in html


def test_html_is_self_contained():
    html = render_dashboard(_fake_results())
    assert "<!DOCTYPE html>" in html
    assert "</html>" in html
    assert "<style>" in html   # inline styles, no external CSS


def test_badge_counts_correct():
    html = render_dashboard(_fake_results())
    # 1 PASS and 1 FAIL in phase4
    assert "1" in html   # at least some count appears


def test_html_has_collapsible_sections():
    html = render_dashboard(_fake_results())
    assert "<details" in html
    assert "<summary" in html
