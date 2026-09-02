# CampusOS — Demo Script

~3 minutes. Run `streamlit run app.py` first (mock mode is on by default, so
this works with zero Databricks setup).

## 1. Open on the campus (30s)
- Land on the 3D campus. Point out the four buildings: **Placement Cell,
  Library, Canteen, R&D Lab**.
- Click the canvas to lock the mouse, walk with **WASD**, look around.
- Walk toward the Placement building — a green "Press E to enter" prompt
  appears when you're close.

## 2. Enter Placement — the production zone (60s)
- Press **E**. The Placement Cell chat page opens.
- Click a sample question chip (e.g. *"How many CSE students were placed in
  2024?"*) or type your own.
- Highlight the answer, the **data table**, and the **SQL panel** — "every
  answer shows the exact SQL Genie ran, so you can verify it yourself."
- This is the one zone wired to real data end-to-end; the rest use the same
  architecture as stubs (see below).

## 3. Show the architecture repeats (45s)
- Go back to campus (**← Back to campus** button), walk to Library or
  Canteen, press E.
- Same chat UI, same SQL-transparency pattern, different mock data — "adding
  a fifth zone is: register a Genie Space ID, done."

## 4. Under the hood (30s)
- `config.py` — the frozen `GenieAnswer` contract every client conforms to.
- `client.py` — one line (`MOCK_MODE`) switches every zone between
  `mock_client.py` and real `genie_client.py` / Databricks Genie.
- `game/public/` — Three.js, zero build step, communicates with Streamlit
  via `postMessage` when you walk into a building.

## 5. Close (15s)
- Mention what's next: wire the remaining 3 Genie Spaces, deploy via
  `app.yaml` to Databricks Apps, swap the low-poly buildings for the real
  campus reference photos.

---

### If live Databricks is connected
Set `CAMPUSOS_MOCK=false` and the four `CAMPUSOS_*_SPACE_ID` env vars —
everything above is identical, just backed by real Genie + Unity Catalog
data instead of `mock_client.py`.
