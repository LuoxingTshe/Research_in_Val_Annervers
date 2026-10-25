"""Node–edge flow graph spec for the post-2039 period (upstream left, Rhône right).
Values come from period_models.json (post2039); positions are a hand-made schematic layout."""
import json, sys
M = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "period_models.json", encoding="utf-8"))["post2039"]
V = {(l["source"], l["target"], l["kind"]): l for l in M["links"]}
def val(s, t, k=None):
    c = [l for (a, b, kk), l in V.items() if a == s and b == t and (k is None or kk == k)]
    assert len(c) == 1, (s, t, k, c); return c[0]["value"]
X = [80, 300, 540, 790, 1040, 1250, 1430]
nodes = [
 # id, type, x, y, title, sub, ref, label position
 ("s_turt_rest","source",X[1],70,"Turtmänna below intakes","not captured · Turtmann valley","R11","above"),
 ("s_tourt","source",X[0],170,"Tourtemagne intakes","Turtmänna + tributaries","R07 p9; R06 p7","above"),
 ("s_moiry","source",X[0],400,"Moiry catchment","Gougra, incl. Lona","R07 p9","below"),
 ("moiry","reservoir",X[1],300,"Moiry reservoir","77 hm³ live storage · returns 2039","R08 p3; R07 p5","above"),
 ("snow","use",X[2],170,"Snowmaking","Tsarmette offtake","R04 p90","above"),
 ("mottec","plant",X[2],300,"Mottec","Stage 1 · 640 m · 137 GWh/yr","R10; R06 p8","above"),
 ("upper_spill","spill",X[2],420,"Not turbined at Mottec","spill / uncaptured (balance)","R10","below"),
 ("gougra","eco",X[2],520,"Gougra below dam","≥ 90 / 50 L/s","R04 p80","below"),
 ("s_mottec","source",X[2]-90,700,"Mottec area","Navizence intake + Moulins","R07 p9","below"),
 ("irr_up","use",X[3]-60,800,"Bisse Roux + St-Luc","free quota","R04 p101","below"),
 ("vissoie","plant",X[3],300,"Vissoie","Stage 2 · 437 m · 216 GWh/yr","R10; R06 p9","above"),
 ("reach300","eco",X[3],560,"St-Jean–Vissoie reach","≥ 300 L/s + spills","R04 p80","below"),
 ("irr_low","use",X[4],170,"Briey + Niouc","≤ 45 / < 60 L/s","R04 p100–101","above"),
 ("navizence","plant",X[4],300,"Navizence (Chippis)","Stage 3 · 591 m · 299 GWh/yr · FMG to 2084","R10; R06 p10","above"),
 ("s_vissoie","source",X[3]+50,700,"Vissoie area","incl. Fang","R07 p9","below"),
 ("river_low","eco",X[4],560,"Lower Navizence","≥ 470 L/s + spill + laterals","R04 p80; R12","below"),
 ("s_lat","source",X[3]+150,850,"Laterals below intakes","not captured","R11","below"),
 ("fang","eco",X[5],740,"Fang below intake","≥ 50 L/s","R04 p80","below"),
 ("ricard","use",X[5],640,"Bisse de Ricard","right 265 L/s · intake damaged 2018","R05 p18; R04 p81","below"),
 ("rh_turtmann","rhone",X[6],100,"Rhône at Turtmann","","",""),
 ("rh_chippis","rhone",X[6],460,"Rhône at Chippis","","",""),
]
E = lambda s,t,v,kind,unc=False,note="",route="s",lp=0.5,dy=0: dict(source=s,target=t,value=round(v,2),kind=kind,uncertain=unc,note=note,route=route,lp=lp,dy=dy)
edges = [
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
]
spec = dict(key="post2039", width=1560, height=940,
  title="After the 2039 return", eyebrow="GOUGRA / NAVIZENCE · FLOW GRAPH · MEAN YEAR, hm³/yr",
  subtitle="Upper stage reverts to the grantors on 31 Dec 2039; flows shown for today's rules in a mean year. Upstream on the left, the Rhône on the right.",
  columns=[(X[0],"Catchments"),(X[1],"Storage"),(X[2],"Stage 1"),(X[3],"Stage 2"),(X[4],"Stage 3"),(X[5],"Lower reach"),(X[6],"Rhône")],
  nodes=[dict(id=a,type=b,x=c,y=d,title=e,sub=f,ref=g,lab=h) for a,b,c,d,e,f,g,h in nodes], edges=edges,
  shares=M["shares"], notes=M["notes"])
json.dump(spec, open("flow_graph_2039.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(nodes),"nodes",len(edges),"edges")
