import json
from pathlib import Path


def run(repo_root: Path, output_dir: Path) -> dict:
    """Walk repo and document all thesis-relevant files."""
    inventory = {
        "thesis_documents": [],
        "bibliography_files": [],
        "papers": [],
        "chapter_files": [],
        "figures": [],
    }

    # Thesis DOCX
    for p in (repo_root / "thesis").rglob("*.docx"):
        if not p.name.startswith("~$"):
            inventory["thesis_documents"].append({
                "path": str(p.relative_to(repo_root)),
                "size_kb": round(p.stat().st_size / 1024, 1),
            })

    # Bibliography
    for p in repo_root.rglob("*.bib"):
        inventory["bibliography_files"].append(str(p.relative_to(repo_root)))

    # Papers
    papers_dir = repo_root / "thesis" / "papers"
    if papers_dir.exists():
        for p in papers_dir.glob("*.pdf"):
            inventory["papers"].append({
                "path": str(p.relative_to(repo_root)),
                "size_kb": round(p.stat().st_size / 1024, 1),
            })

    # Chapter markdown files
    for p in sorted((repo_root / "thesis" / "health_rl").glob("chapter*.md")):
        inventory["chapter_files"].append(str(p.relative_to(repo_root)))

    # Figures
    figs_dir = repo_root / "thesis" / "health_rl" / "figures"
    if figs_dir.exists():
        for p in figs_dir.glob("*.png"):
            inventory["figures"].append(str(p.relative_to(repo_root)))

    # Write markdown report
    lines = [
        "# Repository Inventory\n\n",
        f"## Thesis Documents ({len(inventory['thesis_documents'])})\n\n",
    ]
    for d in inventory["thesis_documents"]:
        lines.append(f"- `{d['path']}` ({d['size_kb']} KB)\n")
    lines.append(f"\n## Source Papers ({len(inventory['papers'])})\n\n")
    for p in inventory["papers"]:
        lines.append(f"- `{p['path']}` ({p['size_kb']} KB)\n")
    lines.append(f"\n## Chapter Files ({len(inventory['chapter_files'])})\n\n")
    for c in inventory["chapter_files"]:
        lines.append(f"- `{c}`\n")
    lines.append(f"\n## Bibliography Files: {len(inventory['bibliography_files'])}\n")
    lines.append(f"\n## Figures: {len(inventory['figures'])}\n")

    (output_dir / "repository_inventory.md").write_text("".join(lines), encoding="utf-8")
    print(f"[Phase 1] Inventory complete: {len(inventory['papers'])} papers, "
          f"{len(inventory['chapter_files'])} chapters")
    return inventory
