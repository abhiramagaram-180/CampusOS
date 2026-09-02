# CampusOS — Project Context

**Hackathon:** PES University CampusOS
**Updated:** 2026-09-02
**Owner:** Person 1 (Lead Integrator)

---

## What We're Building

A chat interface into Databricks where users click a campus zone (Placement Cell, Library, Admin, Faculty, Social Square) and ask natural-language questions against that zone's data. Only Placement is production quality; the other four show the "same architecture" as stubs.

**Core differentiator:** The SQL transparency panel — every answer shows the exact SQL Databricks Genie ran, so users can verify and learn.

---

## Team & Ownership

| Person | Role | Branch |
|---|---|---|
| P1 (YOU) | Lead Integrator & Backend | `feature/integration` |
| P2 | Databricks Architect & Data Lead | `feature/data` |
| P3 | Frontend / UI Developer | `feature/ui` |
| P4 | QA, Testing & Demo Support | (all branches) |

- Only P1 merges to `main`.
- No rebases, no force pushes.

---

## Architecture

```
streamlit app (pages/)
 └─ asks genie_client.py (or mock_client.py)
 └─ calls Databricks Genie API
 └─ queries Unity Catalog tables
 └─ SQL Warehouse computes answer
```

### Data contract

The contract between backend and frontend is `GenieAnswer` (frozen dataclass in `config.py`).

**No field changes after Hour 0 — committed, locked.**

```python
@dataclass(frozen=True)
class GenieAnswer:
 answer_text: str
 data: pl.DataFrame | None
 sql: str | None
 conversation_id: str | None
 error: str | None
```

### Mock mode

Set `MOCK_MODE = True` in `config.py` to use `mock_client.py` (returns fake data in ~1s). Flip to `False` to hit real Databricks.

---

## Databricks Setup (P2 delivers these by Hour ~3)

| Item | Placeholder | Source |
|---|---|---|
| Workspace hostname | — | P2 provides |
| Genie Space ID (Placement) | — | P2 provides |
| SQL Warehouse ID | — | P2 provides |
| Catalog / Schema | `campus.placement` | P2 creates |

Tables:
- `students` — student records (placement-focused columns)
- `companies` — recruiting company data
- `placements` — placement offers/records
- `internships` — internship history

---

## Current Status

| Component | Status | Owner |
|---|---|---|
| `config.py` (`GenieAnswer`) | Planned | P1 |
| `mock_client.py` | Planned | P1 |
| `genie_client.py` | Planned | P1 |
| `app.py` + `pages/` | Planned | P3 |
| `ui/render.py`, `ui/zones.py` | Planned | P3 |
| Tables + synthetic data | Planned | P2 |
| Genie Agent + examples | Planned | P2 |
| Deployment (`app.yaml`) | Planned | P1 |
| DEMO.md | Planned | P1 |
| E2E testing | Planned | P4 |

---

## Key Deadlines

| Time | Milestone |
|---|---|
| Hour 1 | Gate: fake answer renders in UI (chart + SQL panel) |
| Hour 3 | Gate: real Genie call returns rows from Python |
| Hour 4.5 | Gate: real end-to-end question in the app |
| Hour 6.5 | Deploy to Databricks Apps |
| Hour 9.5 | Feature freeze |
| Hour 11 | Submit everything |

---

## Rules

1. One person per file. Message the owner if you need a change.
2. `CONTEXT.md` at the top of every AI session.
3. Ask for one function, not an app (after Hour 3).
4. Verify Databricks APIs against the SDK, not AI memory.
5. Branch per person. Commit every 30 min. P1 only merges to `main`.
6. After Hour 9.5: bug fixes only. No new features.
