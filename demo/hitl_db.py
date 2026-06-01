"""Lightweight sqlite3 persistence for HITL reviews.

Uses stdlib sqlite3 (no SQLAlchemy, no async) because request volume
is one-at-a-time and the demo is self-contained.
"""
from __future__ import annotations

import csv
import io
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from demo.pricing_engine import compute_batch_psi

DB_PATH = Path(__file__).parent / "hitl.db"


def _conn() -> sqlite3.Connection:
    """Return a new connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the reviews table if it does not exist."""
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_json  TEXT NOT NULL,
                bandit_action   INTEGER NOT NULL,
                override_action INTEGER NOT NULL,
                reward          REAL NOT NULL,
                underwriter     TEXT NOT NULL,
                created_at      TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_review(
    applicant: dict[str, Any],
    bandit_action: int,
    override_action: int,
    reward: float,
    underwriter: str,
) -> int:
    """Insert a review record and return the new row id."""
    with _conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO reviews (applicant_json, bandit_action, override_action, reward, underwriter, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                json.dumps(applicant, default=str),
                bandit_action,
                override_action,
                round(float(reward), 4),
                underwriter,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def reset_reviews() -> int:
    """Delete all review records. Returns the number of rows removed.

    Used by the demo's reset control so a fresh HITL session can be run
    between defense rehearsals.
    """
    with _conn() as conn:
        cur = conn.execute("SELECT COUNT(*) AS n FROM reviews")
        n = int(cur.fetchone()["n"])
        conn.execute("DELETE FROM reviews")
        conn.commit()
    return n


def get_all_reviews() -> list[dict[str, Any]]:
    """Return every review as a dict."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reviews ORDER BY created_at"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_metrics(window: int = 50) -> dict[str, Any]:
    """Compute HITL metrics from the review log.

    Parameters
    ----------
    window : int
        Rolling window size for override/alignment rate (default 50).

    Returns
    -------
    dict
        total_reviews, override_rate, alignment_rate, avg_reward,
        cumulative_reward, human_cost, recent_rewards list.
    """
    reviews = get_all_reviews()
    n = len(reviews)
    if n == 0:
        return {
            "total_reviews": 0,
            "override_rate": None,
            "alignment_rate": None,
            "avg_reward": None,
            "cumulative_reward": 0.0,
            "human_cost": 0.0,
            "recent_rewards": [],
        }

    # Override = human chose differently from bandit (for non-REFER bandit recs,
    # any human choice from {0,1,2} when bandit said 3 counts as override)
    overrides = 0
    aligns = 0
    non_refer_count = 0
    for r in reviews:
        if r["bandit_action"] != 3:
            non_refer_count += 1
            if r["override_action"] == r["bandit_action"]:
                aligns += 1
            else:
                overrides += 1
        else:
            # Bandit said REFER; any human choice is an "override" of REFER
            overrides += 1

    # Rolling window (last N reviews)
    recent = reviews[-window:]
    recent_overrides = 0
    recent_aligns = 0
    recent_non_refer = 0
    for r in recent:
        if r["bandit_action"] != 3:
            recent_non_refer += 1
            if r["override_action"] == r["bandit_action"]:
                recent_aligns += 1
            else:
                recent_overrides += 1
        else:
            recent_overrides += 1

    rewards = [r["reward"] for r in reviews]
    cum_reward = sum(rewards)

    # Human cost: $35 per override (EXP-008 convention)
    HUMAN_COST_PER_OVERRIDE = 35.0
    total_overrides = overrides  # all overrides including REFER cases
    human_cost = total_overrides * HUMAN_COST_PER_OVERRIDE

    return {
        "total_reviews": n,
        "override_rate": round(recent_overrides / len(recent), 4) if recent else None,
        "alignment_rate": round(recent_aligns / recent_non_refer, 4) if recent_non_refer else None,
        "avg_reward": round(float(np.mean(rewards)), 2),
        "cumulative_reward": round(float(cum_reward), 2),
        "human_cost": round(float(human_cost), 2),
        "recent_rewards": [round(float(r), 2) for r in rewards[-window:]],
    }


def compute_approved_psi(reference_df: pd.DataFrame) -> dict[str, Any] | None:
    """Compute PSI on the approved pool (STANDARD + RATED overrides) vs reference."""
    reviews = get_all_reviews()
    approved = [r for r in reviews if r["override_action"] in (0, 1)]
    if not approved:
        return None

    rows = []
    for r in approved:
        rows.append(json.loads(r["applicant_json"]))
    approved_df = pd.DataFrame(rows)

    # Ensure columns exist that reference_df has
    for col in ["region", "occupation", "wealth_quintile", "age"]:
        if col not in approved_df.columns:
            approved_df[col] = "Unknown"

    return compute_batch_psi(approved_df, reference_df)


def export_csv() -> str:
    """Return the full review log as a CSV string."""
    reviews = get_all_reviews()
    if not reviews:
        return ""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "underwriter", "bandit_action", "override_action",
        "reward", "age", "gender", "region", "occupation",
        "wealth_quintile", "mortality_multiplier", "created_at",
    ])
    ACTION_NAMES = ["STANDARD", "RATED", "DECLINE", "REFER"]
    for r in reviews:
        a = json.loads(r["applicant_json"])
        writer.writerow([
            r["id"],
            r["underwriter"],
            ACTION_NAMES[r["bandit_action"]],
            ACTION_NAMES[r["override_action"]],
            r["reward"],
            a.get("age", ""),
            a.get("gender", ""),
            a.get("region", ""),
            a.get("occupation", ""),
            a.get("wealth_quintile", ""),
            a.get("mortality_multiplier", ""),
            r["created_at"],
        ])
    return output.getvalue()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


# Initialise on first import
init_db()
