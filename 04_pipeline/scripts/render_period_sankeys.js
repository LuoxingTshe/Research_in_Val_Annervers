// Render period_models.json into standalone, editable SVGs (explicit colours, named layers, live text).
// Usage: node render_period_sankeys.js period_models.json outdir
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const models = JSON.parse(fs.readFileSync(process.argv[2] || 'period_models.json', 'utf8'));
const out = process.argv[3] || 'svg'; fs.mkdirSync(out, { recursive: true });
const NM = path.join(__dirname, 'node_modules');
const font = (fam, pkg, file, w) => `@font-face{font-family:"${fam}";font-weight:${w};src:url(data:font/woff2;base64,${fs.readFileSync(`${NM}/@fontsource/${pkg}/files/${file}`).toString('base64')}) format("woff2")}`;
const fontCss = [font('Source Sans 3','source-sans-3','source-sans-3-latin-400-normal.woff2',400), font('Source Sans 3','source-sans-3','source-sans-3-latin-600-normal.woff2',600),
  font('IBM Plex Mono','ibm-plex-mono','ibm-plex-mono-latin-400-normal.woff2',400), font('IBM Plex Mono','ibm-plex-mono','ibm-plex-mono-latin-500-normal.woff2',500),
  font('Source Serif 4','source-serif-4','source-serif-4-latin-700-normal.woff2',700)].join('\n');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1200 } });
  await p.setContent(`<!doctype html><meta charset="utf-8"><style>${fontCss}</style><body></body>`);
  await p.addScriptTag({ path: `${NM}/d3/dist/d3.min.js` });
  await p.addScriptTag({ path: `${NM}/d3-sankey/dist/d3-sankey.min.js` });
  await p.evaluate(() => document.fonts.ready);
  for (const key of Object.keys(models)) {
    const svgText = await p.evaluate((M) => {
      const NS = 'http://www.w3.org/2000/svg';
      const F = { sans: '"Source Sans 3", "Helvetica Neue", Arial, sans-serif', mono: '"IBM Plex Mono", Menlo, Consolas, monospace', serif: '"Source Serif 4", Georgia, serif' };
      const C = { bg:'#ffffff', ink:'#14181c', ink2:'#4b5359', ink3:'#7c858c', rule:'#dfe3e5', power:'#2a78d6', eco:'#1baf7a', use:'#eda100', grey:'#9aa3a9' };
      const kindColor = k => ({power:C.power, pump:C.power, eco:C.eco, use:C.use, river:C.grey, spill:C.grey, mixed:C.grey}[k] || C.grey);
      const nodeColor = k => ({plant:C.power, pump:C.power, eco:C.eco, use:C.use, river:'#7c858c', spill:'#7c858c', mixed:'#7c858c', junction:'#7c858c'}[k] || C.ink2);
      const mk = (tag, a = {}, txt) => { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); if (txt != null) e.textContent = txt; return e; };
      const T = (x, y, s, o = {}) => mk('text', { x, y, 'font-family': o.f || F.sans, 'font-size': o.size || 12, 'font-weight': o.w || 400, fill: o.fill || C.ink2, ...(o.anchor ? { 'text-anchor': o.anchor } : {}), ...(o.ls ? { 'letter-spacing': o.ls } : {}) }, s);
      const fmt = (x, d) => x.toLocaleString('en-GB', { minimumFractionDigits: d, maximumFractionDigits: d });
      const PAD = 44, TOP = 178, SW = 1120, SH = {pre1958:560, post1958:660, post2039:780}[M.key];
      const ncol = M.columns.length, colX = d3.range(ncol).map(i => i * (SW - 10) / (ncol - 1) * (ncol === 6 ? 0.93 : 0.86));
      const hasShares = !!M.shares;
      const W = PAD * 2 + SW + 200;
      const notesY = TOP + SH + 40;
      const H = notesY + M.notes.length * 34 + (hasShares ? 120 : 0) + 60;
      const svg = mk('svg', { xmlns: NS, width: W, height: H, viewBox: `0 0 ${W} ${H}` });
      svg.append(mk('rect', { id: 'background', width: W, height: H, fill: C.bg }));
      const defs = mk('defs'); svg.append(defs);
      ['power','eco','use','grey'].forEach(k => {
        const col = k === 'grey' ? C.grey : C[k];
        const pt = mk('pattern', { id: 'hatch-' + k, patternUnits: 'userSpaceOnUse', width: 6, height: 6, patternTransform: 'rotate(45)' });
        pt.append(mk('rect', { width: 6, height: 6, fill: col, 'fill-opacity': 0.18 }), mk('rect', { width: 2, height: 6, fill: col, 'fill-opacity': 0.75 }));
        defs.append(pt);
      });
      const hatchOf = k => 'url(#hatch-' + ({power:'power',pump:'power',eco:'eco',use:'use'}[k] || 'grey') + ')';
      // title
      const g0 = mk('g', { id: 'title' });
      g0.append(T(PAD, 30, 'GOUGRA / NAVIZENCE WATER SYSTEM · ANNUAL WATER BALANCE, hm³/yr', { f: F.mono, size: 11.5, fill: C.ink3, ls: '0.06em' }));
      g0.append(T(PAD, 66, M.title, { f: F.serif, size: 32, w: 700, fill: C.ink }));
      g0.append(T(PAD, 92, M.subtitle, { size: 15, fill: C.ink2 }));
      svg.append(g0);
      // legend
      const lg = mk('g', { id: 'legend' }); let lx = PAD;
      const items = [['Turbined / generation path', C.power, null], ['Statutory residual flow', C.eco, null], ['Irrigation & snowmaking', C.use, null], ['River, spill or not captured', C.grey, null], ['Hatched: estimate, ceiling or not documented (small ones drawn at 4 hm³)', null, 'url(#hatch-grey)']];
      items.forEach(([t, c, pat]) => { lg.append(mk('rect', { x: lx, y: 110, width: 18, height: 10, rx: 2, fill: pat || c, stroke: pat ? C.ink3 : 'none', 'stroke-width': pat ? 0.75 : 0 })); lg.append(T(lx + 24, 119, t, { size: 12.5 })); lx += 24 + t.length * 6.15 + 22; });
      svg.append(lg);
      // sankey
      const graph = { nodes: M.nodes.map(d => ({ ...d })), links: M.links.map(d => ({ ...d, value: d.display, real: d.value })) };
      const sk = d3.sankey().nodeId(d => d.id).nodeWidth(10).nodePadding(M.key === 'pre1958' ? 34 : 26).nodeAlign(d => d.col).nodeSort(null).extent([[0, 0], [SW, SH]]).iterations(48);
      sk(graph);
      graph.nodes.forEach(n => { const w = n.x1 - n.x0; n.x0 = colX[n.col]; n.x1 = n.x0 + w; });
      // pinned nodes: place directly below (or above) a reference node
      graph.nodes.filter(n => n.pin).forEach(n => { const ref = graph.nodes.find(m => m.id === n.pin[0]); const h = n.y1 - n.y0;
        if (n.pin[1] === 'below') { n.y0 = ref.y1 + n.pin[2]; } else { n.y0 = ref.y0 - n.pin[2] - h; } n.y1 = n.y0 + h; });
      sk.update(graph);
      const real = {}; M.links.forEach(l => { [l.source, l.target].forEach(n => real[n] = real[n] || { i: 0, o: 0 }); real[l.source].o += l.value; real[l.target].i += l.value; });
      const body = mk('g', { id: 'sankey', transform: `translate(${PAD},${TOP})` });
      const heads = mk('g', { id: 'column-heads' });
      M.columns.forEach((c, i) => heads.append(T(colX[i], -28, c.toUpperCase(), { f: F.mono, size: 10.5, fill: C.ink3, ls: '0.06em' })));
      const links = mk('g', { id: 'links', fill: 'none' });
      graph.links.forEach(l => {
        const pth = mk('path', { id: `link_${l.source.id}_to_${l.target.id}`, d: d3.sankeyLinkHorizontal()(l), fill: 'none',
          stroke: l.uncertain ? hatchOf(l.kind) : kindColor(l.kind), 'stroke-opacity': l.uncertain ? 1 : 0.42, 'stroke-width': Math.max(1.5, l.width).toFixed(2) });
        pth.append(mk('title', {}, `${l.source.name} → ${l.target.name}: ${fmt(l.real, l.real < 1 ? 2 : 1)} hm³/yr${l.uncertain ? ' (estimate / ceiling)' : ''}`));
        links.append(pth);
      });
      const nodes = mk('g', { id: 'nodes' });
      graph.nodes.forEach(n => nodes.append(mk('rect', { id: 'node_' + n.id, x: n.x0.toFixed(2), y: n.y0.toFixed(2), width: (n.x1 - n.x0).toFixed(2), height: Math.max(2, n.y1 - n.y0).toFixed(2), rx: 1.5, fill: nodeColor(n.kind) })));
      const labels = mk('g', { id: 'labels' });
      graph.nodes.forEach(n => {
        const x = n.x1 + 8, y = (n.y0 + n.y1) / 2, v = Math.max(real[n.id].i, real[n.id].o);
        const lines = [[n.name, { size: 13.5, w: 600, fill: C.ink }]];
        const unc = M.links.some(l => (l.target === n.id || l.source === n.id) && l.uncertain) && ['use','mixed'].includes(n.kind);
        lines.push([(n.sub ? n.sub + ' · ' : '') + (unc ? '≤ ' : '') + fmt(v, v < 2 ? 2 : 1) + ' hm³', { size: 11.5, fill: C.ink3 }]);
        if (n.energy) lines.push([n.energy, { f: F.mono, size: 11.5, w: 500, fill: C.ink }]);
        if (n.ref) lines.push(['[' + n.ref + ']', { f: F.mono, size: 10, fill: C.ink3 }]);
        const lh = 14.5, y0 = y - (lines.length - 1) * lh / 2 + 4;
        const g = mk('g', { id: 'label_' + n.id });
        lines.forEach(([s, o], i) => g.append(T(x.toFixed(1), (y0 + i * lh).toFixed(1), s, o)));
        labels.append(g);
      });
      const halos = mk('g', { id: 'label-halos (delete if not needed)' });
      labels.querySelectorAll('text').forEach(t => { const h = t.cloneNode(true); h.setAttribute('fill', C.bg); h.setAttribute('stroke', C.bg); h.setAttribute('stroke-width', '4'); h.setAttribute('stroke-linejoin', 'round'); halos.append(h); });
      body.append(heads, links, nodes, halos, labels); svg.append(body);
      // shares panel
      let y = notesY;
      if (hasShares) {
        const sp = mk('g', { id: 'grantor-shares' });
        sp.append(T(PAD, y, 'Upper-stage hydraulic power by grantor after the return (estimate, fixed at expiry) [R08 p3]', { size: 13, w: 600, fill: C.ink }));
        const bw = SW + 150, by = y + 14, bh = 18; let bx = PAD; const unl = [];
        const ramp = ['#0d366b','#184f95','#256abf','#3987e5','#6da7ec','#9ec5f4','#cde2fb'];
        M.shares.forEach(([nm, s], i) => {
          const w = bw * s / 100;
          sp.append(mk('rect', { id: 'share_' + nm.replace(/\W+/g, '_'), x: bx.toFixed(1), y: by, width: Math.max(1, w - 2).toFixed(1), height: bh, fill: ramp[i] }));
          const lab = `${nm} ${fmt(s, 1)} %`;
          const fits = w > lab.length * 6.6 + 8; if (fits) sp.append(T((bx + 6).toFixed(1), by + 13, lab, { size: 11.5, fill: i < 4 ? '#ffffff' : C.ink }));
          else unl.push(lab);
          bx += w;
        });
        const small = unl.join(' · ');
        sp.append(T(PAD, by + bh + 18, 'Unlabelled segments, left to right: ' + small + '. Canton may raise its stake to 31.7 % via its purchase right (art. 59b LcFH) [R08 p8].', { size: 12, fill: C.ink2 }));
        svg.append(sp); y += 84;
      }
      const ft = mk('g', { id: 'notes' });
      M.notes.forEach((s, i) => {
        // wrap at ~175 chars
        const words = s.split(' '); let line = '', li = 0, out = [];
        words.forEach(w => { if ((line + ' ' + w).length > 172) { out.push(line); line = w; } else line = line ? line + ' ' + w : w; }); out.push(line);
        out.forEach((ln, j) => ft.append(T(PAD + (j ? 12 : 0), y + j * 16, (j ? '' : '• ') + ln, { size: 12, fill: C.ink2 })));
        y += out.length * 16 + 6;
      });
      ft.append(T(PAD, y + 12, 'Reference IDs [R##] are listed with page locators in EVIDENCE.md. Band widths are annual volumes; stage volumes are reused water and cannot be summed.', { size: 11.5, fill: C.ink3 }));
      svg.append(ft);
      svg.setAttribute('height', y + 40); svg.setAttribute('viewBox', `0 0 ${W} ${y + 40}`); svg.querySelector('#background').setAttribute('height', y + 40);
      return svg.outerHTML;
    }, models[key]);
    const name = { pre1958: 'gougra_sankey_1_before-1958', post1958: 'gougra_sankey_2_after-1958', post2039: 'gougra_sankey_3_after-2039-return' }[key];
    fs.writeFileSync(path.join(out, name + '.svg'), '<?xml version="1.0" encoding="UTF-8"?>\n' + svgText);
    const q = await b.newPage(); const m = svgText.match(/width="([\d.]+)" height="([\d.]+)"/);
    await q.setViewportSize({ width: Math.ceil(+m[1]), height: Math.ceil(+m[2]) });
    await q.setContent(`<!doctype html><meta charset="utf-8"><style>${fontCss} body{margin:0}</style>${svgText}`); await q.evaluate(() => document.fonts.ready);
    await q.screenshot({ path: path.join(out, '_' + name + '_preview.png') }); await q.close();
    console.log('wrote', name);
  }
  await b.close();
})();
