import json
import re
from pathlib import Path

_CITATION_RE = re.compile(
    r'\(([A-Z][A-Za-zÀ-ÿ\s\&,\.]+,\s*\d{4}[a-z]?)\)'
)
_KNOWN_PAPER_STEMS = {
    "1772690.1772758", "agrawal13", "S0002-9904-1952-09620-8", "zhou20a", "ensign18a"
}


def _citation_matches_known_paper(cit: str) -> bool:
    cit_lower = cit.lower()
    known_keywords = {
        "li", "agrawal", "robbins", "zhou", "ensign",
        "thompson", "linucb", "neuralucb"
    }
    return any(kw in cit_lower for kw in known_keywords)


def run(repo_root: Path, cache_dir: Path) -> list:
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))

    issues = []

    for eq in equations:
        if not eq.get("display"):
            continue  # only audit display equations for citations

        citations = eq.get("citations", [])

        # Missing citation on a display equation
        if not citations:
            issues.append({
                "location": eq["equation_id"],
                "issue_type": "MISSING_CITATION",
                "text": eq.get("latex_md", "")[:100],
                "notes": "Display equation has no nearby citation",
            })
            continue

        # Check citations reference known papers
        for cit in citations:
            if not _citation_matches_known_paper(cit):
                issues.append({
                    "location": eq["equation_id"],
                    "issue_type": "UNCACHED_PAPER",
                    "text": cit,
                    "notes": f"Citation '{cit}' does not match any paper in thesis/papers/",
                })

    out_path = cache_dir / "phase_results" / "phase8_citations.json"
    out_path.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Phase 8] Citation issues: {len(issues)}")
    return issues
