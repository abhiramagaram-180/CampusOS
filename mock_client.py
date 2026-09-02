"""
CampusOS — fake Genie, for building the UI before Databricks is ready.

OWNER: Person 1.

This exists so Person 3 is never blocked. It returns the same GenieAnswer
shape as the real client, after a short sleep so loading states are testable.

It is ALSO the demo fallback: if Genie or the warehouse dies during judging,
`export CAMPUSOS_MOCK=true` and the app still runs.
"""

import time
from typing import Optional

import pandas as pd

from config import BUILT_ZONES, GenieAnswer

_FAKE_SQL = """SELECT c.company_name,
       COUNT(o.offer_id) AS offers,
       ROUND(AVG(o.package_lpa), 2) AS avg_package_lpa
FROM campus.placement.offers o
JOIN campus.placement.companies c ON o.company_id = c.company_id
WHERE o.offer_year = 2025
GROUP BY c.company_name
ORDER BY offers DESC
LIMIT 5"""

_FAKE_DF = pd.DataFrame({
    "company_name":    ["Cisco", "Oracle", "Arctic Wolf", "Couchbase", "ION Group"],
    "offers":          [24, 19, 12, 9, 7],
    "avg_package_lpa": [18.5, 16.2, 22.0, 20.4, 26.8],
})

# A few canned shapes so the UI can be tested against different result types.
_TEXT_ONLY_TRIGGERS = ("how many", "count of", "what is the total")


def ask_genie(
    zone: str,
    question: str,
    conversation_id: Optional[str] = None,
) -> GenieAnswer:
    """Fake implementation. Same signature as the real one."""
    time.sleep(1.2)  # simulate Genie latency so spinners get exercised

    q = (question or "").strip().lower()

    # Mirror the real client: only built zones answer. Lets Person 3 build
    # and test the "this zone isn't built yet" panel without Databricks.
    if zone not in BUILT_ZONES:
        return GenieAnswer(
            text="",
            conversation_id=conversation_id,
            error=f"The {zone} zone isn't wired up yet.",
        )

    if not q:
        return GenieAnswer(
            text="",
            conversation_id=conversation_id or "mock-conv-001",
            error="Please type a question.",
        )

    # Simulate a failure path so Person 3 can build the error state.
    if "fail" in q or "error" in q:
        return GenieAnswer(
            text="",
            conversation_id=conversation_id or "mock-conv-001",
            error="Genie could not answer that. Try rephrasing the question.",
        )

    # Simulate a text-only answer (no table to render).
    if any(t in q for t in _TEXT_ONLY_TRIGGERS):
        return GenieAnswer(
            text="There were 312 offers made across 41 companies in 2025.",
            sql="SELECT COUNT(*) FROM campus.placement.offers WHERE offer_year = 2025",
            df=None,
            conversation_id=conversation_id or "mock-conv-001",
        )

    # Default: a full tabular answer with a chart-friendly shape.
    return GenieAnswer(
        text=(
            "Cisco made the most offers in 2025 with 24, followed by Oracle with 19. "
            "ION Group offered the highest average package at 26.8 LPA."
        ),
        sql=_FAKE_SQL,
        df=_FAKE_DF.copy(),
        conversation_id=conversation_id or "mock-conv-001",
    )
