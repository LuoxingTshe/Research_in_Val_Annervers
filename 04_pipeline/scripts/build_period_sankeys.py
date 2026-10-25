"""Three Sankey models of the Gougra / Navizence system: before 1958, after 1958 (as commissioned), after the 2039 return.
Inputs: mqn_points.csv (BAFU MQN), v2 cascade_model.json (gougra_cascade_energy). Output: period_models.json"""
import csv, json, sys
D = [31,28,31,30,31,30,31,31,30,31,30,31]
mq = {r["point"]: r for r in csv.DictReader(open(sys.argv[1] if len(sys.argv)>1 else "mqn_points.csv", encoding="utf-8-sig"))}
v2 = json.load(open(sys.argv[2] if len(sys.argv)>2 else "v2_model.json", encoding="utf-8"))
A = lambda p: float(mq[p]["annual_hm3"])
MON = ["q_jan_m3s","q_feb_m3s","q_mar_m3s","q_apr_m3s","q_mai_m3s","q_jun_m3s","q_jul_m3s","q_aug_m3s","q_sep_m3s","q_okt_m3s","q_nov_m3s","q_dez_m3s"]
def capped(p, cap):  # monthly-mean flow capped at gallery capacity -> hm3/yr
    return sum(min(float(mq[p][m]), cap)*d*86400 for m, d in zip(MON, D))/1e6
kwh = lambda h: 9.81*h/3600
ls_season = lambda ls, days: ls/1000*days*86400/1e6
NAV_CHIPPIS, NAV_VISSOIE, TURT = A("Navisence_Chippis"), A("Navisence_Vissoie"), A("Turtmaenna_Turtmann")
TOTAL = NAV_CHIPPIS + TURT
r = lambda x: round(x, 3)
FLOOR = 4.0
def L(s, t, v, kind, unc=False): return dict(source=s, target=t, value=r(v), display=r(max(v, FLOOR) if unc else v), kind=kind, uncertain=unc)
def N(i, name, sub, col, kind, ref="", energy=None, pin=None): return dict(id=i, name=name, sub=sub, col=col, kind=kind, ref=ref, energy=energy, pin=pin)
briey_1912 = ls_season(120, 92)          # 1 Jun-31 Aug
ricard = ls_season(265, 154)            # 20 Apr-20 Sep
models = {}

# ---------------- 1. before 1958 (state c. 1950) ----------------
gougra, lona, mottec = A("Gougra_Moiry_dam"), A("Lona_torrent"), A("Navisence_Mottec_intake")
mid = NAV_VISSOIE - gougra - lona - mottec
low = NAV_CHIPPIS - NAV_VISSOIE
gallery = capped("Navisence_Vissoie", 7.0)
chippis = gallery - briey_1912
spill = NAV_VISSOIE - gallery
models["pre1958"] = dict(
 key="pre1958", title="Before 1958", subtitle="State c. 1950: run-of-river use at Chippis, no storage in Anniviers; Turtmänna used in its own valley",
 columns=["Natural runoff","Navisence at Vissoie","Use","Irrigation","Rhône"],
 nodes=[
  N("s_gougra","Gougra (Moiry)","no dam yet",0,"src","R11"),
  N("s_lona","Lona","flows to the Gougra",0,"src","R11; R02 p3"),
  N("s_mottec","Navisence at Mottec","",0,"src","R11"),
  N("s_mid","Moulins, Nava & laterals","above Vissoie",0,"src","R11"),
  N("s_low","Laterals below Vissoie","incl. Fang",0,"src","R11"),
  N("s_turt","Turtmänna","Turtmann valley",0,"src","R11"),
  N("vissoie","AIAG intake at Vissoie","free-flow gallery ≤ 7 m³/s",1,"junction","R01 p2–3"),
  N("chippis","Chippis–Navisence plant","AIAG, since 1908 · 590 m",2,"plant","R01 p2; R04 p77", energy=f"{chippis*kwh(590):.0f} GWh/yr theor."),
  N("river","Navisence below Vissoie","not captured",2,"river","R11"),
  N("briey","Bisse de Briey","1912 right 120 L/s, Jun–Aug",2,"use","R04 p100", pin=["river","below",16]),
  N("itag","ITAG plants & river","Oberems–Turtmann, since 1925 · 772 m",2,"mixed","R01 p2"),
  N("ricard","Bisse de Ricard","right 265 L/s, 20 Apr–20 Sep",3,"use","R05 p18", pin=["river","below",58]),
  N("rh_chippis","Rhône at Chippis","",4,"sink"),
  N("rh_turtmann","Rhône at Turtmann","",4,"sink"),
 ],
 links=[
  L("s_gougra","vissoie",gougra,"river"), L("s_lona","vissoie",lona,"river"), L("s_mottec","vissoie",mottec,"river"), L("s_mid","vissoie",mid,"river"),
  L("vissoie","chippis",chippis,"power"), L("vissoie","briey",briey_1912,"use",True), L("vissoie","river",spill,"river"),
  L("s_low","river",low,"river"), L("river","ricard",ricard,"use",True), L("river","rh_chippis",spill+low-ricard,"river"),
  L("chippis","rh_chippis",chippis,"power"),
  L("s_turt","itag",TURT,"mixed",True), L("itag","rh_turtmann",TURT,"mixed",True),
 ],
 notes=[
  "Natural runoff from BAFU MQN (modelled mean flows, recent reference period); glaciers were larger c. 1950, so absolute volumes are indicative.",
  f"Gallery intake: monthly mean flow at Vissoie capped at 7 m³/s gives ≈ {gallery:.0f} hm³/yr; daily peaks would add spill. Gallery enlarged to 12 m³/s in 1954/55 (R01 p3).",
  "No residual-flow rules before 1958: water not taken by the gallery stays in the river. The Turtmänna split between ITAG plants and river is not documented.",
  "Concessions: Navisence Vissoie–Chippis to AIAG for 99 years (1905); upper Navisence to SIS (1908); Gougra waters granted 1943 (R04 p77).",
 ],
 totals=dict(natural=r(TOTAL), gallery=r(gallery), spill=r(spill), chippis_theor_GWh=r(chippis*kwh(590))),
)

# ---------------- 2. after 1958: Gougra scheme as commissioned (design average year) ----------------
T2 = {"lona":5.5,"moiry_mottec":79.6,"tourt_mottec":10.6,"mottec_vissoie":198.8,"vissoie_chippis":209.7}   # Robert 1962 Table 2
area = {"moiry":29.3,"lona":6.2,"tourt":36.6,"barneusa":4.5}                                                 # Robert 1962 Table 1
upper = T2["moiry_mottec"] + T2["tourt_mottec"]                    # 90.2, incl. Lona 5.5
per_km2 = (upper - T2["lona"]) / (area["moiry"] + area["tourt"] + area["barneusa"])
moiry_nat, tourt_cap, barn = per_km2*area["moiry"], per_km2*area["tourt"], per_km2*area["barneusa"]
tourt_grp = tourt_cap + barn
tourt_to_moiry = tourt_grp - T2["tourt_mottec"]
navi_mottec = T2["mottec_vissoie"] - upper                          # 108.6
rem = T2["vissoie_chippis"] - T2["mottec_vissoie"]                 # 10.9
anniv_captured = moiry_nat + T2["lona"] + barn + navi_mottec + rem
uncapt = NAV_CHIPPIS - anniv_captured - briey_1912
turt_rest = TURT - tourt_cap
models["post1958"] = dict(
 key="post1958", title="After 1958", subtitle="Gougra scheme as commissioned 1958–61: design average year (Robert 1962, Table 2)",
 columns=["Inflow","Storage","Stage 1","Stage 2","Stage 3","Rhône"],
 nodes=[
  N("s_moiry","Moiry catchment","29.3 km² · share est.",0,"src","R01 p4"),
  N("s_lona","Lona","via Lona plant, 331 m, 4 GWh",0,"src","R01 p2, p4"),
  N("s_tourt","Tourtemagne + Barneusaz","40.1 km² · share est.",0,"src","R01 p4"),
  N("moiry","Moiry reservoir","77 hm³ · built 1954–58",1,"store","R01 p2; R04 p78"),
  N("t_direct","Tourtemagne direct","gallery to Mottec · 6 m³/s design",1,"junction","R01 p4"),
  N("mottec","Mottec plant","685 m · 69 MW",2,"plant","R01 p3–4; R02 p3", energy="125 GWh/yr · W 119 / S 6"),
  N("s_navi","Navizence at Mottec + Moulins","107.6 km²",2,"src","R01 p4"),
  N("vissoie","Vissoie plant","439 m · 45 MW",3,"plant","R01 p3–4", energy="185 GWh/yr · W 93 / S 92"),
  N("s_rem","Remaining basin, captured","60.5 km² basin",3,"src","R01 p4"),
  N("s_uncapt","Navisence runoff not captured","indicative",3,"src","R11"),
  N("s_turt_rest","Turtmänna not captured","indicative",3,"src","R11"),
  N("chippis","Chippis–Navisence plant","590 m · 50 MW",4,"plant","R01 p2–4", energy="255 GWh/yr · W 134 / S 121"),
  N("briey","Bisse de Briey","1912 right 120 L/s",4,"use","R04 p100", pin=["chippis","below",16]),
  N("river","Navisence below intakes","no residual-flow rule",4,"river","R11"),
  N("itag","Turtmann valley","ITAG plants & river",4,"mixed","R01 p2"),
  N("rh_chippis","Rhône at Chippis","",5,"sink"),
  N("ricard","Bisse de Ricard","right 265 L/s",5,"use","R05 p18", pin=["rh_chippis","below",18]),
  N("rh_turtmann","Rhône at Turtmann","",5,"sink"),
 ],
 links=[
  L("s_moiry","moiry",moiry_nat,"power",True), L("s_lona","moiry",T2["lona"],"power"),
  L("s_tourt","moiry",tourt_to_moiry,"power",True), L("s_tourt","t_direct",T2["tourt_mottec"],"power"), L("t_direct","mottec",T2["tourt_mottec"],"power"),
  L("moiry","mottec",T2["moiry_mottec"],"power"),
  L("mottec","vissoie",upper,"power"), L("s_navi","vissoie",navi_mottec,"power"),
  L("vissoie","chippis",T2["mottec_vissoie"],"power"), L("s_rem","chippis",rem,"power"), L("s_rem","briey",briey_1912,"use",True),
  L("s_uncapt","river",uncapt,"river",True), L("river","ricard",ricard,"use",True), L("river","rh_chippis",uncapt-ricard,"river",True),
  L("chippis","rh_chippis",T2["vissoie_chippis"],"power"),
  L("s_turt_rest","itag",turt_rest,"mixed",True), L("itag","rh_turtmann",turt_rest,"mixed",True),
 ],
 notes=[
  "Stage volumes and energy are the 1962 design average year: 569 GWh/yr, 347 in winter and 222 in summer; Moiry water is turbined entirely in winter (R01 p3–4).",
  "Split of the 90.2 hm³ upper-stage volume between the Moiry catchment and Tourtemagne + Barneusaz is by catchment area (estimate). Tourtemagne water reaches Moiry by gravity in spring, by siphon pump once Moiry is higher (R03 p2).",
  "Storage pump (3.9 m³/s) lifts Navizence water to Moiry only in dry years, so it is not in the average-year balance (R03 p2; R02 p3).",
  "Not-captured runoff = BAFU MQN natural flow minus design volumes: indicative only (different reference periods). No residual-flow rules before the 2004 / 2016 decisions.",
 ],
 totals=dict(natural=r(TOTAL), design_GWh=569, uncaptured=r(uncapt), turt_rest=r(turt_rest), moiry_nat=r(moiry_nat), tourt_to_moiry=r(tourt_to_moiry)),
)

# ---------------- 3. after the 2039 return (current rules, mean year, v2 flows) ----------------
nodes3, links3 = [], []
rename = {"mottec": ("Mottec plant","Stage 1 · returns 2039"), "vissoie": ("Vissoie plant","Stage 2 · returns 2039"),
          "navizence": ("Navizence plant","Stage 3 · FMG concession to 2084"), "moiry": ("Moiry reservoir","77 hm³ · returns 2039"),
          "rhone": ("Rhône at Chippis",""), "river_low": ("Lower Navizence","≥ 470 L/s + spill + laterals")}
refs3 = {"src_moiry":"R07 p9","src_tourt":"R07 p9; R06 p7","pump_src":"R10; R13 p4","moiry":"R08 p3; R07 p5","mottec":"R10; R06 p8",
         "snow":"R04 p90","upper_spill":"R10 (balance)","gougra":"R04 p80","src_mottec":"R07 p9","vissoie":"R10; R06 p9","irr_up":"R04 p101",
         "pump_sink":"R10; R13 p4","reach300":"R04 p80","src_vissoie":"R07 p9","irr_low":"R04 p100–101","navizence":"R10; R06 p10",
         "river_low":"R04 p80; R12","fang":"R04 p80","rhone":""}
E = v2["E_wasta_GWh"]
energy3 = {"mottec": f"{E['mottec']:.0f} GWh/yr · 640 m", "vissoie": f"{E['vissoie']+E['vissoie_aux']:.0f} GWh/yr · 437 m", "navizence": f"{E['navizence']:.0f} GWh/yr · 591 m"}
for n in v2["nodes"]:
    nm, sb = rename.get(n["id"], (n["name"], n["sub"]))
    kind = n["kind"]
    nodes3.append(N(n["id"], nm, sb, n["col"], kind, refs3.get(n["id"],""), energy3.get(n["id"])))
for l in v2["links"]:
    links3.append(dict(source=l["source"], target=l["target"], value=l["value"], display=l["display"], kind=l["kind"], uncertain=l["uncertain"]))
lat = NAV_CHIPPIS - (v2["inflow"]["moiry"] + v2["inflow"]["mottec"] + v2["inflow"]["vissoie"])
turt_rest3 = TURT - v2["inflow"]["tourt"]
nodes3.append(N("s_lat","Laterals below intakes","not captured · indicative",3,"src","R11"))
nodes3.append(N("s_turt_rest","Turtmänna not captured","indicative",3,"src","R11"))
nodes3.append(N("ricard","Bisse de Ricard","right 265 L/s · intake damaged 2018",5,"use","R05 p18; R04 p81", pin=["rhone","below",16]))
nodes3.append(N("itag","Turtmann valley","river & downstream plants",4,"mixed","R11"))
nodes3.append(N("rh_turtmann","Rhône at Turtmann","",5,"sink"))
links3 += [L("s_lat","river_low",lat,"river",True), L("s_turt_rest","itag",turt_rest3,"mixed",True), L("itag","rh_turtmann",turt_rest3,"mixed",True)]
for l in links3:
    if l["source"]=="river_low" and l["target"]=="rhone":
        l["value"] = r(l["value"] + lat - ricard); l["display"] = l["value"]; l["kind"]="river"
links3.append(L("river_low","ricard",ricard,"use",True))
models["post2039"] = dict(
 key="post2039", title="After the 2039 return", subtitle="Upper stage reverts to the grantors in 2039; flows shown for today's rules in a mean year (v2 model)",
 columns=["Inflow","Storage","Stage 1","Stage 2","Stage 3","Rhône"],
 nodes=nodes3, links=links3,
 shares=[["Anniviers",55.4],["Ergisch",18.1],["Turtmann-Unterems",11.9],["Oberems",9.4],["Canton du Valais",2.4],["Chippis",2.2],["Chalais",0.6]],
 notes=[
  "Upper stage (Moiry, Tourtemagne, Lona, Mottec, Vissoie) returns to the grantors on 31 Dec 2039 for an indemnity of 15.05 MCHF, at most ≈ 20 MCHF (R08 p1, p7; R09 p3). The Navizence stage stays under the 2004 concession to 2084 (R07 p5).",
  "Flows assume today's residual-flow rules and a mean year (10-yr mean inflow 265.5 hm³, plant volumes from BFE WASTA ÷ energy coefficients; R07 p8; R10; R06 p8–10). The future concession and operating rules are not yet decided (R09 p3).",
  "VS message gives 450 GWh/yr mean upper-stage production (R08 p7); WASTA expects 355 GWh for Mottec + Vissoie + Lona. Moiry raising (≈ 9 m, new Mottec pump) would need a separate convention (R07 p6; R08 p1).",
  "Grey bands: water not turbined (calibration against WASTA), Vissoie spill (≈ 20 hm³ in 2001, R12), and runoff not captured (BAFU MQN, indicative).",
 ],
 totals=dict(natural=r(TOTAL), laterals=r(lat), turt_rest=r(turt_rest3)),
)
for k, m in models.items():
    ins = {}; outs = {}
    for l in m["links"]:
        outs[l["source"]] = outs.get(l["source"],0)+l["value"]; ins[l["target"]] = ins.get(l["target"],0)+l["value"]
    srcs = [n["id"] for n in m["nodes"] if n["id"] not in ins]; sinks = [n["id"] for n in m["nodes"] if n["id"] not in outs]
    tot_in = sum(outs[s] for s in srcs); tot_out = sum(ins[s] for s in sinks)
    bad = [(n, round(ins[n]-outs[n],3)) for n in ins if n in outs and abs(ins[n]-outs[n])>0.01]
    print(k, "in", round(tot_in,2), "out", round(tot_out,2), "unbalanced nodes", bad)
json.dump(models, open("period_models.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k:m["totals"] for k,m in models.items()}, indent=1))
