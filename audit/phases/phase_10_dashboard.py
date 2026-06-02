import json
from pathlib import Path
from audit.lib.render_html import render_dashboard


def run(repo_root: Path, cache_dir: Path, output_dir: Path) -> Path:
    """Aggregate all phase results and render the HTML dashboard."""

    def _load(filename: str) -> list:
        p = cache_dir / "phase_results" / filename
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return []

    thesis_eqs_path = cache_dir / "thesis_equations.json"
    thesis_eqs = (json.loads(thesis_eqs_path.read_text(encoding="utf-8"))
                  if thesis_eqs_path.exists() else [])

    # Collect LLM queue entries
    llm_queue_dir = output_dir / "llm_review_queue"
    llm_queue = sorted(p.stem for p in llm_queue_dir.glob("*.txt")) if llm_queue_dir.exists() else []

    results = {
        "phase4": _load("phase4_traceability.json"),
        "phase5": _load("phase5_validation.json"),
        "phase6": _load("phase6_notation.json"),
        "phase7": _load("phase7_literature.json"),
        "phase8": _load("phase8_citations.json"),
        "phase9": _load("phase9_rl_fairness.json"),
        "thesis_equations": thesis_eqs,
        "llm_queue": llm_queue,
    }

    html = render_dashboard(results)
    out_path = output_dir / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"[Phase 10] Dashboard written to {out_path}")
    return out_path
