/* =====================================================================
 * 5. BOUCLE PRINCIPALE
 * ===================================================================== */
(function () {
  var cv = document.getElementById('gl'), last = 0, saveT = 0, frameN = 0, errBox = null;
  function fail(msg) { var d = document.createElement('div'); d.style.cssText = 'position:fixed;inset:0;z-index:99;background:#16283a;color:#fff;padding:24px;font:16px system-ui;display:flex;align-items:center;justify-content:center;text-align:center'; d.textContent = msg; document.body.appendChild(d); }
  if (!window.THREE) { fail('Impossible de charger le moteur 3D (Three.js).'); return; }
  var loaded = Engine.load(); Engine.init(loaded);
  var off = loaded ? Engine.offline() : null;
  try { Gfx.init(cv, 'medium'); } catch (e) { fail('Votre appareil ne prend pas en charge WebGL : ' + e.message); return; }
  var R = Gfx.info().renderer; R.shadowMap.autoUpdate = false;
  UI.init(); UI.applyQuality(); UI.pendingOffline = off;
  var wasPortrait = window.innerHeight > window.innerWidth;
  window.addEventListener('resize', function () { var pt = window.innerHeight > window.innerWidth; if (pt !== wasPortrait) { wasPortrait = pt; Gfx.setView(pt ? 38 : 22); } Gfx.resize(); });
  window.addEventListener('orientationchange', function () { setTimeout(Gfx.resize, 200); });
  function save() { Engine.save(); }
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) { save(); } else { var o = Engine.offline(); Engine.state().last = Engine.now(); last = 0; if (o && UI.isStarted()) UI.offlineModal(o); }
  });
  window.addEventListener('pagehide', save);
  function loop(t) {
    requestAnimationFrame(loop);
    var rdt = last ? Math.min(0.25, (t - last) / 1000) : 0.016; last = t; var dt = Math.min(rdt, 0.1);
    Engine.tick(dt); Gfx.frame(dt); UI.update(dt, rdt);
    if (frameN++ % 3 === 0) R.shadowMap.needsUpdate = true;
    Gfx.render();
    saveT += rdt; if (saveT > 10) { saveT = 0; save(); }
  }
  requestAnimationFrame(loop);
})();
