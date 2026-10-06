const { chromium } = require('playwright');
const fs = require('fs');
const fontCss = (() => {
  const f = (fam, pkg, file, w) => `@font-face{font-family:"${fam}";font-weight:${w};src:url(data:font/woff2;base64,${fs.readFileSync(`node_modules/@fontsource/${pkg}/files/${file}`).toString('base64')}) format("woff2")}`;
  return [f('Source Sans 3','source-sans-3','source-sans-3-latin-400-normal.woff2',400), f('Source Sans 3','source-sans-3','source-sans-3-latin-600-normal.woff2',600),
          f('IBM Plex Mono','ibm-plex-mono','ibm-plex-mono-latin-400-normal.woff2',400), f('IBM Plex Mono','ibm-plex-mono','ibm-plex-mono-latin-500-normal.woff2',500),
          f('Source Serif 4','source-serif-4','source-serif-4-latin-600-normal.woff2',600), f('Source Serif 4','source-serif-4','source-serif-4-latin-700-normal.woff2',700)].join('\n');
})();
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1000 }, colorScheme: 'light' });
  await p.route('**/d3.min.js', r => r.fulfill({ path: 'node_modules/d3/dist/d3.min.js', contentType: 'text/javascript' }));
  await p.route('**/d3-sankey.min.js', r => r.fulfill({ path: 'node_modules/d3-sankey/dist/d3-sankey.min.js', contentType: 'text/javascript' }));
  await p.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: fontCss, contentType: 'text/css' }));
  const html = fs.readFileSync('out/index.html', 'utf8');
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>' + html + '</body></html>', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);

  const out = await p.evaluate(() => {
    const FONT = { 'Source Sans 3': '"Source Sans 3", "Helvetica Neue", Arial, sans-serif', 'IBM Plex Mono': '"IBM Plex Mono", Menlo, Consolas, monospace', 'Source Serif 4': '"Source Serif 4", Georgia, serif' };
    const famOf = cs => { const f = cs.fontFamily; for (const k in FONT) if (f.includes(k)) return FONT[k]; return f; };
    const css = getComputedStyle(document.documentElement);
    const BG = '#ffffff';
    function inline(src) {
      const clone = src.cloneNode(true);
      const so = [src, ...src.querySelectorAll('*')], co = [clone, ...clone.querySelectorAll('*')];
      so.forEach((el, i) => {
        const c = co[i], cs = getComputedStyle(el), tag = el.tagName.toLowerCase();
        if (['path','rect','line','text'].includes(tag)) {
          const fill = cs.fill; c.setAttribute('fill', fill.startsWith('url') ? fill.replace(/"/g, '') : fill);
          if (cs.fillOpacity !== '1') c.setAttribute('fill-opacity', cs.fillOpacity);
          const st = cs.stroke; c.setAttribute('stroke', st.startsWith('url') ? st.replace(/"/g, '') : st);
          if (st !== 'none') { c.setAttribute('stroke-width', cs.strokeWidth); if (cs.strokeOpacity !== '1') c.setAttribute('stroke-opacity', cs.strokeOpacity); }
        }
        if (tag === 'text') {
          c.setAttribute('font-family', famOf(cs)); c.setAttribute('font-size', cs.fontSize); c.setAttribute('font-weight', cs.fontWeight);
          if (cs.letterSpacing !== 'normal') c.setAttribute('letter-spacing', cs.letterSpacing);
          if (cs.textTransform === 'uppercase') c.textContent = c.textContent.toUpperCase();
          c.removeAttribute('paint-order'); c.setAttribute('stroke', 'none'); c.removeAttribute('stroke-width');
        }
        if (tag === 'rect' && el.closest('pattern')) { c.setAttribute('fill', cs.fill); }
        c.removeAttribute('class'); c.removeAttribute('tabindex'); c.removeAttribute('style');
      });
      return clone;
    }
    const NS = 'http://www.w3.org/2000/svg';
    const mk = (tag, attrs = {}, text) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (text != null) e.textContent = text; return e; };
    const ink = css.getPropertyValue('--ink').trim(), ink2 = css.getPropertyValue('--ink-2').trim(), ink3 = css.getPropertyValue('--ink-3').trim();
    const col = n => css.getPropertyValue(n).trim();
    const T = (x, y, s, opt = {}) => mk('text', { x, y, 'font-family': opt.f || FONT['Source Sans 3'], 'font-size': opt.size || 13, 'font-weight': opt.w || 400, fill: opt.fill || ink2, ...(opt.anchor ? { 'text-anchor': opt.anchor } : {}) }, s);

    // ---------- Sankey ----------
    const src = document.getElementById('sankey');
    const cl = inline(src);
    const vb = src.viewBox.baseVal; const PAD = 40, TOP = 118, W = vb.width + PAD * 2, H = vb.height + TOP + 118;
    const svg = mk('svg', { xmlns: NS, 'xmlns:xlink': 'http://www.w3.org/1999/xlink', width: W, height: H, viewBox: `0 0 ${W} ${H}` });
    svg.appendChild(mk('rect', { id: 'background', x: 0, y: 0, width: W, height: H, fill: BG }));
    const defs = cl.querySelector('defs'); svg.appendChild(defs);
    const head = mk('g', { id: 'title' });
    head.append(T(PAD, 46, 'Gougra Cascade Water Balance', { f: FONT['Source Serif 4'], size: 30, w: 700, fill: ink }));
    head.append(T(PAD, 72, 'Mean-year water routing (hm³/yr = million m³): 2016–2025 mean inflow, plant volumes calibrated to BFE WASTA · Val d’Anniviers · v2, 6 Oct 2026', { size: 14 }));
    svg.appendChild(head);
    const leg = mk('g', { id: 'legend' }); let lx = PAD;
    [['Generation path', col('--power'), null], ['Statutory residual flow', col('--eco'), null], ['Irrigation & snowmaking', col('--use'), null], ['Spilled or not captured', col('--spill'), null], ['Hatched: estimate or calibration term (min. 4 hm³ drawn)', null, 'url(#h-spill)']].forEach(([t, c, pat]) => {
      leg.append(mk('rect', { x: lx, y: 92, width: 18, height: 10, rx: 2, fill: pat || c, stroke: pat ? ink3 : 'none', 'stroke-width': pat ? 0.75 : 0 }));
      const tt = T(lx + 24, 101, t, { size: 13 }); leg.append(tt); lx += 24 + t.length * 6.6 + 26;
    });
    svg.appendChild(leg);
    const body = mk('g', { id: 'sankey', transform: `translate(${PAD},${TOP})` });
    const groups = [...cl.children].filter(e => e.tagName.toLowerCase() !== 'defs');
    // groups: links g, nodes g, label g (per-node g of texts), loose texts
    const links = groups[0]; links.setAttribute('id', 'links');
    const nodes = groups[1]; nodes.setAttribute('id', 'nodes');
    const labels = mk('g', { id: 'labels' });
    const halos = mk('g', { id: 'label-halos (delete if not needed)' });
    groups.slice(2).forEach(g => { (g.tagName.toLowerCase() === 'text' ? [g] : [...g.querySelectorAll('text')]).forEach(t => labels.appendChild(t)); });
    [...labels.children].forEach(t => { const h = t.cloneNode(true); h.setAttribute('fill', BG); h.setAttribute('stroke', BG); h.setAttribute('stroke-width', '4'); h.setAttribute('stroke-linejoin', 'round'); halos.appendChild(h); });
    // name links/nodes from bound data
    const srcLinks = src.querySelectorAll('path.link'); [...links.children].forEach((pth, i) => { const d = d3.select(srcLinks[i]).datum(); pth.setAttribute('id', `link_${d.source.id}_to_${d.target.id}`); });
    const srcNodes = src.querySelectorAll('rect.node'); [...nodes.children].forEach((r, i) => { const d = d3.select(srcNodes[i]).datum(); r.setAttribute('id', `node_${d.id}`); });
    body.append(links, nodes, halos, labels); svg.appendChild(body);
    const foot = mk('g', { id: 'footnote' }); const fy = TOP + vb.height + 34;
    ['Plant volumes = BFE WASTA expected generation ÷ FMG leaflet energy coefficient; WASTA expected generation per plant shown at each stage (653.9 GWh/yr in total).',
     'Grey bands balance the inflow against those volumes: surplus above Mottec assumed to spill and be recaptured at Vissoie; Vissoie spill due to the ≈10.8 m³/s tunnel (≈20 hm³ in 2001, BGE 150 II 83).',
     'Residual flows annualised and deducted in full (upper bound); irrigation at allocation ceilings; pumping ≈ 15 hm³ = 30.2 GWh at the storage pump. Stage volumes are reused water and cannot be summed.',
     'Sources: BFE WASTA 31.12.2025; BAFU MQN; FMG leaflet 2014 and Rapport de gestion 2025; BGE 150 II 83; VS message Convention 2022; Savoy 2025 WP6; Alpiq 2025.']
      .forEach((s, i) => foot.append(T(PAD, fy + i * 19, s, { size: 12, fill: i === 3 ? ink3 : ink2 })));
    svg.appendChild(foot);

    // ---------- small charts ----------
    function small(id, title, unit, legendItems) {
      const s = document.getElementById(id); const c = inline(s); const v = s.viewBox.baseVal;
      const P = 24, TT = 70, w = v.width + P * 2, h = v.height + TT + 20;
      const o = mk('svg', { xmlns: NS, width: w, height: h, viewBox: `0 0 ${w} ${h}` });
      o.append(mk('rect', { id: 'background', width: w, height: h, fill: BG }));
      const hd = mk('g', { id: 'title' }); hd.append(T(P, 30, title, { size: 15, w: 600, fill: ink }), T(P + title.length * 7.6 + 8, 30, unit, { size: 12, fill: ink3 })); o.append(hd);
      const lg = mk('g', { id: 'legend' }); let x = P; legendItems.forEach(([t, cc]) => { lg.append(mk('rect', { x, y: 44, width: 16, height: 9, rx: 2, fill: cc }), T(x + 22, 53, t, { size: 12 })); x += 22 + t.length * 6.2 + 22; }); o.append(lg);
      const g = mk('g', { id: 'chart', transform: `translate(${P},${TT})` }); [...c.childNodes].forEach(n => g.appendChild(n)); o.append(g);
      return o.outerHTML;
    }
    return {
      sankey: svg.outerHTML, W, H,
      price: small('priceChart', '2025 Swiss day-ahead price, monthly mean', 'CHF/MWh · euenergy.live (ENTSO-E)', [['Winter Oct–Mar', col('--winter')], ['Summer Apr–Sep', col('--summer')]]),
      strat: small('stratChart', 'Revenue per m³ of water, net of pumping', 'CHF/m³ · 2025 seasonal mean prices', [['Generate directly in summer', col('--summer')], ['Store in Moiry, generate in winter', col('--winter')]]),
    };
  });
  const decl = '<?xml version="1.0" encoding="UTF-8"?>\n';
  fs.mkdirSync('vector', { recursive: true });
  fs.writeFileSync('vector/gougra_cascade_sankey.svg', decl + out.sankey);
  fs.writeFileSync('vector/gougra_price_2025.svg', decl + out.price);
  fs.writeFileSync('vector/gougra_storage_value.svg', decl + out.strat);
  // PDFs (vector, fonts embedded)
  for (const [name, svgText] of [['gougra_cascade_sankey', out.sankey], ['gougra_price_2025', out.price], ['gougra_storage_value', out.strat]]) {
    const q = await b.newPage();
    const m = svgText.match(/width="([\d.]+)" height="([\d.]+)"/);
    await q.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${fontCss} @page{size:${m[1]}px ${m[2]}px;margin:0} html,body{margin:0}</style></head><body>${svgText}</body></html>`, { waitUntil: 'networkidle' });
    await q.evaluate(() => document.fonts.ready);
    await q.pdf({ path: `vector/${name}.pdf`, width: m[1] + 'px', height: m[2] + 'px', printBackground: true, pageRanges: '1' });
    await q.setViewportSize({ width: Math.ceil(+m[1]), height: Math.ceil(+m[2]) });
    await q.screenshot({ path: `vector/_${name}_preview.png` });
    await q.close();
  }
  await b.close();
  console.log('done', out.W, out.H);
})();
