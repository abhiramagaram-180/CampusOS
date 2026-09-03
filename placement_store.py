"""
CampusOS — local placement record store.

A tiny append-only store so the "Submit Placement" form persists records
even in mock mode, and the Placement chat can reason over them (e.g. recognise
a newly submitted highest package).

Records live in data/placements.json next to this file. This is demo
persistence, not a real database — just enough to show submitted data flowing
through into the analytics answers.
"""

from __future__ import annotations

import json
import os

import pandas as pd

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
_PATH = os.path.join(_DIR, "placements.json")

MAX_LEADERBOARD_ROWS = 12

# Known existing placements, so "highest package" has a baseline to beat.
# Mirrors the figures the mock Genie already reports.
BASELINE = [
    {"company_name": "ION Group",   "package_ctc_lpa": 26.8},
    {"company_name": "Arctic Wolf", "package_ctc_lpa": 22.0},
    {"company_name": "Couchbase",   "package_ctc_lpa": 20.4},
    {"company_name": "Cisco",       "package_ctc_lpa": 18.5},
    {"company_name": "Oracle",      "package_ctc_lpa": 16.2},
]


def _load() -> list[dict]:
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # Don't silently start from empty — that would make the next write wipe
        # every earlier record. Move the bad file aside so it's recoverable.
        try:
            os.replace(_PATH, _PATH + ".corrupt")
        except OSError:
            pass
        return []


def add_placement(record: dict) -> None:
    """Append one submitted placement record to the store (atomic write)."""
    records = _load()
    records.append(record)
    os.makedirs(_DIR, exist_ok=True)
    tmp = _PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    os.replace(tmp, _PATH)  # atomic: an interrupted write can't corrupt the store


def get_submitted() -> list[dict]:
    """Every record submitted through the form so far."""
    return _load()


def clear() -> None:
    """Wipe the store (handy when resetting a demo)."""
    try:
        os.remove(_PATH)
    except FileNotFoundError:
        pass


def combined_df() -> pd.DataFrame:
    """Baseline + submitted, as company_name / package_ctc_lpa rows."""
    rows = [dict(r) for r in BASELINE]
    for r in _load():
        if r.get("company_name") and r.get("package_ctc_lpa") is not None:
            rows.append(
                {
                    "company_name": r["company_name"],
                    "package_ctc_lpa": float(r["package_ctc_lpa"]),
                }
            )
    return pd.DataFrame(rows)


def highest_package():
    """(company_name, package_lpa) with the max package across baseline + submitted."""
    df = combined_df()
    if df.empty:
        return None
    row = df.loc[df["package_ctc_lpa"].idxmax()]
    return str(row["company_name"]), float(row["package_ctc_lpa"])


def leaderboard_df() -> pd.DataFrame:
    """One row per placement (baseline + every submission), ranked by package.

    Keeps duplicate companies as separate rows and carries a unique ``rank``
    label so a bar chart shows every offer instead of summing same-name rows.
    """
    rows = [
        {"company_name": r["company_name"], "package_ctc_lpa": float(r["package_ctc_lpa"]), "source": "existing"}
        for r in BASELINE
    ]
    for r in _load():
        if r.get("company_name") and r.get("package_ctc_lpa") is not None:
            rows.append(
                {
                    "company_name": r["company_name"],
                    "package_ctc_lpa": float(r["package_ctc_lpa"]),
                    "source": "submitted",
                }
            )
    df = pd.DataFrame(rows).sort_values("package_ctc_lpa", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    df.insert(1, "placement", df["rank"].astype(str) + ". " + df["company_name"])
    return df
