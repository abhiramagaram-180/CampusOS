"""
CampusOS — the only file that talks to Databricks.

OWNER: Person 1 (Lead Integrator).

Person 3 imports exactly one thing from here:

    from genie_client import ask_genie

That import never changes, in mock mode or live mode. The MOCK_MODE switch
happens inside this file, so the frontend has no idea which is running.

--------------------------------------------------------------------------
BEFORE TRUSTING THIS FILE: verify the SDK method names.
The Databricks SDK renames things between versions (Genie Spaces became
Genie Agents; the jump from 0.67 to 0.133 moved several methods). Run this
in a Databricks notebook first:

    from databricks.sdk import WorkspaceClient
    w = WorkspaceClient()
    print([m for m in dir(w.genie) if not m.startswith('_')])

Fix the names below to match what you actually see. Do not assume.
--------------------------------------------------------------------------
"""

from typing import Optional

import pandas as pd

from config import (
    GenieAnswer,
    MOCK_MODE,
    ZONE_SPACE_IDS,
    GENIE_TIMEOUT_SECONDS,
)

# Lazily created so importing this module never fails when the SDK is absent
# (e.g. Person 3 running the UI locally in mock mode).
_client = None


def _get_client():
    global _client
    if _client is None:
        from databricks.sdk import WorkspaceClient
        _client = WorkspaceClient()
    return _client


# ---------------------------------------------------------------------------
# Attachment parsing
# ---------------------------------------------------------------------------

def _extract(space_id: str, msg) -> tuple[str, Optional[str], Optional[pd.DataFrame]]:
    """Pull text, SQL and rows out of a completed Genie message.

    A message carries a list of attachments. Each is either a text answer or a
    query (which has the generated SQL, and a result set fetched separately).
    """
    text_parts: list[str] = []
    sql: Optional[str] = None
    df: Optional[pd.DataFrame] = None

    for att in (getattr(msg, "attachments", None) or []):
        # ---- text attachment
        if getattr(att, "text", None) is not None:
            content = getattr(att.text, "content", None)
            if content:
                text_parts.append(content)

        # ---- query attachment
        query = getattr(att, "query", None)
        if query is not None:
            sql = getattr(query, "query", None) or sql

            # Genie sometimes puts a one-line description on the query itself.
            desc = getattr(query, "description", None)
            if desc and not text_parts:
                text_parts.append(desc)

            if df is None:
                df = _fetch_rows(space_id, msg, att)

    return ("\n\n".join(text_parts).strip(), sql, df)


def _fetch_rows(space_id: str, msg, att) -> Optional[pd.DataFrame]:
    """Fetch the result rows for a query attachment.

    Wrapped defensively: if the result fetch fails we still want the user to
    see the text answer and the SQL. A missing table is a degraded answer,
    not a broken one.
    """
    try:
        w = _get_client()
        result = w.genie.get_message_attachment_query_result(
            space_id=space_id,
            conversation_id=msg.conversation_id,
            message_id=msg.id,
            attachment_id=att.attachment_id,
        )

        sr = getattr(result, "statement_response", None)
        if sr is None:
            return None

        manifest = getattr(sr, "manifest", None)
        schema = getattr(manifest, "schema", None)
        columns = [c.name for c in (getattr(schema, "columns", None) or [])]

        data = getattr(sr, "result", None)
        rows = getattr(data, "data_array", None) or []

        if not columns:
            return None
        return pd.DataFrame(rows, columns=columns)

    except Exception as e:  # noqa: BLE001 — degraded answer is acceptable here
        print(f"[genie_client] could not fetch rows: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API — the contract
# ---------------------------------------------------------------------------

def ask_genie(
    zone: str,
    question: str,
    conversation_id: Optional[str] = None,
) -> GenieAnswer:
    """Ask one question of one zone's Genie Agent.

    Args:
        zone: 'placement', 'admin', ... (key into ZONE_SPACE_IDS)
        question: the user's plain-English question
        conversation_id: pass the previous answer's id to ask a follow-up

    Returns:
        GenieAnswer. Never raises — failures come back as .error.
    """
    if MOCK_MODE:
        from mock_client import ask_genie as _mock
        return _mock(zone, question, conversation_id)

    if not question or not question.strip():
        return GenieAnswer(text="", conversation_id=conversation_id,
                           error="Please type a question.")

    space_id = ZONE_SPACE_IDS.get(zone, "")
    if not space_id:
        return GenieAnswer(
            text="", conversation_id=conversation_id,
            error=f"The {zone} zone isn't wired up yet.",
        )

    try:
        w = _get_client()

        if conversation_id:
            msg = w.genie.create_message_and_wait(
                space_id, conversation_id, question,
                timeout=_timeout(),
            )
        else:
            msg = w.genie.start_conversation_and_wait(
                space_id, question,
                timeout=_timeout(),
            )

        status = str(getattr(msg, "status", "")).upper()
        if "FAILED" in status or "CANCELLED" in status:
            return GenieAnswer(
                text="", conversation_id=getattr(msg, "conversation_id", conversation_id),
                error="Genie couldn't answer that one. Try rephrasing it.",
            )

        text, sql, df = _extract(space_id, msg)

        if not text and df is None:
            return GenieAnswer(
                text="", sql=sql,
                conversation_id=getattr(msg, "conversation_id", conversation_id),
                error="Genie returned an empty answer. Try rephrasing it.",
            )

        return GenieAnswer(
            text=text or "Here's what I found.",
            sql=sql,
            df=df,
            conversation_id=getattr(msg, "conversation_id", conversation_id),
        )

    except TimeoutError:
        return GenieAnswer(
            text="", conversation_id=conversation_id,
            error="That took too long. The warehouse may be starting up — try again.",
        )
    except Exception as e:  # noqa: BLE001 — the UI must never crash
        print(f"[genie_client] error: {type(e).__name__}: {e}")
        return GenieAnswer(
            text="", conversation_id=conversation_id,
            error="Something went wrong reaching Genie. Try again.",
        )


def _timeout():
    from datetime import timedelta
    return timedelta(seconds=GENIE_TIMEOUT_SECONDS)
