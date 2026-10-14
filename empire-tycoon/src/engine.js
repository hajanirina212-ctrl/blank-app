/* =====================================================================
 * 1. MOTEUR D'ÉCONOMIE (aucun DOM, aucun Three.js : testable seul)
 *    Commerces, niveaux, paliers, quartiers, conseillers, quêtes, dés,
 *    boosts, événements, gains hors ligne, prestige, sauvegarde.
 * ===================================================================== */
var Engine = (function () {
'use strict';

var SAVE_KEY = 'empire_tycoon_save_v1';
var clock = function () { return Date.now(); };

/* ---------- Données : quartiers et commerces ---------- */
var DISTRICTS = [
  { name: 'Centre-ville',          color: '#8b5a2b' },
  { name: 'Quartier des loisirs',  color: '#2fb5d6' },
  { name: 'Quartier marchand',     color: '#f08a24' },
  { name: 'Quartier d\'affaires',  color: '#2e9e5b' }
];
/* [id, nom, croissance du prix, durée du cycle (s)] ; prix d'achat et revenu sont calculés par formules */
var ROWS = [
  ['cafe', 'Café', 1.07, 1], ['bakery', 'Boulangerie', 1.15, 2], ['salon', 'Salon de beauté', 1.14, 4],
  ['pet', 'Animalerie', 1.13, 8], ['games', 'Salle de jeux', 1.12, 16], ['cinema', 'Cinéma', 1.11, 30],
  ['market', 'Supermarché', 1.10, 60], ['pharmacy', 'Pharmacie', 1.09, 120], ['resto', 'Restaurant', 1.085, 240],
  ['hotel', 'Hôtel', 1.08, 480], ['agency', 'Agence immobilière', 1.075, 900], ['tower', 'Tour d\'affaires', 1.07, 1800]
];
var START = 2500, DAY_S = 10, LIVING = 900, TAX = 0.12, INTEREST = 0.015, GARNISH = 0.3;   // épargne de départ, 1 jour = 10 s, vie courante /mois, impôt annuel, intérêt mensuel, part des revenus qui rembourse la dette
var B0 = 2000, RATIO = 8, PB0 = 120, PBG = 1.8;           // prix du 1er commerce, ratio de prix, temps de remboursement (s)
var BIZ = ROWS.map(function (r, i) {
  var b = B0 * Math.pow(RATIO, i), payback = PB0 * Math.pow(PBG, i);   // prix du 1er niveau (×40 par commerce) ; temps de remboursement d'un niveau (s)
  return { id: r[0], name: r[1], dist: Math.floor(i / 3), b: b, g: r[2], t: r[3], r: (b / payback) * r[3] };
});
var MS = [25, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1250, 1500, 2000, 2500, 3000];   // paliers : revenu ×2
var SPD_MS = [100, 300, 500, 800, 1200];                                                              // paliers : cycle ×2 plus rapide
var TIER_MS = [25, 50, 100, 200];                                                                      // paliers visibles (maisons → hôtel)
var MAX_ROLLS = 5, ROLL_EVERY = 240000, OFFLINE_CAP = 4 * 3600, OFFLINE_EFF = 0.5;

/* ---------- Conseillers (portraits générés par le code côté interface) ---------- */
var RARITY = [{ n: 'Commun', w: 70 }, { n: 'Rare', w: 22 }, { n: 'Épique', w: 7 }, { n: 'Légendaire', w: 1 }];
var PERK = {
  cost: 'Réduit le coût des améliorations de ', rev: 'Augmente tous les revenus de ', speed: 'Accélère tous les cycles de ',
  offline: 'Augmente les gains hors ligne de ', buy: 'Réduit le prix d\'achat des commerces de ', vip: 'Fait venir les VIP plus souvent : '
};
var ADV = [
  { id: 'lambert', name: 'Mme Lambert', rar: 0, k: 'cost', v: 0.05 }, { id: 'okafor', name: 'M. Okafor', rar: 0, k: 'rev', v: 0.10 },
  { id: 'lea', name: 'Léa', rar: 0, k: 'speed', v: 0.05 }, { id: 'tom', name: 'Tom', rar: 0, k: 'offline', v: 0.10 },
  { id: 'ines', name: 'Inès', rar: 0, k: 'buy', v: 0.05 }, { id: 'hugo', name: 'Hugo', rar: 0, k: 'vip', v: 0.10 },
  { id: 'camille', name: 'Camille', rar: 1, k: 'cost', v: 0.10 }, { id: 'yuki', name: 'Yuki', rar: 1, k: 'rev', v: 0.25 },
  { id: 'karim', name: 'Karim', rar: 1, k: 'speed', v: 0.10 },
  { id: 'moreau', name: 'Dr Moreau', rar: 2, k: 'rev', v: 0.60 }, { id: 'sofia', name: 'Sofia', rar: 2, k: 'cost', v: 0.20 },
  { id: 'aurelio', name: 'Maître Aurelio', rar: 3, k: 'rev', v: 2.00, k2: 'speed', v2: 0.10 }
];
var ADVBY = {}; ADV.forEach(function (a) { ADVBY[a.id] = a; });

/* ---------- Mini-plateau de dés (clin d'œil au jeu de société) ---------- */
var BOARD = [
  { k: 'start', t: 'Départ' }, { k: 'cash', m: 120, t: 'Recette' }, { k: 'chance', t: 'Fortune' }, { k: 'cash', m: 240, t: 'Recette' },
  { k: 'tax', p: 0.03, t: 'Impôts' }, { k: 'boost', b: 'rev', t: 'Boom' }, { k: 'cash', m: 300, t: 'Recette' }, { k: 'chance', t: 'Fortune' },
  { k: 'jail', t: 'Contrôle' }, { k: 'cash', m: 180, t: 'Recette' }, { k: 'boost', b: 'spd', t: 'Turbo' }, { k: 'cash', m: 600, t: 'Gros lot' },
  { k: 'chance', t: 'Fortune' }, { k: 'tax', p: 0.02, t: 'Impôts' }, { k: 'adv', t: 'Recrue' }, { k: 'cash', m: 360, t: 'Recette' },
  { k: 'park', t: 'Parc' }, { k: 'cash', m: 900, t: 'Gros lot' }, { k: 'chance', t: 'Fortune' }, { k: 'cash', m: 1500, t: 'Jackpot' }
];
var CARDS = [
  { k: 'cash', m: 600, t: 'Un client fortuné laisse un gros pourboire : 2,5 minutes de revenus !' },
  { k: 'boost', b: 'rev', t: 'Un article élogieux dans la presse : revenus ×2 pendant 60 s !' },
  { k: 'adv', t: 'Un talent frappe à votre porte : un conseiller rejoint votre équipe !' },
  { k: 'tax', p: 0.02, t: 'Taxe foncière : vous payez 2 % de votre trésorerie.' },
  { k: 'move', n: 3, t: 'Voyage d\'affaires : avancez de 3 cases !' },
  { k: 'cash', m: 300, t: 'Remboursement d\'un trop-perçu : 1 minute de revenus.' },
  { k: 'boost', b: 'spd', t: 'Les livraisons sont en avance : cycles ×2 pendant 30 s !' },
  { k: 'cash', m: 1200, t: 'Un investisseur rachète des parts : 5 minutes de revenus !' }
];
/* ---------- Concurrents : des rivaux qui ouvrent à côté de chez vous et courent après la première place ---------- */
var RIVALS = [
  { name: 'Groupe Vantor', ic: '🦅', m: 0.5, tag: 'Prudent' }, { name: 'Maison Delcourt & Fils', ic: '🦊', m: 0.8, tag: 'Familial' }, { name: 'NovaRetail', ic: '🐺', m: 1.05, tag: 'Agressif' }
];
var COMP_HIT = 0.65, COMP_LIFE = 300000;
var GIFTS = {
  BIENVENUE: { cash: 300, t: 'Bienvenue ! 5 minutes de revenus offertes.' },
  EMPIRE: { adv: 1, t: 'Un conseiller vous est offert !' },
  TYCOON: { rolls: 3, t: '3 lancers de dés offerts !' }
};

/* ---------- Formatage des grands nombres ---------- */
var SUF = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc', 'Ud', 'Dd', 'Td', 'Qad', 'Qid', 'Sxd', 'Spd', 'Ocd', 'Nod', 'Vg'];
function fmt(n) {
  if (!isFinite(n)) return '∞';
  if (n < 0) return '-' + fmt(-n);
  if (n < 10) return n.toFixed(2);
  if (n < 1000) return String(Math.round(n));
  if (n < 1e6) return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '\u202f');
  var e = Math.floor(Math.log10(n) / 3);
  if (e >= SUF.length) return n.toExponential(2).replace('e+', 'e');
  var v = n / Math.pow(1000, e);
  if (v >= 999.995) { v = 1; e++; if (e >= SUF.length) return n.toExponential(2).replace('e+', 'e'); }
  return (v < 100 ? v.toFixed(2) : v.toFixed(1)) + SUF[e];
}
function fmtTime(s) {
  s = Math.max(0, Math.ceil(s));
  var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60;
  var two = function (v) { return (v < 10 ? '0' : '') + v; };
  return h > 0 ? h + ':' + two(m) + ':' + two(x) : two(m) + ':' + two(x);
}

/* ---------- État ---------- */
var S = null, listeners = [], dirty = true, T = null;
function emit(type, data) { for (var i = 0; i < listeners.length; i++) { try { listeners[i](type, data); } catch (e) {} } }
function randName() { var a = ['Audacieux', 'Rusé', 'Brillant', 'Fortuné', 'Malin', 'Visionnaire'], b = ['Castor', 'Faucon', 'Lynx', 'Renard', 'Aigle', 'Tigre']; return a[Math.floor(Math.random() * a.length)] + b[Math.floor(Math.random() * b.length)] + Math.floor(100 + Math.random() * 900); }
function newState() {
  var now = clock();
  return {
    v: 1, cash: START, run: 0, life: 0, stars: 0,
    biz: BIZ.map(function () { return { n: 0, p: 0 }; }), up: BIZ.map(function () { return 0; }), qdone: BIZ.map(function () { return 0; }),
    adv: {}, eq: [], slots: 2, hired: 0,
    quests: [], qseq: 1,
    dice: { pos: 0, rolls: 3, next: now + ROLL_EVERY, jail: 0 },
    boost: { revEnd: 0, spdEnd: 0, revCd: 0, spdCd: 0 },
    vip: { next: now + 480000, cur: null },
    ev: { type: null, until: 0, next: now + 240000 },
    day: 0, month: 0, mInc: 0, lastMInc: 0, yInc: 0, debt: 0, bill: null, news: [], comp: DISTRICTS.map(function () { return null; }), compNext: now + 420000, rivalW: [0, 0, 0], rivalNews: 0, inc: BIZ.map(function () { return null; }), incNext: now + 200000, mult: 1, gifts: {}, name: randName(),
    set: { sound: true, music: true, quality: 'auto' }, last: now, t0: now, tut: 0
  };
}
function init(loaded) { S = loaded || newState(); dirty = true; ensureQuests(); return S; }

/* ---------- Calculs dérivés ---------- */
function totals() {
  if (!dirty && T) return T;
  T = { cost: 0, rev: 0, speed: 0, offline: 0, buy: 0, vip: 0 };
  S.eq.forEach(function (id) {
    var a = ADVBY[id], c = S.adv[id] || 0; if (!a || !c) return;
    var f = 1 + 0.5 * (c - 1); T[a.k] += a.v * f; if (a.k2) T[a.k2] += a.v2 * f;
  });
  T.cost = Math.min(T.cost, 0.6); T.buy = Math.min(T.buy, 0.6); dirty = false; return T;
}
function now() { return clock(); }
function active(end) { return end > clock(); }
function evType() { return active(S.ev.until) ? S.ev.type : null; }
function mRev() { var t = totals(); return (1 + t.rev) * (1 + 0.05 * S.stars) * (active(S.boost.revEnd) ? 2 : 1) * (evType() === 'boom' ? 1.5 : 1); }
function mSpd() { var t = totals(); return (1 + t.speed) * (active(S.boost.spdEnd) ? 2 : 1) * (evType() === 'rush' ? 2 : 1); }
function costMul() { return (1 - totals().cost) * (evType() === 'sale' ? 0.75 : 1); }
function msCount(n) { var c = 0; for (var i = 0; i < MS.length; i++) if (n >= MS[i]) c++; return c; }
function spdCount(n) { var c = 0; for (var i = 0; i < SPD_MS.length; i++) if (n >= SPD_MS[i]) c++; return c; }
function tierOf(n) { var c = 0; for (var i = 0; i < TIER_MS.length; i++) if (n >= TIER_MS[i]) c++; return c; }
function nextMs(n) { for (var i = 0; i < MS.length; i++) if (n < MS[i]) return MS[i]; return null; }
function distComplete(d) { return S.biz[d * 3].n > 0 && S.biz[d * 3 + 1].n > 0 && S.biz[d * 3 + 2].n > 0; }
function owned() { var c = 0; for (var i = 0; i < S.biz.length; i++) if (S.biz[i].n > 0) c++; return c; }
function rev(i) { var b = S.biz[i]; if (b.n <= 0) return 0; return BIZ[i].r * b.n * Math.pow(2, msCount(b.n)) * (distComplete(BIZ[i].dist) ? 2 : 1) * mRev() * (S.comp[BIZ[i].dist] ? COMP_HIT : 1); }
function time(i) { return BIZ[i].t / Math.pow(2, spdCount(S.biz[i].n)) / mSpd(); }
function perSec(i) { return S.biz[i].n > 0 && !(S.inc && S.inc[i]) ? rev(i) / time(i) : 0; }
function totalPerSec() { var s = 0; for (var i = 0; i < S.biz.length; i++) s += perSec(i); return s; }
/* Prix de k unités à partir de n unités possédées (n = 0 : achat du commerce, remise « achat ») */
function price(i, k) {
  var B = BIZ[i], n = S.biz[i].n;
  if (n === 0) return B.b * (1 - totals().buy) * (evType() === 'sale' ? 0.75 : 1);
  return B.b * Math.pow(B.g, n) * (Math.pow(B.g, k) - 1) / (B.g - 1) * costMul();
}
function maxUnits(i) {
  var B = BIZ[i], n = S.biz[i].n; if (n === 0) return 0;
  var budget = S.cash / costMul(), unit = B.b * Math.pow(B.g, n);
  var k = Math.floor(Math.log(1 + budget * (B.g - 1) / unit) / Math.log(B.g));
  if (!isFinite(k) || k < 0) k = 0; k = Math.min(k, 5000);
  while (k > 0 && price(i, k) > S.cash) k--;
  return k;
}
/* Nombre d'unités que le bouton « Améliorer » achètera selon le mode (×1, ×10, ×100, Max) */
function buyCount(i) { var m = S.mult; if (m === 0) return Math.max(1, maxUnits(i)); return m; }

/* ---------- Actions ---------- */
function gain(x) {
  if (!isFinite(x)) return; var pay = 0; if (S.debt > 0) { pay = Math.min(S.debt, x * GARNISH); S.debt -= pay; }
  S.cash = Math.min(S.cash + x - pay, 1e300); S.run += x; S.life += x; S.mInc += x; S.yInc += x;
}
function buy(i) {
  var b = S.biz[i]; if (b.n > 0) return { ok: false, msg: 'Déjà acheté' };
  if (i > 0 && S.biz[i - 1].n <= 0) return { ok: false, msg: 'Achetez d\'abord le commerce précédent' };
  var p = price(i, 1); if (S.cash < p) return { ok: false, msg: 'Pas assez d\'argent' };
  S.cash -= p; b.n = 1; b.p = 0; S.up[i] += 0;
  addNews('Nouveau commerce : ' + BIZ[i].name + ' !');
  if (distComplete(BIZ[i].dist)) addNews('Quartier complet : ' + DISTRICTS[BIZ[i].dist].name + ' — revenus ×2 !');
  emit('purchase', { i: i }); return { ok: true };
}
function upgrade(i) {
  var b = S.biz[i]; if (b.n <= 0) return { ok: false };
  var k = buyCount(i), p = price(i, k);
  if (S.cash < p) { if (S.mult === 0 || k > 1) { k = maxUnits(i); if (k < 1) return { ok: false, msg: 'Pas assez d\'argent' }; p = price(i, k); } else return { ok: false, msg: 'Pas assez d\'argent' }; }
  var tier0 = tierOf(b.n), ms0 = msCount(b.n);
  S.cash -= p; b.n += k; S.up[i] += k;
  var tier1 = tierOf(b.n);
  if (msCount(b.n) > ms0) addNews(BIZ[i].name + ' atteint le niveau ' + b.n + ' : revenus ×2 !');
  emit('upgrade', { i: i, k: k, tier: tier1, tierUp: tier1 > tier0 }); return { ok: true, k: k };
}
function setMult(m) { S.mult = m; }
function cycleMult() { var o = [1, 10, 100, 0]; S.mult = o[(o.indexOf(S.mult) + 1) % o.length]; return S.mult; }

/* ---------- Conseillers ---------- */
function hireCost() { return 25000 * Math.pow(5, S.hired); }
function pickAdvisor() {
  var tot = 0, r, i; RARITY.forEach(function (x) { tot += x.w; }); r = Math.random() * tot;
  var rar = 0; for (i = 0; i < RARITY.length; i++) { if (r < RARITY[i].w) { rar = i; break; } r -= RARITY[i].w; }
  var pool = ADV.filter(function (a) { return a.rar === rar; }); return pool[Math.floor(Math.random() * pool.length)];
}
function giveAdvisor() {
  var a = pickAdvisor(); S.adv[a.id] = (S.adv[a.id] || 0) + 1;
  if (S.eq.length < S.slots && S.eq.indexOf(a.id) < 0) S.eq.push(a.id);
  dirty = true; addNews('Nouveau conseiller : ' + a.name + ' (' + RARITY[a.rar].n + ')'); emit('advisor', { a: a, count: S.adv[a.id] }); return a;
}
function hire() { var c = hireCost(); if (S.cash < c) return { ok: false, msg: 'Pas assez d\'argent' }; S.cash -= c; S.hired++; return { ok: true, a: giveAdvisor() }; }
function equip(id) {
  if (!S.adv[id]) return false; var k = S.eq.indexOf(id);
  if (k >= 0) { S.eq.splice(k, 1); dirty = true; return true; }
  if (S.eq.length >= S.slots) return false; S.eq.push(id); dirty = true; return true;
}
function slotCost() { return 1e9 * Math.pow(1000, S.slots - 2); }
function buySlot() { if (S.slots >= 4) return { ok: false, msg: 'Maximum atteint' }; var c = slotCost(); if (S.cash < c) return { ok: false, msg: 'Pas assez d\'argent' }; S.cash -= c; S.slots++; return { ok: true }; }
function advPerk(a, count) { var f = 1 + 0.5 * (count - 1), txt = PERK[a.k] + Math.round(a.v * f * 100) + ' %'; if (a.k2) txt += ' et ' + PERK[a.k2].toLowerCase() + Math.round(a.v2 * f * 100) + ' %'; return txt; }

/* ---------- Boosts, VIP, événements ---------- */
function boostState(w) { var e = w === 'rev' ? S.boost.revEnd : S.boost.spdEnd, c = w === 'rev' ? S.boost.revCd : S.boost.spdCd, n = clock(); return { on: e > n, left: Math.max(0, (e - n) / 1000), cd: Math.max(0, (c - n) / 1000) }; }
function useBoost(w) {
  var st = boostState(w); if (st.on || st.cd > 0) return false; var n = clock();
  if (w === 'rev') { S.boost.revEnd = n + 60000; S.boost.revCd = n + 1200000; } else { S.boost.spdEnd = n + 30000; S.boost.spdCd = n + 900000; }
  emit('boost', { w: w }); return true;
}
function vipAccept() {
  var v = S.vip.cur; if (!v) return null; var n = clock(), out = { type: v.type };
  if (v.type === 'investor') { out.amt = Math.max(totalPerSec() * v.mins * 60, price(0, 1) * 2); gain(out.amt); }
  else { S.boost.spdEnd = Math.max(S.boost.spdEnd, n) + 30000; out.secs = 30; }
  S.vip.cur = null; scheduleVip(); emit('vipdone', out); return out;
}
function vipDecline() { S.vip.cur = null; scheduleVip(); }
function scheduleVip() { S.vip.next = clock() + (420 + Math.random() * 300) * 1000 * (1 - Math.min(0.5, totals().vip)); }
var EVENTS = [
  { type: 'boom', ms: 90000, t: 'Boom économique : revenus +50 % pendant 90 s !' },
  { type: 'sale', ms: 60000, t: 'Soldes immobiliers : coûts -25 % pendant 60 s !' },
  { type: 'rush', ms: 45000, t: 'Heure de pointe : cycles ×2 pendant 45 s !' }
];

/* ---------- Dés ---------- */
function rollsLeft() { return S.dice.rolls; }
function rollDice() {
  if (S.dice.rolls <= 0) return null;
  S.dice.rolls--; var d1 = 1 + Math.floor(Math.random() * 6), d2 = 1 + Math.floor(Math.random() * 6), steps = d1 + d2, pos = S.dice.pos, path = [];
  for (var s = 1; s <= steps; s++) path.push((pos + s) % BOARD.length);
  var passed = pos + steps >= BOARD.length; S.dice.pos = path[path.length - 1];
  if (S.dice.rolls < MAX_ROLLS && S.dice.next < clock()) S.dice.next = clock() + ROLL_EVERY;
  return { d1: d1, d2: d2, path: path, passedStart: passed && S.dice.pos !== 0 };
}
function landOn(pos, card) {
  var t = card || BOARD[pos], ps = Math.max(totalPerSec(), 1), out = { k: t.k, text: '' };
  if (t.k === 'start') { out.amt = Math.max(ps * 75, 20); gain(out.amt); out.text = 'Case Départ : prime de ' + fmt(out.amt) + ' € !'; }
  else if (t.k === 'cash') { out.amt = Math.max(ps * t.m * 0.25, 20); gain(out.amt); out.text = 'Vous encaissez ' + fmt(out.amt) + ' € !'; }
  else if (t.k === 'tax') { out.amt = S.cash * t.p; S.cash -= out.amt; out.text = 'Impôts : -' + fmt(out.amt) + ' €.'; }
  else if (t.k === 'boost') { var n = clock(); if (t.b === 'rev') { S.boost.revEnd = Math.max(S.boost.revEnd, n) + 60000; out.text = 'Boom : revenus ×2 pendant 60 s !'; } else { S.boost.spdEnd = Math.max(S.boost.spdEnd, n) + 30000; out.text = 'Turbo : cycles ×2 pendant 30 s !'; } }
  else if (t.k === 'adv') { var a = giveAdvisor(); out.adv = a; out.text = 'Recrue : ' + a.name + ' rejoint votre équipe !'; }
  else if (t.k === 'jail') { if (S.dice.rolls > 0) { S.dice.rolls--; out.text = 'Contrôle fiscal : vous perdez un lancer.'; } else out.text = 'Contrôle fiscal… heureusement, vous n\'aviez rien à perdre !'; }
  else if (t.k === 'park') { out.text = 'Pause au parc : vous respirez un peu.'; }
  else if (t.k === 'chance') { var c = CARDS[Math.floor(Math.random() * CARDS.length)]; out.card = c; out.text = c.t; if (c.k === 'move') { out.move = c.n; } else { var r = landOn(pos, c); out.amt = r.amt; out.adv = r.adv; } }
  return out;
}

/* ---------- Quêtes ---------- */
function qProgress(q) {
  if (q.t === 'up') return Math.min(q.n, S.up[q.i] - q.base);
  if (q.t === 'own') return Math.min(q.n, owned());
  if (q.t === 'earn') return Math.min(q.n, S.run - q.base);
  return Math.min(q.n, S.biz[q.i].n);
}
function qTitle(q) {
  if (q.t === 'up') return 'Améliorez ' + BIZ[q.i].name + ' ' + q.n + ' fois';
  if (q.t === 'own') return 'Possédez ' + q.n + ' commerce' + (q.n > 1 ? 's' : '');
  if (q.t === 'earn') return 'Gagnez ' + fmt(q.n) + ' €';
  return BIZ[q.i].name + ' : atteignez le niveau ' + q.n;
}
function genQuest() {
  var ps = Math.max(totalPerSec(), 1), own = [], i, tries = 0, q;
  for (i = 0; i < S.biz.length; i++) if (S.biz[i].n > 0) own.push(i);
  while (tries++ < 20) {
    var kind = own.length === 0 ? 'own' : ['up', 'up', 'own', 'earn', 'tier'][Math.floor(Math.random() * 5)];
    if (kind === 'own') { if (owned() >= BIZ.length) continue; q = { t: 'own', n: owned() + 1, rew: Math.max(ps * 150, price(Math.min(owned(), BIZ.length - 1), 1) * 0.2) }; }
    else if (kind === 'up') { i = own[Math.floor(Math.random() * own.length)]; var n = [25, 50, 100, 200, 400][Math.min(4, S.qdone[i])]; q = { t: 'up', i: i, n: n, base: S.up[i], rew: ps * 120 * (n / 25) }; }
    else if (kind === 'earn') { var tgt = Math.max(500, ps * 1800); q = { t: 'earn', n: tgt, base: S.run, rew: ps * 150 }; }
    else { i = own[Math.floor(Math.random() * own.length)]; var nm = nextMs(S.biz[i].n); if (!nm) continue; q = { t: 'tier', i: i, n: nm, rew: ps * 200 }; }
    var dup = S.quests.some(function (o) { return o.t === q.t && o.i === q.i; }); if (dup) continue;
    q.id = S.qseq++; q.rew = Math.max(q.rew, 5); return q;
  }
  return null;
}
function ensureQuests() { while (S.quests.length < 5) { var q = genQuest(); if (!q) break; S.quests.push(q); } }
function claimQuest(id) {
  var k = -1, q; for (var j = 0; j < S.quests.length; j++) if (S.quests[j].id === id) { k = j; q = S.quests[j]; }
  if (k < 0 || qProgress(q) < q.n) return null;
  gain(q.rew); if (q.t === 'up') S.qdone[q.i]++; S.quests.splice(k, 1); ensureQuests(); emit('questdone', { q: q }); return q;
}
function questsReady() { var c = 0; S.quests.forEach(function (q) { if (qProgress(q) >= q.n) c++; }); return c; }

/* ---------- Incidents : la vie d'un patron n'est pas un long fleuve tranquille ---------- */
var INCIDENTS = [
  { t: 'panne', ic: '🔧', n: 'Panne d\'équipement', lb: 'Réparer', m: 45, x: 'Le matériel est en panne : le commerce est à l\'arrêt jusqu\'à réparation.' },
  { t: 'greve', ic: '✊', n: 'Grève du personnel', lb: 'Négocier', m: 60, d: 150, x: 'Le personnel est en grève ! Négociez, ou attendez la fin du mouvement.' },
  { t: 'inspection', ic: '📋', n: 'Contrôle sanitaire', lb: 'Mise aux normes', m: 30, x: 'Un inspecteur ferme le commerce le temps de la mise aux normes.' },
  { t: 'eau', ic: '💧', n: 'Dégât des eaux', lb: 'Assécher', m: 50, x: 'Une canalisation a lâché : travaux nécessaires avant de rouvrir.' }
];
function incident(i) { return S.inc ? S.inc[i] : null; }
function incCount() { var c = 0; for (var i = 0; i < S.inc.length; i++) if (S.inc[i]) c++; return c; }
function spawnIncident() {
  var own = [], i; for (i = 0; i < S.biz.length; i++) if (S.biz[i].n > 0 && !S.inc[i]) own.push(i);
  if (own.length === 0 || incCount() >= 2) return;
  var n = clock(), r = Math.random();
  if (r < 0.25) {   // incidents instantanés : vol ou amende
    var loss = Math.min(S.cash * 0.08, Math.max(totalPerSec() * 90, 1)), theft = Math.random() < 0.5; if (loss < 1) return; S.cash -= loss;
    addNews(theft ? 'Cambriolage ! Vous perdez ' + fmt(loss) + ' € de caisse.' : 'Amende de l\'administration fiscale : -' + fmt(loss) + ' €.'); emit('incident', { instant: true, theft: theft, amt: loss }); return;
  }
  i = own[Math.floor(Math.random() * own.length)]; var T = INCIDENTS[Math.floor(Math.random() * INCIDENTS.length)], ps = rev(i) / time(i);
  S.inc[i] = { t: T.t, cost: Math.max(ps * T.m, 5), until: T.d ? n + T.d * 1000 : 0 };
  addNews(T.ic + ' ' + T.n + ' : ' + BIZ[i].name + ' est à l\'arrêt !'); emit('incident', { i: i, type: T });
}
function fixIncident(i) {
  var inc = S.inc[i]; if (!inc) return { ok: false }; if (S.cash < inc.cost) return { ok: false, msg: 'Pas assez d\'argent pour régler le problème' };
  S.cash -= inc.cost; S.inc[i] = null; addNews(BIZ[i].name + ' : problème réglé, on rouvre !'); emit('fixed', { i: i }); return { ok: true };
}

function distRate(d) { var s = 0; for (var k = d * 3; k < d * 3 + 3; k++) if (S.biz[k].n > 0) s += rev(k) / time(k); return s / (S.comp[d] ? COMP_HIT : 1); }
function spawnRival() {
  var ds = [], d; for (d = 0; d < DISTRICTS.length; d++) if (!S.comp[d] && S.biz[d * 3].n > 0) ds.push(d);
  if (!ds.length) return; d = ds[Math.floor(Math.random() * ds.length)]; var r = Math.floor(Math.random() * RIVALS.length);
  S.comp[d] = { r: r, until: clock() + COMP_LIFE, cost: Math.max(distRate(d) * 120, 20) };
  addNews('⚔️ ' + RIVALS[r].name + ' ouvre en face : revenus de ' + DISTRICTS[d].name + ' -35 % !'); emit('rival', { d: d, r: r });
}
function counter(d) {
  var c = S.comp[d]; if (!c) return { ok: false }; if (S.cash < c.cost) return { ok: false, msg: 'Pas assez d\'argent pour la campagne' };
  S.cash -= c.cost; S.comp[d] = null; addNews('📣 Campagne réussie : ' + RIVALS[c.r].name + ' quitte ' + DISTRICTS[d].name + '.'); emit('fixed', { d: d }); return { ok: true };
}
function ranking() {
  var a = RIVALS.map(function (r, k) { return { name: r.name, ic: r.ic, tag: r.tag, w: S.rivalW[k], me: false }; }); a.push({ name: S.name, ic: '👑', tag: 'Vous', w: S.life, me: true });
  a.sort(function (x, y) { return y.w - x.w; }); return a;
}
function myRank() { var r = ranking(); for (var i = 0; i < r.length; i++) if (r[i].me) return i + 1; return 4; }
function rivalsTick(dt, ps) {
  for (var k = 0; k < RIVALS.length; k++) S.rivalW[k] += dt * (ps * RIVALS[k].m + 0.05 * k);
}

/* ---------- Vie d'un entrepreneur : calendrier, charges de vie, impôts, dette ---------- */
function age() { return 25 + Math.floor(S.day / 360); }
function dateInfo() { var d = Math.floor(S.day); return { year: Math.floor(d / 360) + 1, month: Math.floor(d % 360 / 30) + 1, day: d % 30 + 1, age: 25 + Math.floor(d / 360) }; }
function livingCost() { return LIVING + 0.02 * S.mInc; }
function creditLimit() { return 5000 + 400 * totalPerSec(); }
function charge(x) { if (S.cash >= x) S.cash -= x; else { S.debt += x - S.cash; S.cash = 0; } }
function endMonth() {
  var living = livingCost(), interest = S.debt * INTEREST, tax = 0; S.debt += interest; charge(living);
  S.month++; if (S.month % 12 === 0) { tax = S.yInc * TAX; S.yInc = 0; charge(tax); }
  S.bill = { m: S.month, inc: S.mInc, living: living, interest: interest, tax: tax }; S.lastMInc = S.mInc; S.mInc = 0;
  addNews('📅 Mois ' + S.month + ' : vie courante -' + fmt(living) + ' €' + (interest > 1 ? ', intérêts -' + fmt(interest) + ' €' : '') + (tax ? ', impôts -' + fmt(tax) + ' €' : '') + '.');
  emit('month', S.bill);
}
function borrow(x) {
  var room = creditLimit() - S.debt; x = Math.min(x, room); if (x < 1) return { ok: false, msg: 'La banque refuse : endettement maximal atteint.' };
  S.cash += x; S.debt += x; addNews('🏦 Prêt bancaire : +' + fmt(x) + ' € (intérêts ' + (INTEREST * 100) + ' % par mois).'); return { ok: true, amt: x };
}
function repay(x) {
  x = Math.min(x, S.debt, S.cash); if (x < 1) return { ok: false, msg: S.debt < 1 ? 'Aucune dette.' : 'Pas assez d\'argent.' };
  S.cash -= x; S.debt -= x; if (S.debt < 0.5) S.debt = 0; addNews('🏦 Remboursement : -' + fmt(x) + ' €.'); return { ok: true, amt: x };
}

/* ---------- Journal ---------- */
function addNews(t) { S.news.unshift({ t: clock(), x: t }); if (S.news.length > 40) S.news.length = 40; emit('news', { x: t }); }

/* ---------- Boucle ---------- */
function tick(dt) {
  var n = clock(), i, b, tm, rv, k, g;
  for (i = 0; i < S.biz.length; i++) {
    b = S.biz[i]; if (b.n <= 0) continue;
    if (S.inc[i]) { if (S.inc[i].until && n > S.inc[i].until) { S.inc[i] = null; addNews('La grève est terminée à ' + BIZ[i].name + '.'); emit('fixed', { i: i }); } continue; }
    tm = time(i); rv = rev(i);
    if (tm < 0.25) { gain(rv / tm * dt); b.p = (b.p + dt / tm) % 1; }
    else {
      b.p += dt / tm;
      if (b.p >= 1) { k = Math.floor(b.p); b.p -= k; g = rv * k; gain(g); emit('payout', { i: i, amt: g }); }
    }
  }
  // dés rechargés avec le temps
  while (S.dice.rolls < MAX_ROLLS && n >= S.dice.next) { S.dice.rolls++; S.dice.next += ROLL_EVERY; emit('rolls', {}); }
  if (S.dice.rolls >= MAX_ROLLS) S.dice.next = n + ROLL_EVERY;
  S.day += dt / DAY_S; while (S.month < Math.floor(S.day / 30)) endMonth();
  rivalsTick(dt, totalPerSec());
  for (i = 0; i < S.comp.length; i++) if (S.comp[i] && n > S.comp[i].until) { addNews(RIVALS[S.comp[i].r].name + ' ferme sa boutique à ' + DISTRICTS[i].name + '.'); S.comp[i] = null; }
  if (n >= S.compNext && owned() >= 3) { S.compNext = n + (360 + Math.random() * 300) * 1000; spawnRival(); if (Math.random() < 0.3) { var vk = Math.floor(Math.random() * 3); if (S.rivalW[vk] > S.life * 0.5) { S.rivalW[vk] *= 0.7; addNews('📉 ' + RIVALS[vk].name + ' traverse un scandale : sa fortune chute !'); } } }
  var rk = myRank(); if (S.rankLast && rk !== S.rankLast && S.life > 5000) { addNews(rk < S.rankLast ? '🏆 Vous passez ' + rk + (rk === 1 ? 'er' : 'e') + ' au classement des empires !' : '⚠️ Un rival vous dépasse : vous êtes ' + rk + 'e.'); emit('rank', { rk: rk }); } S.rankLast = rk;
  if (n >= S.incNext && owned() >= 2) { S.incNext = n + (240 + Math.random() * 240) * 1000; spawnIncident(); }
  // VIP
  if (S.vip.cur && n > S.vip.cur.until) { S.vip.cur = null; scheduleVip(); }
  if (!S.vip.cur && n >= S.vip.next && owned() >= 1) { S.vip.cur = { type: Math.random() < 0.55 ? 'investor' : 'manager', mins: 2 + Math.floor(Math.random() * 4), until: n + 45000 }; emit('vip', S.vip.cur); }
  // événements de marché
  if (S.ev.type && n > S.ev.until) { S.ev.type = null; }
  if (!S.ev.type && n >= S.ev.next && owned() >= 2) {
    var e = EVENTS[Math.floor(Math.random() * EVENTS.length)]; S.ev.type = e.type; S.ev.until = n + e.ms; S.ev.next = n + (360 + Math.random() * 240) * 1000; addNews(e.t); emit('event', e);
  }
}
/* Gains hors ligne : tous les commerces tournent seuls ; on crédite ce qui a été gagné pendant l'absence */
function offline() {
  var n = clock(), secs = Math.max(0, (n - S.last) / 1000);
  if (secs < 60 || owned() === 0) return null;
  var eff = Math.min(secs, OFFLINE_CAP * (1 + totals().offline)), amt = totalPerSec() * eff * OFFLINE_EFF;
  gain(amt); rivalsTick(eff, totalPerSec()); var mo = Math.min(48, Math.floor(eff / (DAY_S * 30))); S.day += eff / DAY_S; if (mo > 0) { var share = S.mInc / mo; for (var q = 0; q < mo; q++) { S.mInc = share; endMonth(); } S.month = Math.floor(S.day / 30); S.mInc = 0; } return { secs: secs, amt: amt, capped: secs > eff };
}

/* ---------- Prestige : « Expansion mondiale » ---------- */
function starsPotential() { return Math.max(0, Math.floor(Math.sqrt(S.life / 1e10)) - S.stars); }
function prestige() {
  var g = starsPotential(); if (g < 1) return false;
  var keep = { day: S.day, month: S.month, rivalW: S.rivalW, adv: S.adv, eq: S.eq, slots: S.slots, hired: S.hired, life: S.life, stars: S.stars + g, name: S.name, set: S.set, gifts: S.gifts, news: S.news, dice: S.dice, tut: 3 };
  var s = newState(); for (var k in keep) s[k] = keep[k]; s.cash = START + 500 * keep.stars; S = s; dirty = true; ensureQuests();
  addNews('Expansion mondiale ! +' + g + ' étoile(s) : revenus +' + (g * 5) + ' %.'); emit('prestige', { g: g }); return g;
}

/* ---------- Codes cadeau ---------- */
function gift(code) {
  code = String(code || '').trim().toUpperCase(); var g = GIFTS[code];
  if (!g) return { ok: false, msg: 'Code inconnu' }; if (S.gifts[code]) return { ok: false, msg: 'Code déjà utilisé' };
  S.gifts[code] = 1;
  if (g.cash) gain(Math.max(totalPerSec() * g.cash, 100)); if (g.adv) giveAdvisor(); if (g.rolls) S.dice.rolls = Math.min(MAX_ROLLS + 3, S.dice.rolls + g.rolls);
  return { ok: true, msg: g.t };
}

/* ---------- Sauvegarde ---------- */
function toJSON() { S.last = clock(); return JSON.stringify(S); }
function save() { try { localStorage.setItem(SAVE_KEY, toJSON()); return true; } catch (e) { return false; } }
function parse(str) {
  try { var o = JSON.parse(str); if (!o || o.v !== 1 || !o.biz || o.biz.length !== BIZ.length) return null; var d = newState(); for (var k in o) d[k] = o[k]; return d; } catch (e) { return null; }
}
function load() { try { var s = localStorage.getItem(SAVE_KEY); return s ? parse(s) : null; } catch (e) { return null; } }
function exportCode() { try { return btoa(unescape(encodeURIComponent(toJSON()))); } catch (e) { return ''; } }
function importCode(code) { try { var o = parse(decodeURIComponent(escape(atob(String(code).trim())))); if (!o) return false; S = o; dirty = true; ensureQuests(); return true; } catch (e) { return false; } }
function reset() { S = newState(); dirty = true; ensureQuests(); }

return {
  BIZ: BIZ, DISTRICTS: DISTRICTS, ADV: ADV, ADVBY: ADVBY, RARITY: RARITY, BOARD: BOARD, MS: MS, TIER_MS: TIER_MS, EVENTS: EVENTS, START: START, age: age, dateInfo: dateInfo, livingCost: livingCost, creditLimit: creditLimit, borrow: borrow, repay: repay, RIVALS: RIVALS, ranking: ranking, myRank: myRank, counter: counter, spawnRival: spawnRival, INCIDENTS: INCIDENTS, incident: incident, fixIncident: fixIncident, spawnIncident: spawnIncident, MAX_ROLLS: MAX_ROLLS,
  fmt: fmt, fmtTime: fmtTime, init: init, state: function () { return S; }, on: function (fn) { listeners.push(fn); }, setClock: function (fn) { clock = fn; },
  now: now, tick: tick, offline: offline, rev: rev, time: time, perSec: perSec, totalPerSec: totalPerSec, price: price, maxUnits: maxUnits, buyCount: buyCount,
  buy: buy, upgrade: upgrade, cycleMult: cycleMult, setMult: setMult, tierOf: tierOf, nextMs: nextMs, msCount: msCount, distComplete: distComplete, owned: owned,
  totals: totals, hireCost: hireCost, hire: hire, equip: equip, slotCost: slotCost, buySlot: buySlot, advPerk: advPerk,
  boostState: boostState, useBoost: useBoost, vipAccept: vipAccept, vipDecline: vipDecline, evType: evType, mRev: mRev,
  rollDice: rollDice, landOn: landOn, rollsLeft: rollsLeft, qProgress: qProgress, qTitle: qTitle, claimQuest: claimQuest, questsReady: questsReady, ensureQuests: ensureQuests,
  addNews: addNews, starsPotential: starsPotential, prestige: prestige, gift: gift, save: save, load: load, parse: parse, exportCode: exportCode, importCode: importCode, reset: reset, toJSON: toJSON,
  markDirty: function () { dirty = true; }
};
})();
