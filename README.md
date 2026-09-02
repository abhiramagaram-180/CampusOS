# CampusOS
A 3D campus game with AI Genie agents for each zone. Built with Three.js (HiggsField-compatible) + Streamlit.

## What This Is

You walk around a 3D campus. When you enter a zone (Library, Canteen, R&D), a phone pops up with that zone's Genie assistant. Ask it questions — it talks to Databricks Genie.

## Quick Start

### 1. Start the 3D Game
```bash
cd game
npm install
node server.js
# Opens at http://localhost:3000
```

### 2. Start Streamlit
```bash
pip install streamlit
streamlit run app.py
# Opens at http://localhost:8501
```

## Project Structure
```
campusos/
├── app.py # Main entry — embeds the 3D game
├── pages/
│ ├── library_chat.py # Library Genie chat page
│ ├── canteen_chat.py # Canteen Genie chat page
│ └── rd_chat.py # R&D Genie chat page
├── game/
│ ├── index.html # 3D game HTML entry point
│ ├── public/
│ │ ├── index.html # Served copy
│ │ └── src/main.js # Three.js game engine
│ ├── src/main.js # Game source
│ ├── server.js # Express server for game + API
│ └── package.json
├── config.py # Genie config + zone space IDs
├── mock_client.py # Mock Databricks responses
└── generate_data.py # Synthetic data generation
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

This uses Three.js directly for maximum compatibility. If your team is using HiggsField (Three.js wrapper), the `src/main.js` scene graph and entity system map directly to HiggsField's component API — just replace `THREE.*` calls with HiggsField equivalents.
