/**
 * CampusOS Game Server
 *
 * Serves the 3D game frontend and proxies Genie queries
 * to the Streamlit backend (or directly to Databricks).
 */

const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

/* ============================================================
 HEALTH CHECK
============================================================ */
app.get('/api/health', (req, res) => {
 res.json({ status: 'ok', service: 'campusos-game' });
});

/* ============================================================
 GENIE QUERY PROXY
============================================================ */

/**
 * Zone → Streamlit endpoint mapping
 * The game sends queries here; we forward to Streamlit or mock.
 */
const ZONE_ENDPOINTS = {
 library: process.env.CAMPUSOS_LIBRARY_ENDPOINT || null,
 canteen: process.env.CAMPUSOS_CANTEEN_ENDPOINT || null,
 rd: process.env.CAMPUSOS_RD_ENDPOINT || null,
};

app.post('/api/genie/query', async (req, res) => {
 const { zone, question } = req.body;

 if (!zone || !question) {
 return res.status(400).json({ error: 'zone and question are required' });
 }

 // If we have a real Streamlit endpoint for this zone, proxy it
 const endpoint = ZONE_ENDPOINTS[zone];
 if (endpoint) {
 try {
 const response = await fetch(endpoint, {
 method: 'POST',
 headers: { 'Content-Type': 'application/json' },
 body: JSON.stringify({ question }),
 });
 const data = await response.json();
 return res.json(data);
 } catch (err) {
 console.error(`Error querying ${zone} Genie:`, err);
 // Fall through to mock response
 }
 }

 // Mock response when no real endpoint is configured
 const mockResponses = getMockResponse(zone, question);
 res.json({
 answer: mockResponses,
 zone,
 question,
 source: 'mock',
 timestamp: new Date().toISOString(),
 });
});

function getMockResponse(zone, question) {
 const q = question.toLowerCase();
 const responses = {
 library: {
 default: "I found some resources related to your query. The library has extended hours during exam season.",
 hours: "The library is open 8 AM to 11 PM on weekdays, and 9 AM to 9 PM on weekends.",
 book: "I searched our catalog and found 3 relevant books. Would you like me to reserve one?",
 study: "There are 5 study rooms available right now. Want me to book one for you?",
 },
 canteen: {
 default: "Here's what I found about the canteen. Would you like today's menu?",
 menu: "Today: Breakfast — Idli/Dosa/Poha | Lunch — Rice, Roti, Dal, Veg Curry | Snacks — Samosa, Juice",
 timing: "Breakfast: 7:30-10 AM | Lunch: 12-2 PM | Snacks: 4-6 PM | Dinner: 7:9 PM",
 veg: "Yes! We have dedicated veg counters and Jain options. Items #7 and #12 are vegan.",
 },
 rd: {
 default: "Great question! The R&D lab currently has 3 active projects that might interest you.",
 project: "Current projects: AI Navigation, Smart Campus IoT, and Blockchain Certificates.",
 publish: "5 papers published this semester — 2 at IEEE, 2 at ACM, 1 at Springer.",
 equipment: "You can book lab equipment through the portal. Need help with that?",
 },
 };

 const zoneResponses = responses[zone] || responses.library;

 // Try to find a keyword match
 for (const [keyword, answer] of Object.entries(zoneResponses)) {
 if (keyword !== 'default' && q.includes(keyword)) {
 return answer;
 }
 }

 return zoneResponses.default || "I'm here to help! Ask me anything about this zone.";
}

/* ============================================================
 STREAMLIT INTEGRATION — MESSAGE BRIDGE
============================================================ */

/**
 * When the game is embedded in Streamlit via components.html,
 * it receives queries via window.postMessage.
 * This endpoint can also serve as the target.
 */

app.post('/api/game/query', async (req, res) => {
 const { zone, question } = req.body;

 // Forward to the matching Streamlit page if configured
 const streamlitPages = {
 library: '/library_chat',
 canteen: '/canteen_chat',
 rd: '/rd_chat',
 };

 const targetPage = streamlitPages[zone];
 if (targetPage) {
 // In production, this would forward to the Streamlit backend
 // For now, return a mock response
 res.json({
 type: 'campusos-genie-response',
 zone,
 question,
 answer: getMockResponse(zone, question),
 });
 } else {
 res.json({
 type: 'campusos-genie-response',
 zone,
 question,
 answer: "This zone's Genie is coming soon!",
 });
 }
});

/* ============================================================
 BUILD: Copy game files to public/
============================================================ */

const fs = require('fs');
const { execSync } = require('child_process');

// Ensure public directory exists with game files
const publicDir = path.join(__dirname, 'public');
const srcDir = path.join(__dirname, 'src');

if (!fs.existsSync(publicDir)) {
 fs.mkdirSync(publicDir, { recursive: true });
}

// Copy index.html to public
if (fs.existsSync(path.join(__dirname, 'index.html'))) {
 fs.copyFileSync(
 path.join(__dirname, 'index.html'),
 path.join(publicDir, 'index.html')
 );
}

// Copy src to public
if (fs.existsSync(srcDir)) {
 copyDirSync(srcDir, path.join(publicDir, 'src'));
}

function copyDirSync(src, dest) {
 if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
 const entries = fs.readdirSync(src, { withFileTypes: true });
 for (const entry of entries) {
 const srcPath = path.join(src, entry.name);
 const destPath = path.join(dest, entry.name);
 if (entry.isDirectory()) {
 copyDirSync(srcPath, destPath);
 } else {
 fs.copyFileSync(srcPath, destPath);
 }
 }
}

// Start server
app.listen(PORT, () => {
 console.log(`\n🎮 CampusOS Game Server running at http://localhost:${PORT}`);
 console.log(`📡 API available at http://localhost:${PORT}/api`);
 console.log(`\nZone endpoints:`);
 Object.entries(ZONE_ENDPOINTS).forEach(([zone, ep]) => {
 console.log(` ${zone}: ${ep || 'mock mode'}`);
 });
});
