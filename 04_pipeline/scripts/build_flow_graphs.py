"""Node–edge flow-graph specs for the three periods (upstream left, Rhône right).
Values come from period_models.json; positions are hand-made schematic layouts sharing the same columns.
Usage: python3 build_flow_graphs.py period_models.json [outdir]"""
import json, os, sys
MM = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "period_models.json", encoding="utf-8"))
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
X = [80, 300, 540, 790, 1040, 1250, 1430]
def getter(M):
    def val(s, t, k=None):
        c = [l for l in M["links"] if l["source"] == s and l["target"] == t and (k is None or l["kind"] == k)]
        assert len(c) == 1, (s, t, k, c); return c[0]["value"]
    return val
def N(i, tp, x, y, title, sub, ref, lab, badge=""): return dict(id=i, type=tp, x=x, y=y, title=title, sub=sub, ref=ref, lab=lab, badge=badge)
def E(s, t, v, kind, unc=False, note="", route="s", lp=0.5, dy=0): return dict(source=s, target=t, value=round(v, 2), kind=kind, uncertain=unc, note=note, route=route, lp=lp, dy=dy)
specs = {}

# ---------------- 1. before 1958 ----------------
M = MM["pre1958"]; val = getter(M)
specs["1_before-1958"] = dict(key="pre1958", width=1560, height=900, title="Before 1958",
 eyebrow="GOUGRA / NAVIZENCE · FLOW GRAPH · STATE c. 1950, hm³/yr",
 subtitle="Run-of-river use at Chippis, no storage in Anniviers; the Turtmänna is used in its own valley. Upstream on the left, the Rhône on the right.",
 columns=[(X[0],"Catchments"),(X[3],"Vissoie intake"),(X[4],"Plant / reach"),(X[5],"Lower reach"),(X[6],"Rhône")],
 nodes=[
  N("s_turt","source",X[0],110,"Turtmänna","Turtmann valley, natural runoff","R11","above"),
  N("itag","plant_other",X[3],110,"ITAG plants & river","Oberems–Turtmann, since 1925 · 772 m · split not documented","R01 p2","above","T"),
  N("s_gougra","source",X[0],300,"Gougra (Moiry)","no dam yet","R11","above"),
  N("s_lona","source",X[0],420,"Lona","flows to the Gougra","R11; R02 p3","below"),
  N("s_mottec","source",X[0],600,"Navisence at Mottec","Zinal valley","R11","below"),
  N("s_mid","source",X[2],660,"Moulins, Nava & laterals","joining above Vissoie","R11","below"),
  N("vissoie","junction",X[3],420,"AIAG intake at Vissoie","gallery ≤ 7 m³/s (monthly means capped)","R01 p2–3","above"),
  N("briey","use",X[4],230,"Bisse de Briey","1912 right 120 L/s, Jun–Aug","R04 p100","above"),
  N("chippis","plant",X[4],360,"Chippis–Navisence","AIAG, since 1908 · 590 m · ≈ 202 GWh/yr theor.","R01 p2; R04 p77","above","C"),
  N("river","river",X[4],580,"Navisence below Vissoie","not captured · no minimum-flow rule","R11","below"),
  N("s_low","source",X[3]+60,780,"Laterals below Vissoie","incl. Fang","R11","below"),
  N("ricard","use",X[5],690,"Bisse de Ricard","right 265 L/s, 20 Apr–20 Sep","R05 p18","below"),
  N("rh_turtmann","rhone",X[6],100,"Rhône at Turtmann","","",""),
  N("rh_chippis","rhone",X[6],470,"Rhône at Chippis","","",""),
 ],
 edges=[
  E("s_turt","itag",val("s_turt","itag"),"mixed",True,"natural runoff, ITAG plants and river",lp=0.5),
  E("itag","rh_turtmann",val("itag","rh_turtmann"),"mixed",True),
  E("s_gougra","vissoie",val("s_gougra","vissoie"),"river",lp=0.4),
  E("s_lona","vissoie",val("s_lona","vissoie"),"river",lp=0.4),
  E("s_mottec","vissoie",val("s_mottec","vissoie"),"river",lp=0.4),
  E("s_mid","vissoie",val("s_mid","vissoie"),"river",lp=0.55),
  E("vissoie","chippis",val("vissoie","chippis"),"power",lp=0.45,dy=-6),
  E("vissoie","briey",val("vissoie","briey"),"use",True,lp=0.6),
  E("vissoie","river",val("vissoie","river"),"river",note="left in the river",lp=0.5),
  E("s_low","river",val("s_low","river"),"river",lp=0.4),
  E("river","ricard",val("river","ricard"),"use",True),
  E("river","rh_chippis",val("river","rh_chippis"),"river",lp=0.45),
  E("chippis","rh_chippis",val("chippis","rh_chippis"),"power",lp=0.45),
 ], notes=M["notes"])

# ---------------- 2. after 1958 ----------------
M = MM["post1958"]; val = getter(M)
specs["2_after-1958"] = dict(key="post1958", width=1560, height=920, title="After 1958",
 eyebrow="GOUGRA / NAVIZENCE · FLOW GRAPH · DESIGN AVERAGE YEAR 1962, hm³/yr",
 subtitle="Gougra scheme as commissioned 1958–61 (Robert 1962, Table 2). Upstream on the left, the Rhône on the right.",
 columns=[(X[0],"Catchments"),(X[1],"Storage"),(X[2],"Stage 1"),(X[3],"Stage 2"),(X[4],"Stage 3"),(X[5],"Lower reach"),(X[6],"Rhône")],
 nodes=[
  N("s_turt_rest","source",X[1],70,"Turtmänna not captured","indicative · Turtmann valley","R11","above"),
  N("itag","plant_other",X[3],70,"Turtmann valley","ITAG plants & river","R01 p2","above","T"),
  N("s_tourt","source",X[0],190,"Tourtemagne + Barneusaz","40.1 km² · share by area","R01 p4","above"),
  N("s_moiry","source",X[0],400,"Moiry catchment","29.3 km² · share by area","R01 p4","below"),
  N("s_lona","source",X[0],560,"Lona","Lona plant 1961 · 331 m · 4 GWh","R01 p2, p4","below"),
  N("moiry","reservoir",X[1],320,"Moiry reservoir","77 hm³ · built 1954–58","R01 p2; R04 p78","above"),
  N("t_direct","junction",X[1]+90,190,"Tourtemagne direct","gallery to Mottec · 6 m³/s design","R01 p4","above"),
  N("mottec","plant",X[2],320,"Mottec","685 m · 69 MW · 125 GWh/yr (W 119 / S 6)","R01 p3–4; R02 p3","above","1"),
  N("s_navi","source",X[2]-80,640,"Navizence at Mottec + Moulins","107.6 km²","R01 p4","below"),
  N("vissoie","plant",X[3],320,"Vissoie","439 m · 45 MW · 185 GWh/yr (W 93 / S 92)","R01 p3–4","above","2"),
  N("s_rem","source",X[3]+60,470,"Remaining basin, captured","60.5 km² basin","R01 p4","below"),
  N("chippis","plant",X[4],320,"Chippis–Navisence","590 m · 50 MW · 255 GWh/yr (W 134 / S 121)","R01 p2–4","above","3"),
  N("briey","use",X[4]+60,560,"Bisse de Briey","1912 right 120 L/s","R04 p100","below"),
  N("s_uncapt","source",X[3],760,"Navisence runoff not captured","indicative (MQN minus design)","R11","below"),
  N("river","river",X[4],700,"Navisence below intakes","no minimum-flow rule","R11","below"),
  N("ricard","use",X[5],690,"Bisse de Ricard","right 265 L/s","R05 p18","below"),
  N("rh_turtmann","rhone",X[6],80,"Rhône at Turtmann","","",""),
  N("rh_chippis","rhone",X[6],470,"Rhône at Chippis","","",""),
 ],
 edges=[
  E("s_turt_rest","itag",val("s_turt_rest","itag"),"mixed",True,lp=0.5),
  E("itag","rh_turtmann",val("itag","rh_turtmann"),"mixed",True,"Turtmänna and ITAG plants",lp=0.5),
  E("s_tourt","moiry",val("s_tourt","moiry"),"power",True,"gravity in spring, then siphon pump",lp=0.33),
  E("s_tourt","t_direct",val("s_tourt","t_direct"),"power",lp=0.6),
  E("t_direct","mottec",val("t_direct","mottec"),"power",lp=0.55),
  E("s_moiry","moiry",val("s_moiry","moiry"),"power",True,lp=0.45),
  E("s_lona","moiry",val("s_lona","moiry"),"power",lp=0.5),
  E("moiry","mottec",val("moiry","mottec"),"power",note="all turbined in winter",lp=0.5,dy=-18),
  E("mottec","vissoie",val("mottec","vissoie"),"power"),
  E("s_navi","vissoie",val("s_navi","vissoie"),"power",note="Mottec intake",lp=0.55),
  E("vissoie","chippis",val("vissoie","chippis"),"power",note="gallery 12 m³/s since 1954/55",lp=0.5,dy=-20),
  E("s_rem","chippis",val("s_rem","chippis"),"power",lp=0.55),
  E("s_rem","briey",val("s_rem","briey"),"use",True,lp=0.6),
  E("s_uncapt","river",val("s_uncapt","river"),"river",True,lp=0.5),
  E("river","ricard",val("river","ricard"),"use",True),
  E("river","rh_chippis",val("river","rh_chippis"),"river",True,lp=0.45),
  E("chippis","rh_chippis",val("chippis","rh_chippis"),"power",lp=0.45),
 ], notes=M["notes"])

# ---------------- 3. after the 2039 return (test layout, unchanged) ----------------
M = MM["post2039"]; val = getter(M)
specs["3_after-2039-return"] = dict(key="post2039", width=1560, height=940, title="After the 2039 return",
 eyebrow="GOUGRA / NAVIZENCE · FLOW GRAPH · MEAN YEAR, hm³/yr",
 subtitle="Upper stage reverts to the grantors on 31 Dec 2039; flows shown for today's rules in a mean year. Upstream on the left, the Rhône on the right.",
 columns=[(X[0],"Catchments"),(X[1],"Storage"),(X[2],"Stage 1"),(X[3],"Stage 2"),(X[4],"Stage 3"),(X[5],"Lower reach"),(X[6],"Rhône")],
 nodes=[
  N("s_turt_rest","source",X[1],70,"Turtmänna below intakes","not captured · Turtmann valley","R11","above"),
  N("s_tourt","source",X[0],170,"Tourtemagne intakes","Turtmänna + tributaries","R07 p9; R06 p7","above"),
  N("s_moiry","source",X[0],400,"Moiry catchment","Gougra, incl. Lona","R07 p9","below"),
  N("moiry","reservoir",X[1],300,"Moiry reservoir","77 hm³ live storage · returns 2039","R08 p3; R07 p5","above"),
  N("snow","use",X[2],170,"Snowmaking","Tsarmette offtake","R04 p90","above"),
  N("mottec","plant",X[2],300,"Mottec","Stage 1 · 640 m · 137 GWh/yr","R10; R06 p8","above","1"),
  N("upper_spill","spill",X[2],420,"Not turbined at Mottec","spill / uncaptured (balance)","R10","below"),
  N("gougra","eco",X[2],520,"Gougra below dam","≥ 90 / 50 L/s","R04 p80","below"),
  N("s_mottec","source",X[2]-90,700,"Mottec area","Navizence intake + Moulins","R07 p9","below"),
  N("irr_up","use",X[3]-60,800,"Bisse Roux + St-Luc","free quota","R04 p101","below"),
  N("vissoie","plant",X[3],300,"Vissoie","Stage 2 · 437 m · 216 GWh/yr","R10; R06 p9","above","2"),
  N("reach300","eco",X[3],560,"St-Jean–Vissoie reach","≥ 300 L/s + spills","R04 p80","below"),
  N("irr_low","use",X[4],170,"Briey + Niouc","≤ 45 / < 60 L/s","R04 p100–101","above"),
  N("navizence","plant",X[4],300,"Navizence (Chippis)","Stage 3 · 591 m · 299 GWh/yr · FMG to 2084","R10; R06 p10","above","3"),
  N("s_vissoie","source",X[3]+50,700,"Vissoie area","incl. Fang","R07 p9","below"),
  N("river_low","eco",X[4],560,"Lower Navizence","≥ 470 L/s + spill + laterals","R04 p80; R12","below"),
  N("s_lat","source",X[3]+150,850,"Laterals below intakes","not captured","R11","below"),
  N("fang","eco",X[5],740,"Fang below intake","≥ 50 L/s","R04 p80","below"),
  N("ricard","use",X[5],640,"Bisse de Ricard","right 265 L/s · intake damaged 2018","R05 p18; R04 p81","below"),
  N("rh_turtmann","rhone",X[6],100,"Rhône at Turtmann","","",""),
  N("rh_chippis","rhone",X[6],460,"Rhône at Chippis","","",""),
 ],
 edges=[
  E("s_tourt","moiry",val("src_tourt","moiry"),"power",note="gallery ≤ 8 m³/s; gravity or siphon",lp=0.28),
  E("s_moiry","moiry",val("src_moiry","moiry"),"power"),
  E("s_mottec","moiry",val("pump_src","moiry"),"pump",True,"storage pump 3.9 m³/s, 570–664 m","pump",0.5),
  E("moiry","mottec",val("moiry","mottec"),"power"),
  E("moiry","snow",val("moiry","snow"),"use",True),
  E("moiry","upper_spill",val("moiry","upper_spill"),"spill",True,lp=0.62),
  E("moiry","gougra",val("moiry","gougra"),"eco",note="dam release",lp=0.3),
  E("mottec","vissoie",val("mottec","vissoie"),"power"),
  E("s_mottec","vissoie",val("src_mottec","vissoie"),"power",note="intake 12 (max 18) m³/s"),
  E("s_mottec","irr_up",val("src_mottec","irr_up"),"use",True),
  E("s_mottec","reach300",val("src_mottec","reach300","eco"),"eco",True,"release at Mottec intake",lp=0.45),
  E("s_mottec","reach300",val("src_mottec","reach300","spill"),"spill",True,"intake overflow",lp=0.65,dy=26),
  E("upper_spill","reach300",val("upper_spill","reach300"),"spill",True),
  E("gougra","reach300",val("gougra","reach300"),"eco"),
  E("vissoie","irr_low",val("vissoie","irr_low"),"use",True),
  E("vissoie","navizence",val("vissoie","navizence"),"power",note="tunnel ≤ 11.5 m³/s",lp=0.5,dy=-14),
  E("vissoie","river_low",val("vissoie","river_low"),"spill",True,"Vissoie spill (≈ 20 hm³ in 2001)",lp=0.82),
  E("reach300","navizence",val("reach300","navizence"),"power",True,"recaptured at Vissoie intake",lp=0.22),
  E("reach300","river_low",val("reach300","river_low"),"eco",lp=0.55,dy=14),
  E("s_vissoie","navizence",val("src_vissoie","navizence"),"power",lp=0.7),
  E("s_vissoie","river_low",val("src_vissoie","river_low"),"eco",True),
  E("s_vissoie","fang",val("src_vissoie","fang"),"eco"),
  E("s_lat","river_low",val("s_lat","river_low"),"river",True),
  E("navizence","rh_chippis",val("navizence","rhone"),"power"),
  E("river_low","rh_chippis",val("river_low","rhone"),"river",lp=0.4),
  E("river_low","ricard",val("river_low","ricard"),"use",True),
  E("fang","rh_chippis",val("fang","rhone"),"eco",lp=0.55),
  E("s_turt_rest","rh_turtmann",val("s_turt_rest","itag"),"river",True,"Turtmänna and downstream plants",lp=0.5),
 ], shares=M["shares"], notes=M["notes"])

for name, sp in specs.items():
    # balance check per spec: every non-source, non-Rhône node must have inflow == outflow
    ins, outs = {}, {}
    for e in sp["edges"]:
        outs[e["source"]] = outs.get(e["source"], 0) + e["value"]; ins[e["target"]] = ins.get(e["target"], 0) + e["value"]
    bad = [(n, round(ins[n] - outs[n], 2)) for n in ins if n in outs and abs(ins[n] - outs[n]) > 0.05 and n != "moiry" and n != "s_mottec"]
    srcs = sum(v for n, v in outs.items() if n not in ins); sinks = sum(v for n, v in ins.items() if n not in outs)
    print(name, "sources", round(srcs, 1), "sinks", round(sinks, 1), "unbalanced", bad)
    json.dump(sp, open(os.path.join(OUT, f"flow_graph_{name}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
