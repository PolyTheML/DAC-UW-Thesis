import json
from pathlib import Path
from audit.lib.extract_pdf import extract_paper


def run(repo_root: Path, cache_dir: Path) -> dict:
    """Ingest all PDFs from thesis/papers/ and write per-paper JSON."""
    papers_dir = repo_root / "thesis" / "papers"
    papers_cache_dir = cache_dir / "papers"
    papers_cache_dir.mkdir(parents=True, exist_ok=True)

    index: dict[str, dict] = {}
    for pdf_path in sorted(papers_dir.glob("*.pdf")):
        print(f"[Phase 2] Ingesting {pdf_path.name} ...")
        paper = extract_paper(pdf_path)
        out_path = papers_cache_dir / f"{pdf_path.stem}.json"
        out_path.write_text(json.dumps(paper, indent=2, ensure_ascii=False), encoding="utf-8")
        index[pdf_path.stem] = {
            "title": paper["title"],
            "year": paper["year"],
            "equations_count": len(paper["equations"]),
            "pages": len(paper["raw_pages"]),
            "cache_file": str(out_path.relative_to(cache_dir.parent)),
        }
        print(f"  -> {len(paper['equations'])} equations, {len(paper['raw_pages'])} pages")

    (cache_dir / "paper_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[Phase 2] Indexed {len(index)} papers")
    return index
