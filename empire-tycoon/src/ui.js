/* =====================================================================
 * 3. SONS (Web Audio, tout est généré par le code) + PORTRAITS (canvas)
 * ===================================================================== */
var Sfx = (function () {
  var ctx = null, master = null, enabled = true, musicOn = true, timer = null, last = {}, step = 0;
  function init() {
    if (ctx) { if (ctx.state === 'suspended') ctx.resume(); return; }
    try { var AC = window.AudioContext || window.webkitAudioContext; ctx = new AC(); master = ctx.createGain(); master.gain.value = 0.55; master.connect(ctx.destination); startMusic(); } catch (e) { ctx = null; }
  }
  function tone(f, t0, d, type, v, to) {
    if (!ctx || !enabled) return; var o = ctx.createOscillator(), g = ctx.createGain(), t = ctx.currentTime + t0;
    o.type = type || 'sine'; o.frequency.setValueAtTime(f, t); if (to) o.frequency.exponentialRampToValueAtTime(to, t + d);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(v || 0.2, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + d + 0.05);
  }
  function noise(t0, d, v, f) {
    if (!ctx || !enabled) return; var n = Math.floor(ctx.sampleRate * d), b = ctx.createBuffer(1, n, ctx.sampleRate), a = b.getChannelData(0), i;
    for (i = 0; i < n; i++) a[i] = (Math.random() * 2 - 1) * (1 - i / n);
    var s = ctx.createBufferSource(), fl = ctx.createBiquadFilter(), g = ctx.createGain(); fl.type = 'bandpass'; fl.frequency.value = f || 2000; g.gain.value = v || 0.15;
    s.buffer = b; s.connect(fl); fl.connect(g); g.connect(master); s.start(ctx.currentTime + t0);
  }
  function gate(k, ms) { var n = Date.now(); if (last[k] && n - last[k] < ms) return false; last[k] = n; return true; }
  var P = [0, 2, 4, 7, 9, 12, 14, 16], BASE = 261.63;
  function note(i) { return BASE * Math.pow(2, P[i % 8] / 12 + Math.floor(i / 8)); }
  function startMusic() {
    if (timer) return;
    timer = setInterval(function () {
      if (!ctx || !enabled || !musicOn || document.hidden) return;
      var seq = [0, 2, 4, 2, 5, 4, 2, 1, 0, 3, 4, 6, 5, 4, 2, 3], n = note(seq[step % 16]);
      tone(n, 0, 1.6, 'sine', 0.045); if (step % 4 === 0) tone(n / 2, 0, 2.4, 'triangle', 0.05); if (step % 2 === 1) tone(n * 2, 0.15, 0.8, 'sine', 0.02); step++;
    }, 780);
  }
  return {
    init: init, set: function (s, m) { enabled = s; musicOn = m; },
    coin: function () { if (!gate('coin', 110)) return; tone(988, 0, 0.09, 'square', 0.05); tone(1319, 0.07, 0.16, 'square', 0.05); },
    up: function () { if (!gate('up', 50)) return; tone(523, 0, 0.1, 'triangle', 0.16); tone(784, 0.07, 0.16, 'triangle', 0.16); },
    buy: function () { tone(392, 0, 0.14, 'triangle', 0.2); tone(523, 0.09, 0.14, 'triangle', 0.2); tone(659, 0.18, 0.14, 'triangle', 0.2); tone(1046, 0.27, 0.35, 'triangle', 0.22); noise(0, 0.25, 0.08, 800); },
    click: function () { tone(660, 0, 0.05, 'sine', 0.1); },
    err: function () { if (!gate('err', 250)) return; tone(220, 0, 0.18, 'sawtooth', 0.08, 140); },
    claim: function () { [523, 659, 784, 1046, 1319].forEach(function (f, i) { tone(f, i * 0.07, 0.25, 'triangle', 0.17); }); },
    roll: function () { for (var i = 0; i < 9; i++) noise(i * 0.07, 0.05, 0.12, 1500 + Math.random() * 1500); },
    step: function () { tone(440, 0, 0.06, 'square', 0.06, 520); },
    win: function () { [392, 523, 659, 784].forEach(function (f, i) { tone(f, i * 0.09, 0.3, 'triangle', 0.18); }); },
    vip: function () { tone(880, 0, 0.12, 'sine', 0.18); tone(1175, 0.12, 0.3, 'sine', 0.18); }
  };
})();

var Portrait = (function () {
  var cache = {}, SKIN = ['#f4c7a1', '#e0a67a', '#b97b52', '#8a5a3a', '#f8d9bd'], HAIR = ['#2b1d12', '#5a3a1e', '#c9a14a', '#8a2e1a', '#222831', '#9ea7b3'], SUIT = ['#2d5fa8', '#7b3f98', '#2e8a57', '#b5472f', '#3a4756', '#c98a1b'];
  function hash(s) { var h = 7; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0; return h; }
  var BG = [['#cfd8e2', '#9fb0c2'], ['#9fd0ff', '#4f93e8'], ['#d6b4ff', '#8f5be8'], ['#ffe08a', '#f0a312']];
  function make(a, locked) {
    var key = a.id + (locked ? '_l' : ''); if (cache[key]) return cache[key];
    var c = document.createElement('canvas'); c.width = c.height = 120; var x = c.getContext('2d'), h = hash(a.id), g;
    g = x.createLinearGradient(0, 0, 0, 120); g.addColorStop(0, BG[a.rar][0]); g.addColorStop(1, BG[a.rar][1]); x.fillStyle = g; x.fillRect(0, 0, 120, 120);
    var skin = SKIN[h % SKIN.length], hair = HAIR[(h >> 3) % HAIR.length], suit = SUIT[(h >> 6) % SUIT.length], style = (h >> 9) % 5, glasses = ((h >> 12) % 3) === 0, tie = (h >> 14) % 2;
    if (locked) { skin = hair = suit = '#5a6674'; }
    x.fillStyle = suit; x.beginPath(); x.moveTo(14, 124); x.quadraticCurveTo(18, 84, 60, 80); x.quadraticCurveTo(102, 84, 106, 124); x.fill();
    x.fillStyle = locked ? '#6b7886' : '#fff'; x.beginPath(); x.moveTo(46, 82); x.lineTo(60, 100); x.lineTo(74, 82); x.closePath(); x.fill();
    if (tie) { x.fillStyle = locked ? '#444' : '#e5484d'; x.beginPath(); x.moveTo(56, 92); x.lineTo(64, 92); x.lineTo(66, 116); x.lineTo(60, 122); x.lineTo(54, 116); x.closePath(); x.fill(); }
    x.fillStyle = skin; x.fillRect(51, 66, 18, 20);
    if (style === 1) { x.fillStyle = hair; x.beginPath(); x.ellipse(60, 52, 31, 38, 0, 0, 7); x.fill(); x.fillRect(29, 52, 62, 36); }
    if (style === 3) { x.fillStyle = hair; x.beginPath(); x.arc(60, 18, 13, 0, 7); x.fill(); }
    x.fillStyle = skin; x.beginPath(); x.ellipse(60, 52, 25, 29, 0, 0, 7); x.fill();
    x.fillStyle = hair;
    if (style === 0) { x.beginPath(); x.ellipse(60, 33, 27, 15, 0, Math.PI, 0); x.fill(); x.fillRect(33, 30, 54, 8); }
    if (style === 1) { x.beginPath(); x.ellipse(60, 30, 28, 17, 0, Math.PI, 0); x.fill(); x.fillRect(32, 30, 12, 24); x.fillRect(76, 30, 12, 24); }
    if (style === 2) { x.beginPath(); x.ellipse(60, 31, 26, 12, 0, Math.PI, 0); x.fill(); }
    if (style === 3) { x.beginPath(); x.ellipse(60, 32, 27, 15, 0, Math.PI, 0); x.fill(); }
    if (style === 4) { x.fillStyle = suit; x.beginPath(); x.ellipse(60, 33, 28, 14, 0, Math.PI, 0); x.fill(); x.fillRect(30, 31, 60, 6); x.fillStyle = '#fff'; x.fillRect(30, 35, 60, 3); }
    x.fillStyle = locked ? '#333' : '#1b2430'; x.beginPath(); x.arc(49, 54, 3.2, 0, 7); x.arc(71, 54, 3.2, 0, 7); x.fill();
    x.strokeStyle = locked ? '#333' : '#7a3a2a'; x.lineWidth = 2.5; x.lineCap = 'round'; x.beginPath(); x.arc(60, 63, 9, 0.2, Math.PI - 0.2); x.stroke();
    if (glasses) { x.strokeStyle = '#1b2430'; x.lineWidth = 2; x.beginPath(); x.arc(49, 54, 8, 0, 7); x.moveTo(65, 54); x.arc(71, 54, 8, 0, 7); x.moveTo(57, 54); x.lineTo(63, 54); x.stroke(); }
    if (a.rar === 3 && !locked) { x.fillStyle = '#ffd54a'; x.beginPath(); x.moveTo(36, 22); x.lineTo(44, 8); x.lineTo(52, 20); x.lineTo(60, 4); x.lineTo(68, 20); x.lineTo(76, 8); x.lineTo(84, 22); x.closePath(); x.fill(); }
    if (locked) { x.fillStyle = 'rgba(255,255,255,.85)'; x.font = 'bold 44px system-ui'; x.textAlign = 'center'; x.fillText('?', 60, 70); }
    return (cache[key] = c.toDataURL());
  }
  return { get: make };
})();

/* =====================================================================
 * 4. INTERFACE (HTML par-dessus la ville 3D)
 * ===================================================================== */
var UI = (function () {
  var $ = function (id) { return document.getElementById(id); };
  var S = function () { return Engine.state(); };
  var fmt = Engine.fmt, BIZ = Engine.BIZ;
  var cards = [], el = {}, fxN = 0, lastPay = {}, contT = {}, curSheet = null, modalQ = [], modalOpen = false, started = false;
  var plotState = [], tipOn = -1;

  /* ---------- utilitaires ---------- */
  function setTxt(e, t) { if (e._t !== t) { e._t = t; e.textContent = t; } }
  function setHtml(e, t) { if (e._h !== t) { e._h = t; e.innerHTML = t; } }
  function setCls(e, c, on) { if (e._c === undefined) e._c = {}; if (e._c[c] !== on) { e._c[c] = on; e.classList.toggle(c, on); } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function money(n) { return fmt(n) + ' €'; }
  var toastT = 0;
  function toast(t) { var e = $('toast'); e.textContent = t; e.style.display = 'block'; clearTimeout(toastT); toastT = setTimeout(function () { e.style.display = 'none'; }, 2400); }
  function floatText(x, y, t, cls) {
    if (fxN > 28) return; fxN++; var d = document.createElement('div'); d.className = 'flt' + (cls ? ' ' + cls : ''); d.textContent = t; d.style.setProperty('--x', x + 'px'); d.style.setProperty('--y', y + 'px');
    $('fx').appendChild(d); setTimeout(function () { d.remove(); fxN--; }, 1250);
  }
  function ago(t) { var s = Math.max(0, (Engine.now() - t) / 1000); if (s < 60) return 'à l\'instant'; if (s < 3600) return Math.floor(s / 60) + ' min'; if (s < 86400) return Math.floor(s / 3600) + ' h'; return Math.floor(s / 86400) + ' j'; }
  function durTxt(s) { var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60); return h > 0 ? h + ' h ' + (m < 10 ? '0' : '') + m + ' min' : m + ' min'; }

  /* ---------- synchronisation ville 3D <-> état ---------- */
  function plotStateOf(i) { var n = S().biz[i].n; return n > 0 ? 2 : (i === 0 || S().biz[i - 1].n > 0) ? 1 : 0; }
  function syncCity(animate) { if (!Gfx.pawnMoving()) Gfx.pawnSet(S().dice.pos); for (var i = 0; i < BIZ.length; i++) Gfx.setPlot(i, plotStateOf(i), Engine.tierOf(S().biz[i].n), animate); }
  function nextToBuy() { for (var i = 0; i < BIZ.length; i++) if (S().biz[i].n <= 0) return i; return -1; }

  /* ---------- cartes des commerces ---------- */
  function buildCards() {
    var host = $('cards'); host.innerHTML = '';
    BIZ.forEach(function (b, i) {
      var d = document.createElement('div'); d.className = 'card lock hide'; d.dataset.i = i;
      d.innerHTML = '<div class="box"><div class="c-head"><span class="c-dot" style="background:' + Engine.DISTRICTS[b.dist].color + '"></span><span class="c-name"></span><span class="c-x2" title="Quartier complet : revenus ×2">★</span><span class="c-lvl"></span></div>' +
        '<div class="c-cp"></div><div class="c-bar"><i></i><span></span><b></b></div><div class="c-ms"><i></i></div>' +
        '<button class="c-up"><span></span><b></b></button><button class="c-buy"><span>Acheter</span><b></b></button></div>';
      host.appendChild(d);
      cards[i] = { cp: d.querySelector('.c-cp'), d: d, name: d.querySelector('.c-name'), lvl: d.querySelector('.c-lvl'), bar: d.querySelector('.c-bar i'), bl: d.querySelector('.c-bar span'), br: d.querySelector('.c-bar b'),
        ms: d.querySelector('.c-ms i'), up: d.querySelector('.c-up'), upl: d.querySelector('.c-up span'), upp: d.querySelector('.c-up b'), buy: d.querySelector('.c-buy'), buyp: d.querySelector('.c-buy b'), box: d.querySelector('.box') };
    });
  }
  var holdT = null, holdI = null;
  function doUpgrade(i) {
    if (Engine.incident(i)) { var f = Engine.fixIncident(i); if (!f.ok) { Sfx.err(); if (f.msg) toast(f.msg); } return false; }
    var r = Engine.upgrade(i); if (!r.ok) { Sfx.err(); if (r.msg) toast(r.msg); return false; }
    var p = Gfx.cardPos(i); floatText(p.x, p.y - 80, '+' + r.k + ' niv', 'big'); return true;
  }
  function doBuy(i) {
    var r = Engine.buy(i); if (!r.ok) { Sfx.err(); toast(r.msg); return; }
    var p = Gfx.cardPos(i); floatText(p.x, p.y - 90, BIZ[i].name + ' !', 'big');
  }
  function stopHold() { clearInterval(holdT); clearTimeout(holdT); holdT = null; holdI = null; }
  function bindCards() {
    var host = $('cards');
    host.addEventListener('pointerdown', function (e) {
      var up = e.target.closest('.c-up'), by = e.target.closest('.c-buy'); if (!up && !by) return;
      var i = +e.target.closest('.card').dataset.i; Sfx.init(); e.preventDefault();
      if (by) { doBuy(i); return; }
      if (doUpgrade(i)) { holdI = i; holdT = setTimeout(function () { holdT = setInterval(function () { if (holdI !== null && !doUpgrade(holdI)) stopHold(); }, 130); }, 420); }
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (n) { host.addEventListener(n, stopHold); });
    window.addEventListener('pointerup', stopHold);
  }
  function lastMs(n) { var p = 0, M = Engine.MS; for (var i = 0; i < M.length; i++) if (n >= M[i]) p = M[i]; return p; }
  function updateCards() {
    var s = S(), W = window.innerWidth, H = window.innerHeight, ppu = Gfx.pxPerUnit(), sc = Math.max(0.6, Math.min(1.1, ppu / 28)), mult = s.mult;
    for (var i = 0; i < BIZ.length; i++) {
      var c = cards[i], b = s.biz[i], st = plotStateOf(i), p = Gfx.cardPos(i);
      var vis = p.x > -90 && p.x < W + 90 && p.y > 20 && p.y < H + 150;
      setCls(c.d, 'hide', !vis); if (!vis) continue;
      c.d.style.transform = 'translate(' + p.x.toFixed(1) + 'px,' + p.y.toFixed(1) + 'px) scale(' + sc.toFixed(3) + ') translate(-50%,-100%)';
      if (plotState[i] !== st) { plotState[i] = st; setCls(c.d, 'lock', st === 0); setCls(c.d, 'next', st === 1); setCls(c.d, 'own', st === 2); }
      setTxt(c.name, (st === 0 ? '🔒 ' : '') + BIZ[i].name);
      if (st === 0) continue;
      if (st === 1) { var pr = Engine.price(i, 1); setTxt(c.buyp, money(pr)); var ok = s.cash >= pr; setCls(c.buy, 'no', !ok); setCls(c.d, 'pulse', ok && i === nextToBuy()); continue; }
      var cmp = s.comp[BIZ[i].dist]; setCls(c.d, 'cmp', !!cmp); if (cmp) setTxt(c.cp, '⚔️ ' + Engine.RIVALS[cmp.r].name + ' · -35 %');
      var inc = Engine.incident(i); setCls(c.d, 'inc', !!inc);
      if (inc) {
        var IT = Engine.INCIDENTS.filter(function (z) { return z.t === inc.t; })[0];
        setTxt(c.lvl, b.n); setTxt(c.bl, IT.ic + ' ' + IT.n); setTxt(c.br, inc.until ? Math.max(0, Math.ceil((inc.until - Engine.now()) / 1000)) + ' s' : '');
        c.bar.style.transform = 'scaleX(0)'; setTxt(c.upl, '🛠 ' + IT.lb); setTxt(c.upp, money(inc.cost)); setCls(c.up, 'no', s.cash < inc.cost); continue;
      }
      var tm = Engine.time(i), cont = tm < 0.25;
      setTxt(c.lvl, b.n); setCls(c.d, 'dc', Engine.distComplete(BIZ[i].dist));
      c.bar.style.transform = 'scaleX(' + (cont ? 1 : b.p).toFixed(3) + ')';
      setTxt(c.bl, '+' + money(Engine.rev(i))); setTxt(c.br, cont ? fmt(Engine.perSec(i)) + '/s' : (tm * (1 - b.p) < 10 ? (tm * (1 - b.p)).toFixed(1) + ' s' : Engine.fmtTime(tm * (1 - b.p))));
      var nm = Engine.nextMs(b.n), pm = lastMs(b.n); c.ms.style.transform = 'scaleX(' + (nm ? (b.n - pm) / (nm - pm) : 1).toFixed(3) + ')';
      var k = Engine.buyCount(i), cost = Engine.price(i, k), can = s.cash >= cost && (mult !== 0 || Engine.maxUnits(i) > 0);
      setTxt(c.upl, mult === 0 ? 'Max' + (Engine.maxUnits(i) > 0 ? ' ×' + k : '') : 'Améliorer' + (k > 1 ? ' ×' + k : '')); setTxt(c.upp, money(cost)); setCls(c.up, 'no', !can);
    }
  }

  /* ---------- barre du haut, rail, navigation ---------- */
  function buildHud() {
    $('rail').innerHTML = '<button class="rb" id="rbRev" title="Revenus ×2 pendant 60 s">💰<small></small></button><button class="rb" id="rbSpd" title="Cycles ×2 pendant 30 s">⚡<small></small></button><button class="rb vip" id="rbVip" style="display:none">🤵<small></small></button><button class="rb" id="rbComp" style="display:none;background:linear-gradient(#ff9aa0,#e5484d)">⚔️<small></small></button><button class="rb star" id="rbStar" style="display:none">⭐<small>+0 ⭐</small></button>';
    $('nav').innerHTML =
      '<button class="nb g" data-p="quests"><div class="ic">📜</div><span class="lb">Quêtes</span><div class="bdg" id="bdgQ"></div></button>' +
      '<button class="nb k" data-p="news"><div class="ic">📰</div><span class="lb">Journal</span></button>' +
      '<button class="nb p" data-p="team" style="flex:1.7;max-width:140px"><div id="slots"></div><span class="lb">Conseillers</span></button>' +
      '<button class="nb o" data-p="dice"><div class="ic">🎲</div><span class="lb">Dés</span><div class="bdg" id="bdgD"></div></button>' +
      '<button class="nb k" data-p="settings"><div class="ic">⚙️</div><span class="lb">Réglages</span></button>';
    $('nav').addEventListener('click', function (e) { var b = e.target.closest('[data-p]'); if (!b) return; Sfx.init(); Sfx.click(); openPanel(b.dataset.p); });
    $('cashbox').addEventListener('click', function () { Sfx.init(); Sfx.click(); openPanel('fin'); });
    $('fab').addEventListener('click', function () { Sfx.init(); if (curSheet) closePanel(); diceRoll(); });
    $('mult').addEventListener('click', function () { Sfx.init(); Sfx.click(); Engine.cycleMult(); });
    $('rbRev').addEventListener('click', function () { Sfx.init(); if (Engine.useBoost('rev')) Sfx.claim(); else { Sfx.err(); toast('Revenus ×2 : déjà actif ou en recharge.'); } });
    $('rbSpd').addEventListener('click', function () { Sfx.init(); if (Engine.useBoost('spd')) Sfx.claim(); else { Sfx.err(); toast('Cycles ×2 : déjà actif ou en recharge.'); } });
    $('rbVip').addEventListener('click', function () { Sfx.init(); showVip(); });
    $('rbComp').addEventListener('click', function () { Sfx.init(); Sfx.click(); openPanel('news'); });
    $('rbStar').addEventListener('click', function () { Sfx.init(); prestigeModal(); });
    $('veil').addEventListener('click', closePanel); $('sclose').addEventListener('click', closePanel);
  }
  var hudT = 0;
  function updateHud(dt) {
    var s = S(); setTxt($('cash'), money(s.cash)); setTxt($('ps'), '+' + money(Engine.totalPerSec()) + '/s' + (s.debt > 1 ? ' · dette ' + money(s.debt) : '')); var di = Engine.dateInfo(); setTxt($('dt'), '📅 An ' + di.year + ' · mois ' + di.month + ' · j.' + di.day + ' · 👤 ' + di.age + ' ans'); setTxt($('cnt'), Engine.owned() + '/' + BIZ.length);
    setTxt($('mult'), s.mult === 0 ? 'Max' : '×' + s.mult);
    hudT -= dt; if (hudT > 0) return; hudT = 0.2;
    var rev = Engine.boostState('rev'), spd = Engine.boostState('spd'), a = $('rbRev'), b = $('rbSpd');
    a.className = 'rb' + (rev.on ? ' on' : rev.cd > 0 ? ' cd' : ''); setTxt(a.querySelector('small'), rev.on ? Math.ceil(rev.left) + ' s' : rev.cd > 0 ? Engine.fmtTime(rev.cd) : '×2');
    b.className = 'rb' + (spd.on ? ' on' : spd.cd > 0 ? ' cd' : ''); setTxt(b.querySelector('small'), spd.on ? Math.ceil(spd.left) + ' s' : spd.cd > 0 ? Engine.fmtTime(spd.cd) : '×2');
    var v = s.vip.cur, rv = $('rbVip'); rv.style.display = v ? '' : 'none'; if (v) setTxt(rv.querySelector('small'), Math.max(0, Math.ceil((v.until - Engine.now()) / 1000)) + ' s');
    var nc = s.comp.filter(function (z) { return z; }).length; $('rbComp').style.display = nc ? '' : 'none'; setTxt($('rbComp').querySelector('small'), nc + ' rival' + (nc > 1 ? 'aux' : ''));
    var pot = Engine.starsPotential(); $('rbStar').style.display = pot >= 1 ? '' : 'none'; setTxt($('rbStar').querySelector('small'), '+' + pot + ' ⭐');
    var ev = Engine.evType(), eb = $('evt'); if (ev) { var E = Engine.EVENTS.filter(function (x) { return x.type === ev; })[0]; eb.style.display = 'block'; setTxt(eb, ({ boom: '📈 Boom économique : revenus +50 %', sale: '🏷️ Soldes : coûts -25 %', rush: '⚡ Heure de pointe : cycles ×2' })[ev] + ' · ' + Math.ceil((s.ev.until - Engine.now()) / 1000) + ' s'); } else eb.style.display = 'none';
    var q = Engine.questsReady(), bq = $('bdgQ'); bq.style.display = q ? 'grid' : 'none'; setTxt(bq, q); var r = s.dice.rolls; setTxt($('fabn'), r); $('fabn').style.display = r ? '' : 'none'; setCls($('fab'), 'no', r <= 0); var bd = $('bdgD'); bd.style.display = r ? 'grid' : 'none'; setTxt(bd, r);
    var sl = '', i; for (i = 0; i < s.slots; i++) { var id = s.eq[i]; sl += id ? '<div class="slot"><img src="' + Portrait.get(Engine.ADVBY[id]) + '"></div>' : '<div class="slot">+</div>'; } setHtml($('slots'), sl);
    // aide contextuelle
    var h = '', up = s.up.reduce(function (x, y) { return x + y; }, 0);
    if (Engine.owned() === 0) h = 'Touchez « Acheter » pour ouvrir votre premier commerce !';
    else if (up < 3 && s.tut < 2) h = 'Touchez « Améliorer » (maintenez pour répéter) pour gagner plus.'; else if (up >= 3 && s.tut < 2) s.tut = 2;
    else if (Engine.INCIDENTS && s.inc.some(function (z) { return z; })) h = '⚠️ Un problème bloque un commerce : touchez « Réparer » (ou attendez la fin d\'une grève).';
    else if (s.comp.some(function (z) { return z; })) h = '⚔️ Un concurrent vous attaque ! Ouvrez 📰 pour lancer une campagne.';
    else if (q && s.tut < 3) h = 'Une quête est terminée ! Ouvrez 📜 pour récupérer la récompense.';
    var he = $('hint'); he.style.display = h ? 'block' : 'none'; setTxt(he, h);
  }

  /* ---------- panneaux ---------- */
  function openPanel(name) {
    curSheet = name; $('veil').style.display = 'block'; $('sheet').style.display = 'flex'; renderPanel(true);
  }
  function closePanel() { if (!curSheet) return; Sfx.click(); curSheet = null; $('veil').style.display = 'none'; $('sheet').style.display = 'none'; }
  function renderPanel(reset) {
    if (!curSheet) return; var body = $('sbody'), sc = body.scrollTop, t = { quests: '📜 Quêtes', news: '📰 Journal & rivaux', team: '🧑‍💼 Conseillers', dice: '🎲 Plateau de la fortune', settings: '⚙️ Réglages', fin: '💶 Finances' };
    $('stitle').textContent = t[curSheet]; ({ quests: pQuests, news: pNews, team: pTeam, dice: pDice, settings: pSettings, fin: pFin })[curSheet](body); body.scrollTop = reset ? 0 : sc;
  }
  function pFin(b) {
    var s = S(), di = Engine.dateInfo(), bl = s.bill, lim = Engine.creditLimit(), room = Math.max(0, lim - s.debt), mLeft = 12 - (s.month % 12), h = '';
    h += '<div class="lrow" style="display:block"><b>📅 An ' + di.year + ' · mois ' + di.month + ' · jour ' + di.day + '</b><div class="note">👤 Vous avez ' + di.age + ' ans · 1 jour = 10 s, 1 mois = 5 min, 1 an = 1 h de jeu. Les commerces travaillent pour vous, mais la vie a un coût.</div></div>';
    h += '<div class="sec">Bilan du dernier mois</div>';
    h += bl ? '<div class="lrow" style="display:block">Revenus encaissés : <b>' + money(bl.inc) + '</b><br>Vie courante (loyer, nourriture, transports…) : <b>-' + money(bl.living) + '</b><br>Intérêts de la dette : <b>-' + money(bl.interest) + '</b>' + (bl.tax ? '<br>Impôts annuels : <b>-' + money(bl.tax) + '</b>' : '') + '</div>' : '<div class="lrow">Pas encore de bilan : le premier mois se termine bientôt.</div>';
    h += '<div class="sec">À prévoir</div><div class="lrow" style="display:block">Vie courante : <b>≈ ' + money(Engine.livingCost()) + ' / mois</b> (plus vous gagnez, plus votre train de vie monte)<br>Impôts : <b>12 %</b> des revenus de l\'année, dans <b>' + mLeft + ' mois</b> (déjà ≈ ' + money(s.yInc * 0.12) + ')</div>';
    h += '<div class="sec">Dette & banque</div><div class="lrow" style="display:block">Dette : <b style="color:' + (s.debt > 0 ? '#b0262c' : '#2a8f38') + '">' + money(s.debt) + '</b> · intérêts 1,5 % / mois<br>Capacité d\'emprunt restante : <b>' + money(room) + '</b>' +
      '<div class="note">Vos charges non payées (découvert) s\'ajoutent à la dette. 30 % de vos revenus la remboursent automatiquement. Emprunter permet d\'acheter plus vite, mais coûte des intérêts !</div>' +
      '<div style="display:flex;gap:8px;margin-top:8px"><button class="btn sm blue" data-b="q" style="flex:1">Emprunter ' + money(room / 4) + '</button><button class="btn sm blue" data-b="all" style="flex:1">Emprunter ' + money(room) + '</button></div>' +
      '<div style="display:flex;gap:8px;margin-top:8px"><button class="btn sm ' + (s.debt > 0 ? 'gold' : 'no') + '" data-r="half" style="flex:1">Rembourser la moitié</button><button class="btn sm ' + (s.debt > 0 ? 'gold' : 'no') + '" data-r="all" style="flex:1">Tout rembourser</button></div></div>';
    b.innerHTML = h;
    b.onclick = function (e) {
      var x = e.target.closest('[data-b]'), r;
      if (x) { r = Engine.borrow(x.dataset.b === 'q' ? room / 4 : room); if (!r.ok) { Sfx.err(); toast(r.msg); } else { Sfx.claim(); toast('Prêt accordé : +' + money(r.amt)); renderPanel(); } return; }
      x = e.target.closest('[data-r]'); if (x) { r = Engine.repay(x.dataset.r === 'half' ? S().debt / 2 : S().debt); if (!r.ok) { Sfx.err(); toast(r.msg); } else { Sfx.up(); renderPanel(); } }
    };
  }
  function pQuests(b) {
    var s = S(), h = '<div class="note">Terminez les objectifs pour toucher des récompenses en argent. De nouvelles quêtes arrivent aussitôt.</div>';
    s.quests.forEach(function (q) {
      var pr = Engine.qProgress(q), ok = pr >= q.n, pct = Math.min(100, pr / q.n * 100);
      var prog = q.t === 'earn' ? money(pr) + ' / ' + money(q.n) : Math.floor(pr) + ' / ' + q.n;
      h += '<div class="qrow"><div class="qt"><div class="qn">' + esc(Engine.qTitle(q)) + '</div><div class="pb"><i style="width:' + pct + '%"></i></div><div class="qr">' + prog + ' · Récompense : ' + money(q.rew) + '</div></div><button class="btn sm ' + (ok ? 'gold' : 'no') + '" data-q="' + q.id + '">' + (ok ? 'Récupérer' : 'En cours') + '</button></div>';
    });
    b.innerHTML = h;
    b.onclick = function (e) { var x = e.target.closest('[data-q]'); if (!x) return; var q = Engine.claimQuest(+x.dataset.q); if (!q) { Sfx.err(); return; } S().tut = 3; Sfx.claim(); toast('Quête accomplie : +' + money(q.rew)); renderPanel(); };
  }
  function pNews(b) {
    var s = S(), h = '<div class="sec" style="margin-top:4px">🏆 Classement des empires</div>', rk = Engine.ranking();
    rk.forEach(function (r, k) { h += '<div class="lrow" style="' + (r.me ? 'outline:3px solid var(--gold);' : '') + '"><b style="width:22px">' + (k + 1) + '</b><span style="font-size:22px">' + r.ic + '</span><span style="flex:1"><b>' + esc(r.name) + '</b><br><small style="margin:0">' + r.tag + '</small></span><b>' + money(r.w) + '</b></div>'; });
    h += '<div class="note">Fortune cumulée. Les rivaux grandissent en même temps que vous : développez-vous plus vite qu\'eux !</div>';
    var att = s.comp.map(function (c, d) { return c ? { c: c, d: d } : null; }).filter(function (z) { return z; });
    h += '<div class="sec">⚔️ Concurrence</div>';
    if (!att.length) h += '<div class="lrow">Aucun concurrent n\'attaque vos quartiers pour l\'instant.</div>';
    att.forEach(function (a) { var R = Engine.RIVALS[a.c.r], can = s.cash >= a.c.cost; h += '<div class="qrow"><div class="qt"><div class="qn">' + R.ic + ' ' + esc(R.name) + ' à ' + esc(Engine.DISTRICTS[a.d].name) + '</div><div class="qr" style="color:#b0262c">Revenus du quartier -35 % · il repartira dans ' + Engine.fmtTime((a.c.until - Engine.now()) / 1000) + '</div></div><button class="btn sm ' + (can ? 'gold' : 'no') + '" data-c="' + a.d + '">📣 Campagne<br>' + money(a.c.cost) + '</button></div>'; });
    h += '<div class="sec">Journal</div>';
    if (!s.news.length) h += '<div class="lrow">Rien à signaler pour l\'instant.</div>';
    s.news.forEach(function (n) { h += '<div class="lrow"><span>' + esc(n.x) + '</span><small>' + ago(n.t) + '</small></div>'; });
    b.innerHTML = h;
    b.onclick = function (e) { var x = e.target.closest('[data-c]'); if (!x) return; var r = Engine.counter(+x.dataset.c); if (!r.ok) { Sfx.err(); if (r.msg) toast(r.msg); } else { Sfx.claim(); renderPanel(); } };
  }
  function advCard(a, count) {
    var own = count > 0, eq = S().eq.indexOf(a.id) >= 0;
    return '<div class="adv r' + a.rar + (own ? '' : ' lk') + (eq ? ' eq' : '') + '" data-a="' + a.id + '">' + (own ? '<span class="cnt">×' + count + '</span>' : '') + '<img src="' + Portrait.get(a, !own) + '"><div class="an">' + (own ? esc(a.name) : '???') + '</div><div class="an rt' + a.rar + '" style="font-size:10px">' + Engine.RARITY[a.rar].n + '</div><div class="ap">' + (own ? esc(Engine.advPerk(a, count)) : 'Non recruté') + '</div></div>';
  }
  function pTeam(b) {
    var s = S(), t = Engine.totals(), h = '', can = s.cash >= Engine.hireCost();
    h += '<div class="note">Équipez jusqu\'à ' + s.slots + ' conseillers : leurs bonus s\'ajoutent. Un doublon renforce le bonus (+50 %).</div>';
    h += '<div class="sec">Équipe (' + s.eq.length + '/' + s.slots + ')</div><div class="grid">';
    for (var i = 0; i < s.slots; i++) { var id = s.eq[i]; h += id ? advCard(Engine.ADVBY[id], s.adv[id]) : '<div class="adv" style="display:grid;place-items:center;min-height:120px;color:#8b98a6;font-size:13px;' + '">' + 'Emplacement libre' + '</div>'; }
    h += '</div><div class="sec">Bonus actifs</div><div class="lrow">' + [['cost', 'Coût des améliorations', -1], ['rev', 'Revenus', 1], ['speed', 'Vitesse', 1], ['offline', 'Gains hors ligne', 1], ['buy', 'Prix d\'achat', -1], ['vip', 'Visites VIP', 1]].map(function (r) { return '<span style="flex:1;font-size:12px">' + r[1] + '<br><b>' + (t[r[0]] ? (r[2] < 0 ? '-' : '+') + Math.round(t[r[0]] * 100) + ' %' : '—') + '</b></span>'; }).join('').replace(/(<span.*?<\/span>){3}/, '$&</div><div class="lrow">') + '</div>';
    h += '<div class="row" style="display:flex;gap:8px;margin:12px 0"><button class="btn ' + (can ? 'gold' : 'no') + '" data-h="1">Recruter · ' + money(Engine.hireCost()) + '</button>';
    if (s.slots < 4) h += '<button class="btn ' + (s.cash >= Engine.slotCost() ? 'blue' : 'no') + '" data-s="1">+1 emplacement · ' + money(Engine.slotCost()) + '</button>'; h += '</div>';
    h += '<div class="sec">Collection</div><div class="grid">'; Engine.ADV.forEach(function (a) { h += advCard(a, s.adv[a.id] || 0); }); h += '</div>';
    b.innerHTML = h;
    b.onclick = function (e) {
      var x;
      if ((x = e.target.closest('[data-h]'))) { var r = Engine.hire(); if (!r.ok) { Sfx.err(); toast(r.msg); } else renderPanel(); return; }
      if ((x = e.target.closest('[data-s]'))) { var r2 = Engine.buySlot(); if (!r2.ok) { Sfx.err(); toast(r2.msg); } else { Sfx.buy(); renderPanel(); } return; }
      if ((x = e.target.closest('[data-a]'))) { var id = x.dataset.a; if (!S().adv[id]) return; if (!Engine.equip(id)) { Sfx.err(); toast('Emplacements pleins : retirez d\'abord un conseiller.'); } else { Sfx.click(); renderPanel(); } }
    };
  }

  /* ----- dés ----- */
  var TILE_IC = { start: '🏁', cash: '💵', chance: '❓', tax: '🧾', boost: '📈', jail: '🔍', park: '🌳', adv: '🤝' }, diceBusy = false, tokenAt = -1;
  function tileXY(i) { if (i < 6) return [i, 0]; if (i < 11) return [5, i - 5]; if (i < 16) return [4 - (i - 11), 5]; return [0, 4 - (i - 16)]; }
  var FACE = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
  function pDice(b) {
    var s = S(), h = '<div id="board">';
    Engine.BOARD.forEach(function (t, i) { var xy = tileXY(i), ic = t.k === 'boost' && t.b === 'spd' ? '⚡' : TILE_IC[t.k]; h += '<div class="tile ' + t.k + '" data-t="' + i + '" style="grid-column:' + (xy[0] + 1) + ';grid-row:' + (xy[1] + 1) + '"><b>' + ic + '</b>' + t.t + '</div>'; });
    h += '<div id="bmid"><div class="dice"><div class="die" id="d1">⚀</div><div class="die" id="d2">⚁</div></div><button class="btn gold" id="rollBtn">Lancer les dés</button><div style="font-size:12px;font-weight:800" id="rollInfo"></div></div></div>';
    h += '<div id="dres">Lancez les dés : avancez sur le plateau et touchez des bonus ! Un lancer est offert toutes les 4 minutes (5 maximum).</div>';
    h += '<div class="note">Cases : 💵 recette (minutes de revenus) · ❓ carte Fortune · 🧾 impôts (2-3 % de la trésorerie) · 📈⚡ boosts · 🔍 contrôle fiscal (-1 lancer) · 🤝 nouveau conseiller · 🏁 prime à chaque tour.</div>';
    b.innerHTML = h; b.onclick = null; tokenAt = -1; placeToken(s.dice.pos); $('rollBtn').onclick = function () { Sfx.init(); closePanel(); diceRoll(); }; diceInfo();
  }
  function diceInfo() { var e = $('rollInfo'); if (!e) return; var d = S().dice; e.textContent = 'Lancers : ' + d.rolls + '/' + Engine.MAX_ROLLS + (d.rolls < Engine.MAX_ROLLS ? ' · +1 dans ' + Engine.fmtTime((d.next - Engine.now()) / 1000) : ''); var bt = $('rollBtn'); if (bt) { bt.classList.toggle('no', d.rolls <= 0 || diceBusy); } }
  function placeToken(pos) {
    var old = document.querySelector('.tok'); if (old) old.remove(); var cur = document.querySelector('.tile.cur'); if (cur) cur.classList.remove('cur');
    var t = document.querySelector('.tile[data-t="' + pos + '"]'); if (!t) return; var k = document.createElement('div'); k.className = 'tok'; t.appendChild(k); t.classList.add('cur'); tokenAt = pos;
  }
  function say(t) { var e = $('dres'); if (e) e.textContent = t; var r = $('rollres'); if (r) { r.textContent = t; r.style.display = 'block'; clearTimeout(say.t); say.t = setTimeout(function () { r.style.display = 'none'; }, 5200); } }
  function walk(path, i, done) {
    if (i >= path.length) { done(); return; }
    S().dice.pos = path[i]; placeToken(path[i]); Sfx.step();
    Gfx.pawnGo(path[i], 0.34, function () { walk(path, i + 1, done); });
  }
  function diceRoll() {
    if (diceBusy || Gfx.pawnMoving()) return; var r = Engine.rollDice(); if (!r) { Sfx.err(); toast('Plus de lancers : patientez ou jouez pour en gagner !'); return; }
    diceBusy = true; Sfx.roll(); var ov = $('dover'), n = 0; ov.style.display = 'flex'; $('od1').classList.add('roll'); $('od2').classList.add('roll'); if ($('d1')) { $('d1').classList.add('roll'); $('d2').classList.add('roll'); }
    var p0 = Gfx.pawnPos(); Gfx.focusPoint(p0.x, p0.z);
    var iv = setInterval(function () { n++; var a = FACE[1 + Math.floor(Math.random() * 6)], b2 = FACE[1 + Math.floor(Math.random() * 6)]; $('od1').textContent = a; $('od2').textContent = b2; if ($('d1')) { $('d1').textContent = a; $('d2').textContent = b2; } }, 75);
    diceInfo(); say('Les dés roulent…');
    setTimeout(function () {
      clearInterval(iv); [$('od1'), $('od2'), $('d1'), $('d2')].forEach(function (d, k) { if (d) { d.textContent = FACE[k % 2 ? r.d2 : r.d1]; d.classList.remove('roll'); } });
      say('Vous faites ' + (r.d1 + r.d2) + ' ! Votre pion avance…');
      setTimeout(function () { ov.style.display = 'none'; walk(r.path, 0, function () { land(r, r.path[r.path.length - 1], 0); }); }, 700);
    }, 800);
  }
  function land(r, pos, depth) {
    var extra = '';
    if (r && r.passedStart) { var o0 = Engine.landOn(0); extra = o0.text + ' '; Sfx.win(); }
    var o = Engine.landOn(pos); S().dice.pos = pos;
    if (o.k === 'cash' || o.k === 'start') { Sfx.claim(); } else if (o.k === 'tax' || o.k === 'jail') Sfx.err(); else Sfx.win();
    say(extra + (o.card ? '🃏 Fortune : ' : '') + o.text);
    var pp = Gfx.cardPosAt ? null : null; if (o.amt && (o.k === 'cash' || o.k === 'chance')) floatText(window.innerWidth / 2, window.innerHeight / 2, '+' + money(o.amt), 'big');
    if (o.move && depth < 3) {
      var path = [], i; for (i = 1; i <= o.move; i++) path.push((pos + i) % Engine.BOARD.length);
      setTimeout(function () { walk(path, 0, function () { land(null, path[path.length - 1], depth + 1); }); }, 1500);
    } else { diceBusy = false; diceInfo(); }
  }

  /* ----- réglages ----- */
  function seg(key, opts, cur) { return '<div class="seg" data-seg="' + key + '">' + opts.map(function (o) { return '<button data-v="' + o[0] + '" class="' + (o[0] === cur ? 'on' : '') + '">' + o[1] + '</button>'; }).join('') + '</div>'; }
  function pSettings(b) {
    var s = S(), pot = Engine.starsPotential(), nextAt = Math.pow(s.stars + pot + 1, 2) * 1e10, h = '';
    h += '<div class="setrow"><span>🔊 Sons</span><div class="tg ' + (s.set.sound ? 'on' : '') + '" data-tg="sound"></div></div>';
    h += '<div class="setrow"><span>🎵 Musique</span><div class="tg ' + (s.set.music ? 'on' : '') + '" data-tg="music"></div></div>';
    h += '<div class="setrow"><span>🖥️ Qualité</span>' + seg('quality', [['auto', 'Auto'], ['low', 'Faible'], ['medium', 'Moyenne'], ['high', 'Élevée']], s.set.quality) + '</div>';
    h += '<div class="sec">Expansion mondiale</div><div class="lrow" style="display:block"><div class="stars">' + (s.stars ? '⭐ ' + s.stars : '☆') + '</div><div class="note">Chaque étoile = +5 % de revenus pour toujours. Vous repartez de zéro mais gardez conseillers et étoiles. ' +
      (pot >= 1 ? '<b>Vous pouvez gagner ' + pot + ' étoile' + (pot > 1 ? 's' : '') + ' !</b>' : 'Prochaine étoile quand vos gains cumulés atteindront ' + money(nextAt) + ' (actuel : ' + money(s.life) + ').') + '</div><button class="btn ' + (pot >= 1 ? 'gold' : 'no') + '" data-a="prestige" style="width:100%;margin-top:6px">Lancer l\'expansion' + (pot >= 1 ? ' (+' + pot + ' ⭐)' : '') + '</button></div>';
    h += '<div class="sec">Code cadeau</div><div class="lrow" style="display:block"><input class="tx" id="gift" placeholder="Saisissez un code" autocapitalize="characters"><button class="btn blue" data-a="gift" style="width:100%;margin-top:8px">Valider</button></div>';
    h += '<div class="sec">Sauvegarde</div><div class="lrow" style="display:block"><div class="note">Votre partie est enregistrée automatiquement sur cet appareil. Exportez un code pour la copier ailleurs.</div><div style="display:flex;gap:8px"><button class="btn sm blue" data-a="export" style="flex:1">Exporter</button><button class="btn sm blue" data-a="import" style="flex:1">Importer</button></div><textarea class="tx" id="code" placeholder="Code de sauvegarde"></textarea></div>';
    h += '<div class="sec">Compte</div><div class="lrow" style="display:block"><b>' + esc(s.name) + '</b><div class="note">Partie créée il y a ' + durTxt((Engine.now() - s.t0) / 1000) + ' · Gains cumulés : ' + money(s.life) + '</div></div>';
    h += '<button class="btn red" data-a="reset" style="width:100%;margin:10px 0">Effacer ma partie</button><div class="note" style="text-align:center">Empire Tycoon · 100 % gratuit, aucune publicité, aucun achat intégré.<br>Tous les personnages et noms sont originaux.</div>';
    b.innerHTML = h;
    b.onclick = function (e) {
      var x = e.target.closest('[data-tg]'), s2 = S();
      if (x) { var k = x.dataset.tg; s2.set[k] = !s2.set[k]; Sfx.set(s2.set.sound, s2.set.music); Sfx.click(); x.classList.toggle('on', s2.set[k]); return; }
      x = e.target.closest('[data-v]'); if (x) { s2.set.quality = x.dataset.v; applyQuality(); Sfx.click(); renderPanel(); return; }
      x = e.target.closest('[data-a]'); if (!x) return; var a = x.dataset.a;
      if (a === 'gift') { var r = Engine.gift($('gift').value); toast(r.msg); if (r.ok) { Sfx.claim(); $('gift').value = ''; } else Sfx.err(); }
      else if (a === 'export') { var c = Engine.exportCode(); $('code').value = c; try { navigator.clipboard.writeText(c).then(function () { toast('Code copié !'); }, function () { toast('Copiez le code ci-dessous.'); }); } catch (er) { toast('Copiez le code ci-dessous.'); } }
      else if (a === 'import') { if (Engine.importCode($('code').value)) { syncCity(false); closePanel(); toast('Partie importée !'); } else { Sfx.err(); toast('Code invalide.'); } }
      else if (a === 'prestige') { if (Engine.starsPotential() >= 1) prestigeModal(); else { Sfx.err(); toast('Pas encore assez de gains cumulés.'); } }
      else if (a === 'reset') confirmBox('Effacer la partie ?', 'Toute votre progression sera perdue. Cette action est définitive.', 'Effacer', 'red', function () { Engine.reset(); syncCity(false); closePanel(); Gfx.focusPlot(0, true); toast('Nouvelle partie !'); });
    };
  }

  /* ---------- fenêtres ---------- */
  function showModal(html, binder) { modalQ.push({ h: html, b: binder }); if (!modalOpen) nextModal(); }
  function nextModal() {
    var m = modalQ.shift(); if (!m) { modalOpen = false; $('modal').style.display = 'none'; $('veil').style.display = curSheet ? 'block' : 'none'; return; }
    modalOpen = true; var e = $('modal'); e.innerHTML = m.h; e.style.display = 'block'; $('veil').style.display = 'block'; e.style.animation = 'none'; void e.offsetWidth; e.style.animation = '';
    if (m.b) m.b(e); e.querySelectorAll('[data-close]').forEach(function (x) { x.addEventListener('click', function () { Sfx.click(); nextModal(); }); });
  }
  function confirmBox(title, text, label, cls, fn) {
    showModal('<h2>' + esc(title) + '</h2><p>' + esc(text) + '</p><div class="row"><button class="btn gray" data-close>Annuler</button><button class="btn ' + cls + '" id="ok">' + esc(label) + '</button></div>', function (m) { m.querySelector('#ok').addEventListener('click', function () { nextModal(); fn(); }); });
  }
  function prestigeModal() {
    var pot = Engine.starsPotential(); if (pot < 1) return;
    confirmBox('Expansion mondiale ⭐', 'Vous gagnerez ' + pot + ' étoile' + (pot > 1 ? 's' : '') + ' (+' + (pot * 5) + ' % de revenus). Vos commerces et votre argent repartent de zéro ; conseillers et étoiles restent.', 'Lancer', 'gold', function () {
      if (Engine.prestige()) { syncCity(false); closePanel(); Gfx.focusPlot(0, true); Sfx.win(); toast('Expansion réussie !'); }
    });
  }
  function showVip() {
    var v = S().vip.cur; if (!v) return;
    var inv = v.type === 'investor', amt = Math.max(Engine.totalPerSec() * v.mins * 60, Engine.price(0, 1) * 2);
    showModal('<div style="font-size:54px">' + (inv ? '🤵' : '👩‍💼') + '</div><h2>' + (inv ? 'Un investisseur VIP !' : 'Une directrice d\'exploitation !') + '</h2><p>' + (inv ? 'Il souhaite investir dans votre empire :' : 'Elle propose d\'accélérer tous vos commerces ×2 pendant 30 secondes.') + '</p>' + (inv ? '<div class="big">+' + money(amt) + '</div><p>(environ ' + v.mins + ' minutes de revenus)</p>' : '') +
      '<div class="row"><button class="btn gray" data-close id="no">Non merci</button><button class="btn" id="yes">Accepter</button></div>', function (m) {
      m.querySelector('#no').addEventListener('click', function () { Engine.vipDecline(); });
      m.querySelector('#yes').addEventListener('click', function () { var o = Engine.vipAccept(); nextModal(); if (o) { Sfx.claim(); toast(o.amt ? 'Investissement reçu : +' + money(o.amt) : 'Cycles ×2 pendant 30 s !'); } });
    });
  }
  function offlineModal(o) {
    showModal('<div style="font-size:46px">🌙</div><h2>Bon retour, patron !</h2><p>Pendant votre absence (' + durTxt(o.secs) + '), vos commerces ont continué à travailler :</p><div class="big">+' + money(o.amt) + '</div>' + (o.capped ? '<p>(gains hors ligne : 50 % d\'efficacité, limités à 4 h)</p>' : '') + '<div class="row"><button class="btn gold" data-close>Récupérer</button></div>', function () { Sfx.claim(); });
  }
  function advisorModal(a, count) {
    showModal('<h2>Nouveau conseiller !</h2><img src="' + Portrait.get(a) + '" style="width:130px;height:130px;border-radius:18px;border:4px solid #fff;box-shadow:0 3px 10px rgba(0,0,0,.3)"><h2 class="rt' + a.rar + '" style="margin-top:8px">' + esc(a.name) + '</h2><p><b class="rt' + a.rar + '">' + Engine.RARITY[a.rar].n + '</b>' + (count > 1 ? ' · exemplaire n°' + count : '') + '</p><p>' + esc(Engine.advPerk(a, count)) + '</p><div class="row"><button class="btn" data-close>Super !</button></div>', function () { Sfx.win(); });
  }

  /* ---------- évènements du moteur ---------- */
  function onEvent(type, d) {
    if (!started) return;
    if (type === 'payout') {
      var n = Date.now(); if (lastPay[d.i] && n - lastPay[d.i] < 350) return; lastPay[d.i] = n; var p = Gfx.cardPos(d.i); if (p.x > 0 && p.x < window.innerWidth) { floatText(p.x, p.y - 108, '+' + money(d.amt)); Sfx.coin(); }
    } else if (type === 'purchase') { Sfx.buy(); syncCity(true); var nx = nextToBuy(); if (nx >= 0) Gfx.focusPlot(d.i, false, nx); Engine.save(); }
    else if (type === 'upgrade') { Sfx.up(); syncCity(true); if (d.tierUp) { Sfx.win(); toast('🏗️ Votre ' + BIZ[d.i].name.toLowerCase() + ' s\'agrandit !'); } if (curSheet === 'quests') renderPanel(); }
    else if (type === 'advisor') { advisorModal(d.a, d.count); if (curSheet === 'team') renderPanel(); }
    else if (type === 'incident') {
      Sfx.err(); if (d.instant) toast((d.theft ? '🦹 Cambriolage ! -' : '🧾 Amende fiscale : -') + money(d.amt)); else toast(d.type.ic + ' ' + d.type.n + ' à ' + BIZ[d.i].name + ' !');
      if (d.i !== undefined) Gfx.focusPlot(d.i, false);
    }
    else if (type === 'month') { toast('📅 Fin de mois : vie courante -' + money(d.living) + (d.tax ? ' · impôts -' + money(d.tax) : '')); if (S().debt > 0) Sfx.err(); if (curSheet === 'fin') renderPanel(); }
    else if (type === 'fixed') { Sfx.claim(); if (curSheet === 'news') renderPanel(); }
    else if (type === 'rival') { Sfx.err(); toast('⚔️ ' + Engine.RIVALS[d.r].name + ' attaque : ' + Engine.DISTRICTS[d.d].name + ' !'); }
    else if (type === 'rank') { toast(d.rk === 1 ? '🏆 Vous êtes n°1 !' : 'Classement : ' + d.rk + 'e'); }
    else if (type === 'vip') { Sfx.vip(); toast('🤵 Un VIP vous rend visite !'); }
    else if (type === 'event') { Sfx.vip(); toast(d.t); }
    else if (type === 'questdone' && curSheet === 'quests') renderPanel();
    else if (type === 'news' && curSheet === 'news') renderPanel();
  }

  /* ---------- caméra : glisser, pincer, molette, toucher un bâtiment ---------- */
  function bindCanvas() {
    var cv = $('gl'), ptr = {}, np = 0, moved = 0, startP = null, lastD = 0;
    function dist() { var k = Object.keys(ptr); if (k.length < 2) return 0; var a = ptr[k[0]], b = ptr[k[1]]; return Math.hypot(a.x - b.x, a.y - b.y); }
    cv.addEventListener('pointerdown', function (e) { cv.setPointerCapture(e.pointerId); ptr[e.pointerId] = { x: e.clientX, y: e.clientY }; np = Object.keys(ptr).length; if (np === 1) { moved = 0; startP = { x: e.clientX, y: e.clientY }; } lastD = dist(); Sfx.init(); });
    cv.addEventListener('pointermove', function (e) {
      var p = ptr[e.pointerId]; if (!p) return; var dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;
      if (np === 1) { moved += Math.abs(dx) + Math.abs(dy); if (moved > 6) Gfx.pan(dx, dy); }
      else if (np >= 2) { var d = dist(); if (lastD > 0 && d > 0) Gfx.zoomBy(lastD / d); lastD = d; moved = 99; }
    });
    function up(e) {
      if (!ptr[e.pointerId]) return; delete ptr[e.pointerId]; var was = np; np = Object.keys(ptr).length; lastD = dist();
      if (was === 1 && moved <= 6 && startP) tap(e.clientX, e.clientY);
    }
    cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
    cv.addEventListener('wheel', function (e) { e.preventDefault(); Gfx.zoomBy(e.deltaY > 0 ? 1.1 : 0.9); }, { passive: false });
  }
  function tap(x, y) {
    var best = -1, bd = 1e9, ppu = Gfx.pxPerUnit(), s = S(), i;
    for (i = 0; i < BIZ.length; i++) { if (s.biz[i].n <= 0) continue; var p = Gfx.bodyPos(i), d = Math.hypot(p.x - x, (p.y - y) * 0.9); if (d < bd) { bd = d; best = i; } }
    if (best < 0 || bd > ppu * 6.5) return;
    var b = s.biz[best], tm = Engine.time(best); if (Engine.incident(best)) { toast('Ce commerce est à l\'arrêt : réparez-le d\'abord.'); return; } if (tm >= 0.25) { b.p = Math.min(0.995, b.p + 1 / tm); }
    var q = Gfx.bodyPos(best); floatText(q.x, q.y - 20, '⚡ +1 s'); Gfx.puff(Gfx.info().plots[best].pos.x, 4.5, Gfx.info().plots[best].pos.z); Sfx.click();
  }

  /* ---------- qualité ---------- */
  var coarse = false;
  function autoQ() { return coarse ? 'medium' : 'high'; }
  function applyQuality() { var q = S().set.quality; Gfx.setQuality(q === 'auto' ? autoQ() : q); }
  var fpsAcc = 0, fpsN = 0, lastDown = 0;
  function watchFps(rdt) {
    if (S().set.quality !== 'auto' || !started) return; fpsAcc += rdt; fpsN++;
    if (fpsAcc > 4) { var fps = fpsN / fpsAcc; fpsAcc = 0; fpsN = 0; var q = Gfx.qualityName(); if (fps < 32 && q !== 'low' && Date.now() - lastDown > 6000) { lastDown = Date.now(); Gfx.setQuality(q === 'high' ? 'medium' : 'low'); } }
  }

  /* ---------- initialisation ---------- */
  function init() {
    coarse = !!(window.matchMedia && window.matchMedia('(pointer:coarse)').matches);
    buildCards(); bindCards(); buildHud(); bindCanvas(); Engine.on(onEvent);
    var s = S(); Sfx.set(s.set.sound, s.set.music); syncCity(false); Gfx.pawnSet(s.dice.pos); Gfx.setView(window.innerHeight > window.innerWidth ? 38 : 22); var nb = nextToBuy(); if (nb <= 0) Gfx.focusPlot(0, true, 1); else Gfx.focusPlot(nb - 1, true, nb);
    var done = function () { $('splash').style.display = 'none'; };
    $('splash').addEventListener('click', function () { if (started) return; started = true; Sfx.init(); Sfx.click(); done(); if (UI.pendingOffline) { offlineModal(UI.pendingOffline); UI.pendingOffline = null; } }, { once: false });
  }
  function update(dt, rdt) {
    if (Gfx.pawnMoving()) { var pw = Gfx.pawnPos(); Gfx.focusPoint(pw.x, pw.z); }
    updateCards(); updateHud(dt); watchFps(rdt);
    // textes flottants des commerces en continu
    for (var i = 0; i < BIZ.length; i++) { if (S().biz[i].n <= 0 || Engine.time(i) >= 0.25) continue; contT[i] = (contT[i] || 0) + dt; if (contT[i] > 1.6) { var p = Gfx.cardPos(i); if (started && p.x > 0 && p.x < window.innerWidth) { floatText(p.x, p.y - 108, '+' + money(Engine.perSec(i) * contT[i])); Sfx.coin(); } contT[i] = 0; } }
    smokeT -= dt; if (smokeT <= 0) { smokeT = 1.1; for (var k = 0; k < BIZ.length; k++) if (S().inc[k] && S().biz[k].n > 0) { var pp = Gfx.info().plots[k].pos; Gfx.puff(pp.x, 3.5, pp.z); } }
    if (curSheet === 'dice' || curSheet === 'quests') { panelT -= rdt; if (panelT <= 0) { panelT = 1; if (curSheet === 'dice') diceInfo(); else renderPanel(); } }
  }
  var panelT = 0, smokeT = 0;
  return { init: init, update: update, syncCity: syncCity, applyQuality: applyQuality, offlineModal: offlineModal, showModal: showModal, toast: toast, pendingOffline: null, isStarted: function () { return started; }, openPanel: openPanel, closePanel: closePanel, showVip: showVip, floatText: floatText, tap: tap };
})();
