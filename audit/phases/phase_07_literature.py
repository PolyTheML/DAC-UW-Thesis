import json
import re
from pathlib import Path
from rapidfuzz import fuzz

_EPISTEMIC_RE = re.compile(
    r'(?<=[.!?\n])[ \t]*([^.!?\n]{20,200}?'
    r'(?:achieves?|shows?|proves?|demonstrates?|outperforms?|'
    r'is bounded by|guarantees?|establishes?|confirms?)[^.!?\n]{5,150}[.!?])',
    re.IGNORECASE,
)
_CITATION_RE = re.compile(
    r'\(([A-Z][A-Za-zÀ-ÿ\s\&,\.]+,\s*\d{4}[a-z]?(?:;\s*[A-Z][A-Za-zÀ-ÿ\s\&,\.]+,\s*\d{4}[a-z]?)*)\)'
)
_CITATION_TO_FILE = {
    "li": "1772690.1772758", "linucb": "1772690.1772758",
    "agrawal": "agrawal13", "thompson": "agrawal13",
    "robbins": "S0002-9904-1952-09620-8",
    "zhou": "zhou20a",
    "ensign": "ensign18a",
}


def _find_paper_stem(citation: str) -> str:
    cit_lower = citation.lower()
    for key, stem in _CITATION_TO_FILE.items():
        if key in cit_lower:
            return stem
    return ""


def run(repo_root: Path, cache_dir: Path) -> list:
    lit_review_path = repo_root / "thesis" / "health_rl" / "chapter03_literature_review.md"
    text = lit_review_path.read_text(encoding="utf-8")

    papers_cache: dict[str, str] = {}
    for jp in (cache_dir / "papers").glob("*.json"):
        p = json.loads(jp.read_text(encoding="utf-8"))
        papers_cache[jp.stem] = "\n".join(p["raw_pages"].values())

    results = []

    for m in _EPISTEMIC_RE.finditer(text):
        claim = m.group(1).strip()
        # Find citations within 300 chars of the claim
        window_start = max(0, m.start() - 200)
        window = text[window_start:m.end() + 200]
        cit_matches = _CITATION_RE.findall(window)
        citations = []
        for c in cit_matches:
            citations.extend([s.strip() for s in c.split(";")])

        if not citations:
            results.append({
                "claim_text": claim[:200],
                "chapter": "03",
                "section": "",
                "citations": [],
                "status": "NO_CITED_PAPER",
                "evidence": "",
            })
            continue

        best_status = "UNSUPPORTED"
        best_evidence = ""

        for cit in citations:
            stem = _find_paper_stem(cit)
            if stem not in papers_cache:
                continue
            paper_text = papers_cache[stem]
            key_terms = " ".join(w for w in claim.split() if len(w) > 4)[:200]
            score = fuzz.partial_ratio(key_terms.lower(), paper_text.lower()) / 100.0
            if score > 0.75:
                best_status = "SUPPORTED"
                best_evidence = f"Strong match in {stem} (score {score:.2f})"
                break
            elif score > 0.50:
                best_status = "PARTIALLY_SUPPORTED"
                best_evidence = f"Partial match in {stem} (score {score:.2f})"

        results.append({
            "claim_text": claim[:200],
            "chapter": "03",
            "section": "",
            "citations": citations[:3],
            "status": best_status,
            "evidence": best_evidence,
        })

    out_path = cache_dir / "phase_results" / "phase7_literature.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"[Phase 7] Literature claims: {counts}")
    return results
