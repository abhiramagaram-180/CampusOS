/* ============================================================
 CampusOS — 3D Campus Game Engine
 Built with Three.js (HiggsField-compatible)
 Zones: Library | Canteen | R&D | Placement
============================================================ */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
 CONFIG
============================================================ */

const CONFIG = {
 player: {
 speed: 0.12,
 height: 1.7,
 eyeHeight: 1.5,
 },
 camera: {
 height: 8,
 distance: 12,
 smoothness: 0.06,
 },
 zones: {
 library: {
 x: -22, z: -18, w: 14, d: 12, name: 'Library',
 color: 0x3a5f8a, accent: 0x5b9bd5,
 icon: '📚', agent: 'Library Genie',
 description: 'Ask about books, study rooms, research papers & more',
 },
 canteen: {
 x: -22, z: 14, w: 14, d: 12, name: 'Canteen',
 color: 0x8a5a3a, accent: 0xe8945b,
 icon: '🍽️', agent: 'Canteen Genie',
 description: 'Menu, timings, nutrition info & dietary options',
 },
 rd: {
 x: 20, z: -2, w: 14, d: 14, name: 'R&D Lab',
 color: 0x5a3a8a, accent: 0x9b5bf5,
 icon: '🔬', agent: 'R&D Genie',
 description: 'Projects, publications, lab equipment & research',
 },
 placement: {
 x: 20, z: 18, w: 14, d: 12, name: 'Placement Cell',
 color: 0x1f6b4a, accent: 0x35e38a,
 icon: '💼', agent: 'Placement Genie',
 description: 'Placements, companies, eligibility, packages & recruitment',
 },
 },
 campus: { width: 80, depth: 60, groundColor: 0x1a3320 },
};

/* ============================================================
 GLOBALS
============================================================ */

let scene, camera, renderer, clock;
let player, playerVelocity = new THREE.Vector3();
let ground, buildings = [];
let currentZone = null;
let phoneOpen = false;
let phoneEl, phoneScreen, phoneCloseBtn;
let geniePanel, chatMessages, chatInput, sendBtn;
let keys = {};
let messages = {};
let cameraTarget = new THREE.Vector3();
let isChatting = false;
let cameraDistance = 12;

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

/* ============================================================
 INIT
============================================================ */

function init() {
 clock = new THREE.Clock();

 scene = new THREE.Scene();
 scene.background = new THREE.Color(0x080b10);
 scene.fog = new THREE.FogExp2(0x080b10, 0.012);

 camera = new THREE.PerspectiveCamera(
 55,
 window.innerWidth / window.innerHeight,
 0.1,
 200
 );

 camera.position.set(
 0,
 CONFIG.camera.height,
 CONFIG.camera.distance
 );

 const canvas = document.getElementById('game-canvas');

 renderer = new THREE.WebGLRenderer({
 canvas,
 antialias: true
 });

 renderer.setSize(window.innerWidth, window.innerHeight);
 renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
 renderer.shadowMap.enabled = true;
 renderer.shadowMap.type = THREE.PCFSoftShadowMap;
 renderer.toneMapping = THREE.ACESFilmicToneMapping;
 renderer.toneMappingExposure = 1.2;

 setupLighting();
 createGround();
 createRoads();
 createZones();
 createPlayer();
 createEnvironment();
 createPhoneUI();

 setupEvents();

 setTimeout(() => {
 const loading = document.getElementById('loading');

 if (loading) {
 loading.classList.add('hidden');

 setTimeout(() => {
 if (loading) loading.remove();
 }, 1000);
 }
 }, 2000);

 animate();
}

/* ============================================================
 LIGHTING
============================================================ */

function setupLighting() {

 const ambient = new THREE.AmbientLight(
 0x404060,
 0.6
 );

 scene.add(ambient);

 const dirLight = new THREE.DirectionalLight(
 0xffeedd,
 1.2
 );

 dirLight.position.set(20, 30, 10);
 dirLight.castShadow = true;

 dirLight.shadow.mapSize.set(2048, 2048);

 dirLight.shadow.camera.left = -50;
 dirLight.shadow.camera.right = 50;
 dirLight.shadow.camera.top = 50;
 dirLight.shadow.camera.bottom = -50;

 dirLight.shadow.camera.near = 0.5;
 dirLight.shadow.camera.far = 100;

 dirLight.shadow.bias = -0.0001;

 scene.add(dirLight);

 const moonLight = new THREE.DirectionalLight(
 0x6688cc,
 0.3
 );

 moonLight.position.set(-10, 15, -20);

 scene.add(moonLight);

 const hemiLight = new THREE.HemisphereLight(
 0x334455,
 0x111111,
 0.4
 );

 scene.add(hemiLight);
}

/* ============================================================
 GROUND
============================================================ */

function createGround() {

 const geo = new THREE.PlaneGeometry(
 CONFIG.campus.width + 20,
 CONFIG.campus.depth + 20
 );

 const mat = new THREE.MeshStandardMaterial({
 color: CONFIG.campus.groundColor,
 roughness: 0.9,
 });

 ground = new THREE.Mesh(geo, mat);

 ground.rotation.x = -Math.PI / 2;
 ground.position.y = -0.05;

 ground.receiveShadow = true;

 scene.add(ground);

 const gridHelper = new THREE.GridHelper(
 CONFIG.campus.width + 20,
 40,
 0x2a4a2a,
 0x1f3a1f
 );

 gridHelper.position.y = 0.01;

 scene.add(gridHelper);

 const borderGeo = new THREE.EdgesGeometry(
 new THREE.BoxGeometry(
 CONFIG.campus.width,
 0.1,
 CONFIG.campus.depth
 )
 );

 const borderMat = new THREE.LineBasicMaterial({
 color: 0x35e38a,
 transparent: true,
 opacity: 0.15
 });

 const border = new THREE.LineSegments(
 borderGeo,
 borderMat
 );

 border.position.y = 0.05;

 scene.add(border);
}

/* ============================================================
 ROADS
============================================================ */

function createRoads() {

 const roadMat = new THREE.MeshStandardMaterial({
 color: 0x1a1d22,
 roughness: 0.95
 });

 const hRoad = new THREE.Mesh(
 new THREE.PlaneGeometry(
 CONFIG.campus.width + 4,
 5
 ),
 roadMat
 );

 hRoad.rotation.x = -Math.PI / 2;
 hRoad.position.y = 0.02;
 hRoad.receiveShadow = true;

 scene.add(hRoad);

 const vRoad = new THREE.Mesh(
 new THREE.PlaneGeometry(
 5,
 CONFIG.campus.depth + 4
 ),
 roadMat
 );

 vRoad.rotation.x = -Math.PI / 2;
 vRoad.position.y = 0.02;
 vRoad.receiveShadow = true;

 scene.add(vRoad);

 const markMat = new THREE.MeshBasicMaterial({
 color: 0xd8c96b
 });

 for (
 let i = -CONFIG.campus.width / 2;
 i < CONFIG.campus.width / 2;
 i += 3
 ) {

 const mark = new THREE.Mesh(
 new THREE.PlaneGeometry(1.5, 0.15),
 markMat
 );

 mark.rotation.x = -Math.PI / 2;
 mark.position.set(i, 0.03, 0);

 scene.add(mark);
 }

 for (
 let i = -CONFIG.campus.depth / 2;
 i < CONFIG.campus.depth / 2;
 i += 3
 ) {

 const mark = new THREE.Mesh(
 new THREE.PlaneGeometry(0.15, 1.5),
 markMat
 );

 mark.rotation.x = -Math.PI / 2;
 mark.position.set(0, 0.03, i);

 scene.add(mark);
 }
}

/* ============================================================
 ZONE BUILDINGS
============================================================ */

function createZones() {

 const entranceMarkers = [];

 Object.entries(CONFIG.zones).forEach(([key, zone]) => {

 const group = new THREE.Group();

 group.position.set(
 zone.x,
 0,
 zone.z
 );

 group.userData = {
 zoneKey: key,
 zone
 };

 const baseGeo = new THREE.BoxGeometry(
 zone.w,
 0.3,
 zone.d
 );

 const baseMat = new THREE.MeshStandardMaterial({
 color: zone.color,
 roughness: 0.7,
 metalness: 0.1,
 });

 const base = new THREE.Mesh(
 baseGeo,
 baseMat
 );

 base.position.y = 0.15;

 base.castShadow = true;
 base.receiveShadow = true;

 group.add(base);

 const bodyH = 4 + Math.random() * 3;

 const bodyGeo = new THREE.BoxGeometry(
 zone.w - 0.5,
 bodyH,
 zone.d - 0.5
 );

 const bodyMat = new THREE.MeshStandardMaterial({
 color: new THREE.Color(zone.color).multiplyScalar(0.7),
 roughness: 0.6,
 metalness: 0.15,
 });

 const body = new THREE.Mesh(
 bodyGeo,
 bodyMat
 );

 body.position.y = 0.3 + bodyH / 2;

 body.castShadow = true;
 body.receiveShadow = true;

 group.add(body);

 const roofGeo = new THREE.BoxGeometry(
 zone.w + 0.5,
 0.4,
 zone.d + 0.5
 );

 const roofMat = new THREE.MeshStandardMaterial({
 color: zone.accent,
 roughness: 0.3,
 metalness: 0.3,
 emissive: zone.accent,
 emissiveIntensity: 0.1,
 });

 const roof = new THREE.Mesh(
 roofGeo,
 roofMat
 );

 roof.position.y = 0.3 + bodyH;

 group.add(roof);

 const entGeo = new THREE.PlaneGeometry(
 4,
 3
 );

 const entMat = new THREE.MeshStandardMaterial({
 color: zone.accent,
 roughness: 0.5,
 emissive: zone.accent,
 emissiveIntensity: 0.2,
 transparent: true,
 opacity: 0.4,
 });

 const entrance = new THREE.Mesh(
 entGeo,
 entMat
 );

 entrance.rotation.x = -Math.PI / 2;

 entrance.position.set(
 0,
 0.06,
 zone.d / 2 + 1.5
 );

 group.add(entrance);

 const winCount = Math.floor(zone.w / 3);

 for (let i = 0; i < winCount; i++) {

 const winGeo = new THREE.PlaneGeometry(
 1.8,
 1.5
 );

 const winMat = new THREE.MeshStandardMaterial({
 color: 0x88ccff,
 emissive: 0x4488aa,
 emissiveIntensity: 0.5,
 roughness: 0.1,
 metalness: 0.5,
 });

 const win = new THREE.Mesh(
 winGeo,
 winMat
 );

 win.position.set(
 -zone.w / 2 + 1.5 + i * 3,
 1.5 + Math.random() * 2,
 zone.d / 2 + 0.26
 );

 group.add(win);
 }

 const signGeo = new THREE.PlaneGeometry(
 zone.w * 0.6,
 0.8
 );

 const signMat = new THREE.MeshBasicMaterial({
 color: zone.accent,
 transparent: true,
 opacity: 0.9,
 });

 const sign = new THREE.Mesh(
 signGeo,
 signMat
 );

 sign.position.set(
 0,
 2,
 zone.d / 2 + 0.27
 );

 group.add(sign);

 const ringGeo = new THREE.RingGeometry(
 1.5,
 1.8,
 32
 );

 const ringMat = new THREE.MeshBasicMaterial({
 color: zone.accent,
 transparent: true,
 opacity: 0.5,
 side: THREE.DoubleSide,
 });

 const ring = new THREE.Mesh(
 ringGeo,
 ringMat
 );

 ring.rotation.x = -Math.PI / 2;

 ring.position.set(
 0,
 0.08,
 zone.d / 2 + 1.5
 );

 ring.userData = {
 isRing: true,
 zoneKey: key
 };

 group.add(ring);

 scene.add(group);

 buildings.push({
 group,
 zone,
 key,
 bodyH
 });

 entranceMarkers.push({
 x: zone.x,
 z: zone.z + zone.d / 2 + 1.5,
 w: zone.w,
 d: 3,
 zoneKey: key,
 });
 });

 CONFIG._entranceMarkers = entranceMarkers;
}

/* ============================================================
 PLAYER CHARACTER
============================================================ */

function createPlayer() {

 player = new THREE.Group();

 player.userData = {
 velocity: new THREE.Vector3()
 };

 const shadowGeo = new THREE.CircleGeometry(
 0.5,
 16
 );

 const shadowMat = new THREE.MeshBasicMaterial({
 color: 0x000000,
 transparent: true,
 opacity: 0.3
 });

 const shadow = new THREE.Mesh(
 shadowGeo,
 shadowMat
 );

 shadow.rotation.x = -Math.PI / 2;
 shadow.position.y = 0.02;

 player.add(shadow);

 const bodyGeo = new THREE.CapsuleGeometry(
 0.35,
 1.0,
 4,
 8
 );

 const bodyMat = new THREE.MeshStandardMaterial({
 color: 0x4d7cff,
 roughness: 0.4,
 metalness: 0.1,
 emissive: 0x111133,
 emissiveIntensity: 0.3,
 });

 const body = new THREE.Mesh(
 bodyGeo,
 bodyMat
 );

 body.position.y = 1.2;

 body.castShadow = true;

 player.add(body);

 const headGeo = new THREE.SphereGeometry(
 0.3,
 16,
 16
 );

 const headMat = new THREE.MeshStandardMaterial({
 color: 0xf1bd91,
 roughness: 0.6,
 });

 const head = new THREE.Mesh(
 headGeo,
 headMat
 );

 head.position.y = 2.1;

 head.castShadow = true;

 player.add(head);

 const hairGeo = new THREE.SphereGeometry(
 0.32,
 16,
 8,
 0,
 Math.PI * 2,
 0,
 Math.PI / 2
 );

 const hairMat = new THREE.MeshStandardMaterial({
 color: 0x1a1a1a,
 roughness: 0.8
 });

 const hair = new THREE.Mesh(
 hairGeo,
 hairMat
 );

 hair.position.y = 2.1;

 player.add(hair);

 const glowGeo = new THREE.SphereGeometry(
 1.2,
 16,
 16
 );

 const glowMat = new THREE.MeshBasicMaterial({
 color: 0x4d7cff,
 transparent: true,
 opacity: 0.06,
 });

 const glow = new THREE.Mesh(
 glowGeo,
 glowMat
 );

 glow.position.y = 1.2;

 glow.userData = {
 isGlow: true
 };

 player.add(glow);

 player.position.set(
 0,
 0,
 5
 );

 scene.add(player);
}

/* ============================================================
 ENVIRONMENT
============================================================ */

function createEnvironment() {

 const treePositions = [
 [-30, -25],
 [-35, -10],
 [-35, 15],
 [-30, 25],
 [25, -25],
 [35, -10],
 [35, 10],
 [25, 25],
 [-15, -28],
 [15, -28],
 [-15, 28],
 [15, 28],
 ];

 treePositions.forEach(([tx, tz]) => {

 const tree = new THREE.Group();

 const trunkGeo = new THREE.CylinderGeometry(
 0.2,
 0.3,
 2,
 8
 );

 const trunkMat = new THREE.MeshStandardMaterial({
 color: 0x4a3728,
 roughness: 0.9
 });

 const trunk = new THREE.Mesh(
 trunkGeo,
 trunkMat
 );

 trunk.position.y = 1;
 trunk.castShadow = true;

 tree.add(trunk);

 const foliageGeo = new THREE.SphereGeometry(
 1.5,
 8,
 8
 );

 const foliageMat = new THREE.MeshStandardMaterial({
 color: 0x2d5a1e,
 roughness: 0.8,
 emissive: 0x0a1a05,
 emissiveIntensity: 0.2,
 });

 const foliage = new THREE.Mesh(
 foliageGeo,
 foliageMat
 );

 foliage.position.y = 3;
 foliage.castShadow = true;

 tree.add(foliage);

 tree.position.set(
 tx,
 0,
 tz
 );

 scene.add(tree);
 });

 const lampPositions = [
 [-8, -8],
 [8, -8],
 [-8, 8],
 [8, 8],
 [-8, 20],
 [8, 20],
 [-8, -20],
 [8, -20],
 ];

 lampPositions.forEach(([lx, lz]) => {

 const lamp = new THREE.Group();

 const poleGeo = new THREE.CylinderGeometry(
 0.08,
 0.1,
 4,
 8
 );

 const poleMat = new THREE.MeshStandardMaterial({
 color: 0x444444,
 metalness: 0.8,
 roughness: 0.3
 });

 const pole = new THREE.Mesh(
 poleGeo,
 poleMat
 );

 pole.position.y = 2;
 pole.castShadow = true;

 lamp.add(pole);

 const lightGeo = new THREE.SphereGeometry(
 0.25,
 8,
 8
 );

 const lightMat = new THREE.MeshStandardMaterial({
 color: 0xffeedd,
 emissive: 0xffdd88,
 emissiveIntensity: 1,
 });

 const lightMesh = new THREE.Mesh(
 lightGeo,
 lightMat
 );

 lightMesh.position.y = 4.1;

 lamp.add(lightMesh);

 const pointLight = new THREE.PointLight(
 0xffdd88,
 0.8,
 12,
 2
 );

 pointLight.position.y = 4;

 lamp.add(pointLight);

 lamp.position.set(
 lx,
 0,
 lz
 );

 scene.add(lamp);
 });

 createRnDNPC();
}

/* ============================================================
 R&D NPC
============================================================ */

function createRnDNPC() {

 const npc = new THREE.Group();

 npc.name = 'R&D Assistant NPC';

 const bodyGeo = new THREE.CapsuleGeometry(
 0.32,
 0.9,
 4,
 8
 );

 const bodyMat = new THREE.MeshStandardMaterial({
 color: 0xf08a5d,
 roughness: 0.5
 });

 const body = new THREE.Mesh(
 bodyGeo,
 bodyMat
 );

 body.position.y = 1.1;
 body.castShadow = true;

 npc.add(body);

 const headGeo = new THREE.SphereGeometry(
 0.28,
 16,
 16
 );

 const headMat = new THREE.MeshStandardMaterial({
 color: 0xd99a72,
 roughness: 0.6
 });

 const head = new THREE.Mesh(
 headGeo,
 headMat
 );

 head.position.y = 2.0;
 head.castShadow = true;

 npc.add(head);

 const hairGeo = new THREE.SphereGeometry(
 0.30,
 16,
 8,
 0,
 Math.PI * 2,
 0,
 Math.PI / 2
 );

 const hairMat = new THREE.MeshStandardMaterial({
 color: 0x202020,
 roughness: 0.8
 });

 const hair = new THREE.Mesh(
 hairGeo,
 hairMat
 );

 hair.position.y = 2.02;

 npc.add(hair);

 const badgeGeo = new THREE.BoxGeometry(
 0.18,
 0.25,
 0.04
 );

 const badgeMat = new THREE.MeshStandardMaterial({
 color: 0x35e38a,
 emissive: 0x35e38a,
 emissiveIntensity: 0.5
 });

 const badge = new THREE.Mesh(
 badgeGeo,
 badgeMat
 );

 badge.position.set(
 0,
 1.25,
 0.33
 );

 npc.add(badge);

 const canvas = document.createElement('canvas');

 canvas.width = 512;
 canvas.height = 128;

 const ctx = canvas.getContext('2d');

 ctx.fillStyle = 'rgba(5, 8, 12, 0.88)';
 ctx.beginPath();
 ctx.roundRect(
 8,
 8,
 496,
 112,
 24
 );
 ctx.fill();

 ctx.strokeStyle = '#9b5bf5';
 ctx.lineWidth = 4;
 ctx.beginPath();
 ctx.roundRect(
 8,
 8,
 496,
 112,
 24
 );
 ctx.stroke();

 ctx.fillStyle = '#ffffff';
 ctx.font = 'bold 42px Arial';
 ctx.textAlign = 'center';
 ctx.textBaseline = 'middle';

 ctx.fillText(
 'R&D Assistant',
 256,
 64
 );

 const labelTexture = new THREE.CanvasTexture(
 canvas
 );

 const labelMaterial = new THREE.SpriteMaterial({
 map: labelTexture,
 transparent: true,
 depthTest: false
 });

 const label = new THREE.Sprite(
 labelMaterial
 );

 label.scale.set(
 4.8,
 1.2,
 1
 );

 label.position.y = 3.25;

 npc.add(label);

 const rd = CONFIG.zones.rd;

 npc.position.set(
 rd.x,
 0,
 rd.z + rd.d / 2 + 3.8
 );

 scene.add(npc);
}

/* ============================================================
 PHONE UI
============================================================ */

function createPhoneUI() {

 phoneEl = document.createElement('div');

 phoneEl.id = 'phone';

 phoneEl.innerHTML = `
 <div class="phone-frame">
 <div class="phone-notch"></div>

 <div class="phone-content" id="phone-content">

 <div class="phone-home">

 <div class="phone-header">
 <div class="phone-time" id="phone-time"></div>
 <div class="phone-zone-name" id="phone-zone-name">
 Campus
 </div>
 </div>

 <div class="phone-zone-info" id="phone-zone-info">
 Walk into a zone to access its Genie
 </div>

 <div class="phone-zone-icons" id="phone-zone-icons"></div>

 </div>

 <div class="phone-chat" id="phone-chat" style="display:none">

 <div class="chat-header">
 <button class="chat-back" id="chat-back">
 ← Back
 </button>

 <span class="chat-title" id="chat-title">
 Genie
 </span>

 </div>

 <div class="chat-messages" id="chat-messages"></div>

 <div class="chat-input-area">

 <input
 type="text"
 id="chat-input"
 placeholder="Ask anything..."
 autocomplete="off"
 >

 <button id="chat-send">
 ➤
 </button>

 </div>

 </div>

 </div>
 </div>
 `;

 const style = document.createElement('style');

 style.textContent = `

 #phone {
 position: fixed;
 right: 25px;
 bottom: 15px;
 width: 340px;
 height: 620px;
 z-index: 200;
 pointer-events: none;
 opacity: 0;
 transform: translateX(400px) rotate(12deg);
 transition:
 transform 0.5s cubic-bezier(0.2,0.8,0.2,1),
 opacity 0.3s;
 }

 #phone.open {
 pointer-events: auto;
 opacity: 1;
 transform: translateX(0) rotate(0deg);
 }

 .phone-frame {
 width: 100%;
 height: 100%;
 background: #0a0d12;
 border: 8px solid #1a1e25;
 border-radius: 40px;
 overflow: hidden;
 box-shadow:
 0 25px 80px rgba(0,0,0,0.8),
 0 0 40px rgba(53,227,138,0.1);
 position: relative;
 }

 .phone-notch {
 width: 100px;
 height: 24px;
 background: #0a0d12;
 border-radius: 0 0 16px 16px;
 margin: 0 auto;
 position: relative;
 z-index: 2;
 }

 .phone-content {
 width: 100%;
 height: 100%;
 overflow: hidden;
 position: relative;
 }

 .phone-time {
 position: absolute;
 top: 8px;
 left: 20px;
 color: #999;
 font-size: 12px;
 }

 .phone-zone-name {
 text-align: center;
 color: #fff;
 font-size: 20px;
 font-weight: bold;
 margin-top: 10px;
 }

 .phone-zone-info {
 text-align: center;
 color: #777;
 font-size: 12px;
 margin-top: 6px;
 padding: 0 15px;
 line-height: 1.4;
 }

 .phone-zone-icons {
 display: flex;
 justify-content: center;
 gap: 15px;
 margin-top: 30px;
 padding: 0 20px;
 flex-wrap: wrap;
 }

 .zone-icon-btn {
 width: 60px;
 height: 60px;
 border-radius: 16px;
 border: 2px solid rgba(255,255,255,0.1);
 background: rgba(255,255,255,0.05);
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 28px;
 cursor: pointer;
 transition: 0.2s;
 }

 .zone-icon-btn:hover {
 background: rgba(255,255,255,0.1);
 transform: scale(1.05);
 }

 .zone-icon-btn .icon-label {
 font-size: 9px;
 color: #777;
 margin-top: 4px;
 text-align: center;
 }

 .icon-wrapper {
 display: flex;
 flex-direction: column;
 align-items: center;
 }

 .chat-header {
 display: flex;
 align-items: center;
 gap: 10px;
 padding: 12px 16px;
 border-bottom: 1px solid #1a1e25;
 background: rgba(10,13,18,0.95);
 position: sticky;
 top: 0;
 }

 .chat-back {
 background: none;
 border: none;
 color: #35e38a;
 font-size: 18px;
 cursor: pointer;
 }

 .chat-title {
 color: #fff;
 font-size: 16px;
 font-weight: bold;
 }

 .chat-messages {
 height: calc(100% - 130px);
 overflow-y: auto;
 padding: 15px;
 display: flex;
 flex-direction: column;
 gap: 10px;
 }

 .chat-msg {
 max-width: 85%;
 padding: 10px 14px;
 border-radius: 16px;
 font-size: 13px;
 line-height: 1.4;
 word-wrap: break-word;
 }

 .chat-msg.user {
 align-self: flex-end;
 background: #35e38a;
 color: #06120c;
 border-bottom-right-radius: 4px;
 }

 .chat-msg.ai {
 align-self: flex-start;
 background: #1a1e25;
 color: #ddd;
 border-bottom-left-radius: 4px;
 }

 .chat-msg.ai .agent-name {
 font-size: 10px;
 color: #35e38a;
 margin-bottom: 3px;
 font-weight: bold;
 }

 .chat-input-area {
 position: absolute;
 bottom: 0;
 left: 0;
 right: 0;
 display: flex;
 gap: 8px;
 padding: 10px 12px;
 border-top: 1px solid #1a1e25;
 background: rgba(10,13,18,0.95);
 }

 #chat-input {
 flex: 1;
 background: #1a1e25;
 border: 1px solid #2a2e35;
 border-radius: 20px;
 padding: 10px 16px;
 color: #fff;
 font-size: 13px;
 outline: none;
 }

 #chat-input::placeholder {
 color: #555;
 }

 #chat-send {
 width: 38px;
 height: 38px;
 border-radius: 50%;
 border: none;
 background: #35e38a;
 color: #06120c;
 font-size: 16px;
 cursor: pointer;
 display: flex;
 align-items: center;
 justify-content: center;
 font-weight: bold;
 }

 #chat-send:hover {
 background: #2bc278;
 }

 .genie-avatar {
 width: 28px;
 height: 28px;
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 14px;
 margin-right: 6px;
 flex-shrink: 0;
 }

 .chat-msg.ai-inner {
 display: flex;
 align-items: flex-start;
 gap: 0;
 }

 .typing-indicator {
 display: flex;
 gap: 4px;
 padding: 8px 12px;
 }

 .typing-dot {
 width: 6px;
 height: 6px;
 background: #35e38a;
 border-radius: 50%;
 animation: typingBounce 1.4s infinite;
 }

 .typing-dot:nth-child(2) {
 animation-delay: 0.2s;
 }

 .typing-dot:nth-child(3) {
 animation-delay: 0.4s;
 }

 @keyframes typingBounce {

 0%, 60%, 100% {
 transform: translateY(0);
 }

 30% {
 transform: translateY(-4px);
 }

 }

 `;

 document.head.appendChild(style);
 document.body.appendChild(phoneEl);

 phoneScreen = phoneEl.querySelector('#phone-content');

 phoneCloseBtn = null;

 const iconsContainer =
 phoneEl.querySelector('#phone-zone-icons');

 Object.entries(CONFIG.zones).forEach(
 ([key, zone]) => {

 const btn =
 document.createElement('div');

 btn.className = 'zone-icon-btn';

 btn.dataset.zone = key;

 btn.innerHTML = `
 <div class="icon-wrapper">
 <span>${zone.icon}</span>
 <span class="icon-label">${zone.name}</span>
 </div>
 `;

 btn.addEventListener(
 'click',
 () => openChat(key)
 );

 iconsContainer.appendChild(btn);
 });

 geniePanel =
 phoneEl.querySelector('#phone-chat');

 chatMessages =
 phoneEl.querySelector('#chat-messages');

 chatInput =
 phoneEl.querySelector('#chat-input');

 sendBtn =
 phoneEl.querySelector('#chat-send');

 phoneEl
 .querySelector('#chat-back')
 .addEventListener(
 'click',
 closeChat
 );

 sendBtn.addEventListener(
 'click',
 sendMessage
 );

 chatInput.addEventListener(
 'keydown',
 (e) => {
 if (e.key === 'Enter') {
 sendMessage();
 }
 }
 );

 updatePhoneTime();

 setInterval(
 updatePhoneTime,
 30000
 );
}

function updatePhoneTime() {

 const now = new Date();

 const timeStr =
 now.toLocaleTimeString(
 [],
 {
 hour: '2-digit',
 minute: '2-digit'
 }
 );

 const el =
 document.getElementById(
 'phone-time'
 );

 if (el) {
 el.textContent = timeStr;
 }
}

function showPhoneZoneInfo(zoneKey) {

 const zone =
 CONFIG.zones[zoneKey];

 if (!zone) return;

 document.getElementById(
 'phone-zone-name'
 ).textContent =
 zone.name;

 document.getElementById(
 'phone-zone-info'
 ).textContent =
 zone.description;

 document
 .querySelectorAll('.zone-icon-btn')
 .forEach(btn => {

 btn.style.borderColor =
 btn.dataset.zone === zoneKey
 ? '#' +
 zone.accent
 .toString(16)
 .padStart(6, '0')
 : 'rgba(255,255,255,0.1)';

 });
}

function openPhone() {

 phoneOpen = true;

 phoneEl.classList.add('open');
}

function closePhone() {

 phoneOpen = false;

 phoneEl.classList.remove('open');

 closeChat();
}

function openChat(zoneKey) {

 const zone =
 CONFIG.zones[zoneKey];

 if (!zone) return;

 document.querySelector(
 '.phone-home'
 ).style.display = 'none';

 geniePanel.style.display = 'block';

 document.getElementById(
 'chat-title'
 ).textContent =
 zone.icon + ' ' + zone.agent;

 if (!messages[zoneKey]) {

 messages[zoneKey] = [
 {
 type: 'ai',
 text:
 `Hey! I'm ${zone.agent}. How can I help you with ${zone.name.toLowerCase()} today?`,
 zone: zoneKey,
 }
 ];

 }

 renderMessages(zoneKey);

 isChatting = true;
}

function closeChat() {

 document.querySelector(
 '.phone-home'
 ).style.display = 'block';

 geniePanel.style.display = 'none';

 isChatting = false;
}

function renderMessages(zoneKey) {

 chatMessages.innerHTML = '';

 const msgs =
 messages[zoneKey] || [];

 const zone =
 CONFIG.zones[zoneKey];

 msgs.forEach(msg => {

 const div =
 document.createElement('div');

 div.className =
 `chat-msg ${msg.type}`;

 if (msg.type === 'ai') {

 div.innerHTML = `
 <div class="chat-msg ai-inner">

 <div
 class="genie-avatar"
 style="
 background: #${zone.accent.toString(16).padStart(6,'0')}22;
 color: #${zone.accent.toString(16).padStart(6,'0')}
 "
 >
 ${zone.icon}
 </div>

 <div>

 <div class="agent-name">
 ${zone.agent}
 </div>

 <div>
 ${msg.text}
 </div>

 </div>

 </div>
 `;

 } else {

 div.textContent =
 msg.text;

 }

 chatMessages.appendChild(div);

 });

 chatMessages.scrollTop =
 chatMessages.scrollHeight;
}

function showTyping() {

 const div =
 document.createElement('div');

 div.className =
 'chat-msg ai';

 div.id =
 'typing-indicator';

 div.innerHTML = `
 <div class="chat-msg ai-inner">

 <div class="typing-indicator">
 <div class="typing-dot"></div>
 <div class="typing-dot"></div>
 <div class="typing-dot"></div>
 </div>

 </div>
 `;

 chatMessages.appendChild(div);

 chatMessages.scrollTop =
 chatMessages.scrollHeight;
}

function removeTyping() {

 const el =
 document.getElementById(
 'typing-indicator'
 );

 if (el) {
 el.remove();
 }
}

async function sendMessage() {

 const text =
 chatInput.value.trim();

 if (!text) return;

 const zoneKey =
 currentZone;

 const zone =
 CONFIG.zones[zoneKey];

 if (!zone) return;

 messages[zoneKey].push({
 type: 'user',
 text
 });

 chatInput.value = '';

 renderMessages(zoneKey);

 showTyping();

 const response =
 await queryGenie(
 zoneKey,
 text
 );

 removeTyping();

 messages[zoneKey].push({
 type: 'ai',
 text: response,
 zone: zoneKey
 });

 renderMessages(zoneKey);

 sendToStreamlit(
 zoneKey,
 text,
 response
 );
}

async function queryGenie(
 zoneKey,
 question
) {

 try {

 if (
 window.parent &&
 window.parent !== window
 ) {

 window.parent.postMessage(
 {
 type: 'campusos-genie-query',
 zone: zoneKey,
 question: question
 },
 '*'
 );

 return new Promise(
 resolve => {

 const handler =
 event => {

 if (
 event.data &&
 event.data.type ===
 'campusos-genie-response'
 ) {

 window.removeEventListener(
 'message',
 handler
 );

 resolve(
 event.data.answer
 );

 }

 };

 window.addEventListener(
 'message',
 handler
 );

 setTimeout(
 () => {

 window.removeEventListener(
 'message',
 handler
 );

 resolve(
 getMockResponse(
 zoneKey,
 question
 )
 );

 },
 3000
 );

 }
 );

 }

 } catch (e) {
 }

 await new Promise(
 r =>
 setTimeout(
 r,
 800 +
 Math.random() * 1000
 )
 );

 return getMockResponse(
 zoneKey,
 question
 );
}

function getMockResponse(
 zoneKey,
 question
) {

 const responses = {

 library: [
 "I found 3 books related to your query. Want me to reserve one?",
 "The library has extended hours during exam season — open until 11 PM.",
 "There's a study room available on the 2nd floor. Want me to book it?",
 "I searched our catalog and found several relevant research papers.",
 "The quiet zone is on the 3rd floor."
 ],

 canteen: [
 "Today's special is biryani! Available from 12-2 PM.",
 "The canteen has vegan and gluten-free options.",
 "Breakfast is served 7:30-10 AM. Lunch 12-2 PM.",
 "Today's menu includes Idli, Dosa, Poha, Rice, Roti and Dal.",
 "The canteen is currently not very busy."
 ],

 rd: [
 "Currently 3 active projects match your interests. Want details?",
 "The R&D lab has published 5 papers this semester.",
 "Equipment booking for the lab can be done through the portal.",
 "Our latest project is on AI-powered campus navigation.",
 "The R&D department has 2 open research assistant positions."
 ],

 placement: [
 "I can help you find companies visiting campus and their eligibility criteria.",
 "Ask me about placement statistics, packages, recruiters, or hiring timelines.",
 "I can help check whether your profile matches a company's placement eligibility.",
 "Want to know which companies are recruiting and what packages they offer?",
 "I can answer questions about placements using the campus placement data."
 ]

 };

 const zoneResponses =
 responses[zoneKey] ||
 responses.library;

 return zoneResponses[
 Math.floor(
 Math.random() *
 zoneResponses.length
 )
 ];
}

function sendToStreamlit(
 zoneKey,
 question,
 answer
) {

 try {

 if (
 window.parent &&
 window.parent !== window
 ) {

 window.parent.postMessage(
 {
 type: 'campusos-genie-query',
 zone: zoneKey,
 question: question,
 answer: answer
 },
 '*'
 );

 }

 } catch (e) {
 }
}

/* ============================================================
 ZONE DETECTION
============================================================ */

function checkZones() {

 const px =
 player.position.x;

 const pz =
 player.position.z;

 let inZone = null;

 for (
 const [key, zone]
 of Object.entries(CONFIG.zones)
 ) {

 const zx =
 zone.x;

 const zz =
 zone.z;

 const hw =
 zone.w / 2;

 const hd =
 zone.d / 2;

 if (
 px > zx - hw - 2 &&
 px < zx + hw + 2 &&
 pz > zz - hd - 2 &&
 pz < zz + hd + 2
 ) {

 inZone = key;

 break;
 }

 }

 if (
 inZone &&
 inZone !== currentZone
 ) {

 currentZone =
 inZone;

 openPhone();

 showPhoneZoneInfo(
 inZone
 );

 showZonePopup(
 CONFIG.zones[inZone].name
 );

 } else if (
 !inZone &&
 currentZone
 ) {

 currentZone = null;

 closePhone();

 }

}

/* ============================================================
 ZONE POPUP
============================================================ */

function showZonePopup(
 zoneName
) {

 const existing =
 document.querySelector(
 '.zone-popup'
 );

 if (existing) {
 existing.remove();
 }

 const popup =
 document.createElement(
 'div'
 );

 popup.className =
 'zone-popup';

 popup.innerHTML =
 `<span style="color:#35e38a;">●</span>&nbsp; Entered <strong>${zoneName}</strong> — Phone activated`;

 document.body.appendChild(
 popup
 );

 setTimeout(
 () => popup.remove(),
 3000
 );
}

/* ============================================================
 INPUT
============================================================ */

function setupEvents() {

 window.addEventListener(
 'keydown',
 e => {
 keys[e.key.toLowerCase()] = true;
 }
 );

 window.addEventListener(
 'keyup',
 e => {
 keys[e.key.toLowerCase()] = false;
 }
 );

 window.addEventListener(
 'resize',
 () => {

 camera.aspect =
 window.innerWidth /
 window.innerHeight;

 camera.updateProjectionMatrix();

 renderer.setSize(
 window.innerWidth,
 window.innerHeight
 );

 }
 );

 // CAMERA ZOOM
 window.addEventListener(
 'wheel',
 e => {

 if (
 phoneOpen ||
 isChatting
 ) {
 return;
 }

 e.preventDefault();

 cameraDistance +=
 e.deltaY * 0.012;

 cameraDistance =
 THREE.MathUtils.clamp(
 cameraDistance,
 6,
 20
 );

 },
 {
 passive: false
 }
 );

 window.addEventListener(
 'click',
 e => {

 if (isChatting) return;

 mouse.x =
 (e.clientX /
 window.innerWidth) *
 2 - 1;

 mouse.y =
 -(e.clientY /
 window.innerHeight) *
 2 + 1;

 raycaster.setFromCamera(
 mouse,
 camera
 );

 const intersects =
 raycaster.intersectObjects(
 scene.children,
 true
 );

 for (
 const hit of intersects
 ) {

 let obj =
 hit.object;

 while (obj) {

 if (
 obj.userData &&
 obj.userData.isRing
 ) {

 const zoneKey =
 obj.userData.zoneKey;

 const worldPos =
 new THREE.Vector3();

 obj.getWorldPosition(
 worldPos
 );

 const dir =
 worldPos
 .clone()
 .sub(player.position)
 .normalize();

 dir.y = 0;

 player.position.add(
 dir.multiplyScalar(2)
 );

 break;
 }

 obj = obj.parent;

 }

 }

 });

}

/* ============================================================
 COLLISION DETECTION
============================================================ */

function checkCollision(
 newX,
 newZ
) {

 const margin = 0.8;

 const halfW =
 CONFIG.campus.width / 2;

 const halfD =
 CONFIG.campus.depth / 2;

 if (
 newX <
 -halfW + margin ||
 newX >
 halfW - margin
 ) {
 return true;
 }

 if (
 newZ <
 -halfD + margin ||
 newZ >
 halfD - margin
 ) {
 return true;
 }

 for (
 const building
 of buildings
 ) {

 const bx =
 building.group.position.x;

 const bz =
 building.group.position.z;

 const bw =
 building.zone.w / 2 +
 margin;

 const bd =
 building.zone.d / 2 +
 margin;

 if (
 newX > bx - bw &&
 newX < bx + bw &&
 newZ > bz - bd &&
 newZ < bz + bd
 ) {

 return true;

 }

 }

 return false;
}

/* ============================================================
 MOVEMENT
============================================================ */

function updatePlayer() {

 if (isChatting) return;

 const moveDir =
 new THREE.Vector3();

 if (
 keys['w'] ||
 keys['arrowup']
 ) {
 moveDir.z -= 1;
 }

 if (
 keys['s'] ||
 keys['arrowdown']
 ) {
 moveDir.z += 1;
 }

 if (
 keys['a'] ||
 keys['arrowleft']
 ) {
 moveDir.x -= 1;
 }

 if (
 keys['d'] ||
 keys['arrowright']
 ) {
 moveDir.x += 1;
 }

 if (
 moveDir.length() > 0
 ) {

 moveDir.normalize();

 moveDir.multiplyScalar(
 CONFIG.player.speed
 );

 const newX =
 player.position.x +
 moveDir.x;

 const newZ =
 player.position.z +
 moveDir.z;

 if (
 !checkCollision(
 newX,
 newZ
 )
 ) {

 player.position.x =
 newX;

 player.position.z =
 newZ;

 } else if (
 !checkCollision(
 newX,
 player.position.z
 )
 ) {

 player.position.x =
 newX;

 } else if (
 !checkCollision(
 player.position.x,
 newZ
 )
 ) {

 player.position.z =
 newZ;

 }

 const angle =
 Math.atan2(
 moveDir.x,
 moveDir.z
 );

 player.rotation.y =
 THREE.MathUtils.lerp(
 player.rotation.y,
 angle,
 0.15
 );

 const time =
 clock.getElapsedTime();

 player.position.y =
 Math.abs(
 Math.sin(time * 10)
 ) * 0.08;

 }

}

/* ============================================================
 CAMERA
============================================================ */

function updateCamera() {

 const targetPos =
 new THREE.Vector3(

 player.position.x,

 player.position.y +
 CONFIG.camera.height *
 (cameraDistance / 12),

 player.position.z +
 cameraDistance

 );

 camera.position.lerp(
 targetPos,
 CONFIG.camera.smoothness
 );

 cameraTarget.lerp(
 player.position,
 CONFIG.camera.smoothness
 );

 camera.lookAt(
 cameraTarget
 );

}

/* ============================================================
 ANIMATIONS
============================================================ */

function updateAnimations() {

 const time =
 clock.getElapsedTime();

 scene.traverse(
 obj => {

 if (
 obj.userData &&
 obj.userData.isRing
 ) {

 obj.rotation.z =
 time * 0.5;

 obj.material.opacity =
 0.3 +
 Math.sin(time * 2) *
 0.2;

 }

 });

 player.children.forEach(
 child => {

 if (
 child.userData &&
 child.userData.isGlow
 ) {

 child.material.opacity =
 0.04 +
 Math.sin(time * 3) *
 0.02;

 }

 });

}

/* ============================================================
 ANIMATE LOOP
============================================================ */

function animate() {

 requestAnimationFrame(
 animate
 );

 updatePlayer();
 updateCamera();
 updateAnimations();
 checkZones();

 renderer.render(
 scene,
 camera
 );

}

/* ============================================================
 START
============================================================ */

init();

window.CampusOS = {

 openPhone,
 closePhone,
 openChat,
 closeChat,
 queryGenie,

 getPlayerPosition: () =>
 player
 ? {
 x: player.position.x,
 z: player.position.z
 }
 : null,

 getCurrentZone: () =>
 currentZone

};