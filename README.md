# CampusOS
A 3D campus game with AI Genie agents for each zone. Built with Three.js (HiggsField-compatible) + Streamlit.

## What This Is

You walk around a 3D campus. When you enter a zone (Library, Canteen, R&D), a phone pops up with that zone's Genie assistant. Ask it questions — it talks to Databricks Genie.

## Quick Start

Just run Streamlit — `app.py` reads the game files straight off disk and
inlines them into the page, so **no separate game server or npm install is
required** for the normal flow:

```bash
pip install -r requirements.txt
streamlit run app.py
# Opens at http://localhost:8501, mock mode on by default (CAMPUSOS_MOCK=true)
```

`game/server.js` is optional and only for testing the 3D scene standalone in
a plain browser tab (no Streamlit, no zone chat — just movement/collision):

```bash
cd game
node server.js
# Opens at http://localhost:3000 (zero dependencies, no npm install needed)
```

## Project Structure
```
campusos/
├── app.py              # Main entry — embeds the 3D game, page nav, bridge
├── client.py            # ask(zone, question) → routes to mock or real Genie
├── config.py             # GenieAnswer contract + zone space IDs (frozen)
├── mock_client.py         # Per-zone fake Genie answers for dev/demo
├── genie_client.py         # Real Databricks Genie + SQL Warehouse client
├── requirements.txt
├── app.yaml               # Databricks Apps deploy manifest
├── DEMO.md                 # 3-minute demo script
├── pages/
│   ├── placement_chat.py     # Production zone (real architecture, live data)
│   ├── library_chat.py        # Same architecture, stub
│   ├── canteen_chat.py         # Same architecture, stub
│   └── rd_chat.py                # Same architecture, stub
├── ui/
│   ├── zones.py                   # Single source of truth for zone metadata
│   └── render.py                    # Shared chat/SQL-panel rendering + run_zone_page()
├── game/
│   ├── package.json
│   ├── server.js                     # Optional zero-dependency standalone server
│   └── public/
│       ├── index.html                 # 3D game HTML shell (Three.js via CDN)
│       └── src/main.js                 # Game logic: movement, buildings, zone triggers
├── generate_data.py                      # Synthetic data → Databricks (full dataset)
└── generate_placement_data.py             # Synthetic data → Databricks (placement only)
```

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrows | Move player |
| Click building | Walk toward it |
| Walk into zone | Opens phone with Genie |

## Zones

| Zone | Icon | Genie | Ask about |
|------|------|-------|-----------|
| Library | 📚 | Library Genie | Books, study rooms, research papers, hours |
| Canteen | 🍽️ | Canteen Genie | Menu, timings, nutrition, dietary options |
| R&D Lab | 🔬 | R&D Genie | Projects, publications, equipment, jobs |

## Architecture

```
┌─────────────────────────────────────────┐
│ Streamlit (port 8501) │
│ ├── app.py — embeds 3D game │
│ ├── pages/library_chat.py │
│ ├── pages/canteen_chat.py │
│ └── pages/rd_chat.py │
│ │ │
│ ▼ postMessage │
├─────────────────────────────────────────┤
│ Game Server (port 3000) │
│ ├── Serves Three.js game │
│ ├── /api/genie/query → Streamlit/Databricks │
│ └── Mock responses for dev │
└─────────────────────────────────────────┘
```

## Connecting Real Databricks Genie

Set these environment variables:
```bash
export CAMPUSOS_LIBRARY_SPACE_ID="your-space-id"
export CAMPUSOS_CANTEEN_SPACE_ID="your-space-id"
export CAMPUSOS_RD_SPACE_ID="your-space-id"
export CAMPUSOS_WAREHOUSE_ID="your-warehouse-id"
export DATABRICKS_HOST="https://your-workspace.azuredatabricks.net"
```

Then in `game/server.js`, set the endpoint URLs:
```js
const ZONE_ENDPOINTS = {
 library: 'http://localhost:8501/library_chat',
 canteen: 'http://localhost:8501/canteen_chat',
 rd: 'http://localhost:8501/rd_chat',
};
```

## HiggsField

The current `game/public/src/main.js` is plain Three.js (loaded from CDN via
an import map, no build step) so it runs anywhere without extra tooling.
Swapping in HiggsField-generated 3D assets (e.g. building meshes closer to
the real campus reference photos) is additive: drop `.glb` files in
`game/public/assets/` and load them with Three's `GLTFLoader` in place of
the current primitive-geometry buildings — the movement, collision, and
zone-trigger code doesn't need to change.
