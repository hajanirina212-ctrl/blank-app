/* =====================================================================
 * 2. DÉCOR 3D (Three.js) : ville isométrique, bâtiments évolutifs, trafic, jour/nuit
 * ===================================================================== */
var Gfx = (function () {
'use strict';

var CELL = 12, COLS = 3, ROWS = 4, FH = 2.5;           // taille d'une case, grille 3×4, hauteur d'un étage
var QUAL = {
  low:    { pr: 1.25, shadow: 1024, cars: 8,  trees: 0.5 },
  medium: { pr: 1.75, shadow: 2048, cars: 14, trees: 1 },
  high:   { pr: 2,    shadow: 4096, cars: 20, trees: 1 }
};
var renderer, scene, camera, sun, hemi, moon, ground, Q = QUAL.medium, qName = 'medium';
var tgt = new THREE.Vector3(0, 0, 8), viewH = 30, W = 1, H = 1, ELEV = 36 * Math.PI / 180;
var plots = [], cars = [], nightMats = [], lampPools = [], pops = [], puffs = [], clouds = [], dayT = 0.22, nightF = 0, clockT = 0;
var TEX = {}, MATS = {};

/* ---------- Utilitaires ---------- */
function C(hex) { return new THREE.Color(hex).convertSRGBToLinear(); }
function rnd(a, b) { return a + Math.random() * (b - a); }
function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
function smooth(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }
function mulberry(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function canvas(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function tex(c, srgb, rx, ry) {
  var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  if (srgb !== false) t.encoding = THREE.sRGBEncoding; if (rx) t.repeat.set(rx, ry); return t;
}
function mesh(parent, geo, mat, x, y, z, sx, sy, sz, cast, recv) {
  var m = new THREE.Mesh(geo, mat); m.position.set(x || 0, y || 0, z || 0); if (sx !== undefined) m.scale.set(sx, sy, sz);
  m.castShadow = !!cast; m.receiveShadow = recv !== false; parent.add(m); return m;
}
function grp(parent, x, y, z) { var g = new THREE.Group(); g.position.set(x || 0, y || 0, z || 0); if (parent) parent.add(g); return g; }
function std(color, o) { var p = { color: C(color), roughness: 0.8, metalness: 0 }; if (o) for (var k in o) p[k] = o[k]; return new THREE.MeshStandardMaterial(p); }
function glow(color, k) { var m = new THREE.MeshStandardMaterial({ color: C('#222222'), emissive: C(color), emissiveIntensity: k, roughness: 0.5 }); nightMats.push({ m: m, base: k, mode: 'night' }); return m; }

/* ---------- Bruit fractal + textures PBR procédurales (asphalte, herbe, dalles) ---------- */
function Fbm(rng, base, oct) {
  this.L = []; var norm = 0;
  for (var o = 0; o < oct; o++) { var p = base << o, lat = new Float32Array(p * p); for (var i = 0; i < p * p; i++) lat[i] = rng(); var a = Math.pow(0.5, o); this.L.push({ p: p, lat: lat, a: a }); norm += a; }
  this.norm = norm;
}
Fbm.prototype.get = function (u, v) {
  var s = 0;
  for (var i = 0; i < this.L.length; i++) {
    var l = this.L[i], p = l.p, x = u * p, y = v * p, xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi;
    xi = ((xi % p) + p) % p; yi = ((yi % p) + p) % p; var x1 = (xi + 1) % p, y1 = (yi + 1) % p; fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
    var a = l.lat[yi * p + xi], b = l.lat[yi * p + x1], c = l.lat[y1 * p + xi], d = l.lat[y1 * p + x1]; s += l.a * ((a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy);
  }
  return s / this.norm;
};
function buildPBR(size, fn, bump) {
  var n = size * size, Hh = new Float32Array(n), col = new Uint8ClampedArray(n * 4), rou = new Uint8ClampedArray(n * 4), nor = new Uint8ClampedArray(n * 4), o = { h: 0, r: 0, g: 0, b: 0, ro: 1 }, x, y, i;
  for (y = 0; y < size; y++) for (x = 0; x < size; x++) {
    fn((x + 0.5) / size, (y + 0.5) / size, o); i = y * size + x; Hh[i] = o.h;
    col[i * 4] = o.r * 255; col[i * 4 + 1] = o.g * 255; col[i * 4 + 2] = o.b * 255; col[i * 4 + 3] = 255; rou[i * 4] = rou[i * 4 + 1] = rou[i * 4 + 2] = o.ro * 255; rou[i * 4 + 3] = 255;
  }
  var k = bump * size / 256;
  for (y = 0; y < size; y++) for (x = 0; x < size; x++) {
    var l = Hh[y * size + (x - 1 + size) % size], r = Hh[y * size + (x + 1) % size], t = Hh[((y - 1 + size) % size) * size + x], b = Hh[((y + 1) % size) * size + x];
    var nx = -(r - l) * k, ny = (b - t) * k, len = Math.sqrt(nx * nx + ny * ny + 1); i = (y * size + x) * 4;
    nor[i] = (nx / len * 0.5 + 0.5) * 255; nor[i + 1] = (ny / len * 0.5 + 0.5) * 255; nor[i + 2] = (1 / len * 0.5 + 0.5) * 255; nor[i + 3] = 255;
  }
  function cv(d) { var c = canvas(size, size), ctx = c.getContext('2d'), im = ctx.createImageData(size, size); im.data.set(d); ctx.putImageData(im, 0, 0); return c; }
  return { map: cv(col), normal: cv(nor), rough: cv(rou) };
}
function pbrMat(set, rx, ry, extra) {
  var p = { map: tex(set.map, true, rx, ry), normalMap: tex(set.normal, false, rx, ry), roughnessMap: tex(set.rough, false, rx, ry), roughness: 1, metalness: 0 };
  if (extra) for (var k in extra) p[k] = extra[k]; return new THREE.MeshStandardMaterial(p);
}
function makeTextures() {
  var rng = mulberry(11), sz = QUAL[qName] === QUAL.low ? 256 : 512;
  var fg = new Fbm(rng, 4, 5), fg2 = new Fbm(rng, 32, 3);
  var grass = buildPBR(sz, function (u, v, o) { var n = fg.get(u, v), m = fg2.get(u, v), t = n * 0.6 + m * 0.4; o.r = 0.22 + 0.16 * t; o.g = 0.42 + 0.2 * t; o.b = 0.12 + 0.08 * t; o.h = m; o.ro = 0.95; }, 1.2);
  var fa = new Fbm(rng, 8, 4), fa2 = new Fbm(rng, 64, 2);
  var asph = buildPBR(sz, function (u, v, o) { var n = fa.get(u, v), m = fa2.get(u, v), k = 0.2 + 0.1 * n + 0.06 * m; o.r = k; o.g = k * 1.02; o.b = k * 1.08; o.h = m; o.ro = 0.85 + 0.1 * n; }, 1.4);
  var fc = new Fbm(rng, 8, 3);
  var conc = buildPBR(sz, function (u, v, o) {
    var tu = (u * 4) % 1, tv = (v * 4) % 1, d = Math.min(tu, 1 - tu, tv, 1 - tv), n = fc.get(u, v), k = 0.62 + 0.2 * n;
    if (d < 0.02) { k *= 0.55; o.h = 0.1; } else o.h = 0.55 + 0.3 * n;
    o.r = k; o.g = k * 0.98; o.b = k * 0.94; o.ro = 0.9;
  }, 1.6);
  TEX.grass = grass; TEX.asph = asph; TEX.conc = conc;
}

/* ---------- Façades : texture de fenêtres + texture « lumières allumées » (nuit) ---------- */
function drawFacade(kind, v, n, seed) {
  var Wd = 256, Hh = 108, c = canvas(Wd, Hh), e = canvas(Wd, Hh), x = c.getContext('2d'), y = e.getContext('2d'), rng = mulberry(seed);
  x.fillStyle = v.wall; x.fillRect(0, 0, Wd, Hh); y.fillStyle = '#000'; y.fillRect(0, 0, Wd, Hh);
  x.strokeStyle = 'rgba(0,0,0,0.07)'; x.lineWidth = 1; for (var r = 6; r < Hh; r += 9) { x.beginPath(); x.moveTo(0, r); x.lineTo(Wd, r); x.stroke(); }   // joints
  for (var k = 0; k < 160; k++) { x.fillStyle = 'rgba(' + (rng() < 0.5 ? '0,0,0' : '255,255,255') + ',' + (0.02 + rng() * 0.04) + ')'; x.fillRect(rng() * Wd, rng() * Hh, 2 + rng() * 6, 1 + rng() * 3); }   // grain
  x.fillStyle = 'rgba(0,0,0,0.16)'; x.fillRect(0, Hh - 3, Wd, 3); x.fillStyle = 'rgba(255,255,255,0.12)'; x.fillRect(0, 0, Wd, 2);
  function glass(px, py, pw, ph, lit) {
    x.fillStyle = v.trim; x.fillRect(px - 4, py - 4, pw + 8, ph + 8);
    var g = x.createLinearGradient(0, py, 0, py + ph); g.addColorStop(0, '#9cc9f2'); g.addColorStop(0.55, '#4b7fb4'); g.addColorStop(1, '#2f5a88'); x.fillStyle = g; x.fillRect(px, py, pw, ph);
    x.fillStyle = 'rgba(255,255,255,0.35)'; x.beginPath(); x.moveTo(px, py + ph * 0.55); x.lineTo(px + pw * 0.55, py); x.lineTo(px + pw * 0.8, py); x.lineTo(px, py + ph * 0.9); x.fill();   // reflet
    x.fillStyle = v.trim; x.fillRect(px + pw / 2 - 1.5, py, 3, ph); x.fillRect(px, py + ph * 0.45, pw, 3);
    x.fillStyle = 'rgba(0,0,0,0.25)'; x.fillRect(px - 6, py + ph + 4, pw + 12, 3);
    if (lit) { var gg = y.createLinearGradient(0, py, 0, py + ph); gg.addColorStop(0, '#ffe9a8'); gg.addColorStop(1, '#ffb347'); y.fillStyle = gg; y.fillRect(px, py, pw, ph); }
  }
  if (kind === 'shop') {
    var gw = Wd - 100, gx = 14, gy = 16, gh = Hh - 24;
    x.fillStyle = v.trim; x.fillRect(gx - 5, gy - 5, gw + 10, gh + 10);
    var g = x.createLinearGradient(0, gy, 0, gy + gh); g.addColorStop(0, '#b8dcf5'); g.addColorStop(0.5, '#6a9cc8'); g.addColorStop(1, '#3a6a98'); x.fillStyle = g; x.fillRect(gx, gy, gw, gh);
    x.fillStyle = 'rgba(255,255,255,0.28)'; x.beginPath(); x.moveTo(gx, gy + gh * 0.6); x.lineTo(gx + gw * 0.35, gy); x.lineTo(gx + gw * 0.5, gy); x.lineTo(gx, gy + gh * 0.95); x.fill();
    x.fillStyle = v.trim; x.fillRect(gx + gw / 2 - 2, gy, 4, gh); x.fillRect(gx + gw / 4, gy, 2, gh); x.fillRect(gx + gw * 0.75, gy, 2, gh);
    x.fillStyle = 'rgba(40,30,20,0.55)'; x.fillRect(gx, gy + gh - 8, gw, 8);                       // soubassement
    y.fillStyle = '#ffd98a'; y.fillRect(gx, gy, gw, gh); y.fillStyle = 'rgba(255,255,255,0.15)'; y.fillRect(gx, gy, gw, 10);
    var dx = Wd - 74, dw = 52;                                                                    // porte
    x.fillStyle = v.trim; x.fillRect(dx - 5, 12, dw + 10, Hh - 12); x.fillStyle = '#3a2a1e'; x.fillRect(dx, 17, dw, Hh - 17);
    var dg = x.createLinearGradient(0, 17, 0, 80); dg.addColorStop(0, '#a8d2ee'); dg.addColorStop(1, '#4c80ae'); x.fillStyle = dg; x.fillRect(dx + 6, 23, dw - 12, 48); x.fillStyle = '#e8d08a'; x.fillRect(dx + dw - 12, 62, 4, 12);
    y.fillStyle = '#ffd98a'; y.fillRect(dx + 6, 23, dw - 12, 48);
  } else {
    var ww = Wd / n * 0.52, wh = kind === 'sideShop' ? 54 : 56, wy = kind === 'sideShop' ? 22 : 26;
    for (var i = 0; i < n; i++) glass((i + 0.5) * Wd / n - ww / 2, wy, ww, wh, rng() < (kind === 'sideShop' ? 0.9 : 0.55));
  }
  return { c: c, e: e };
}
function facadeMat(kind, v, n, seed) {
  var d = drawFacade(kind, v, n, seed);
  var m = new THREE.MeshStandardMaterial({ map: tex(d.c, true), emissive: new THREE.Color(0xffffff), emissiveMap: tex(d.e, true), emissiveIntensity: 0.0, roughness: 0.78, metalness: 0.05 });
  nightMats.push({ m: m, base: 1.15, mode: 'night', shop: kind === 'shop' }); return m;
}

/* ---------- Enseignes dessinées au canvas ---------- */
var ICON = {
  cup: function (x, cx, cy, s, c) { x.fillStyle = c; x.beginPath(); x.moveTo(cx - s * 0.5, cy - s * 0.3); x.lineTo(cx + s * 0.4, cy - s * 0.3); x.lineTo(cx + s * 0.3, cy + s * 0.45); x.lineTo(cx - s * 0.4, cy + s * 0.45); x.fill(); x.strokeStyle = c; x.lineWidth = s * 0.12; x.beginPath(); x.arc(cx + s * 0.45, cy, s * 0.2, -1.2, 1.2); x.stroke(); x.fillRect(cx - s * 0.6, cy + s * 0.5, s * 1.1, s * 0.1); },
  bread: function (x, cx, cy, s, c) { x.fillStyle = c; x.beginPath(); x.ellipse(cx, cy, s * 0.6, s * 0.35, 0, 0, 7); x.fill(); x.strokeStyle = 'rgba(0,0,0,0.35)'; x.lineWidth = s * 0.07; for (var i = -1; i <= 1; i++) { x.beginPath(); x.moveTo(cx + i * s * 0.25 - s * 0.08, cy - s * 0.2); x.lineTo(cx + i * s * 0.25 + s * 0.08, cy + s * 0.2); x.stroke(); } },
  scissors: function (x, cx, cy, s, c) { x.strokeStyle = c; x.lineWidth = s * 0.1; x.beginPath(); x.arc(cx - s * 0.3, cy + s * 0.3, s * 0.2, 0, 7); x.arc(cx + s * 0.3, cy + s * 0.3, s * 0.2, 0, 7); x.stroke(); x.beginPath(); x.moveTo(cx - s * 0.2, cy + s * 0.15); x.lineTo(cx + s * 0.4, cy - s * 0.5); x.moveTo(cx + s * 0.2, cy + s * 0.15); x.lineTo(cx - s * 0.4, cy - s * 0.5); x.stroke(); },
  paw: function (x, cx, cy, s, c) { x.fillStyle = c; x.beginPath(); x.ellipse(cx, cy + s * 0.2, s * 0.35, s * 0.28, 0, 0, 7); x.fill(); [[-0.42, -0.1], [-0.15, -0.38], [0.15, -0.38], [0.42, -0.1]].forEach(function (p) { x.beginPath(); x.ellipse(cx + p[0] * s, cy + p[1] * s, s * 0.14, s * 0.18, 0, 0, 7); x.fill(); }); },
  pad: function (x, cx, cy, s, c) { x.fillStyle = c; x.beginPath(); x.roundRect ? x.roundRect(cx - s * 0.65, cy - s * 0.32, s * 1.3, s * 0.65, s * 0.25) : x.rect(cx - s * 0.65, cy - s * 0.32, s * 1.3, s * 0.65); x.fill(); x.fillStyle = 'rgba(0,0,0,0.55)'; x.fillRect(cx - s * 0.45, cy - s * 0.06, s * 0.3, s * 0.1); x.fillRect(cx - s * 0.35, cy - s * 0.16, s * 0.1, s * 0.3); x.beginPath(); x.arc(cx + s * 0.25, cy, s * 0.07, 0, 7); x.arc(cx + s * 0.45, cy - s * 0.1, s * 0.07, 0, 7); x.fill(); },
  film: function (x, cx, cy, s, c) { x.fillStyle = c; x.fillRect(cx - s * 0.6, cy - s * 0.15, s * 1.2, s * 0.65); x.fillStyle = 'rgba(0,0,0,0.6)'; for (var i = 0; i < 4; i++) { x.beginPath(); x.moveTo(cx - s * 0.6 + i * s * 0.3, cy - s * 0.45); x.lineTo(cx - s * 0.3 + i * s * 0.3, cy - s * 0.45); x.lineTo(cx - s * 0.45 + i * s * 0.3, cy - s * 0.15); x.lineTo(cx - s * 0.75 + i * s * 0.3, cy - s * 0.15); x.fill(); } },
  cart: function (x, cx, cy, s, c) { x.strokeStyle = c; x.lineWidth = s * 0.1; x.beginPath(); x.moveTo(cx - s * 0.65, cy - s * 0.4); x.lineTo(cx - s * 0.4, cy - s * 0.4); x.lineTo(cx - s * 0.2, cy + s * 0.25); x.lineTo(cx + s * 0.45, cy + s * 0.25); x.lineTo(cx + s * 0.6, cy - s * 0.2); x.lineTo(cx - s * 0.35, cy - s * 0.2); x.stroke(); x.fillStyle = c; x.beginPath(); x.arc(cx - s * 0.1, cy + s * 0.5, s * 0.1, 0, 7); x.arc(cx + s * 0.35, cy + s * 0.5, s * 0.1, 0, 7); x.fill(); },
  cross: function (x, cx, cy, s, c) { x.fillStyle = c; x.fillRect(cx - s * 0.15, cy - s * 0.5, s * 0.3, s * 1.0); x.fillRect(cx - s * 0.5, cy - s * 0.15, s * 1.0, s * 0.3); },
  fork: function (x, cx, cy, s, c) { x.strokeStyle = c; x.lineWidth = s * 0.09; x.beginPath(); x.moveTo(cx - s * 0.3, cy - s * 0.5); x.lineTo(cx - s * 0.3, cy + s * 0.5); x.moveTo(cx - s * 0.45, cy - s * 0.5); x.lineTo(cx - s * 0.45, cy - s * 0.1); x.moveTo(cx - s * 0.15, cy - s * 0.5); x.lineTo(cx - s * 0.15, cy - s * 0.1); x.moveTo(cx - s * 0.45, cy - s * 0.1); x.lineTo(cx - s * 0.15, cy - s * 0.1); x.stroke(); x.fillStyle = c; x.beginPath(); x.ellipse(cx + s * 0.35, cy - s * 0.2, s * 0.13, s * 0.3, 0, 0, 7); x.fill(); x.fillRect(cx + s * 0.32, cy, s * 0.06, s * 0.5); },
  star: function (x, cx, cy, s, c) { x.fillStyle = c; x.beginPath(); for (var i = 0; i < 10; i++) { var a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? s * 0.25 : s * 0.55; x.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); } x.fill(); },
  house: function (x, cx, cy, s, c) { x.fillStyle = c; x.beginPath(); x.moveTo(cx - s * 0.6, cy); x.lineTo(cx, cy - s * 0.55); x.lineTo(cx + s * 0.6, cy); x.lineTo(cx + s * 0.45, cy); x.lineTo(cx + s * 0.45, cy + s * 0.5); x.lineTo(cx - s * 0.45, cy + s * 0.5); x.lineTo(cx - s * 0.45, cy); x.fill(); x.fillStyle = 'rgba(0,0,0,0.5)'; x.fillRect(cx - s * 0.1, cy + s * 0.1, s * 0.2, s * 0.4); },
  tower: function (x, cx, cy, s, c) { x.fillStyle = c; x.fillRect(cx - s * 0.25, cy - s * 0.55, s * 0.5, s * 1.1); x.fillRect(cx - s * 0.5, cy - s * 0.1, s * 0.25, s * 0.65); x.fillRect(cx + s * 0.25, cy + s * 0.1, s * 0.25, s * 0.45); x.fillStyle = 'rgba(0,0,0,0.4)'; for (var i = 0; i < 4; i++) x.fillRect(cx - s * 0.12, cy - s * 0.45 + i * s * 0.25, s * 0.24, s * 0.08); }
};
function signCanvas(text, icon, bg, fg, w, h) {
  var c = canvas(w, h), x = c.getContext('2d'); x.fillStyle = bg; x.fillRect(0, 0, w, h);
  x.strokeStyle = fg; x.globalAlpha = 0.55; x.lineWidth = 4; x.strokeRect(6, 6, w - 12, h - 12); x.globalAlpha = 1;
  var s = h * 0.62; ICON[icon](x, h * 0.62, h / 2, s, fg);
  var fs = Math.floor(h * 0.5); x.font = '900 ' + fs + 'px "Arial Black", Arial, sans-serif';
  while (x.measureText(text).width > w - h * 1.4 && fs > 10) { fs -= 2; x.font = '900 ' + fs + 'px "Arial Black", Arial, sans-serif'; }
  x.fillStyle = fg; x.textBaseline = 'middle'; x.fillText(text, h * 1.15, h / 2 + 2); return c;
}
function signMesh(parent, text, icon, bg, fg, w, h, x, y, z) {
  var c = signCanvas(text, icon, bg, fg, 512, Math.round(512 * h / w)), t = tex(c, true);
  var m = new THREE.MeshStandardMaterial({ map: t, emissive: new THREE.Color(0xffffff), emissiveMap: t, emissiveIntensity: 0.0, roughness: 0.6 }); nightMats.push({ m: m, base: 0.8, mode: 'night' });
  var b = mesh(parent, new THREE.BoxGeometry(w, h, 0.14), [std('#222222'), std('#222222'), std('#222222'), std('#222222'), m, std('#222222')], x, y, z, 1, 1, 1, false); return b;
}
function stripeTex(a, b, n) {
  var c = canvas(128, 32), x = c.getContext('2d'), w = 128 / n; for (var i = 0; i < n; i++) { x.fillStyle = i % 2 ? b : a; x.fillRect(i * w, 0, w, 32); }
  x.fillStyle = 'rgba(0,0,0,0.18)'; x.fillRect(0, 24, 128, 8); return tex(c, true);
}

/* ---------- Définition visuelle des 12 commerces ---------- */
var VIS = [
  { wall: '#c58a58', trim: '#4a2f1b', roof: '#6a5040', awn: ['#8a3b2a', '#f3e8d0'], sign: ['CAFÉ', 'cup', '#4a2f1b', '#ffe9c7'], base: 1, w: 6, d: 6, kind: 'cafe' },
  { wall: '#ecc872', trim: '#7a5a1a', roof: '#a86a3a', awn: ['#2f6fb5', '#ffffff'], sign: ['BOULANGERIE', 'bread', '#7a4a1a', '#fff3d6'], base: 1, w: 6, d: 6, kind: 'bakery' },
  { wall: '#f4bfd0', trim: '#a83a6a', roof: '#c75a86', awn: ['#d4457a', '#ffffff'], sign: ['SALON', 'scissors', '#a83a6a', '#ffe6ef'], base: 1, w: 6, d: 6, kind: 'salon' },
  { wall: '#66ccc0', trim: '#1f6f68', roof: '#2a8a80', awn: ['#1f9a90', '#ffffff'], sign: ['ANIMALERIE', 'paw', '#1f6f68', '#e6fff9'], base: 1, w: 6, d: 6, kind: 'pet' },
  { wall: '#7656b8', trim: '#2a1a5a', roof: '#3a2a6a', awn: ['#4a2f9a', '#22d3ee'], sign: ['GAMING', 'pad', '#1c1240', '#8ff3ff'], base: 1, w: 6, d: 6, kind: 'games' },
  { wall: '#b8323f', trim: '#3a0a14', roof: '#4a1a22', awn: ['#7a1020', '#ffd34d'], sign: ['CINÉMA', 'film', '#26080e', '#ffd34d'], base: 1, w: 6, d: 6, kind: 'cinema' },
  { wall: '#f1f1e8', trim: '#2e8a4a', roof: '#7a8a80', awn: ['#2e8a4a', '#ffffff'], sign: ['SUPERMARCHÉ', 'cart', '#2e8a4a', '#ffffff'], base: 1, w: 7.4, d: 5.4, kind: 'market' },
  { wall: '#f4f8f4', trim: '#2e9e5b', roof: '#8a9a90', awn: ['#2e9e5b', '#ffffff'], sign: ['PHARMACIE', 'cross', '#1f7a44', '#ffffff'], base: 1, w: 6, d: 6, kind: 'pharmacy' },
  { wall: '#b25a40', trim: '#3a1a10', roof: '#5a3a30', awn: ['#a01828', '#fff1d6'], sign: ['RESTAURANT', 'fork', '#3a1a10', '#ffe1b5'], base: 1, w: 6, d: 6, kind: 'resto' },
  { wall: '#9ab0cc', trim: '#2a3a54', roof: '#4a5a70', awn: ['#c9a227', '#f3e8c0'], sign: ['HÔTEL', 'star', '#1a2a44', '#ffd76a'], base: 2, w: 6, d: 6, kind: 'hotel' },
  { wall: '#dcd5c4', trim: '#5a4a30', roof: '#8a6a50', awn: ['#8a2a2a', '#ffffff'], sign: ['IMMOBILIER', 'house', '#5a4a30', '#ffffff'], base: 2, w: 6, d: 6, kind: 'agency' },
  { wall: '#86a8d0', trim: '#1a2a40', roof: '#2a3a52', awn: ['#c9a227', '#1a2a40'], sign: ['EMPIRE', 'tower', '#1a2a40', '#ffd76a'], base: 3, w: 6, d: 6, kind: 'tower' }
];

/* ---------- Un bâtiment évolutif : étages empilés + toit + aile + couronne dorée ---------- */
function makeBuilding(i) {
  var v = VIS[i], w = v.w, d = v.d, g = grp(null), maxF = v.base + 4, k, seed = 100 + i * 17;
  var mShopF = facadeMat('shop', v, 0, seed), mShopS = facadeMat('sideShop', v, 2, seed + 1), mUpF = facadeMat('up', v, w > 7 ? 4 : 3, seed + 2), mUpS = facadeMat('side', v, 2, seed + 3);
  var roofM = std(v.roof, { roughness: 0.95 }), wallM = std(v.wall), trimM = std(v.trim, { roughness: 0.6 });
  var floorGeo = new THREE.BoxGeometry(w, FH, d), floors = [];
  for (k = 0; k < maxF; k++) {
    var mats = k === 0 ? [mShopS, mShopS, roofM, roofM, mShopF, mShopF] : [mUpS, mUpS, roofM, roofM, mUpF, mUpF];
    floors.push(mesh(g, floorGeo, mats, 0, k * FH + FH / 2, 0, 1, 1, 1, true));
  }
  // enseigne + auvent sur la façade avant (+z)
  var awnM = new THREE.MeshStandardMaterial({ map: stripeTex(v.awn[0], v.awn[1], 8), roughness: 0.85 });
  var aw = grp(g, 0, 1.95, d / 2 + 0.5); aw.rotation.x = 0.42; mesh(aw, new THREE.BoxGeometry(w - 0.9, 0.07, 1.15), awnM, 0, 0, 0, 1, 1, 1, true);
  mesh(g, new THREE.BoxGeometry(0.08, 1.6, 0.08), trimM, -(w - 1.1) / 2, 1.1, d / 2 + 0.95, 1, 1, 1, false); mesh(g, new THREE.BoxGeometry(0.08, 1.6, 0.08), trimM, (w - 1.1) / 2, 1.1, d / 2 + 0.95, 1, 1, 1, false);
  signMesh(g, v.sign[0], v.sign[1], v.sign[2], v.sign[3], Math.min(w - 1.2, 4.9), 0.62, 0, 2.23, d / 2 + 0.07);
  // toit : rebord + équipements propres à chaque commerce
  var roof = grp(g, 0, 0, 0), par = 0.28, pm = std(v.trim, { roughness: 0.7 });
  mesh(roof, new THREE.BoxGeometry(w + 0.2, par, 0.2), pm, 0, par / 2, d / 2, 1, 1, 1, true); mesh(roof, new THREE.BoxGeometry(w + 0.2, par, 0.2), pm, 0, par / 2, -d / 2, 1, 1, 1, true);
  mesh(roof, new THREE.BoxGeometry(0.2, par, d), pm, w / 2, par / 2, 0, 1, 1, 1, true); mesh(roof, new THREE.BoxGeometry(0.2, par, d), pm, -w / 2, par / 2, 0, 1, 1, 1, true);
  mesh(roof, new THREE.BoxGeometry(1.0, 0.7, 0.8), std('#8a9096', { metalness: 0.5, roughness: 0.5 }), -w * 0.28, 0.35 + par, -d * 0.2, 1, 1, 1, true);
  roofProps(v.kind, roof, w, d);
  // aile supplémentaire (palier 3) et couronne dorée (palier 4 = « hôtel »)
  var wing = grp(g, w / 2 + 1.25, 0, -0.4); var wf = new THREE.BoxGeometry(2.4, FH * 2, d - 1.2);
  mesh(wing, wf, [mUpS, mUpS, roofM, roofM, mUpF, mUpF], 0, FH, 0, 1, 1, 1, true); mesh(wing, new THREE.BoxGeometry(2.6, 0.2, d - 1), pm, 0, FH * 2 + 0.1, 0, 1, 1, 1, true); wing.visible = false;
  var gold = std('#e8b830', { metalness: 0.9, roughness: 0.25 }), crown = grp(g, 0, 0, 0), gm = glow('#ffcf4a', 1.4);
  mesh(crown, new THREE.BoxGeometry(w + 0.5, 0.18, 0.28), gold, 0, 0.5, d / 2 + 0.05, 1, 1, 1, false); mesh(crown, new THREE.BoxGeometry(w + 0.5, 0.18, 0.28), gold, 0, 0.5, -d / 2 - 0.05, 1, 1, 1, false);
  mesh(crown, new THREE.BoxGeometry(0.28, 0.18, d + 0.5), gold, w / 2 + 0.05, 0.5, 0, 1, 1, 1, false); mesh(crown, new THREE.BoxGeometry(0.28, 0.18, d + 0.5), gold, -w / 2 - 0.05, 0.5, 0, 1, 1, 1, false);
  mesh(crown, new THREE.CylinderGeometry(0.04, 0.04, 2.4, 8), gold, w / 2 - 0.3, 1.6, d / 2 - 0.3, 1, 1, 1, false); mesh(crown, new THREE.BoxGeometry(0.9, 0.5, 0.04), std('#d62828'), w / 2 - 0.75, 2.5, d / 2 - 0.3, 1, 1, 1, false);
  var star = mesh(crown, new THREE.OctahedronGeometry(0.45, 0), gm, 0, 1.9, 0, 1, 1.4, 1, false); star.userData.spin = true; crown.visible = false; crown.userData.star = star;
  var api = { group: g, floors: floors, roof: roof, wing: wing, crown: crown, base: v.base, maxF: maxF, tier: -1, popT: 1, w: w, d: d };
  g.userData.api = api; return api;
}
function setTier(api, t, animate) {
  var nf = api.base + t; api.floors.forEach(function (f, k) { f.visible = k < nf; });
  api.roof.position.y = nf * FH; api.crown.position.y = nf * FH; api.wing.visible = t >= 3; api.crown.visible = t >= 4;
  if (animate && api.tier >= 0) api.popT = 0; api.tier = t;
}
function roofProps(kind, r, w, d) {
  var white = std('#f4f4f4'), P = 0.28;
  if (kind === 'cafe') { mesh(r, new THREE.CylinderGeometry(0.55, 0.42, 0.75, 20), white, w * 0.18, 0.4 + P, d * 0.05, 1, 1, 1, true); mesh(r, new THREE.CylinderGeometry(0.5, 0.5, 0.04, 20), std('#4a2a18'), w * 0.18, 0.78 + P, d * 0.05, 1, 1, 1, false); var h = mesh(r, new THREE.TorusGeometry(0.28, 0.06, 8, 16), white, w * 0.18 + 0.62, 0.45 + P, d * 0.05, 1, 1, 1, false); h.rotation.y = Math.PI / 2; mesh(r, new THREE.CylinderGeometry(0.8, 0.8, 0.05, 20), white, w * 0.18, 0.03 + P, d * 0.05, 1, 1, 1, false); }
  else if (kind === 'bakery') { mesh(r, new THREE.BoxGeometry(0.7, 1.6, 0.7), std('#8a4a30'), -w * 0.3, 0.8 + P, -d * 0.1, 1, 1, 1, true); mesh(r, new THREE.BoxGeometry(0.85, 0.15, 0.85), std('#4a2a1a'), -w * 0.3, 1.65 + P, -d * 0.1, 1, 1, 1, false); r.userData.smoke = { x: -w * 0.3, y: 1.8 + P, z: -d * 0.1 }; }
  else if (kind === 'salon') { var pole = mesh(r, new THREE.CylinderGeometry(0.18, 0.18, 1.5, 16), new THREE.MeshStandardMaterial({ map: barberTex(), roughness: 0.4 }), w * 0.3, 0.75 + P, d * 0.28, 1, 1, 1, true); pole.userData.spinY = true; r.userData.pole = pole; mesh(r, new THREE.SphereGeometry(0.22, 12, 10), std('#ffffff'), w * 0.3, 1.55 + P, d * 0.28, 1, 1, 1, false); }
  else if (kind === 'pet') { var pm = std('#ffffff'); mesh(r, new THREE.SphereGeometry(0.55, 14, 12), pm, w * 0.12, 0.55 + P, 0, 1.2, 0.8, 1, true); [[-0.55, 0.5], [-0.2, 0.95], [0.2, 0.95], [0.55, 0.5]].forEach(function (q) { mesh(r, new THREE.SphereGeometry(0.2, 10, 8), pm, w * 0.12 + q[0], 0.55 + q[1] * 0.6 + P, 0.2, 1, 1.2, 1, true); }); }
  else if (kind === 'games') { var neon = glow('#22d3ee', 2.2), neon2 = glow('#ff3df2', 2.2); mesh(r, new THREE.BoxGeometry(w + 0.25, 0.1, 0.1), neon, 0, 0.12 + P, d / 2 + 0.12, 1, 1, 1, false); mesh(r, new THREE.BoxGeometry(0.1, 0.1, d + 0.25), neon2, w / 2 + 0.12, 0.12 + P, 0, 1, 1, 1, false); mesh(r, new THREE.CylinderGeometry(0.12, 0.12, 0.8, 10), std('#222'), -w * 0.2, 0.4 + P, 0.4, 1, 1, 1, true); mesh(r, new THREE.SphereGeometry(0.34, 14, 12), std('#e63946'), -w * 0.2, 0.95 + P, 0.4, 1, 1, 1, true); mesh(r, new THREE.CylinderGeometry(0.7, 0.8, 0.2, 14), std('#222'), -w * 0.2, 0.1 + P, 0.4, 1, 1, 1, true); }
  else if (kind === 'cinema') { var bm = glow('#ffd34d', 1.8), bl = mesh(r, new THREE.BoxGeometry(0.5, 2.4, 0.5), std('#26080e'), w / 2 - 0.4, 1.2 + P, d / 2 - 0.4, 1, 1, 1, true); signMesh(r, 'CINÉ', 'film', '#26080e', '#ffd34d', 2.2, 0.6, w / 2 - 0.4, 1.3 + P, d / 2 - 0.1).rotation.z = Math.PI / 2; for (var q = 0; q < 6; q++) mesh(r, new THREE.SphereGeometry(0.09, 8, 6), bm, -w * 0.4 + q * 0.5, 0.06 + P, d / 2 + 0.05, 1, 1, 1, false); mesh(r, new THREE.CylinderGeometry(0.5, 0.38, 0.8, 14), new THREE.MeshStandardMaterial({ map: stripeTex('#d62828', '#ffffff', 8), roughness: 0.7 }), -w * 0.2, 0.4 + P, 0, 1, 1, 1, true); for (var pp = 0; pp < 5; pp++) mesh(r, new THREE.SphereGeometry(0.22, 8, 6), std('#fff4c8'), -w * 0.2 + Math.cos(pp * 1.3) * 0.25, 0.95 + P + (pp % 2) * 0.12, Math.sin(pp * 1.3) * 0.25, 1, 1, 1, false); }
  else if (kind === 'market') { for (var s = 0; s < 3; s++) { var sp = mesh(r, new THREE.BoxGeometry(1.5, 0.05, 1.0), std('#16345c', { metalness: 0.6, roughness: 0.25 }), -w * 0.25 + s * 1.7, 0.3 + P, -d * 0.1, 1, 1, 1, true); sp.rotation.x = -0.35; } }
  else if (kind === 'pharmacy') { var gm2 = glow('#27e07a', 2.0); mesh(r, new THREE.BoxGeometry(0.4, 1.5, 0.3), gm2, w * 0.28, 1.1 + P, d * 0.2, 1, 1, 1, false); mesh(r, new THREE.BoxGeometry(1.5, 0.4, 0.3), gm2, w * 0.28, 1.1 + P, d * 0.2, 1, 1, 1, false); mesh(r, new THREE.BoxGeometry(0.12, 0.6, 0.12), std('#333'), w * 0.28, 0.3 + P, d * 0.2, 1, 1, 1, false); }
  else if (kind === 'resto') { var chef = std('#ffffff'); mesh(r, new THREE.CylinderGeometry(0.4, 0.34, 0.6, 14), chef, w * 0.2, 0.3 + P, 0, 1, 1, 1, true); [[0, 0], [0.3, 0.1], [-0.3, 0.1], [0, 0.3]].forEach(function (q) { mesh(r, new THREE.SphereGeometry(0.32, 10, 8), chef, w * 0.2 + q[0], 0.85 + P + q[1], q[1] * 0.4, 1, 1, 1, true); }); }
  else if (kind === 'hotel') { mesh(r, new THREE.CylinderGeometry(0.05, 0.05, 2.6, 8), std('#aaa', { metalness: 0.8 }), w * 0.25, 1.3 + P, -d * 0.25, 1, 1, 1, true); var hs = glow('#ff4d4d', 2.5); mesh(r, new THREE.SphereGeometry(0.1, 8, 6), hs, w * 0.25, 2.65 + P, -d * 0.25, 1, 1, 1, false); signMesh(r, 'HÔTEL', 'star', '#1a2a44', '#ffd76a', 2.4, 0.55, -w * 0.15, 0.7 + P, d / 2 - 0.1); }
  else if (kind === 'agency') { mesh(r, new THREE.BoxGeometry(1.4, 0.9, 1.1), std('#d9d0bd'), -w * 0.1, 0.45 + P, 0, 1, 1, 1, true); var rf = mesh(r, new THREE.ConeGeometry(1.15, 0.8, 4), std('#a83a32'), -w * 0.1, 1.3 + P, 0, 1, 1, 1, true); rf.rotation.y = Math.PI / 4; }
  else if (kind === 'tower') { mesh(r, new THREE.CylinderGeometry(0.06, 0.12, 3.2, 8), std('#bbb', { metalness: 0.8, roughness: 0.3 }), 0, 1.6 + P, 0, 1, 1, 1, true); var ts = glow('#ff3b3b', 2.8); mesh(r, new THREE.SphereGeometry(0.14, 8, 6), ts, 0, 3.25 + P, 0, 1, 1, 1, false); mesh(r, new THREE.CylinderGeometry(0.2, 1.3, 0.9, 4), std('#6fa8dc', { metalness: 0.6, roughness: 0.2 }), 0, 0.45 + P, 0, 1, 1, 1, true).rotation.y = Math.PI / 4; }
}
function barberTex() {
  var c = canvas(32, 128), x = c.getContext('2d'); for (var i = 0; i < 8; i++) { x.fillStyle = ['#d62828', '#ffffff', '#1d4ed8', '#ffffff'][i % 4]; x.beginPath(); x.moveTo(0, i * 16); x.lineTo(32, i * 16 - 10); x.lineTo(32, i * 16 + 6); x.lineTo(0, i * 16 + 16); x.fill(); }
  return tex(c, true);
}

/* ---------- Parcelle : trottoir, jardinières, arbres, chantier « à vendre » ---------- */
function makeSite() {
  var g = grp(null), fence = std('#ff8a1f', { roughness: 0.6 }), dirt = std('#8a6a48', { roughness: 1 });
  mesh(g, new THREE.BoxGeometry(6.4, 0.06, 6.4), dirt, 0, 0.12, 0, 1, 1, 1, false);
  var i; for (i = 0; i < 8; i++) { mesh(g, new THREE.BoxGeometry(0.12, 1.0, 0.12), std('#cccccc'), -3.0 + i * 0.86, 0.6, 3.1, 1, 1, 1, true); }
  mesh(g, new THREE.BoxGeometry(6.2, 0.14, 0.05), fence, 0, 0.95, 3.1, 1, 1, 1, true); mesh(g, new THREE.BoxGeometry(6.2, 0.14, 0.05), fence, 0, 0.55, 3.1, 1, 1, 1, true);
  mesh(g, new THREE.BoxGeometry(0.05, 0.14, 6.2), fence, 3.1, 0.95, 0, 1, 1, 1, true); mesh(g, new THREE.BoxGeometry(0.05, 0.14, 6.2), fence, 3.1, 0.55, 0, 1, 1, 1, true);
  for (i = 0; i < 3; i++) mesh(g, new THREE.ConeGeometry(0.22, 0.6, 10), std('#ff6a00'), -2 + i * 2, 0.45, 3.5, 1, 1, 1, true);
  var cr = grp(g, -1.6, 0, -1.4); mesh(cr, new THREE.BoxGeometry(0.3, 5, 0.3), std('#f2c200'), 0, 2.5, 0, 1, 1, 1, true); mesh(cr, new THREE.BoxGeometry(4.2, 0.25, 0.25), std('#f2c200'), 1.2, 5.0, 0, 1, 1, 1, true);
  mesh(cr, new THREE.BoxGeometry(0.8, 0.5, 0.6), std('#444'), -0.6, 4.7, 0, 1, 1, 1, true); mesh(cr, new THREE.CylinderGeometry(0.02, 0.02, 2.2, 6), std('#222'), 2.4, 3.9, 0, 1, 1, 1, false); mesh(cr, new THREE.BoxGeometry(0.4, 0.3, 0.4), std('#d62828'), 2.4, 2.7, 0, 1, 1, 1, true);
  mesh(g, new THREE.BoxGeometry(1.6, 0.8, 1.2), std('#c9c2b0'), 1.6, 0.5, -1.2, 1, 1, 1, true); mesh(g, new THREE.BoxGeometry(1.2, 0.6, 1.0), std('#a8a090'), 1.8, 1.2, -1.2, 1, 1, 1, true);
  var sc = signCanvas('À VENDRE', 'house', '#c62828', '#ffffff', 512, 128), sm = new THREE.MeshStandardMaterial({ map: tex(sc, true), roughness: 0.7 });
  mesh(g, new THREE.BoxGeometry(2.6, 0.65, 0.08), [std('#222'), std('#222'), std('#222'), std('#222'), sm, std('#222')], 0, 1.7, 3.15, 1, 1, 1, true);
  mesh(g, new THREE.BoxGeometry(0.1, 1.2, 0.1), std('#555'), -1.1, 1.0, 3.12, 1, 1, 1, false); mesh(g, new THREE.BoxGeometry(0.1, 1.2, 0.1), std('#555'), 1.1, 1.0, 3.12, 1, 1, 1, false);
  g.userData.crane = cr; return g;
}

/* ---------- Voitures et bus ---------- */
var CAR_COLORS = ['#d62828', '#2a6fdb', '#f2c200', '#2e9e5b', '#8a4adb', '#f08a24', '#e8e8e8', '#222a36'];
function makeCar(kind) {
  var g = grp(null), col = kind === 'bus' ? '#f2b90a' : CAR_COLORS[Math.floor(Math.random() * CAR_COLORS.length)], len = kind === 'bus' ? 3.4 : 1.7, hgt = kind === 'bus' ? 0.95 : 0.5;
  var body = new THREE.MeshStandardMaterial({ color: C(col), roughness: 0.35, metalness: 0.45 }), glass = std('#1a2a3a', { roughness: 0.15, metalness: 0.7 });
  mesh(g, new THREE.BoxGeometry(len, hgt, 0.85), body, 0, 0.3 + hgt / 2, 0, 1, 1, 1, true);
  if (kind === 'bus') { mesh(g, new THREE.BoxGeometry(len * 0.92, 0.35, 0.87), glass, 0, 0.95, 0, 1, 1, 1, false); } else { mesh(g, new THREE.BoxGeometry(len * 0.5, 0.36, 0.78), glass, -0.1, 0.3 + hgt + 0.16, 0, 1, 1, 1, true); }
  var wm = std('#111111', { roughness: 0.9 }); [-len * 0.32, len * 0.32].forEach(function (x) { var a = mesh(g, new THREE.CylinderGeometry(0.2, 0.2, 0.95, 10), wm, x, 0.2, 0, 1, 1, 1, true); a.rotation.x = Math.PI / 2; });
  var hl = glow('#fff2b0', 1.4); mesh(g, new THREE.BoxGeometry(0.06, 0.12, 0.6), hl, len / 2, 0.45, 0, 1, 1, 1, false); mesh(g, new THREE.BoxGeometry(0.06, 0.12, 0.6), std('#aa1111', { emissive: C('#770000') }), -len / 2, 0.45, 0, 1, 1, 1, false);
  return g;
}
var ROADX = [-18, -6, 6, 18], ROADZ = [-24, -12, 0, 12, 24];
function spawnCar(c) {
  var vert = Math.random() < 0.5, dir = Math.random() < 0.5 ? 1 : -1; c.vert = vert; c.dir = dir; c.sp = rnd(3.2, 5.2);
  if (vert) { c.line = ROADX[Math.floor(Math.random() * ROADX.length)]; c.s = rnd(-24, 24); } else { c.line = ROADZ[Math.floor(Math.random() * ROADZ.length)]; c.s = rnd(-18, 18); }
  c.turn = 0; placeCar(c);
}
function placeCar(c) {
  var off = 0.8 * c.dir, x, z;
  if (c.vert) { x = c.line - off; z = c.s; } else { x = c.s; z = c.line + off; }
  c.g.position.set(x, 0.14, z);
  var ang = c.vert ? (c.dir > 0 ? Math.PI / 2 : -Math.PI / 2) : (c.dir > 0 ? 0 : Math.PI); c.ang = c.ang === undefined ? ang : c.ang;
  var d = ang - c.ang; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; c.ang += d * 0.2; c.g.rotation.y = -c.ang;
}
function stepCar(c, dt) {
  var prev = c.s; c.s += c.dir * c.sp * dt;
  var lines = c.vert ? ROADZ : ROADX;
  for (var k = 0; k < lines.length; k++) {
    var L = lines[k];
    if ((prev - L) * (c.s - L) <= 0 && Math.abs(prev - c.s) < 2) {                      // franchit une intersection : on choisit une direction
      var r = Math.random();
      if (r < 0.42) { var np = c.vert ? ROADX : ROADZ, ok = false; var newLine = c.vert ? L : L; var oldS = c.line; c.vert = !c.vert; c.line = L; c.s = oldS; c.dir = Math.random() < 0.5 ? 1 : -1; var lo = c.vert ? -24 : -18, hi = c.vert ? 24 : 18; if ((c.dir > 0 && c.s >= hi) || (c.dir < 0 && c.s <= lo)) c.dir = -c.dir; break; }
    }
  }
  var lim = c.vert ? 26 : 20; if (c.s > lim) { c.s = lim; c.dir = -1; } else if (c.s < -lim) { c.s = -lim; c.dir = 1; }
  placeCar(c);
}

/* ---------- Décor : routes, parcelles, arbres, lampadaires ---------- */
function plotPos(i) { var r = Math.floor(i / COLS), c = i % COLS; return new THREE.Vector3((c - 1) * CELL, 0, (1.5 - r) * CELL); }
function buildCity() {
  var rng = mulberry(5), i, k;
  var gm = pbrMat(TEX.grass, 70, 70, { color: C('#9fd070') });
  ground = mesh(scene, new THREE.PlaneGeometry(500, 500), gm, 0, -0.01, 0, 1, 1, 1, false, true); ground.rotation.x = -Math.PI / 2;
  // routes
  var rm = pbrMat(TEX.asph, 1, 1, { color: C('#dddddd') });
  function roadTex(len) { var m = rm.clone(); m.map = rm.map.clone(); m.map.needsUpdate = true; m.map.repeat.set(len / 6, 1); m.normalMap = rm.normalMap.clone(); m.normalMap.needsUpdate = true; m.normalMap.repeat.set(len / 6, 1); m.roughnessMap = rm.roughnessMap.clone(); m.roughnessMap.needsUpdate = true; m.roughnessMap.repeat.set(len / 6, 1); return m; }
  var lineM = std('#e9d36a', { roughness: 0.8 });
  ROADX.forEach(function (x) { var rd = mesh(scene, new THREE.BoxGeometry(3, 0.1, 54), roadTex(54), x, 0.05, 0, 1, 1, 1, false, true); rd.rotation.y = 0; for (var s = -26; s < 27; s += 2.4) mesh(scene, new THREE.BoxGeometry(0.12, 0.02, 1.1), lineM, x, 0.11, s, 1, 1, 1, false, true); });
  ROADZ.forEach(function (z) { var rd = mesh(scene, new THREE.BoxGeometry(42, 0.1, 3), roadTex(42), 0, 0.05, z, 1, 1, 1, false, true); for (var s = -20; s < 21; s += 2.4) mesh(scene, new THREE.BoxGeometry(1.1, 0.02, 0.12), lineM, s, 0.11, z, 1, 1, 1, false, true); });
  // trottoirs + parcelles
  var cm = pbrMat(TEX.conc, 2, 2, { color: C('#d8d4cc') });
  var curb = std('#9a968c', { roughness: 0.9 });
  for (i = 0; i < ROWS * COLS; i++) {
    var p = plotPos(i), pl = { i: i, pos: p, anchor: new THREE.Vector3(p.x, 0.3, p.z + 4.6), center: new THREE.Vector3(p.x, 2.2, p.z), state: -1 };
    var slab = mesh(scene, new THREE.BoxGeometry(CELL - 3, 0.2, CELL - 3), cm, p.x, 0.1, p.z, 1, 1, 1, false, true);
    mesh(scene, new THREE.BoxGeometry(CELL - 3 + 0.3, 0.12, 0.2), curb, p.x, 0.12, p.z + (CELL - 3) / 2, 1, 1, 1, false); mesh(scene, new THREE.BoxGeometry(CELL - 3 + 0.3, 0.12, 0.2), curb, p.x, 0.12, p.z - (CELL - 3) / 2, 1, 1, 1, false);
    var holder = grp(scene, p.x, 0.2, p.z - 0.6); pl.holder = holder;
    var bld = makeBuilding(i % 12); pl.bld = bld; holder.add(bld.group); bld.group.visible = false;
    var site = makeSite(); pl.site = site; holder.add(site);
    // district : bandeau coloré au sol (comme les groupes de couleur d'un plateau)
    var dc = Engine.DISTRICTS[Math.floor(i / 3)].color; mesh(scene, new THREE.BoxGeometry(CELL - 3, 0.06, 0.55), std(dc, { roughness: 0.6 }), p.x, 0.23, p.z + (CELL - 3) / 2 - 0.55, 1, 1, 1, false, true);
    plots.push(pl);
  }
  // arbres et jardinières (instanciés)
  var nt = Math.floor(70 * Q.trees), trunkG = new THREE.CylinderGeometry(0.1, 0.14, 0.9, 7), crownG = new THREE.IcosahedronGeometry(0.85, 1);
  var trunks = new THREE.InstancedMesh(trunkG, std('#6a4a2a', { roughness: 1 }), nt), crowns = new THREE.InstancedMesh(crownG, new THREE.MeshStandardMaterial({ roughness: 0.8 }), nt), m4 = new THREE.Matrix4(), q4 = new THREE.Quaternion(), s3 = new THREE.Vector3(), p3 = new THREE.Vector3(), col = new THREE.Color();
  for (i = 0; i < nt; i++) {
    var tx, tz, ok = false, tries = 0; while (!ok && tries++ < 30) {
      if (i < nt * 0.55) { var pi = Math.floor(rng() * 12), pp = plotPos(pi), ex = rng() < 0.5 ? -1 : 1; tx = pp.x + ex * (CELL - 3) / 2 * 0.85; tz = pp.z - (CELL - 3) / 2 * (0.6 + rng() * 0.35); ok = true; }
      else { tx = (rng() - 0.5) * 80; tz = (rng() - 0.5) * 90; ok = Math.abs(tx) > 22 || Math.abs(tz) > 28; }
    }
    var sc = 0.8 + rng() * 0.7; p3.set(tx, 0.2 + 0.45 * sc, tz); s3.set(sc, sc, sc); m4.compose(p3, q4, s3); trunks.setMatrixAt(i, m4);
    p3.set(tx, 0.2 + 0.9 * sc + 0.7 * sc, tz); s3.set(sc, sc * (0.9 + rng() * 0.4), sc); m4.compose(p3, q4, s3); crowns.setMatrixAt(i, m4);
    col.setHSL(0.27 + rng() * 0.08, 0.5, 0.3 + rng() * 0.12); crowns.setColorAt(i, col);
  }
  trunks.castShadow = crowns.castShadow = true; trunks.frustumCulled = crowns.frustumCulled = false; scene.add(trunks); scene.add(crowns);
  // lampadaires
  var lamps = [], poleM = std('#3a3f46', { metalness: 0.6, roughness: 0.4 }), headM = glow('#ffe7a0', 2.0), poolM = new THREE.MeshBasicMaterial({ map: tex(radialCanvas(), true), transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, color: C('#ffcf80') });
  nightMats.push({ m: poolM, base: 0.9, mode: 'opacity' });
  ROADX.forEach(function (x, xi) { ROADZ.forEach(function (z, zi) { if ((xi + zi) % 2 === 0) lamps.push([x + 1.9, z + 1.9]); }); });
  lamps.forEach(function (l) {
    mesh(scene, new THREE.CylinderGeometry(0.06, 0.08, 3.4, 8), poleM, l[0], 1.7, l[1], 1, 1, 1, true); mesh(scene, new THREE.BoxGeometry(0.6, 0.12, 0.3), headM, l[0] - 0.2, 3.4, l[1], 1, 1, 1, false);
    var pool = mesh(scene, new THREE.PlaneGeometry(5, 5), poolM, l[0] - 0.2, 0.13, l[1], 1, 1, 1, false); pool.rotation.x = -Math.PI / 2; pool.renderOrder = 3;
  });
  // véhicules
  for (i = 0; i < Q.cars; i++) { var c = { g: makeCar(i % 7 === 0 ? 'bus' : 'car') }; scene.add(c.g); spawnCar(c); cars.push(c); }
  // nuages (ombres douces qui passent)
}
function radialCanvas() { var c = canvas(128, 128), x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 2, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,0.85)'); g.addColorStop(0.4, 'rgba(255,255,255,0.28)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); return c; }

/* ---------- Jour / nuit ---------- */
var KEYS = [   // t, soleil (couleur, intensité), hémisphère (ciel, sol, intensité), fond, nuit
  { t: 0.00, sun: '#ffb070', si: 1.1, sky: '#9fb4d8', gr: '#6a5a4a', hi: 0.55, bg: '#e8b890', n: 0.35 },
  { t: 0.18, sun: '#fff1d6', si: 2.3, sky: '#bfdcff', gr: '#7a7a5a', hi: 0.8, bg: '#bfe0ff', n: 0 },
  { t: 0.42, sun: '#fff1d6', si: 2.2, sky: '#bfdcff', gr: '#7a7a5a', hi: 0.8, bg: '#bcdcff', n: 0 },
  { t: 0.55, sun: '#ff9a5a', si: 1.4, sky: '#e6a888', gr: '#6a4a3a', hi: 0.6, bg: '#f0a070', n: 0.3 },
  { t: 0.66, sun: '#6a82c8', si: 0.55, sky: '#1f2a52', gr: '#1a1a2a', hi: 0.55, bg: '#16203e', n: 1 },
  { t: 0.88, sun: '#6a82c8', si: 0.55, sky: '#1f2a52', gr: '#1a1a2a', hi: 0.55, bg: '#16203e', n: 1 },
  { t: 1.00, sun: '#ffb070', si: 1.1, sky: '#9fb4d8', gr: '#6a5a4a', hi: 0.55, bg: '#e8b890', n: 0.35 }
];
var cA = new THREE.Color(), cB = new THREE.Color();
function lerpCol(out, a, b, t) { cA.set(a).convertSRGBToLinear(); cB.set(b).convertSRGBToLinear(); out.copy(cA).lerp(cB, t); }
function applyDay(t) {
  var k = 0; while (k < KEYS.length - 2 && t > KEYS[k + 1].t) k++;
  var a = KEYS[k], b = KEYS[k + 1], u = smooth((t - a.t) / (b.t - a.t));
  lerpCol(sun.color, a.sun, b.sun, u); sun.intensity = a.si + (b.si - a.si) * u;
  lerpCol(hemi.color, a.sky, b.sky, u); lerpCol(hemi.groundColor, a.gr, b.gr, u); hemi.intensity = a.hi + (b.hi - a.hi) * u;
  lerpCol(scene.background, a.bg, b.bg, u); scene.fog.color.copy(scene.background); nightF = a.n + (b.n - a.n) * u;
  var ang = (t - 0.18) / 0.5 * Math.PI, el = nightF > 0.6 ? 0.9 : Math.max(0.25, Math.sin(clamp(ang, 0.05, 3.1)));
  sun.position.set(tgt.x - 22 + 8 * Math.cos(ang), 22 * el + 6, tgt.z + 16); sun.target.position.copy(tgt);
  renderer.toneMappingExposure = 1.0 + 0.15 * nightF;
  nightMats.forEach(function (o) {
    if (o.mode === 'opacity') o.m.opacity = nightF * o.base;
    else if (o.mode === 'night') o.m.emissiveIntensity = o.base * (o.shop ? 0.25 + 0.75 * nightF : nightF);
  });
}

/* ---------- Initialisation ---------- */
function init(cv, quality) {
  qName = QUAL[quality] ? quality : 'medium'; Q = QUAL[qName];
  renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, powerPreference: 'high-performance' });
  renderer.outputEncoding = THREE.sRGBEncoding; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, Q.pr));
  scene = new THREE.Scene(); scene.background = new THREE.Color(0xbfe0ff); scene.fog = new THREE.Fog(0xbfe0ff, 70, 170);
  camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -200, 400);
  hemi = new THREE.HemisphereLight(0xbfdcff, 0x7a7a5a, 0.8); scene.add(hemi);
  sun = new THREE.DirectionalLight(0xfff1d6, 2.2); sun.castShadow = true; var sc = sun.shadow.camera; sc.left = -34; sc.right = 34; sc.top = 34; sc.bottom = -34; sc.near = 1; sc.far = 120;
  sun.shadow.mapSize.set(Q.shadow, Q.shadow); sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.04; scene.add(sun); scene.add(sun.target);
  makeTextures(); buildCity(); buildPawn(); applyDay(dayT); resize();
}
function resize() {
  var w = window.innerWidth || 400, h = window.innerHeight || 800; W = w; H = h; renderer.setSize(w, h); updateCam();
}
function updateCam() {
  var asp = W / H, hh = viewH, ww = viewH * asp; camera.left = -ww / 2; camera.right = ww / 2; camera.top = hh / 2; camera.bottom = -hh / 2; camera.updateProjectionMatrix();
  var D = 80; camera.position.set(tgt.x + D * Math.cos(ELEV) * 0.7071, tgt.y + D * Math.sin(ELEV), tgt.z + D * Math.cos(ELEV) * 0.7071); camera.lookAt(tgt); camera.updateMatrixWorld(true);
}
function clampTgt() { tgt.x = clamp(tgt.x, -16, 16); tgt.z = clamp(tgt.z, -22, 24); }
function pan(dx, dy) {
  var ppu = H / viewH, s = Math.sin(ELEV), k = 0.7071;
  tgt.x += -(dx / ppu) * k - (dy / (ppu * s)) * k; tgt.z += (dx / ppu) * k - (dy / (ppu * s)) * k;
  focusTarget = null; clampTgt(); updateCam();
}
function zoomBy(f) { viewH = clamp(viewH * f, 16, 62); updateCam(); }
function setView(h) { viewH = clamp(h, 16, 62); updateCam(); }
function focusPlot(i, instant, j) { var p = plotPos(i); if (j !== undefined && plots[j]) { var q = plotPos(j); p = new THREE.Vector3((p.x + q.x) / 2, 0, (p.z + q.z) / 2); } focusTarget = new THREE.Vector3(p.x, 0, p.z + 3); if (instant) { tgt.copy(focusTarget); clampTgt(); updateCam(); focusTarget = null; } }
var focusTarget = null;


/* ---------- Pion du joueur : un patron qui se promène sur l'avenue qui fait le tour de la ville ---------- */
var LOOP = [[18, 24], [-18, 24], [-18, -24], [18, -24]], LOOP_LEN = 168, TILES = 20, PAWN_OFF = 24, pawn = null;
function loopAt(s) {
  s = ((s % LOOP_LEN) + LOOP_LEN) % LOOP_LEN; var i = 0, L = [36, 48, 36, 48];
  while (s > L[i]) { s -= L[i]; i++; }
  var a = LOOP[i], b = LOOP[(i + 1) % 4], t = s / L[i], dx = b[0] - a[0], dz = b[1] - a[1], len = Math.sqrt(dx * dx + dz * dz), nx = dx / len, nz = dz / len;
  // décalage vers l'intérieur de la ville (trottoir) : à gauche du sens de marche
  return { x: a[0] + dx * t - nz * 1.15, z: a[1] + dz * t + nx * 1.15, ry: Math.atan2(nx, nz) };
}
function buildPawn() {
  var g = new THREE.Group(), suit = std('#2b4d9c', { roughness: 0.55 }), skin = std('#f1c49b', { roughness: 0.7 }), gold = std('#ffc93a', { roughness: 0.3, metalness: 0.6 }), dark = std('#1c1f26', { roughness: 0.5 });
  mesh(g, new THREE.CylinderGeometry(0.75, 0.85, 0.18, 24), gold, 0, 0.09, 0, 1, 1, 1, true, true);
  var body = new THREE.Group(); g.add(body);
  mesh(body, new THREE.CylinderGeometry(0.34, 0.5, 1.45, 18), suit, 0, 0.95, 0, 1, 1, 1, true, true);
  mesh(body, new THREE.SphereGeometry(0.36, 20, 16), skin, 0, 1.95, 0, 1, 1, 1, true, true);
  mesh(body, new THREE.CylinderGeometry(0.5, 0.5, 0.06, 20), dark, 0, 2.2, 0, 1, 1, 1, true, true);
  mesh(body, new THREE.CylinderGeometry(0.3, 0.32, 0.5, 20), dark, 0, 2.48, 0, 1, 1, 1, true, true);
  mesh(body, new THREE.BoxGeometry(0.12, 0.62, 0.06), std('#e5484d', { roughness: 0.6 }), 0, 1.35, 0.4, 1, 1, 1, false, false);
  mesh(body, new THREE.BoxGeometry(0.16, 0.16, 0.5), std('#2b4d9c', { roughness: 0.6 }), 0.52, 1.22, 0.14, 1, 1, 1, true, false);
  mesh(body, new THREE.BoxGeometry(0.16, 0.16, 0.5), std('#2b4d9c', { roughness: 0.6 }), -0.52, 1.22, 0.14, 1, 1, 1, true, false);
  var eyeM = std('#111', { roughness: 0.4 }); mesh(body, new THREE.SphereGeometry(0.05, 8, 8), eyeM, 0.13, 2.0, 0.32, 1, 1, 1, false, false); mesh(body, new THREE.SphereGeometry(0.05, 8, 8), eyeM, -0.13, 2.0, 0.32, 1, 1, 1, false, false);
  var arrow = new THREE.Mesh(new THREE.ConeGeometry(0.55, 1.1, 4), new THREE.MeshStandardMaterial({ color: C('#ffc93a'), emissive: C('#ff9d00'), emissiveIntensity: 0.9, roughness: 0.4 })); arrow.rotation.x = Math.PI; arrow.position.y = 5; g.add(arrow);
  g.scale.set(1.5, 1.5, 1.5); scene.add(g);
  pawn = { g: g, body: body, arrow: arrow, s: 0, from: 0, to: 0, t: 1, dur: 1, cb: null, moving: false };
}
function pawnSet(tile) { if (!pawn) return; pawn.s = pawn.from = pawn.to = tile * (LOOP_LEN / TILES); pawn.t = 1; pawn.moving = false; pawn.cb = null; placePawn(); }
function pawnGo(tile, dur, cb) {       // avance toujours dans le même sens, jusqu'à la case « tile »
  if (!pawn) { if (cb) cb(); return; }
  var step = LOOP_LEN / TILES, to = tile * step, from = ((pawn.s % LOOP_LEN) + LOOP_LEN) % LOOP_LEN; if (to < from - 0.01) to += LOOP_LEN;
  pawn.from = from; pawn.to = to; pawn.t = 0; pawn.dur = Math.max(0.05, dur); pawn.cb = cb || null; pawn.moving = true;
}
function placePawn() { var p = loopAt(pawn.s + PAWN_OFF); pawn.g.position.set(p.x, 0.12, p.z); pawn.g.rotation.y = p.ry; }
function pawnPos() { var p = loopAt((pawn ? pawn.s : 0) + PAWN_OFF); return { x: p.x, z: p.z }; }
function stepPawn(dt) {
  if (!pawn) return;
  if (pawn.moving) {
    pawn.t = Math.min(1, pawn.t + dt / pawn.dur); pawn.s = pawn.from + (pawn.to - pawn.from) * pawn.t; placePawn();
    var ph = clockT * 15; pawn.g.position.y = 0.12 + Math.abs(Math.sin(ph)) * 0.22; pawn.body.rotation.x = 0.12; pawn.body.rotation.z = Math.sin(ph) * 0.06;
    if (pawn.t >= 1) { pawn.moving = false; pawn.s = pawn.to % LOOP_LEN; pawn.body.rotation.set(0, 0, 0); var cb = pawn.cb; pawn.cb = null; if (cb) cb(); }
  } else { pawn.body.scale.y = 1 + Math.sin(clockT * 2.2) * 0.015; }
  pawn.arrow.position.y = 5 + Math.sin(clockT * 3) * 0.35; pawn.arrow.rotation.y += dt * 2;
}
function focusPoint(x, z, instant) { focusTarget = new THREE.Vector3(x, 0, z + 3); if (instant) { tgt.copy(focusTarget); clampTgt(); updateCam(); focusTarget = null; } }

/* ---------- États des parcelles ---------- */
function setPlot(i, state, tier, animate) {          // state : 0 verrouillée, 1 à vendre (prochaine), 2 possédée
  var pl = plots[i]; if (!pl) return;
  if (pl.state !== state) {
    var was = pl.state; pl.state = state; pl.site.visible = state < 2; pl.bld.group.visible = state === 2; pl.site.userData.dim = state === 0;
    if (state === 2 && was >= 0 && animate) { pl.bld.popT = 0; pl.bld.rise = 0; puff(pl.pos.x, 1.2, pl.pos.z + 1); puff(pl.pos.x + 1.5, 1, pl.pos.z); puff(pl.pos.x - 1.5, 1, pl.pos.z); }
    if (state === 2 && !animate) pl.bld.rise = 1;
  }
  if (state === 2 && pl.bld.tier !== tier) { var t0 = pl.bld.tier; setTier(pl.bld, tier, animate); if (animate && t0 >= 0 && tier > t0) { puff(pl.pos.x, 3, pl.pos.z); puff(pl.pos.x + 1.2, 2.4, pl.pos.z + 1); } }
}
function puff(x, y, z) {
  var sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex(radialCanvas(), true), transparent: true, opacity: 0.8, depthWrite: false, color: 0xffffff })); sp.position.set(x, y, z); sp.scale.set(1, 1, 1); scene.add(sp); puffs.push({ s: sp, t: 0 });
}

/* ---------- Projection (cartes HTML au-dessus de la ville) ---------- */
var _v = new THREE.Vector3();
function projectPoint(v3) { _v.copy(v3).project(camera); return { x: (_v.x * 0.5 + 0.5) * W, y: (-_v.y * 0.5 + 0.5) * H, z: _v.z }; }
function cardPos(i) { return projectPoint(plots[i].anchor); }
function bodyPos(i) { return projectPoint(plots[i].center); }
function pxPerUnit() { return H / viewH; }

/* ---------- Boucle ---------- */
function frame(dt) {
  clockT += dt; dayT = (dayT + dt / 420) % 1; applyDay(dayT);
  if (focusTarget) { tgt.lerp(focusTarget, 1 - Math.exp(-4 * dt)); if (tgt.distanceTo(focusTarget) < 0.05) focusTarget = null; clampTgt(); updateCam(); }
  else if (sun) { sun.target.position.copy(tgt); }
  for (var i = 0; i < plots.length; i++) {
    var pl = plots[i], b = pl.bld;
    if (pl.state === 2) {
      if (b.rise !== undefined && b.rise < 1) { b.rise = Math.min(1, b.rise + dt * 1.6); var e = smooth(b.rise); b.group.scale.y = Math.max(0.02, e * (1 + Math.sin(e * Math.PI) * 0.1)); }
      else if (b.popT < 1) { b.popT += dt * 2.4; var s = 1 + Math.sin(Math.min(1, b.popT) * Math.PI) * 0.07; b.group.scale.set(s, s, s); } else if (b.group.scale.y !== 1) b.group.scale.set(1, 1, 1);
      if (b.crown.visible) b.crown.userData.star.rotation.y += dt * 1.5;
      if (b.roof.userData.pole) b.roof.userData.pole.rotation.y += dt * 2;
    } else if (pl.site.userData.crane) { pl.site.userData.crane.rotation.y = Math.sin(clockT * 0.4 + i) * 0.5; }
  }
  stepPawn(dt); for (var c = 0; c < cars.length; c++) stepCar(cars[c], dt);
  for (var p = puffs.length - 1; p >= 0; p--) { var pf = puffs[p]; pf.t += dt; pf.s.position.y += dt * 1.6; var sc = 1 + pf.t * 3.2; pf.s.scale.set(sc, sc, sc); pf.s.material.opacity = Math.max(0, 0.8 - pf.t * 0.9); if (pf.t > 0.9) { scene.remove(pf.s); pf.s.material.dispose(); puffs.splice(p, 1); } }
}
function render() { renderer.render(scene, camera); }
function setQuality(q) {
  if (!QUAL[q] || q === qName) return; qName = q; Q = QUAL[q]; renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, Q.pr));
  sun.shadow.mapSize.set(Q.shadow, Q.shadow); if (sun.shadow.map) { sun.shadow.map.dispose(); sun.shadow.map = null; } resize();
}
function info() { return { renderer: renderer, scene: scene, camera: camera, plots: plots, night: nightF, dayT: dayT, viewH: viewH, tgt: tgt }; }

return { init: init, resize: resize, frame: frame, render: render, setPlot: setPlot, cardPos: cardPos, bodyPos: bodyPos, pan: pan, zoomBy: zoomBy, setView: setView, focusPlot: focusPlot,
  setQuality: setQuality, pxPerUnit: pxPerUnit, info: info, night: function () { return nightF; }, setDay: function (t) { dayT = t; applyDay(t); }, VIS: VIS, qualityName: function () { return qName; }, puff: puff, pawnSet: pawnSet, pawnGo: pawnGo, pawnPos: pawnPos, focusPoint: focusPoint, pawnMoving: function () { return !!(pawn && pawn.moving); } };
})();
