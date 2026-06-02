import json
import re
from pathlib import Path
from audit.lib.extract_md import extract_equations_from_file
from audit.lib.extract_docx import extract_equations_from_docx

_CHAPTER_NUM_RE = re.compile(r'chapter(\d+)')

# Primary DOCX to audit (try in order)
_DOCX_CANDIDATES = [
    "thesis/build/I5_ITC_Thesis_Submission_Final_fig21_fig22.docx",
    "thesis/build/I5_ITC_Thesis_Submission_Final.docx",
    "thesis/health_rl/ITC_Thesis_Draft.docx",
]


def _cross_check(md_eqs: list, docx_eqs: list) -> list:
    """
    For each display equation from markdown, try to find a matching DOCX equation.
    Sets build_divergence=True for display equations with no DOCX counterpart.
    """
    docx_latexes = [e["latex_docx"] for e in docx_eqs]
    results = []
    for eq in md_eqs:
        if not eq["display"]:
            eq["source"] = "md_only"
            results.append(eq)
            continue

        matched = False
        for dl in docx_latexes:
            md_tokens = set(re.findall(r'[A-Za-z_]+', eq["latex_md"]))
            docx_tokens = set(re.findall(r'[A-Za-z_]+', dl))
            if md_tokens and docx_tokens:
                overlap = len(md_tokens & docx_tokens) / len(md_tokens)
                if overlap > 0.5:
                    matched = True
                    eq["latex_docx"] = dl
                    eq["source"] = "both"
                    break

        if not matched:
            eq["source"] = "md_only"
            eq["build_divergence"] = True

        results.append(eq)
    return results


def run(repo_root: Path, cache_dir: Path) -> list:
    """Extract equations from all chapter .md files and cross-check against DOCX."""
    chapters_dir = repo_root / "thesis" / "health_rl"

    # Find the DOCX
    docx_path = None
    for candidate in _DOCX_CANDIDATES:
        p = repo_root / candidate
        if p.exists():
            docx_path = p
            break

    all_equations: list[dict] = []

    for md_path in sorted(chapters_dir.glob("chapter*.md")):
        m = _CHAPTER_NUM_RE.search(md_path.stem)
        chapter = m.group(1).zfill(2) if m else "00"
        eqs = extract_equations_from_file(md_path, chapter)
        all_equations.extend(eqs)
        print(f"[Phase 3] {md_path.name}: {len(eqs)} equations")

    # DOCX extraction
    docx_eqs: list[dict] = []
    if docx_path:
        docx_eqs = extract_equations_from_docx(docx_path)
        method = docx_eqs[0]["method"] if docx_eqs else "none"
        print(f"[Phase 3] DOCX ({docx_path.name}): {len(docx_eqs)} equations (method: {method})")
    else:
        print("[Phase 3] WARNING: No DOCX found in expected locations")

    # Cross-check
    all_equations = _cross_check(all_equations, docx_eqs)

    divergent = [e for e in all_equations if e["build_divergence"]]
    if divergent:
        print(f"[Phase 3] NOTE: {len(divergent)} display equations have no DOCX counterpart")

    out_path = cache_dir / "thesis_equations.json"
    out_path.write_text(json.dumps(all_equations, indent=2, ensure_ascii=False), encoding="utf-8")

    n_display = len([e for e in all_equations if e["display"]])
    n_inline = len([e for e in all_equations if not e["display"]])
    print(f"[Phase 3] Total: {len(all_equations)} equations ({n_display} display, {n_inline} inline)")
    return all_equations
