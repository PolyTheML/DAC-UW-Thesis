from __future__ import annotations

import os

import anthropic

from scripts.thesis_scorer import Violation

_REWRITER_SYSTEM = (
    "You are an ITC thesis style compliance editor.\n"
    "Fix ONLY the violations listed below. Do not change any other content — "
    "not arguments, not data, not conclusions.\n"
    "Rules per violation type:\n"
    "- heading_hierarchy: fix the heading level so no level is skipped\n"
    "- citation_placeholder: add [CITATION: needed] directly after the unsupported claim\n"
    "- figure_placeholder: add [FIGURE: description] on its own line where a figure is referenced\n"
    "- table_placeholder: add [TABLE: description] on its own line where a table is referenced\n"
    "- itc_structure: add the missing section heading in the correct position\n"
    "- apa7_format: fix the reference list entry to APA 7 format\n\n"
    "Do not fabricate citations. Do not remove existing text.\n"
    "Return the complete fixed markdown chapter and nothing else."
)


def rewrite_chapter(
    content: str, violations: list[Violation], *, model: str = "claude-opus-4-7"
) -> str:
    """Rewrite chapter to fix violations. Requires ANTHROPIC_API_KEY env var."""
    if not violations:
        return content
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    violations_text = "\n".join(
        f"- [{v.severity.upper()}] Section '{v.section}', Rule '{v.rule}': {v.description}"
        for v in violations
    )
    user_message = f"Violations to fix:\n{violations_text}\n\n---\n\nChapter:\n\n{content}"
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        system=_REWRITER_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text
