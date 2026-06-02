from datetime import datetime

_STATUS_COLOR = {
    "PASS": "#22c55e",
    "WARNING": "#f59e0b",
    "FAIL": "#ef4444",
    "MANUAL_REVIEW": "#3b82f6",
    "LLM_QUEUE": "#8b5cf6",
    "SUPPORTED": "#22c55e",
    "PARTIALLY_SUPPORTED": "#f59e0b",
    "UNSUPPORTED": "#ef4444",
    "NO_CITED_PAPER": "#6b7280",
}

_BADGE = '<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8em;font-weight:bold">{label}</span>'


def _badge(status: str) -> str:
    color = _STATUS_COLOR.get(status, "#6b7280")
    return _BADGE.format(color=color, label=status)


def _count_statuses(items: list, key: str = "status") -> dict:
    counts: dict[str, int] = {}
    for item in items:
        s = item.get(key, "UNKNOWN")
        counts[s] = counts.get(s, 0) + 1
    return counts


def _table_rows(items: list, columns: list) -> str:
    rows = []
    for item in items:
        cells = []
        for col in columns:
            val = item.get(col, "")
            if col == "status":
                val = _badge(str(val))
            else:
                val = str(val)[:120]
            cells.append(f"<td style='padding:4px 8px;border-bottom:1px solid #e5e7eb'>{val}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return "\n".join(rows)


def _section(title: str, content: str) -> str:
    return f"""
<details open style="margin:16px 0;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden">
  <summary style="background:#f9fafb;padding:12px 16px;cursor:pointer;font-weight:bold;font-size:1.05em">{title}</summary>
  <div style="padding:16px">{content}</div>
</details>"""


def _phase_table(items: list, cols: list) -> str:
    if not items:
        return "<p>No issues found.</p>"
    header = "".join(f"<th style='text-align:left;padding:4px 8px;background:#f3f4f6'>{c}</th>" for c in cols)
    return (f"<table style='width:100%;border-collapse:collapse;font-size:0.9em'>"
            f"<tr>{header}</tr>{_table_rows(items, cols)}</table>")


def render_dashboard(results: dict) -> str:
    p4 = results.get("phase4", [])
    p5 = results.get("phase5", [])
    p6 = results.get("phase6", [])
    p7 = results.get("phase7", [])
    p8 = results.get("phase8", [])
    p9 = results.get("phase9", [])
    llm_queue = results.get("llm_queue", [])

    # Counts
    p4_counts = _count_statuses(p4)
    total = len(p4)
    n_pass = p4_counts.get("PASS", 0)
    n_warn = p4_counts.get("WARNING", 0)
    n_fail = p4_counts.get("FAIL", 0)
    n_llm = len(llm_queue)
    n_manual = sum(1 for r in p5 if r.get("status") == "MANUAL_REVIEW")

    summary_table = f"""
<table style="border-collapse:collapse;margin:16px 0">
  <tr><th style="padding:8px 16px;background:#f3f4f6;text-align:left">Metric</th>
      <th style="padding:8px 16px;background:#f3f4f6;text-align:right">Count</th></tr>
  <tr><td style="padding:8px 16px">Total equations audited</td><td style="padding:8px 16px;text-align:right">{total}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('PASS')} Traced to source</td><td style="padding:8px 16px;text-align:right">{n_pass}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('WARNING')} Found in non-cited paper</td><td style="padding:8px 16px;text-align:right">{n_warn}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('FAIL')} Not found in any paper</td><td style="padding:8px 16px;text-align:right">{n_fail}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('LLM_QUEUE')} Queued for manual LLM review</td><td style="padding:8px 16px;text-align:right">{n_llm}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('MANUAL_REVIEW')} Math derivation needs manual check</td><td style="padding:8px 16px;text-align:right">{n_manual}</td></tr>
</table>"""

    # High-priority issues
    fails = [r for r in p4 if r.get("status") == "FAIL"]
    high_priority = ""
    if fails:
        high_priority = "<h3 style='color:#ef4444'>High-Priority Issues</h3>"
        for f in fails:
            high_priority += f"<p>🔴 Equation <code>{f['equation_id']}</code>: {f.get('notes', '')}</p>"

    # LLM queue
    llm_html = ""
    if llm_queue:
        items_html = "".join(
            f"<li><code>{eq}</code> — see <code>audit/llm_review_queue/{eq}.txt</code></li>"
            for eq in llm_queue
        )
        llm_html = _section("⬜ LLM Review Queue",
                             f"<p>{len(llm_queue)} equations need manual review via Claude:</p><ul>{items_html}</ul>")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thesis Equation Audit Dashboard</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 24px 32px; color: #1f2937; }}
  h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
  h2 {{ color: #374151; }}
  code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }}
  details summary:hover {{ background: #f3f4f6; }}
</style>
</head>
<body>
<h1>Thesis Equation Audit Dashboard</h1>
<p style="color:#6b7280">Generated: {now}</p>

<h2>Executive Summary</h2>
{summary_table}
{high_priority}

{_section("Phase 4 — Equation Traceability",
          _phase_table(p4, ["equation_id","status","match_method","confidence","source_paper","source_page","cited","notes"]))}
{_section("Phase 5 — Mathematical Validation",
          _phase_table(p5, ["equation_id","claim","status","notes"]))}
{_section("Phase 6 — Notation Consistency",
          _phase_table(p6, ["symbol","issue_type","locations","notes"]))}
{_section("Phase 7 — Literature Consistency",
          _phase_table(p7, ["claim_text","citations","status","evidence"]))}
{_section("Phase 8 — Citation Audit",
          _phase_table(p8, ["location","issue_type","text","notes"]))}
{_section("Phase 9 — RL &amp; Fairness Audit",
          _phase_table(p9, ["check_id","status","notes"]))}
{llm_html}
</body>
</html>"""
