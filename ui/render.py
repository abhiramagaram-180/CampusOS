"""ui/render.py — shared rendering helpers for every zone chat page.

Kept independent of any single zone so P3-style pages stay ~30 lines each.
"""

from __future__ import annotations

import streamlit as st

from config import GenieAnswer
from ui.zones import ZONES, ZoneMeta


def render_header(zone: ZoneMeta) -> None:
    st.markdown(
        f"""
        <style>
        .zone-header {{
            display: flex; align-items: center; gap: 14px;
            padding: 18px 22px; border-radius: 14px;
            background: linear-gradient(135deg, #0d1117 0%, #131b26 100%);
            border: 1px solid #222; margin-bottom: 18px;
        }}
        .zone-header .icon {{ font-size: 34px; }}
        .zone-header .title {{ font-size: 22px; font-weight: 700; color: #eee; }}
        .zone-header .tagline {{ font-size: 13px; color: #888; margin-top: 2px; }}
        .zone-badge {{
            margin-left: auto; font-size: 11px; padding: 4px 10px;
            border-radius: 20px; border: 1px solid #35e38a; color: #35e38a;
        }}
        .zone-badge.stub {{ border-color: #666; color: #888; }}
        </style>
        <div class="zone-header">
            <div class="icon">{zone.icon}</div>
            <div>
                <div class="title">{zone.title}</div>
                <div class="tagline">{zone.tagline}</div>
            </div>
            <div class="zone-badge {'stub' if not zone.production else ''}">
                {'LIVE' if zone.production else 'STUB · same architecture'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("← Back to campus", key=f"back_{zone.key}"):
        st.switch_page("_home.py")


def render_sample_questions(zone: ZoneMeta) -> str | None:
    """Renders sample-question chips. Returns the clicked question, if any."""
    st.caption("Try asking:")
    cols = st.columns(len(zone.sample_questions))
    clicked = None
    for col, q in zip(cols, zone.sample_questions):
        with col:
            if st.button(q, key=f"sample_{zone.key}_{q[:12]}", use_container_width=True):
                clicked = q
    return clicked


def render_history(history: list[dict]) -> None:
    for turn in history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            render_answer(turn["answer"])


def render_answer(answer: GenieAnswer) -> None:
    if answer.error:
        st.error(answer.answer_text)
        return

    st.write(answer.answer_text)

    if answer.data is not None:
        try:
            n_rows = answer.data.shape[0]
        except Exception:
            n_rows = None
        with st.expander(f"📊 Result data" + (f" ({n_rows} rows)" if n_rows else ""), expanded=True):
            st.dataframe(answer.data, use_container_width=True, hide_index=True)

    if answer.sql:
        with st.expander("🔍 SQL Genie ran", expanded=False):
            st.code(answer.sql, language="sql")


def init_chat_state(zone_key: str) -> str:
    """Ensures session_state keys exist for this zone. Returns the history key."""
    hist_key = f"history_{zone_key}"
    conv_key = f"conv_id_{zone_key}"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []
    if conv_key not in st.session_state:
        st.session_state[conv_key] = None
    return hist_key


def run_zone_page(zone_key: str) -> None:
    """Full page body for a zone's Genie chat. Each pages/*.py calls this
    and nothing else — keeps every zone on the identical architecture per
    CONTEXT.md ("the other four show the same architecture as stubs")."""
    import client

    zone = ZONES[zone_key]
    # NOTE: st.set_page_config is NOT called here — it's called exactly once
    # in app.py (the st.navigation entrypoint). Calling it again here would
    # raise StreamlitAPIException since both scripts run in the same rerun.
    render_header(zone)

    hist_key = init_chat_state(zone.key)
    conv_key = f"conv_id_{zone.key}"

    if not st.session_state[hist_key]:
        clicked = render_sample_questions(zone)
    else:
        clicked = None

    render_history(st.session_state[hist_key])

    question = st.chat_input(f"Ask {zone.title}...") or clicked
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Asking Genie..."):
                answer = client.ask(
                    zone.key, question, conversation_id=st.session_state[conv_key]
                )
            render_answer(answer)
        st.session_state[conv_key] = answer.conversation_id
        st.session_state[hist_key].append({"question": question, "answer": answer})
