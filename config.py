"""
CampusOS — shared configuration and the integration contract.

OWNER: Person 1 (Lead Integrator).
Nobody else edits this file. If you need a field added, message Person 1.

The GenieAnswer dataclass below is FROZEN once agreed at hour 0.
Do not rename fields. The entire frontend is written against it.
"""

import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# THE CONTRACT — frozen at hour 0
# ---------------------------------------------------------------------------

@dataclass
class GenieAnswer:
    """Everything the UI needs to render one answer.

    Person 3 renders this. Person 1 produces it. Neither needs to know
    how the other works.
    """
    text: str                              # natural-language summary from Genie
    sql: Optional[str] = None              # the SQL Genie generated (transparency panel)
    df: Optional[pd.DataFrame] = None      # result rows, or None if text-only
    conversation_id: Optional[str] = None  # pass back in for follow-up questions
    error: Optional[str] = None            # human-readable message if something failed

    @property
    def ok(self) -> bool:
        return self.error is None


# ---------------------------------------------------------------------------
# MODE SWITCH
# ---------------------------------------------------------------------------
# Default is MOCK so a fresh clone runs with zero Databricks setup.
# Flip with:  export CAMPUSOS_MOCK=false
MOCK_MODE = os.getenv("CAMPUSOS_MOCK", "true").lower() in ("1", "true", "yes")


# ---------------------------------------------------------------------------
# DATABRICKS WIRING  —  fill these in at hour ~3 when Person 2 hands them over
# ---------------------------------------------------------------------------
# Read from environment so nothing secret is ever committed.
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")

# One Genie Agent per zone.
ZONE_SPACE_IDS = {
    "placement": os.getenv("GENIE_SPACE_PLACEMENT", ""),
    "library":   os.getenv("GENIE_SPACE_LIBRARY", ""),
    "canteen":   os.getenv("GENIE_SPACE_CANTEEN", ""),
    "rd":        os.getenv("GENIE_SPACE_RD", ""),
    "admin":     os.getenv("GENIE_SPACE_ADMIN", ""),
    "faculty":   os.getenv("GENIE_SPACE_FACULTY", ""),
}

# Zones that actually have a working Genie Agent behind them.
# Person 3 uses this to decide whether to show the chat or the "stub" panel.
BUILT_ZONES = {"placement", "library", "canteen", "rd"}

# How long to wait for Genie before giving up, in seconds.
GENIE_TIMEOUT_SECONDS = 90
