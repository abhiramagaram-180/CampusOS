"""CampusOS configuration — frozen data contract and Databricks settings.

The GenieAnswer dataclass is the contract between backend and frontend.
NO FIELD CHANGES after Hour 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import os


# ---------------------------------------------------------------------------
# Mock mode — flip to False when wiring real Databricks (Hour ~4.5)
# ---------------------------------------------------------------------------
MOCK_MODE: bool = os.getenv("CAMPUSOS_MOCK", "true").lower() in ("1", "true", "yes")


# ---------------------------------------------------------------------------
# GenieAnswer — the immutable contract. Every response from any client
# (mock or real) must conform to this shape.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GenieAnswer:
 """A single answer from Databricks Genie (or the mock).

 Attributes:
 answer_text: Human-readable summary Genie produced.
 data: Query results as a Polars DataFrame, or None.
 sql: The SQL Genie executed, or None if unavailable.
 conversation_id: Genie conversation token for follow-up turns.
 error: Error message if the call failed, else None.
 """

 answer_text: str
 data: Optional[object] # pl.DataFrame | None — avoid importing polars here
 sql: Optional[str]
 conversation_id: Optional[str]
 error: Optional[str]


# ---------------------------------------------------------------------------
# Zone → Genie Space ID mapping
# Add entries as Genie Agents are created (P2 delivers space IDs).
# ---------------------------------------------------------------------------
ZONE_SPACE_IDS: dict[str, str] = {
 "placement": os.getenv("CAMPUSOS_PLACEMENT_SPACE_ID", ""),
 "library": os.getenv("CAMPUSOS_LIBRARY_SPACE_ID", ""),
 "admin": os.getenv("CAMPUSOS_ADMIN_SPACE_ID", ""),
 "faculty": os.getenv("CAMPUSOS_FACULTY_SPACE_ID", ""),
 "social": os.getenv("CAMPUSOS_SOCIAL_SPACE_ID", ""),
}


# ---------------------------------------------------------------------------
# SQL Warehouse — the compute backend for Genie queries
# ---------------------------------------------------------------------------
WAREHOUSE_ID: str = os.getenv("CAMPUSOS_WAREHOUSE_ID", "")


# ---------------------------------------------------------------------------
# Databricks workspace hostname (e.g. https://adb-123456.azuredatabricks.net)
# ---------------------------------------------------------------------------
DATABRICKS_HOST: str = os.getenv("DATABRICKS_HOST", "")
