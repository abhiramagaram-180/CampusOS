import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
 CONFIG
============================================================ */
const CONFIG = {
 player: { speed: 0.12, height: 1.7, eyeHeight: 1.5 },
 camera: { height: 25, distance: 75, minDistance: 10, maxDistance: 100, minHeight: 5, maxHeight: 50, smoothness: 0.06 },
 zones: {
 library: { icon: '📚', agent: 'Library Genie', name: 'Library', description: 'Ask about books, study rooms, research papers & more', sampleQuestions: ['When does the library close?', 'How do I book a study room?', 'How many books are in the collection?'] },
 canteen: { icon: '🍽️', agent: 'Canteen Genie', name: 'Canteen', description: 'Menu, timings, nutrition info & dietary options', sampleQuestions: ["What's today's special?", 'Are there veg options?', 'How do I recharge my meal card?'] },
 rd: { icon: '🔬', agent: 'R&D Genie', name: 'R&D Lab', description: 'Projects, publications, lab equipment & research', sampleQuestions: ['What research projects are active?', 'How do I join a research team?', 'What equipment is available?'] },
 placement: { icon: '💼', agent: 'Placement Genie', name: 'Placement Cell', description: 'Companies, internships, resume tips & interview prep', sampleQuestions: ['Which companies are recruiting?', 'How do I prepare for interviews?', 'What is the average package?'] },
 },
 campus: { width: 100, depth: 80, groundColor: 0x1a3320 },
};

/* ============================================================
 BUILDINGS - PESU Campus Layout
============================================================ */
const BUILDINGS = {
 library: { x: -30, z: -20, w: 18, d: 16, h: 7, color: 0x5588aa, accent: 0x77aacc, emoji: '📚' },
 canteen: { x: -30, z: 22, w: 18, d: 16, h: 6, color: 0xaa7744, accent: 0xcc9955, emoji: '🍽️' },
 rdLab: { x: 28, z: -8, w: 20, d: 18, h: 7, color: 0x7755aa, accent: 0x9977cc, emoji: '🔬' },
 placement: { x: 28, z: 22, w: 18, d: 16, h: 6, color: 0x44aa88, accent: 0x66ccaa, emoji: '💼' },
};

/* ============================================================
 GLOBALS
============================================================ */
let scene, camera, renderer, clock, controls;
let player, playerGroup;
let buildings = {};
let npcs = [];
let currentZone = null;
let phoneVisible = false;

const keys = {};

/* ============================================================
 HELPERS
============================================================ */
function getZoneColor(zoneKey) {
 switch (zoneKey) {
 case 'library': return 0x5588aa;
 case 'canteen': return 0xaa7744;
 case 'rd': return 0x7755aa;
 case 'placement': return 0x44aa88;
 default: return 0xffffff;
 }
}

function detectZone(x, z) {
 for (const [key, bld] of Object.entries(BUILDINGS)) {
 const hw = bld.w / 2 + 2;
 const hd = bld.d / 2 + 2;
 if (x >= bld.x - hw && x <= bld.x + hw && z >= bld.z - hd && z <= bld.z + hd) {
 return key;
 }
 }
 return null;
}

function hexToRgbStr(hex) {
 const r = (hex >> 16) & 0xff;
 const g = (hex >> 8) & 0xff;
 const b = hex & 0xff;
 return r + ',' + g + ',' + b;
}

/* ============================================================
 SCENE SETUP
============================================================ */
function initScene() {
 scene = new THREE.Scene();
 scene.background = new THREE.Color(0x87ceeb);
 scene.fog = new THREE.FogExp2(0x87ceeb, 0.004);

 camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
 camera.position.set(0, 25, 75);

 renderer = new THREE.WebGLRenderer({ antialias: true });
 renderer.setSize(window.innerWidth, window.innerHeight);
 renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
 renderer.shadowMap.enabled = true;
 renderer.shadowMap.type = THREE.PCFSoftShadowMap;
 renderer.domElement.style.display = 'block';
 document.body.appendChild(renderer.domElement);

 clock = new THREE.Clock();

 scene.add(new THREE.AmbientLight(0xffffff, 0.4));

 const dir = new THREE.DirectionalLight(0xffffff, 0.8);
 dir.position.set(30, 50, 20);
 dir.castShadow = true;
 dir.shadow.mapSize.set(2048, 2048);
 dir.shadow.camera.left = -60;
 dir.shadow.camera.right = 60;
 dir.shadow.camera.top = 60;
 dir.shadow.camera.bottom = -60;
 dir.shadow.camera.near = 0.5;
 dir.shadow.camera.far = 200;
 dir.shadow.bias = -0.0005;
 scene.add(dir);

 scene.add(new THREE.HemisphereLight(0x87ceeb, 0x362907, 0.3));

 controls = new OrbitControls(camera, renderer.domElement);
 controls.target.set(0, 0, 0);
 controls.enableDamping = true;
 controls.dampingFactor = 0.08;
 controls.minDistance = 20;
 controls.maxDistance = 120;
 controls.maxPolarAngle = Math.PI / 2.1;
 controls.update();
}

/* ============================================================
 GROUND & ENVIRONMENT
============================================================ */
function createGround() {
 const geo = new THREE.PlaneGeometry(CONFIG.campus.width + 40, CONFIG.campus.depth + 40);
 const mat = new THREE.MeshLambertMaterial({ color: 0x3d7a3d });
 const mesh = new THREE.Mesh(geo, mat);
 mesh.rotation.x = -Math.PI / 2;
 mesh.receiveShadow = true;
 scene.add(mesh);

 const pMat = new THREE.MeshLambertMaterial({ color: 0xcccccc });
 const paths = new THREE.Group();
 addPath(paths, pMat, 0, 0.02, CONFIG.campus.width + 4, 2.5);
 addPath(paths, pMat, 0, 0.02, 2.5, CONFIG.campus.depth + 4);
 scene.add(paths);

 const treePositions = [[-15,-15],[15,-15],[-15,15],[15,15],[-40,0],[40,0],[0,-30],[0,30],[-10,-40],[10,40]];
 for (const [tx, tz] of treePositions) addTree(tx, tz);
}

function addPath(group, mat, x, y, w, d) {
 const geo = new THREE.PlaneGeometry(w, d);
 const mesh = new THREE.Mesh(geo, mat);
 mesh.rotation.x = -Math.PI / 2;
 mesh.position.set(x, y, 0);
 mesh.receiveShadow = true;
 group.add(mesh);
}

function addTree(x, z) {
 const g = new THREE.Group();
 const trunk = new THREE.Mesh(
 new THREE.CylinderGeometry(0.2, 0.3, 1.5, 6),
 new THREE.MeshLambertMaterial({ color: 0x8B4513 })
 );
 trunk.position.y = 0.75;
 trunk.castShadow = true;
 g.add(trunk);

 const leaves = new THREE.Mesh(
 new THREE.SphereGeometry(1.2, 8, 6),
 new THREE.MeshLambertMaterial({ color: 0x2d8a2d })
 );
 leaves.position.y = 2;
 leaves.castShadow = true;
 g.add(leaves);

 g.position.set(x, 0, z);
 scene.add(g);
}

/* ============================================================
 BUILDINGS
============================================================ */
function createBuildings() {
 for (const [key, bld] of Object.entries(BUILDINGS)) {
 const group = new THREE.Group();
 group.position.set(bld.x, 0, bld.z);

 const body = new THREE.Mesh(
 new THREE.BoxGeometry(bld.w, bld.h, bld.d),
 new THREE.MeshLambertMaterial({ color: bld.color })
 );
 body.position.y = bld.h / 2;
 body.castShadow = true;
 body.receiveShadow = true;
 body.userData = { zoneKey: key };
 group.add(body);

 addRoof(group, bld);
 addWindows(group, bld);
 addDoor(group, bld);
 addLabel(group, bld, key);

 scene.add(group);
 buildings[key] = group;
 }
}

function addRoof(group, bld) {
 const roof = new THREE.Mesh(
 new THREE.ConeGeometry(Math.max(bld.w, bld.d) * 0.75, 1.5, 4),
 new THREE.MeshLambertMaterial({ color: 0x444444 })
 );
 roof.position.y = bld.h + 0.75;
 roof.rotation.y = Math.PI / 4;
 roof.castShadow = true;
 group.add(roof);
}

function addWindows(group, bld) {
 const wGeo = new THREE.PlaneGeometry(1.2, 1.2);
 const wMat = new THREE.MeshLambertMaterial({ color: 0xaaddff, emissive: 0x334455, side: THREE.DoubleSide });
 const rows = Math.floor(bld.h / 2.5);
 const cols = Math.floor(bld.w / 3);

 for (let r = 0; r < rows; r++) {
 for (let c = 0; c < cols; c++) {
 const win = new THREE.Mesh(wGeo, wMat);
 win.position.set(-bld.w / 2 + 2 + c * 3, 1.5 + r * 2.5, bld.d / 2 + 0.05);
 group.add(win);
 }
 }
}

function addDoor(group, bld) {
 const door = new THREE.Mesh(
 new THREE.PlaneGeometry(1.8, 2.5),
 new THREE.MeshLambertMaterial({ color: 0x5c3a21, side: THREE.DoubleSide })
 );
 door.position.set(0, 1.25, bld.d / 2 + 0.05);
 group.add(door);

 const steps = new THREE.Mesh(
 new THREE.BoxGeometry(bld.w * 0.4, 0.4, 1.5),
 new THREE.MeshLambertMaterial({ color: 0x888888 })
 );
 steps.position.set(0, 0.2, bld.d / 2 + 0.75);
 steps.receiveShadow = true;
 group.add(steps);
}

function addLabel(group, bld, key) {
 const canvas = document.createElement('canvas');
 canvas.width = 256; canvas.height = 64;
 const ctx = canvas.getContext('2d');
 if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(4, 4, 248, 56, 8); ctx.fillStyle='rgba(0,0,0,0.45)'; ctx.fill(); }
 ctx.font = 'bold 24px sans-serif';
 ctx.textAlign = 'center';
 ctx.textBaseline = 'middle';
 ctx.fillStyle = '#ffffff';
 ctx.fillText(bld.emoji + ' ' + key.toUpperCase(), 128, 32);
 const tex = new THREE.CanvasTexture(canvas);
 const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false }));
 sprite.position.set(0, bld.h + 3, 0);
 sprite.scale.set(8, 2, 1);
 group.add(sprite);
}

/* ============================================================
 PLAYER
============================================================ */
function createPlayer() {
 playerGroup = new THREE.Group();

 const body = new THREE.Mesh(
 new THREE.CapsuleGeometry(0.35, 0.8, 4, 8),
 new THREE.MeshLambertMaterial({ color: 0x2244aa })
 );
 body.position.y = 0.95;
 body.castShadow = true;
 playerGroup.add(body);

 const head = new THREE.Mesh(
 new THREE.SphereGeometry(0.3, 16, 12),
 new THREE.MeshLambertMaterial({ color: 0xffcc99 })
 );
 head.position.y = 1.7;
 head.castShadow = true;
 playerGroup.add(head);

 const arrow = new THREE.Mesh(
 new THREE.ConeGeometry(0.3, 0.6, 4),
 new THREE.MeshLambertMaterial({ color: 0xff4444 })
 );
 arrow.position.set(0, 2.3, 0);
 arrow.rotation.x = Math.PI;
 arrow.name = 'directionArrow';
 playerGroup.add(arrow);

 playerGroup.position.set(0, 0, 5);
 scene.add(playerGroup);
 player = playerGroup;
}

/* ============================================================
 NPCs
============================================================ */
function createNPCs() {
 const npcData = [
 { x: -20, z: -10, zone: 'library', name: 'Librarian Priya', color: 0x5588aa },
 { x: -20, z: -25, zone: 'library', name: 'Student Arjun', color: 0x77aacc },
 { x: -20, z: 18, zone: 'canteen', name: 'Chef Ramesh', color: 0xaa7744 },
 { x: -18, z: 30, zone: 'canteen', name: 'Student Sneha', color: 0xcc9955 },
 { x: 20, z: -5, zone: 'rd', name: 'Dr. Sharma', color: 0x7755aa },
 { x: 35, z: -10, zone: 'rd', name: 'Researcher Karthik', color: 0x9977cc },
 { x: 20, z: 18, zone: 'placement', name: 'Coordinator Meera', color: 0x44aa88 },
 { x: 35, z: 25, zone: 'placement', name: 'Student Vikram', color: 0x66ccaa },
 ];

 for (const data of npcData) {
 const g = new THREE.Group();
 const body = new THREE.Mesh(
 new THREE.CapsuleGeometry(0.25, 0.6, 4, 8),
 new THREE.MeshLambertMaterial({ color: data.color })
 );
 body.position.y = 0.7;
 body.castShadow = true;
 g.add(body);

 const head = new THREE.Mesh(
 new THREE.SphereGeometry(0.22, 12, 8),
 new THREE.MeshLambertMaterial({ color: 0xffcc99 })
 );
 head.position.y = 1.35;
 g.add(head);

 g.position.set(data.x, 0, data.z);
 g.userData = { zone: data.zone, name: data.name, baseX: data.x, baseZ: data.z, phase: Math.random() * Math.PI * 2 };
 scene.add(g);
 npcs.push(g);
 }
}

/* ============================================================
 CAMERA & CONTROLS
============================================================ */
function updateCameraPosition() {
 if (!player) return;
 controls.target.lerp(new THREE.Vector3(player.position.x, 0, player.position.z), 0.1);
 controls.update();
}

/* ============================================================
 INPUT
============================================================ */
function initInput() {
 document.addEventListener('keydown', (e) => { keys[e.key.toLowerCase()] = true; });
 document.addEventListener('keyup', (e) => { keys[e.key.toLowerCase()] = false; });
 renderer.domElement.addEventListener('contextmenu', (e) => e.preventDefault());

 window.addEventListener('resize', () => {
 camera.aspect = window.innerWidth / window.innerHeight;
 camera.updateProjectionMatrix();
 renderer.setSize(window.innerWidth, window.innerHeight);
 });

 window.addEventListener('message', (e) => {
 if (e.data && e.data.type === 'campusos-query') {
 handleGenieQuery(e.data.zone, e.data.question);
 }
 });
}

/* ============================================================
 PLAYER MOVEMENT
============================================================ */
function updatePlayer(dt) {
 if (!player) return;
 let dx = 0, dz = 0;
 if (keys['w'] || keys['arrowup']) dz -= 1;
 if (keys['s'] || keys['arrowdown']) dz += 1;
 if (keys['a'] || keys['arrowleft']) dx -= 1;
 if (keys['d'] || keys['arrowright']) dx += 1;

 if (dx !== 0 || dz !== 0) {
 const len = Math.sqrt(dx * dx + dz * dz);
 dx /= len;
 dz /= len;
 const angle = -controls.getAzimuthalAngle() + Math.PI / 2;
 const rx = dx * Math.cos(angle) - dz * Math.sin(angle);
 const rz = dx * Math.sin(angle) + dz * Math.cos(angle);
 const speed = CONFIG.player.speed * (dt * 60);
 const hw = CONFIG.campus.width / 2 - 1;
 const hd = CONFIG.campus.depth / 2 - 1;
 player.position.x = Math.max(-hw, Math.min(hw, player.position.x + rx * speed));
 player.position.z = Math.max(-hd, Math.min(hd, player.position.z + rz * speed));

 const targetRot = Math.atan2(dx, dz);
 let diff = targetRot - player.rotation.y;
 while (diff > Math.PI) diff -= Math.PI * 2;
 while (diff < -Math.PI) diff += Math.PI * 2;
 player.rotation.y += diff * 0.15;
 }
}

/* ============================================================
 ZONE DETECTION & PHONE UI
============================================================ */
function updateZone() {
 if (!player) return;
 const zone = detectZone(player.position.x, player.position.z);
 if (zone !== currentZone) {
 currentZone = zone;
 updateZoneIndicator();
 if (zone) {
 showPhoneHint(zone);
 } else {
 hidePhoneHint();
 }
 }
}

function updateZoneIndicator() {
 let el = document.getElementById('zone-indicator');
 if (!el) {
 el = document.createElement('div');
 el.id = 'zone-indicator';
 el.style.cssText = 'position:absolute;top:20px;left:50%;transform:translateX(-50%);padding:8px 20px;border-radius:20px;font:bold 14px sans-serif;color:#fff;background:rgba(0,0,0,0.6);backdrop-filter:blur(10px);transition:all 0.4s ease;z-index:10;pointer-events:none;';
 document.body.appendChild(el);
 }
 if (currentZone && CONFIG.zones[currentZone]) {
 const z = CONFIG.zones[currentZone];
 const rgb = hexToRgbStr(getZoneColor(currentZone));
 el.innerHTML = z.icon + ' ' + z.name;
 el.style.background = 'rgba(' + rgb + ',0.75)';
 el.style.opacity = '1';
 } else {
 el.innerHTML = '🏫 PESU Campus';
 el.style.background = 'rgba(0,0,0,0.6)';
 }
}

function showPhoneHint(zoneKey) {
 if (phoneVisible) return;
 const z = CONFIG.zones[zoneKey];
 const rgb = hexToRgbStr(getZoneColor(zoneKey));
 let hint = document.getElementById('phone-hint');
 if (!hint) {
 hint = document.createElement('div');
 hint.id = 'phone-hint';
 hint.style.cssText = 'position:absolute;bottom:100px;left:50%;transform:translateX(-50%);padding:10px 24px;border-radius:25px;font:bold 14px sans-serif;color:#fff;background:rgba(' + rgb + ',0.85);backdrop-filter:blur(10px);cursor:pointer;z-index:20;transition:all 0.3s ease;white-space:nowrap;box-shadow:0 4px 20px rgba(0,0,0,0.3);';
 hint.innerHTML = '📱 Tap to open ' + z.icon + ' ' + z.agent;
 hint.onclick = () => openPhone(zoneKey);
 document.body.appendChild(hint);
 }
}

function hidePhoneHint() {
 const hint = document.getElementById('phone-hint');
 if (hint) hint.remove();
 if (phoneVisible) closePhone();
}

function openPhone(zoneKey) {
 phoneVisible = true;
 const z = CONFIG.zones[zoneKey];
 const color = '#' + getZoneColor(zoneKey).toString(16).padStart(6, '0');

 let phone = document.getElementById('phone-ui');
 if (!phone) {
 phone = document.createElement('div');
 phone.id = 'phone-ui';
 phone.style.cssText = 'position:absolute;bottom:0;left:50%;transform:translateX(-50%) translateY(100%);width:380px;max-width:92vw;height:60vh;background:#1a1a2e;border-radius:24px 24px 0 0;box-shadow:0 -5px 30px rgba(0,0,0,0.5);transition:transform 0.4s cubic-bezier(0.16,1,0.3,1);z-index:30;overflow:hidden;display:flex;flex-direction:column;';
 document.body.appendChild(phone);
 buildPhoneUI(phone, zoneKey);
 }
 phone.style.transform = 'translateX(-50%) translateY(0)';
}

function closePhone() {
 phoneVisible = false;
 const phone = document.getElementById('phone-ui');
 if (phone) {
 phone.style.transform = 'translateX(-50%) translateY(100%)';
 setTimeout(() => { if (phone.parentNode) phone.remove(); }, 400);
 }
}

function buildPhoneUI(phone, zoneKey) {
 const z = CONFIG.zones[zoneKey];
 const color = '#' + getZoneColor(zoneKey).toString(16).padStart(6, '0');

 const header = document.createElement('div');
 header.style.cssText = 'background:' + color + ';padding:16px 20px;color:#fff;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;';
 header.innerHTML = '<div style="display:flex;align-items:center;gap:10px;"><span style="font-size:24px;">' + z.icon + '</span><div><div style="font:bold 16px sans-serif;">' + z.agent + '</div><div style="font-size:11px;opacity:0.8;">' + z.description + '</div></div></div><button id="phone-close" style="background:rgba(255,255,255,0.2);border:none;color:#fff;width:30px;height:30px;border-radius:50%;cursor:pointer;font-size:16px;line-height:1;">✕</button>';
 phone.appendChild(header);
 document.getElementById('phone-close').onclick = closePhone;

 const chat = document.createElement('div');
 chat.id = 'phone-chat';
 chat.style.cssText = 'flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;';
 phone.appendChild(chat);

 const inputArea = document.createElement('div');
 inputArea.style.cssText = 'padding:12px 16px;border-top:1px solid rgba(255,255,255,0.1);display:flex;gap:8px;flex-shrink:0;';
 inputArea.innerHTML = '<input id="phone-input" type="text" placeholder="Ask ' + z.name + '..." style="flex:1;padding:10px 16px;border-radius:20px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.1);color:#fff;font:14px sans-serif;outline:none;" /><button id="phone-send" style="background:' + color + ';border:none;color:#fff;width:40px;height:40px;border-radius:50%;cursor:pointer;font-size:16px;flex-shrink:0;">▶</button>';
 phone.appendChild(inputArea);

 const input = document.getElementById('phone-input');
 const sendBtn = document.getElementById('phone-send');

 function sendMessage() {
 const q = input.value.trim();
 if (!q) return;
 addBubble(chat, q, 'user');
 input.value = '';
 sendBtn.disabled = true;
 sendBtn.style.opacity = '0.5';
 const botBubble = addBubble(chat, 'Thinking…', 'bot', true);
 setTimeout(() => {
 botBubble.querySelector('.chat-text').textContent = generateResponse(zoneKey, q);
 botBubble.querySelector('.chat-text').dataset.loading = 'false';
 sendBtn.disabled = false;
 sendBtn.style.opacity = '1';
 chat.scrollTop = chat.scrollHeight;
 }, 1200 + Math.random() * 800);
 }

 sendBtn.onclick = sendMessage;
 input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });

 addSamples(chat, zoneKey);
 input.focus();
}

function addBubble(container, text, type, loading) {
 const bubble = document.createElement('div');
 bubble.style.cssText = 'max-width:80%;padding:10px 14px;border-radius:16px;font:14px sans-serif;line-height:1.4;word-wrap:break-word;';
 if (type === 'user') {
 bubble.style.cssText += 'background:rgba(255,255,255,0.15);color:#fff;align-self:flex-end;border-bottom-right-radius:4px;';
 } else {
 bubble.style.cssText += 'background:rgba(255,255,255,0.08);color:#e0e0e0;align-self:flex-start;border-bottom-left-radius:4px;';
 }
 const txt = document.createElement('div');
 txt.className = 'chat-text';
 txt.textContent = text;
 txt.dataset.loading = loading ? 'true' : 'false';
 bubble.appendChild(txt);
 container.appendChild(bubble);
 container.scrollTop = container.scrollHeight;
 return bubble;
}

function addSamples(chat, zoneKey) {
 const z = CONFIG.zones[zoneKey];
 if (!z.sampleQuestions) return;
 for (const q of z.sampleQuestions) {
 const btn = document.createElement('button');
 btn.style.cssText = 'background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#aaa;padding:6px 12px;border-radius:12px;font:12px sans-serif;cursor:pointer;text-align:left;transition:background 0.2s;';
 btn.textContent = q;
 btn.onclick = () => {
 document.getElementById('phone-input').value = q;
 document.getElementById('phone-send').click();
 };
 btn.onmouseenter = () => btn.style.background = 'rgba(255,255,255,0.15)';
 btn.onmouseleave = () => btn.style.background = 'rgba(255,255,255,0.08)';
 chat.appendChild(btn);
 }
}

function generateResponse(zoneKey, question) {
 const responses = {
 library: ['The library has over 50,000 books across all engineering disciplines. Study rooms are available on the 2nd floor — book them via the PESU app. The digital library offers 24/7 access to research papers through IEEE and ACM.', 'Library hours: 8:00 AM to 11:00 PM on weekdays, 9:00 AM to 8:00 PM on weekends. The reference section closes at 8 PM. We have a new AI-powered research assistant in the digital lab.', 'Yes! We have 3 group study rooms (4-6 people each) and 12 individual carrels. Room booking opens 2 days in advance. Quiet study floors are on levels 2 and 3.'],
 canteen: ["Today's special: Masala Dosa and Vegetable Biryani! The canteen serves breakfast from 7:30-10:00, lunch 12:00-2:30, and snacks 4:00-6:30. We have both veg and non-veg options.", 'Nutrition info: Masala Dosa (~200 cal), Idli (~150 cal), Chicken Biryani (~450 cal/serving). We also have a salad bar and fresh fruit juices. Dietary options include gluten-free and Jain meals.', 'The canteen accepts campus ID cards, UPI, and cash. Meal plans start at ₹1,500/month for 20 meals. Re-charge your card at any counter or via the PESU app.'],
 rd: ['The R&D Lab focuses on AI/ML, IoT, sustainable energy, and biotechnology. We have 12 active research projects funded by DST and industry partners. Publications this year: 23 journal papers, 18 conference papers.', 'Lab equipment includes oscilloscopes, signal generators, FPGA dev boards, 3D printers, PCB fabrication, and an AI server with 4x A100 GPUs. Equipment booking is via the PSE lab portal.', 'To join a project: 1) Check open positions on the research portal, 2) Talk to the faculty advisor, 3) Submit your CV and interest statement. We accept students from 2nd year onward. Email rd@pesu.edu for inquiries.'],
 placement: ['Top recruiters this year: Microsoft, Amazon, Google, Adobe, Goldman Sachs, and 80+ more. Highest package: ₹45 LPA. Average package: ₹12.5 LPA. 95% of eligible students placed within 3 months.', 'Resume tips: Use the STAR method, keep it to 1 page, quantify achievements, include relevant projects. The placement cell offers free resume reviews every Wednesday. Book via the career portal.', 'Interview prep: 500+ practice problems on DSA, system design courses, mock interviews with alumni. The coding club meets every Tuesday and Thursday. Register for upcoming drive prep sessions on the portal.']
 };
 const pool = responses[zoneKey] || ['I\'m here to help! Ask me anything about ' + (CONFIG.zones[zoneKey]?.name || 'this zone') + '.'];
 return pool[Math.floor(Math.random() * pool.length)];
}

function handleGenieQuery(zone, question) {
 if (!phoneVisible) openPhone(zone);
 const input = document.getElementById('phone-input');
 if (input) {
 input.value = question;
 document.getElementById('phone-send').click();
 }
}

/* ============================================================
 NPC ANIMATION
============================================================ */
function updateNPCs(time) {
 for (const npc of npcs) {
 npc.position.x = npc.userData.baseX + Math.sin(time * 0.5 + npc.userData.phase) * 1.5;
 npc.position.z = npc.userData.baseZ + Math.cos(time * 0.7 + npc.userData.phase) * 1;
 npc.rotation.y = Math.sin(time * 0.3 + npc.userData.phase) * 0.5;
 }
}

/* ============================================================
 CLOUDS
============================================================ */
function createClouds() {
 const mat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 });
 const data = [[-40,25,-30,4],[30,28,-25,5],[-20,22,40,3.5],[50,26,10,4.5],[-50,30,-10,6],[10,24,-45,4]];
 for (const [cx, cy, cz, s] of data) {
 const g = new THREE.Group();
 const count = 3 + Math.floor(Math.random() * 3);
 for (let i = 0; i < count; i++) {
 const m = new THREE.Mesh(new THREE.SphereGeometry(1 + Math.random() * 1.5, 7, 5), mat);
 m.position.set((Math.random()-0.5)*3, (Math.random()-0.5)*0.8, (Math.random()-0.5)*2);
 m.scale.y = 0.5;
 g.add(m);
 }
 g.position.set(cx, cy, cz);
 g.scale.setScalar(s);
 g.userData.speed = 0.1 + Math.random() * 0.2;
 scene.add(g);
 }
}

function updateClouds(dt) {
 scene.children.forEach(c => {
 if (c.userData && c.userData.speed) {
 c.position.x += c.userData.speed * dt;
 if (c.position.x > 70) c.position.x = -70;
 }
 });
}

/* ============================================================
 PARTICLES (Fireflies)
============================================================ */
function createParticles() {
 const count = 80;
 const positions = new Float32Array(count * 3);
 const initY = new Float32Array(count);
 for (let i = 0; i < count; i++) {
 positions[i*3] = (Math.random()-0.5) * CONFIG.campus.width;
 positions[i*3+1] = 0.5 + Math.random() * 3;
 positions[i*3+2] = (Math.random()-0.5) * CONFIG.campus.depth;
 initY[i] = positions[i*3+1];
 }
 const geo = new THREE.BufferGeometry();
 geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
 geo.userData.initY = initY;
 const mat = new THREE.PointsMaterial({ color: 0xffff88, size: 0.25, transparent: true, opacity: 0.6, sizeAttenuation: true });
 const points = new THREE.Points(geo, mat);
 scene.add(points);
}

function updateParticles(time) {
 scene.children.forEach(c => {
 if (c instanceof THREE.Points && c.geometry.userData.initY) {
 const pos = c.geometry.attributes.position.array;
 const init = c.geometry.userData.initY;
 for (let i = 0; i < pos.length / 3; i++) {
 pos[i*3+1] = init[i] + Math.sin(time * 2 + i) * 0.3;
 }
 c.geometry.attributes.position.needsUpdate = true;
 }
 });
}

/* ============================================================
 RENDER LOOP
============================================================ */
function animate() {
 requestAnimationFrame(animate);
 const dt = Math.min(clock.getDelta(), 0.05);
 const time = clock.getElapsedTime();

 updatePlayer(dt);
 updateCameraPosition(false);
 updateZone();
 updateNPCs(time);
 updateClouds(dt);
 updateParticles(time);

 renderer.render(scene, camera);
}

/* ============================================================
 INIT
============================================================ */
function init() {
 const loadEl = document.getElementById('loading');
 if (loadEl) { loadEl.classList.add('hidden'); setTimeout(() => { if (loadEl.parentNode) loadEl.remove(); }, 800); }
 initScene();
 createGround();
 createBuildings();
 createPlayer();
 createNPCs();
 createClouds();
 createParticles();
 initInput();
 updateZoneIndicator();
 animate();
}

window.addEventListener('error', (e) => console.error('Global error:', e.error));
if (document.readyState === 'loading') {
 window.addEventListener('load', init);
} else {
 console.log('[init] DOM already ready, running init() immediately');
 init();
}
