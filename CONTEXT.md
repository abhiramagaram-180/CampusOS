# CONTEXT.md — paste this at the top of EVERY AI coding session

Keep this under one page. Person 1 owns it. Person 2 updates the data section.

---

## What we're building

CampusOS: a Streamlit app showing a PES campus map. Click a zone → chat page →
ask a plain-English question → a Databricks Genie Agent turns it into SQL, runs
it against Unity Catalog tables, and returns rows + a summary. We display the
answer, a chart, and the generated SQL.

Only the **Placement Cell** zone is built. The other four are styled stubs.

## Tech constraints — do not violate

- Streamlit only (Databricks Apps supports it natively). No React.
- Databricks **Free Edition**: ONE app, ONE 2X-Small SQL warehouse, no account console.
- No external API calls from the deployed app (outbound internet is restricted).
- No localStorage/sessionStorage. Use `st.session_state`.
- Do not call Claude/Llama model-serving endpoints — restricted on Free Edition.

## THE CONTRACT — frozen, do not change field names

```python
@dataclass
class GenieAnswer:
    text: str                              # summary from Genie
    sql: Optional[str] = None              # generated SQL, for the transparency panel
    df: Optional[pd.DataFrame] = None      # result rows, or None if text-only
    conversation_id: Optional[str] = None  # pass back for follow-ups
    error: Optional[str] = None            # set on failure; text will be empty

def ask_genie(zone: str, question: str, conversation_id: str | None = None) -> GenieAnswer
```

The frontend only ever writes:

```python
from genie_client import ask_genie
answer = ask_genie("placement", prompt, st.session_state.get("conv_id"))
st.session_state["conv_id"] = answer.conversation_id
```

`ask_genie` never raises. Failures come back as `answer.error`.

## File ownership — nobody edits another person's files

| File | Owner |
|---|---|
| `config.py`, `genie_client.py`, `mock_client.py`, `test_client.py` | P1 |
| `app.yaml`, `requirements.txt`, `.gitignore` | P1 |
| `app.py`, `pages/zone_chat.py`, `ui/render.py`, `ui/zones.py`, `assets/` | P3 |
| `notebooks/*`, `genie/*` | P2 |
| `DEMO.md` | P1 (P2 supplies the questions) |

If you need a change in someone else's file — message them. Do not edit it.

## Current status  <!-- UPDATE THIS AS YOU GO -->

- [ ] Contract agreed and committed (hour 0)
- [ ] Mock client working, UI renders a fake answer (hour 1)
- [ ] Tables created with comments (hour 3)
- [ ] Genie Agent created, space ID handed to P1 (hour 3)
- [ ] First real end-to-end answer in the app (hour 4.5)
- [ ] 10 demo questions verified (hour 6.5)
- [ ] Deployed to Databricks Apps, opens on another device (hour 7.5)
- [ ] FEATURE FREEZE (hour 9.5)
- [ ] Backup video recorded

## Data model  <!-- P2 FILLS THIS IN AT HOUR 3 -->

Catalog/schema: `campus.placement`

| Table | Columns |
|---|---|
| `students` | TBD |
| `companies` | TBD |
| `drives` | TBD |
| `offers` | TBD |

## Rules for AI assistance

1. Ask for ONE function or a diff. Never a whole-file rewrite after hour 3.
2. Verify Databricks SDK method names with `dir(w.genie)` — the API gets renamed.
3. Never run git commands that rewrite history (rebase, force push, reset).
4. After hour 9.5: bug fixes only. Discard any response containing changes you
   didn't ask for.
