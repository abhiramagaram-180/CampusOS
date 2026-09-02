/**
 * server.js — serves the CampusOS 3D game.
 *
 * Deliberately zero-dependency (only Node built-ins) so `node server.js`
 * works immediately without `npm install`. Useful for standalone testing;
 * app.py normally reads game/public/index.html directly and embeds it via
 * components.html, so this server is optional for the Streamlit flow.
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, "public");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
};

// Mirrors mock_client.py's per-zone answers so the standalone game server
// can demo /api/genie/query without the Streamlit/Databricks stack running.
const MOCK_ANSWERS = {
  placement: "340 CSE students were placed in 2024 at an average CTC of ₹12.4 LPA.",
  library: "The reading room is open 8am-10pm on weekdays, 9am-6pm on weekends.",
  canteen: "Today's menu: South Indian breakfast, North Indian thali for lunch, gluten-free salad bar all day.",
  rd: "6 active AI/ML research projects this semester. 3D printer lab has slots Wed/Fri.",
};

function send(res, status, body, contentType) {
  res.writeHead(status, { "Content-Type": contentType });
  res.end(body);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === "/api/genie/query" && req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      let zone = "placement";
      try {
        zone = JSON.parse(body || "{}").zone || "placement";
      } catch (_) {
        /* ignore malformed body, fall back to default zone */
      }
      const answer = MOCK_ANSWERS[zone] || MOCK_ANSWERS.placement;
      send(res, 200, JSON.stringify({ zone, answer_text: answer }), MIME[".json"]);
    });
    return;
  }

  let filePath = path.join(PUBLIC_DIR, url.pathname === "/" ? "index.html" : url.pathname);

  // basic path traversal guard
  if (!filePath.startsWith(PUBLIC_DIR)) {
    send(res, 403, "Forbidden", "text/plain");
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      send(res, 404, "Not found", "text/plain");
      return;
    }
    const ext = path.extname(filePath);
    send(res, 200, data, MIME[ext] || "application/octet-stream");
  });
});

server.listen(PORT, () => {
  console.log(`CampusOS game running at http://localhost:${PORT}`);
});
