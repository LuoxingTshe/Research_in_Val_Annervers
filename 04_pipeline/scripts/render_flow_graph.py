"""Render a node–edge flow graph spec (JSON) to a standalone editable SVG.
Usage: python3 render_flow_graph.py spec.json out.svg"""
import json, math, sys
from xml.sax.saxutils import escape as esc
spec = json.load(open(sys.argv[1], encoding="utf-8")); OUT = sys.argv[2]
C = dict(bg="#ffffff", ink="#14181c", ink2="#4b5359", ink3="#7c858c", rule="#dfe3e5", power="#2a78d6", eco="#1baf7a", use="#eda100", grey="#9aa3a9", rhone="#8fb3d9")
KC = dict(power=C["power"], pump=C["power"], eco=C["eco"], use=C["use"], spill=C["grey"], river=C["grey"], mixed=C["grey"])
F = dict(sans='"Source Sans 3", "Helvetica Neue", Arial, sans-serif', mono='"IBM Plex Mono", Menlo, Consolas, monospace', serif='"Source Serif 4", Georgia, serif')
TOP = 190                     # y offset of the graph area
W = spec["width"]; GH = spec["height"]
nodes = {n["id"]: n for n in spec["nodes"]}
def width(v): return 1.3 + 0.045 * v
def txt(x, y, s, size=12, w=400, fill=None, f="sans", anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family=\'{F[f]}\' font-size="{size}" font-weight="{w}" fill="{fill or C["ink2"]}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'
def fmt(v):
    return f"{v:,.2f}" if v < 1 else f"{v:,.1f}"
# ---------- node geometry ----------
R = dict(source=11, reservoir=22, plant=17, plant_other=17, eco=10, river=10, junction=7, use=8, spill=9, rhone=0)
def port(n, side):            # anchor x on node edge
    if n["type"] == "rhone": return n["x"] - 9
    return n["x"] + (R[n["type"]] if side == "out" else -R[n["type"]])
# distribute ports along the node side so edges don't all meet at one point
outs, ins = {}, {}
for i, e in enumerate(spec["edges"]):
    if e["route"] == "pump": continue
    outs.setdefault(e["source"], []).append(i); ins.setdefault(e["target"], []).append(i)
off_out, off_in = {}, {}
for d, side, key in ((outs, off_out, "target"), (ins, off_in, "source")):
    for nid, lst in d.items():
        lst.sort(key=lambda i: nodes[spec["edges"][i][key]]["y"])
        tot = sum(width(spec["edges"][i]["value"]) for i in lst) + 3 * (len(lst) - 1)
        y = -tot / 2
        for i in lst:
            w = width(spec["edges"][i]["value"]); side[i] = y + w / 2; y += w + 3
def bez(p0, p1, p2, p3, t):
    return tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t**2*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))
svg = []; halo = []; lab = []
defs = []
def arrowhead(tip, d, w, col, op):
    """Plain filled triangle (no SVG marker) so Illustrator imports it as a normal path."""
    L = max(10.0, 0.8 * w + 7); hw = max(5.0, 0.5 * w + 3.5)
    ux, uy = d; bx, by = tip[0] - ux * L, tip[1] - uy * L; px, py = -uy, ux
    pts = [tip, (bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw)]
    return '<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f' Z" fill="{col}" fill-opacity="{op}"/>', (bx + ux * 1.0, by + uy * 1.0)
def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1; return dx / n, dy / n
# ---------- edges ----------
eg = []
for i, e in enumerate(spec["edges"]):
    s, t = nodes[e["source"]], nodes[e["target"]]
    w = width(e["value"]); col = KC[e["kind"]]
    if e["route"] == "pump":   # backward loop: from source top, arcing up and left into the reservoir's underside
        p0 = (s["x"], s["y"] - R[s["type"]] - 2); p3 = (t["x"] + 8, t["y"] + R[t["type"]] + 10)
        p1 = (p0[0] - 10, p0[1] - 160); p2 = (p3[0] + 140, p3[1] + 150)
    else:
        p0 = (port(s, "out"), s["y"] + off_out[i]); p3 = (port(t, "in") - 6, t["y"] + off_in[i])
        dx = max(60, (p3[0] - p0[0]) * 0.5); p1 = (p0[0] + dx, p0[1]); p2 = (p3[0] - dx, p3[1])
    dash = ' stroke-dasharray="7 4"' if e["uncertain"] else ""
    op = 0.55 if e["kind"] in ("power",) else 0.75
    tip = p3; dirv = unit(p2, p3)
    head, base = arrowhead(tip, dirv, w, col, min(1.0, op + 0.25))
    # stop the line at the arrow base so a thick stroke does not cover the head
    p2b = (p2[0] + (base[0] - p3[0]), p2[1] + (base[1] - p3[1]))
    d = f"M{p0[0]:.1f},{p0[1]:.1f} C{p1[0]:.1f},{p1[1]:.1f} {p2b[0]:.1f},{p2b[1]:.1f} {base[0]:.1f},{base[1]:.1f}"
    eid = f'edge_{e["source"]}_to_{e["target"]}' + ("_" + e["kind"] if e["kind"] in ("spill",) and e["source"] == "s_mottec" else "")
    eg.append(f'<g id="{eid}"><title>{esc(s["title"])} → {esc(t["title"])}: {fmt(e["value"])} hm³/yr</title><path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{w:.2f}" stroke-linecap="butt"{dash}/>{head}</g>')
    lx, ly = bez(p0, p1, p2, p3, e["lp"]); ly += e.get("dy", 0)
    pre = "≈ " if e["uncertain"] and e["kind"] in ("spill", "pump", "river") else ("≤ " if e["uncertain"] else "")
    g = [txt(lx, ly - 3, pre + fmt(e["value"]), 12, 500, C["ink"], "mono", "middle")]
    if e.get("note"): g.append(txt(lx, ly + 10, e["note"], 10.5, 400, C["ink3"], "sans", "middle"))
    lab.append(f'<g id="label_{eid}">' + "".join(g) + "</g>")
# ---------- nodes ----------
ng = []
for n in spec["nodes"]:
    x, y, tp = n["x"], n["y"], n["type"]
    if tp == "source":
        ng.append(f'<circle id="node_{n["id"]}" cx="{x}" cy="{y}" r="11" fill="#ffffff" stroke="{C["ink2"]}" stroke-width="2"/><circle cx="{x}" cy="{y}" r="3.5" fill="{C["ink2"]}"/>')
    elif tp == "reservoir":
        ng.append(f'<path id="node_{n["id"]}" d="M{x-26},{y-20} L{x+26},{y-20} L{x+18},{y+22} L{x-18},{y+22} Z" fill="{C["ink2"]}"/><path d="M{x-21},{y-8} L{x+21},{y-8}" stroke="#9ec5f4" stroke-width="2"/>')
    elif tp == "plant":
        stage = n.get("badge") or {"mottec":"1","vissoie":"2","navizence":"3"}.get(n["id"], "")
        ng.append(f'<rect id="node_{n["id"]}" x="{x-17}" y="{y-17}" width="34" height="34" rx="5" fill="{C["power"]}"/>' + txt(x, y + 5, stage, 15, 600, "#ffffff", "sans", "middle"))
    elif tp == "plant_other":
        ng.append(f'<rect id="node_{n["id"]}" x="{x-17}" y="{y-17}" width="34" height="34" rx="5" fill="#ffffff" stroke="{C["grey"]}" stroke-width="2.5" stroke-dasharray="4 2"/>' + txt(x, y + 5, n.get("badge", ""), 15, 600, C["ink3"], "sans", "middle"))
    elif tp == "river":
        ng.append(f'<path id="node_{n["id"]}" d="M{x},{y-11} L{x+11},{y} L{x},{y+11} L{x-11},{y} Z" fill="{C["grey"]}"/>')
    elif tp == "junction":
        ng.append(f'<circle id="node_{n["id"]}" cx="{x}" cy="{y}" r="7" fill="{C["ink2"]}"/>')
    elif tp == "eco":
        ng.append(f'<path id="node_{n["id"]}" d="M{x},{y-11} L{x+11},{y} L{x},{y+11} L{x-11},{y} Z" fill="{C["eco"]}"/>')
    elif tp == "use":
        ng.append(f'<circle id="node_{n["id"]}" cx="{x}" cy="{y}" r="8" fill="{C["use"]}"/>')
    elif tp == "spill":
        ng.append(f'<circle id="node_{n["id"]}" cx="{x}" cy="{y}" r="9" fill="#ffffff" stroke="{C["grey"]}" stroke-width="2.5" stroke-dasharray="3 2"/>')
    elif tp == "rhone":
        ng.append(f'<path id="node_{n["id"]}" d="M{x-9},{y} L{x+9},{y}" stroke="{C["ink2"]}" stroke-width="2"/>')
    if tp == "rhone":
        tin = sum(e["value"] for e in spec["edges"] if e["target"] == n["id"])
        lab.append(f'<g id="label_{n["id"]}">' + txt(x + 18, y - 4, n["title"], 13.5, 600, C["ink"]) + txt(x + 18, y + 12, f"inflow {fmt(tin)} hm³/yr", 11.5, 400, C["ink3"]) + "</g>")
        continue
    lines = [(n["title"], 13.5, 600, C["ink"], "sans")]
    if n["sub"]: lines.append((n["sub"], 11.5, 400, C["ink3"], "sans"))
    if n["ref"]: lines.append(("[" + n["ref"] + "]", 10, 400, C["ink3"], "mono"))
    r = R[tp] if tp != "reservoir" else 22
    if n["lab"] == "above": y0 = y - r - 10 - (len(lines) - 1) * 14
    else: y0 = y + r + 18
    lab.append(f'<g id="label_{n["id"]}">' + "".join(txt(x, y0 + i * 14, s, sz, wt, fl, f, "middle") for i, (s, sz, wt, fl, f) in enumerate(lines)) + "</g>")
# Rhône axis
rx = nodes["rh_chippis"]["x"]
rhone = [f'<path id="rhone_axis" d="M{rx},30 L{rx},{GH-40}" stroke="{C["rhone"]}" stroke-width="14" stroke-linecap="round"/>',
         f'<path d="M{rx},{GH-70} L{rx},{GH-40}" stroke="{C["ink2"]}" stroke-width="2"/>',
         f'<path d="M{rx},{GH-28} L{rx+6},{GH-42} L{rx-6},{GH-42} Z" fill="{C["ink2"]}"/>',
         txt(rx - 16, GH - 46, "Rhône, flowing west", 11.5, 400, C["ink3"], "sans", "end"),
         txt(rx - 16, GH - 32, "Turtmann lies upstream of Chippis", 11.5, 400, C["ink3"], "sans", "end")]
# halos for labels
import re
halo = [re.sub(r'fill="[^"]+"', f'fill="{C["bg"]}" stroke="{C["bg"]}" stroke-width="4" stroke-linejoin="round"', l) for l in lab]
# ---------- header, legend, footer ----------
PAD = 44
head = [txt(PAD, 30, spec["eyebrow"], 11.5, 400, C["ink3"], "mono"), txt(PAD, 66, spec["title"], 32, 700, C["ink"], "serif"), txt(PAD, 92, spec["subtitle"], 15, 400, C["ink2"])]
lg = []; lx = PAD; ly = 122
kinds = {e["kind"] for e in spec["edges"]}
ekeys = [("Turbined / conveyed for generation", C["power"], False, "power"), ("Statutory residual flow", C["eco"], False, "eco"), ("Irrigation & snowmaking", C["use"], False, "use"), ("River, spill or not captured", C["grey"], False, "river"), ("Dashed: estimate, ceiling or calibration term", C["ink3"], True, "")]
for t, col, dash, kk in [k for k in ekeys if (k[3] in kinds or k[3] == "" or (k[3] == "river" and kinds & {"spill", "mixed"}))]:
    lg.append(f'<path d="M{lx},{ly} L{lx+26},{ly}" stroke="{col}" stroke-width="5"{" stroke-dasharray=\"6 3\"" if dash else ""}/>'); lg.append(txt(lx + 32, ly + 4, t, 12.5)); lx += 32 + len(t) * 6.2 + 26
lx = PAD; ly = 148
present = {n["type"] for n in spec["nodes"]}
glyphs = [g for g in [("source", "Catchment / runoff source"), ("reservoir", "Reservoir"), ("junction", "Intake / junction"), ("plant", "Power plant (stage)"), ("plant_other", "Other plants (outside scheme)"), ("eco", "Reach with minimum flow"), ("river", "Reach without minimum flow"), ("use", "Abstraction"), ("spill", "Unturbined water (balance)")] if g[0] in present]
for tp, t in glyphs:
    cx = lx + 10
    if tp == "source": lg.append(f'<circle cx="{cx}" cy="{ly}" r="8" fill="#fff" stroke="{C["ink2"]}" stroke-width="2"/>')
    if tp == "reservoir": lg.append(f'<path d="M{cx-11},{ly-8} L{cx+11},{ly-8} L{cx+7},{ly+8} L{cx-7},{ly+8} Z" fill="{C["ink2"]}"/>')
    if tp == "plant": lg.append(f'<rect x="{cx-9}" y="{ly-9}" width="18" height="18" rx="3" fill="{C["power"]}"/>')
    if tp == "eco": lg.append(f'<path d="M{cx},{ly-8} L{cx+8},{ly} L{cx},{ly+8} L{cx-8},{ly} Z" fill="{C["eco"]}"/>')
    if tp == "use": lg.append(f'<circle cx="{cx}" cy="{ly}" r="7" fill="{C["use"]}"/>')
    if tp == "spill": lg.append(f'<circle cx="{cx}" cy="{ly}" r="7" fill="#fff" stroke="{C["grey"]}" stroke-width="2.5" stroke-dasharray="3 2"/>')
    if tp == "junction": lg.append(f'<circle cx="{cx}" cy="{ly}" r="6" fill="{C["ink2"]}"/>')
    if tp == "plant_other": lg.append(f'<rect x="{cx-9}" y="{ly-9}" width="18" height="18" rx="3" fill="#fff" stroke="{C["grey"]}" stroke-width="2" stroke-dasharray="3 2"/>')
    if tp == "river": lg.append(f'<path d="M{cx},{ly-8} L{cx+8},{ly} L{cx},{ly+8} L{cx-8},{ly} Z" fill="{C["grey"]}"/>')
    lg.append(txt(lx + 26, ly + 4, t, 12.5)); lx += 26 + len(t) * 6.2 + 20
cols = [txt(x, -14, c.upper(), 10.5, 400, C["ink3"], "mono", "middle", ' letter-spacing="0.06em"') for x, c in spec["columns"]]
grid = [f'<path d="M{x},-4 L{x},{GH-60}" stroke="{C["rule"]}" stroke-width="1"/>' for x, c in spec["columns"][:-1]]
y = TOP + GH + 10; foot = []
if spec.get("shares"):
    foot.append(txt(PAD, y, "Upper-stage hydraulic power by grantor after the return (estimate, fixed at expiry) [R08 p3]", 13, 600, C["ink"]))
    bw = W - 2 * PAD; bx = PAD; by = y + 12; unl = []
    ramp = ['#0d366b','#184f95','#256abf','#3987e5','#6da7ec','#9ec5f4','#cde2fb']
    for i, (nm, s) in enumerate(spec["shares"]):
        w = bw * s / 100; foot.append(f'<rect x="{bx:.1f}" y="{by}" width="{max(1, w-2):.1f}" height="18" fill="{ramp[i]}"/>')
        lb = f"{nm} {s:.1f} %"
        if w > len(lb) * 6.6 + 8: foot.append(txt(bx + 6, by + 13, lb, 11.5, 400, "#ffffff" if i < 4 else C["ink"]))
        else: unl.append(lb)
        bx += w
    foot.append(txt(PAD, by + 36, "Unlabelled segments, left to right: " + " · ".join(unl) + ". Canton may raise its stake to 31.7 % via its purchase right [R08 p8].", 12))
    y += 70
for s in spec["notes"]:
    words = s.split(" "); line = ""; out = []
    for w_ in words:
        if len(line) + len(w_) + 1 > 190: out.append(line); line = w_
        else: line = (line + " " + w_).strip()
    out.append(line)
    for j, l in enumerate(out): foot.append(txt(PAD + (12 if j else 0), y + j * 16, ("" if j else "• ") + l, 12))
    y += len(out) * 16 + 6
foot.append(txt(PAD, y + 10, "Edge width ∝ annual volume; values in hm³/yr (million m³). Plant volumes are the same water used in series. Reference IDs [R##] are listed in EVIDENCE.md.", 11.5, 400, C["ink3"]))
H = y + 34
out = [f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect id="background" width="{W}" height="{H}" fill="{C["bg"]}"/>', 
       '<g id="title">' + "".join(head) + "</g>", '<g id="legend">' + "".join(lg) + "</g>",
       f'<g id="graph" transform="translate(0,{TOP})">', '<g id="column-guides">' + "".join(grid) + "".join(cols) + "</g>",
       '<g id="rhone">' + "".join(rhone) + "</g>", '<g id="edges">' + "".join(eg) + "</g>", '<g id="nodes">' + "".join(ng) + "</g>",
       '<g id="label-halos (delete if not needed)">' + "".join(halo) + "</g>", '<g id="labels">' + "".join(lab) + "</g>", "</g>",
       '<g id="notes">' + "".join(foot) + "</g>", "</svg>"]
open(OUT, "w", encoding="utf-8").write("\n".join(out))
print("wrote", OUT, W, H)
