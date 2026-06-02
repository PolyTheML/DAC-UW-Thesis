import json
from pathlib import Path
from audit.lib.match_equations import match_equation


_CITATION_TO_FILE = {
    "li et al": "1772690.1772758",
    "linucb": "1772690.1772758",
    "agrawal": "agrawal13",
    "thompson sampling": "agrawal13",
    "lints": "agrawal13",
    "robbins": "S0002-9904-1952-09620-8",
    "zhou": "zhou20a",
    "neuralucb": "zhou20a",
    "ensign": "ensign18a",
    "fairness": "ensign18a",
}


def _guess_paper_stems(citations: list) -> list:
    """Map citation strings to paper file stems."""
    stems = []
    for cit in citations:
        cit_lower = cit.lower()
        for key, stem in _CITATION_TO_FILE.items():
            if key in cit_lower and stem not in stems:
                stems.append(stem)
    return stems


def run(repo_root: Path, cache_dir: Path) -> tuple:
    """Match each thesis equation against source papers."""
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))

    # Load all paper caches
    papers: dict[str, dict] = {}
    for json_path in (cache_dir / "papers").glob("*.json"):
        papers[json_path.stem] = json.loads(json_path.read_text(encoding="utf-8"))

    llm_queue_dir = cache_dir.parent / "llm_review_queue"
    llm_queue_dir.mkdir(parents=True, exist_ok=True)

    results = []
    llm_queue = []

    for eq in equations:
        # Skip very short inline equations
        if not eq["display"] and len(eq.get("latex_md", "")) < 5:
            continue

        cited_stems = _guess_paper_stems(eq.get("citations", []))
        all_paper_eqs = []

        # Search cited papers first
        for stem in cited_stems:
            if stem in papers:
                for peq in papers[stem]["equations"]:
                    all_paper_eqs.append({**peq, "_paper_stem": stem})

        # Then remaining papers
        for stem, paper in papers.items():
            if stem not in cited_stems:
                for peq in paper["equations"]:
                    all_paper_eqs.append({**peq, "_paper_stem": stem})

        match = match_equation(eq.get("latex_md", ""), all_paper_eqs)
        status = match["status"]

        # Matched but no citation → WARNING
        if status == "PASS" and not eq.get("citations"):
            status = "WARNING"

        result = {
            "equation_id": eq["equation_id"],
            "chapter": eq["chapter"],
            "section": eq.get("section", ""),
            "latex": eq.get("latex_md", "")[:100],
            "status": status,
            "match_method": match["match_method"],
            "confidence": match["confidence"],
            "source_paper": match.get("source_paper", ""),
            "source_page": match.get("source_page", 0),
            "source_text": match.get("source_text", ""),
            "cited": bool(eq.get("citations")),
            "notes": match.get("notes", ""),
        }
        results.append(result)

        if match["status"] == "LLM_QUEUE":
            llm_queue.append(eq["equation_id"])
            prompt_path = llm_queue_dir / f"{eq['equation_id']}.txt"
            if not prompt_path.exists():
                context = eq.get("nearby_text_before", "")[-300:]
                prompt_path.write_text(
                    f"EQUATION REVIEW REQUEST\n"
                    f"Equation ID: {eq['equation_id']}\n"
                    f"Chapter: {eq['chapter']} Section: {eq.get('section', '')}\n"
                    f"LaTeX: {eq.get('latex_md', '')}\n\n"
                    f"Context before: {context}\n\n"
                    f"Candidate paper match (confidence {match['confidence']:.2f}):\n"
                    f"  Paper text: {match.get('source_text', '')}\n\n"
                    f"TASK: Determine if the thesis equation and the paper text express the same\n"
                    f"mathematical object. Answer: SAME / DIFFERENT / UNCERTAIN, with 1-2 sentences\n"
                    f"of explanation.\n",
                    encoding="utf-8"
                )

    out_path = cache_dir / "phase_results" / "phase4_traceability.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"[Phase 4] Traceability: {counts}. LLM queue: {len(llm_queue)}")
    return results, llm_queue
