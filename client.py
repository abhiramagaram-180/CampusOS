"""client.py — routes each zone's question to mock_client or genie_client.

Pages import only `ask()` from here; they never touch MOCK_MODE, space IDs,
or warehouse IDs directly. Keeps the mock/real switch in exactly one place.
"""

from __future__ import annotations

from config import MOCK_MODE, WAREHOUSE_ID, ZONE_SPACE_IDS, GenieAnswer


def ask(zone: str, question: str, conversation_id: str | None = None) -> GenieAnswer:
    """Ask the given zone's Genie (or its mock) a question.

    Args:
        zone: Key into config.ZONE_SPACE_IDS / ui.zones.ZONES (e.g. "placement").
        question: The user's natural-language question.
        conversation_id: Prior conversation token for follow-up turns, if any.

    Returns:
        A GenieAnswer. Never raises — Genie/config errors come back in the
        `error` field so pages can render them uniformly.
    """
    if MOCK_MODE:
        import mock_client

        return mock_client.ask_genie(question, conversation_id=conversation_id, zone=zone)

    import genie_client

    space_id = ZONE_SPACE_IDS.get(zone, "")
    return genie_client.ask_genie(
        question=question,
        space_id=space_id,
        warehouse_id=WAREHOUSE_ID,
        conversation_id=conversation_id,
    )
