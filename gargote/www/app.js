'use strict';
// Toutes les données sont stockées localement (localStorage du WebView) — aucune connexion requise.
const KEY = 'gargote.v1';
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const DEFAULT = {
  settings: { name: 'Ma Gargote', currency: 'Ar' },
  menu: [
    { id: uid(), name: 'Riz + sauce', price: 2000, cat: 'Plats' },
    { id: uid(), name: 'Poulet', price: 4000, cat: 'Plats' },
    { id: uid(), name: 'Brochette', price: 1000, cat: 'Plats' },
    { id: uid(), name: 'Eau', price: 1000, cat: 'Boissons' },
    { id: uid(), name: 'Soda', price: 1500, cat: 'Boissons' },
  ],
  sales: [],     // {id, ts, lines:[{name,price,qty}], total}
  expenses: [],  // {id, ts, label, amount}
};
let db;
try { db = JSON.parse(localStorage.getItem(KEY)) || DEFAULT; } catch { db = DEFAULT; }
db.settings = Object.assign({}, DEFAULT.settings, db.settings);
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(db)); } catch { toast('Erreur de sauvegarde'); } };

const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const money = n => Math.round(n).toLocaleString('fr-FR') + ' ' + esc(db.settings.currency);
const dayStart = (d = new Date()) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
const fmtTime = ts => new Date(ts).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
function toast(m) { const t = $('#toast'); t.textContent = m; t.classList.add('on'); setTimeout(() => t.classList.remove('on'), 1600); }

let tab = 'caisse', ticket = {}, period = 'jour';

function render() {
  $('#shopName').textContent = db.settings.name;
  document.querySelectorAll('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
  $('#view').innerHTML = ({ caisse, menu, depenses, bilan, reglages }[tab])();
  window.scrollTo(0, 0);
}
document.querySelectorAll('#tabs button').forEach(b => b.onclick = () => { tab = b.dataset.tab; render(); });
const ask = (msg, def = '') => { const v = prompt(msg, def); return v === null ? null : v.trim(); };
const num = v => { const n = parseFloat(String(v).replace(',', '.').replace(/\s/g, '')); return isFinite(n) && n >= 0 ? n : NaN; };

/* ---------- Caisse ---------- */
function ticketTotal() { return Object.entries(ticket).reduce((s, [id, q]) => { const m = db.menu.find(x => x.id === id); return s + (m ? m.price * q : 0); }, 0); }
function caisse() {
  if (!db.menu.length) return '<div class="empty">Ajoutez d\'abord des plats dans l\'onglet Menu.</div>';
  const cats = [...new Set(db.menu.map(m => m.cat || 'Autres'))];
  let h = cats.map(c => `<h2>${esc(c)}</h2><div class="grid">${db.menu.filter(m => (m.cat || 'Autres') === c).map(m =>
    `<button class="item" onclick="addT('${m.id}')">${esc(m.name)}<b>${money(m.price)}</b></button>`).join('')}</div>`).join('');
  const ids = Object.keys(ticket).filter(id => db.menu.some(m => m.id === id));
  h += `<h2>Ticket en cours</h2><div class="card">` + (ids.length ? ids.map(id => {
    const m = db.menu.find(x => x.id === id);
    return `<div class="row"><div class="g">${esc(m.name)}<small>${money(m.price)}</small></div>
      <div class="q"><button onclick="chgT('${id}',-1)">−</button><b>${ticket[id]}</b><button onclick="chgT('${id}',1)">+</button></div></div>`;
  }).join('') + `<div class="tot">${money(ticketTotal())}</div>
    <button class="b" onclick="pay()">✅ Encaisser</button><button class="b s" onclick="ticket={};render()">Vider</button>`
    : '<div class="empty">Touchez un plat pour l\'ajouter</div>') + '</div>';
  return h;
}
window.addT = id => { ticket[id] = (ticket[id] || 0) + 1; render(); };
window.chgT = (id, d) => { ticket[id] = (ticket[id] || 0) + d; if (ticket[id] <= 0) delete ticket[id]; render(); };
window.pay = () => {
  const lines = Object.entries(ticket).map(([id, qty]) => { const m = db.menu.find(x => x.id === id); return m && { name: m.name, price: m.price, qty }; }).filter(Boolean);
  if (!lines.length) return;
  db.sales.push({ id: uid(), ts: Date.now(), lines, total: lines.reduce((s, l) => s + l.price * l.qty, 0) });
  save(); toast('Vente enregistrée ✔'); ticket = {}; render();
};

/* ---------- Menu ---------- */
function menu() {
  return `<button class="b" onclick="editM()">➕ Ajouter un plat / boisson</button><div class="card">` +
    (db.menu.map(m => `<div class="row"><div class="g">${esc(m.name)}<small>${esc(m.cat || 'Autres')} · ${money(m.price)}</small></div>
      <button class="x" onclick="editM('${m.id}')">✏️</button><button class="x" onclick="delM('${m.id}')">🗑️</button></div>`).join('') || '<div class="empty">Menu vide</div>') + '</div>';
}
window.editM = id => {
  const m = db.menu.find(x => x.id === id) || {};
  const name = ask('Nom ?', m.name || ''); if (!name) return;
  const price = num(ask('Prix ?', m.price ?? '')); if (isNaN(price)) return toast('Prix invalide');
  const cat = ask('Catégorie (ex: Plats, Boissons) ?', m.cat || 'Plats') || 'Autres';
  if (m.id) Object.assign(m, { name, price, cat }); else db.menu.push({ id: uid(), name, price, cat });
  save(); render();
};
window.delM = id => { if (confirm('Supprimer ce produit ? (les ventes passées sont conservées)')) { db.menu = db.menu.filter(m => m.id !== id); delete ticket[id]; save(); render(); } };

/* ---------- Dépenses ---------- */
function depenses() {
  const list = [...db.expenses].sort((a, b) => b.ts - a.ts).slice(0, 100);
  return `<div class="card"><input id="eL" placeholder="Achat (ex: riz, charbon, gaz…)"><input id="eA" type="number" inputmode="decimal" placeholder="Montant (${esc(db.settings.currency)})">
    <button class="b" onclick="addE()">Enregistrer la dépense</button></div><h2>Dernières dépenses</h2><div class="card">` +
    (list.map(e => `<div class="row"><div class="g">${esc(e.label)}<small>${fmtTime(e.ts)}</small></div><b>${money(e.amount)}</b>
      <button class="x" onclick="delE('${e.id}')">🗑️</button></div>`).join('') || '<div class="empty">Aucune dépense</div>') + '</div>';
}
window.addE = () => {
  const label = $('#eL').value.trim(), amount = num($('#eA').value);
  if (!label || isNaN(amount) || amount <= 0) return toast('Remplissez les deux champs');
  db.expenses.push({ id: uid(), ts: Date.now(), label, amount }); save(); toast('Dépense enregistrée'); render();
};
window.delE = id => { if (confirm('Supprimer cette dépense ?')) { db.expenses = db.expenses.filter(e => e.id !== id); save(); render(); } };

/* ---------- Bilan ---------- */
function bilan() {
  const now = new Date();
  const from = period === 'jour' ? dayStart() : period === 'semaine' ? dayStart(new Date(now - ((now.getDay() + 6) % 7) * 864e5)) : new Date(now.getFullYear(), now.getMonth(), 1).getTime();
  const S = db.sales.filter(s => s.ts >= from), E = db.expenses.filter(e => e.ts >= from);
  const sv = S.reduce((a, s) => a + s.total, 0), ev = E.reduce((a, e) => a + e.amount, 0), pr = sv - ev;
  const top = {}; S.forEach(s => s.lines.forEach(l => { top[l.name] = (top[l.name] || 0) + l.qty; }));
  const tops = Object.entries(top).sort((a, b) => b[1] - a[1]).slice(0, 5);
  return `<div class="seg">${['jour', 'semaine', 'mois'].map(p => `<button class="${p === period ? 'on' : ''}" onclick="period='${p}';render()">${p === 'jour' ? "Aujourd'hui" : p === 'semaine' ? 'Semaine' : 'Mois'}</button>`).join('')}</div>
  <div class="stats" style="margin-top:10px"><div>Ventes<b>${money(sv)}</b></div><div>Dépenses<b>${money(ev)}</b></div><div>Bénéfice<b class="${pr >= 0 ? 'pos' : 'neg'}">${money(pr)}</b></div></div>
  <h2>Les plus vendus</h2><div class="card">${tops.map(([n, q]) => `<div class="row"><div class="g">${esc(n)}</div><b>× ${q}</b></div>`).join('') || '<div class="empty">Pas de vente</div>'}</div>
  <h2>Ventes (${S.length})</h2><div class="card">${[...S].reverse().slice(0, 100).map(s => `<div class="row"><div class="g">${s.lines.map(l => esc(l.name) + ' ×' + l.qty).join(', ')}<small>${fmtTime(s.ts)}</small></div><b>${money(s.total)}</b>
    <button class="x" onclick="delS('${s.id}')">🗑️</button></div>`).join('') || '<div class="empty">Aucune vente</div>'}</div>`;
}
window.delS = id => { if (confirm('Annuler cette vente ?')) { db.sales = db.sales.filter(s => s.id !== id); save(); render(); } };

/* ---------- Réglages ---------- */
function reglages() {
  return `<div class="card"><h2>Ma gargote</h2><input id="sN" value="${esc(db.settings.name)}" placeholder="Nom"><input id="sC" value="${esc(db.settings.currency)}" placeholder="Devise (Ar, FCFA, €…)">
    <button class="b" onclick="saveS()">Enregistrer</button></div>
  <div class="card"><h2>Sauvegarde</h2><p style="color:var(--mut);margin:0 0 6px;font-size:.85rem">Les données sont uniquement sur ce téléphone. Faites une sauvegarde régulière (désinstaller l'appli efface tout).</p>
    <button class="b" onclick="exportD()">📤 Exporter (fichier)</button>
    <button class="b s" onclick="$('#imp').click()">📥 Importer une sauvegarde</button>
    <input id="imp" type="file" accept=".json,application/json" hidden onchange="importD(this.files[0])"></div>
  <div class="card"><button class="b s" style="color:var(--ko)" onclick="resetD()">Tout effacer</button></div>`;
}
window.$ = $;
window.saveS = () => { db.settings.name = $('#sN').value.trim() || 'Ma Gargote'; db.settings.currency = $('#sC').value.trim() || 'Ar'; save(); toast('Enregistré'); render(); };
window.exportD = () => {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(db, null, 1)], { type: 'application/json' }));
  a.download = 'gargote-' + new Date().toISOString().slice(0, 10) + '.json'; a.click();
};
window.importD = f => {
  if (!f) return; const r = new FileReader();
  r.onload = () => { try { const d = JSON.parse(r.result); if (!Array.isArray(d.menu) || !Array.isArray(d.sales)) throw 0;
    if (confirm('Remplacer toutes les données actuelles ?')) { db = Object.assign({}, DEFAULT, d); save(); toast('Importé ✔'); render(); } } catch { toast('Fichier invalide'); } };
  r.readAsText(f);
};
window.resetD = () => { if (confirm('Effacer TOUTES les données ?') && confirm('Vraiment sûr ?')) { db = JSON.parse(JSON.stringify(DEFAULT)); save(); render(); } };

render();
