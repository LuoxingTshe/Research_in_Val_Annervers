// Render archived web sources (JSON / text saved on 2026-10-06) as static page images for the evidence folder.
// Usage: node render_web_evidence.js references.json <web_sources_dir> <outdir>
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const refs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const W = process.argv[3]; const out = process.argv[4]; fs.mkdirSync(out, { recursive: true });
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const head = (rid, r, loc, retrievedAt) => `<div class="hd"><div class="tag">${rid} · ${loc} · ARCHIVED WEB SOURCE</div>
<div class="cit">${esc(r.citation)}</div><div class="url">${esc(r.url)}</div>
<div class="note">Rendered on 2026-10-11 from the response saved at ${esc(retrievedAt)} (file 04_pipeline/work/web_sources/${esc(r.archive)}). The live page could not be reached from the rendering environment, so this image shows the archived content, not a browser screenshot.</div></div>`;
const css = `body{margin:0;background:#fff;font:14px/1.5 "DejaVu Sans",Arial,sans-serif;color:#14181c}.pg{width:1100px;padding:28px 32px}
.hd{border:1px solid #c9ced2;background:#f4f6f7;padding:12px 14px;margin-bottom:18px}.tag{font:600 12px monospace;letter-spacing:.05em;color:#4b5359}
.cit{font-weight:600;margin-top:4px}.url{font:12px monospace;color:#2a5ea8;word-break:break-all;margin-top:2px}.note{font-size:12px;color:#4b5359;margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:12.5px}th,td{border:1px solid #d6dadd;padding:4px 6px;text-align:right}th{background:#eef1f2;font-weight:600}td:first-child,th:first-child{text-align:left}
pre{white-space:pre-wrap;font:13px/1.55 "DejaVu Serif",Georgia,serif;margin:0}mark{background:#fff1a8}h3{margin:16px 0 8px;font-size:14px}`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1164, height: 800 } });
  const shot = async (html, name) => { await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}</style><div class="pg">${html}</div>`); await p.screenshot({ path: path.join(out, name), fullPage: true }); console.log(name); };
  // R10 WASTA
  { const r = refs.R10, d = JSON.parse(fs.readFileSync(path.join(W, r.archive), 'utf8'));
    const keys = ['name','location','hydropowerplanttype_fr','hydropowerplantoperationalstatus_fr','beginningofoperation','fallheight','performanceturbinemaximum','performancegeneratormaximum','productionexpected','pumpspowerinputmaximum','enginepowerdemand','dateofstatistic'];
    const rows = d.data.features.map(f => `<tr><td>${f.featureId}</td>${keys.map(k => `<td>${esc(f.attributes[k] ?? '')}</td>`).join('')}</tr>`).join('');
    await shot(head('R10', r, 'web01', d.retrieved) + `<div style="font:12px monospace;margin-bottom:8px">Query: ${esc(d.query)}</div><table><tr><th>featureId</th>${keys.map(k => `<th>${k}</th>`).join('')}</tr>${rows}</table>
      <p style="font-size:12px;color:#4b5359">Units as served: performance… in MW, productionexpected and enginepowerdemand in GWh/yr. Features 502800 (Turtmann) and 503000 (Chippis-Rhône) are not FMG plants.</p>`, `R10_${r.token}_${r.year}_web01.png`); }
  // R11 MQN
  { const r = refs.R11, d = JSON.parse(fs.readFileSync(path.join(W, r.archive), 'utf8')); const mon = ['jan','feb','mar','apr','mai','jun','jul','aug','sep','okt','nov','dez'];
    const rows = Object.entries(d.sites).map(([k, s]) => { const h = (s.hits || [])[0] || {}; return `<tr><td>${esc(k)}</td><td>${h.id ?? ''}</td><td>${s.lv95.join(', ')}</td><td>${h.mqn_jahr != null ? (+h.mqn_jahr).toFixed(2) : ''}</td>${mon.map(m => `<td>${h['mqn_' + m] != null ? (+h['mqn_' + m]).toFixed(2) : ''}</td>`).join('')}<td>${esc(h.regimetyp ?? '')}</td></tr>`; }).join('');
    await shot(head('R11', r, 'web01', d.meta.retrieved) + `<div style="font:12px monospace;margin-bottom:8px">API: ${esc(d.meta.api)} · layer ${esc(d.meta.layer)} · units ${esc(d.meta.units)}</div>
      <table><tr><th>site (project label)</th><th>segment id</th><th>LV95</th><th>MQN year</th>${mon.map(m => `<th>${m}</th>`).join('')}<th>regime</th></tr>${rows}</table>`, `R11_${r.token}_${r.year}_web01.png`); }
  // R12 BGE
  { const r = refs.R12, t = fs.readFileSync(path.join(W, r.archive), 'utf8'); const lines = t.split('\n'); const ret = (t.match(/RETRIEVED: (.*)/) || [])[1];
    const grab = (start, end) => lines.filter(l => l.trim()).slice(start, end);
    const iA = lines.findIndex(l => l.startsWith('A. Par concession')); const i753 = lines.findIndex(l => l.startsWith('7.5.3'));
    const hi = s => esc(s).replace(/(un volume d'environ 20 millions de mètres cubes d'eau[^.]*\.)/, '<mark>$1</mark>').replace(/(les eaux déversées ne font pas partie des débits utilisables[^.]*\.)/, '<mark>$1</mark>');
    const blockA = lines.slice(iA, iA + 12).filter(l => l.trim()).slice(0, 4).join('\n\n');
    await shot(head('R12', r, 'web01 · faits A–B', ret) + `<h3>ATF 150 II 83 — Faits</h3><pre>${hi(blockA)}</pre>`, `R12_${r.token}_${r.year}_web01.png`);
    const block7 = lines.slice(i753, i753 + 4).filter(l => l.trim()).join('\n\n');
    await shot(head('R12', r, 'web02 · consid. 7.5.3', ret) + `<h3>ATF 150 II 83 — Considérant 7.5.3</h3><pre>${hi(block7)}</pre>`, `R12_${r.token}_${r.year}_web02.png`); }
  await b.close();
})();
