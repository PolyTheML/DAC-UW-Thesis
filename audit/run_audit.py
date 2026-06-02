#!/usr/bin/env python3
"""
Thesis Equation Audit Pipeline
Run: python audit/run_audit.py

Produces:
  audit/dashboard.html        -- unified HTML report
  audit/repository_inventory.md
  audit/llm_review_queue/     -- equations needing manual LLM review
"""
import shutil
import sys
from pathlib import Path

# Ensure project root is on path
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from audit.phases import (
    phase_01_inventory,
    phase_02_papers,
    phase_03_thesis,
    phase_04_traceability,
    phase_05_validation,
    phase_06_notation,
    phase_07_literature,
    phase_08_citations,
    phase_09_rl_fairness,
    phase_10_dashboard,
)

_AUDIT_DIR = _REPO_ROOT / "audit"
_CACHE_DIR = _AUDIT_DIR / "cache"


def reset_cache() -> None:
    """Delete and recreate the cache directory. Preserves llm_review_queue/."""
    if _CACHE_DIR.exists():
        shutil.rmtree(_CACHE_DIR)
    _CACHE_DIR.mkdir(parents=True)
    (_CACHE_DIR / "papers").mkdir()
    (_CACHE_DIR / "phase_results").mkdir()


def main() -> None:
    print("=" * 60)
    print("Thesis Equation Audit Pipeline")
    print("=" * 60)

    reset_cache()
    (_AUDIT_DIR / "llm_review_queue").mkdir(exist_ok=True)

    print("\n-- Phase 1: Repository Inventory --")
    phase_01_inventory.run(_REPO_ROOT, _AUDIT_DIR)

    print("\n-- Phase 2: Paper Ingestion --")
    phase_02_papers.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 3: Thesis Ingestion --")
    phase_03_thesis.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 4: Equation Traceability --")
    phase_04_traceability.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 5: Mathematical Validation --")
    phase_05_validation.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 6: Notation Consistency --")
    phase_06_notation.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 7: Literature Consistency --")
    phase_07_literature.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 8: Citation Audit --")
    phase_08_citations.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 9: RL & Fairness Audit --")
    phase_09_rl_fairness.run(_REPO_ROOT, _CACHE_DIR)

    print("\n-- Phase 10: HTML Dashboard --")
    dashboard_path = phase_10_dashboard.run(_REPO_ROOT, _CACHE_DIR, _AUDIT_DIR)

    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print(f"Dashboard: {dashboard_path}")
    llm_q = list((_AUDIT_DIR / "llm_review_queue").glob("*.txt"))
    if llm_q:
        print(f"LLM queue: {len(llm_q)} equations need manual review")
        print("  -> audit/llm_review_queue/")
    print("=" * 60)


if __name__ == "__main__":
    main()
