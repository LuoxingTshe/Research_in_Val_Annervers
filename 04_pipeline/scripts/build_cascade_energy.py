"""Gougra cascade: mean-year water routing & energy model, v2 (2026-10-06).
Calibrated to BFE WASTA expected production per plant and FMG 2014 leaflet energy coefficients.
Run from project root: python3 04_pipeline/scripts/build_cascade_energy.py
Reads 02_outputs/flow_diagram_sources/{wasta_plants,mqn_points}.csv
Writes 02_outputs/gougra_cascade_energy/cascade_model.json and index.html (from template next to this script)."""
import csv, json, os, sys
G = 9.81
DAY = 86400
def hm3(ls_s, ls_w=None):            # L/s held Apr-Sep (183 d) / Oct-Mar (182 d) -> hm3/yr
    ls_w = ls_s if ls_w is None else ls_w
    return (ls_s/1000*183*DAY + ls_w/1000*182*DAY)/1e6
def rows(path): return list(csv.DictReader(open(path, encoding="utf-8-sig")))

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = os.path.join(ROOT, "02_outputs/flow_diagram_sources")
wasta = {r["name"]: r for r in rows(os.path.join(SRC, "wasta_plants.csv"))}
mqn = {r["point"]: r for r in rows(os.path.join(SRC, "mqn_points.csv"))}
num = lambda s: float(str(s).split()[0])

# ---- inputs ----
INFLOW_2025 = {"moiry":28.45, "tourt":47.56, "mottec":106.50, "vissoie":12.00}   # FMG RG 2025 p.9
MEAN_INFLOW = 265.5                                                              # FMG RG 2025 p.8, 10-yr mean
scale = MEAN_INFLOW / sum(INFLOW_2025.values())
inflow = {k: v*scale for k, v in INFLOW_2025.items()}                            # mean-year split (2025 shares)
COEF = {"mottec": (1.324+1.551)/2, "mottec_lo":1.324, "mottec_hi":1.551, "vissoie":0.986, "navizence":1.277}  # leaflet 2014
E_W = {"lona": num(wasta["Lona"]["production_expected_GWh"]), "mottec": num(wasta["Mottec"]["production_expected_GWh"]),
       "vissoie": num(wasta["Vissoie"]["production_expected_GWh"]), "vissoie_aux": num(wasta["Vissoie groupe auxiliaire"]["production_expected_GWh"]),
       "navizence": num(wasta["Navizence"]["production_expected_GWh"])}
HEAD = {"lona": num(wasta["Lona"]["fall_height"]), "mottec": num(wasta["Mottec"]["fall_height"]),
        "vissoie": num(wasta["Vissoie"]["fall_height"]), "navizence": num(wasta["Navizence"]["fall_height"])}
MW = {k: num(wasta[n]["turbine_max_MW"]) for k, n in [("lona","Lona"),("mottec","Mottec"),("vissoie","Vissoie"),("navizence","Navizence")]}
PUMP_GWH = num(wasta["Mottec"]["motor_energy_GWh"])                              # 30.2
PUMP_KWH_M3 = G*617/3600/0.85                                                    # storage pump, 617 m mean head, 85 %
eco = {"gougra": hm3(90,50), "stjean_reach": hm3(300), "below_vissoie": hm3(470), "fang": hm3(50)}   # Savoy p80-81
irr = {"roux_stluc":0.152, "briey":45/1000*139*DAY/1e6, "niouc":60/1000*139*DAY/1e6}                 # Savoy p101
snow = 0.0011*MEAN_INFLOW

# ---- turbined volumes implied by official expected production ----
V = {"mottec": E_W["mottec"]/COEF["mottec"], "vissoie": E_W["vissoie"]/COEF["vissoie"], "navizence": E_W["navizence"]/COEF["navizence"]}
V_range_mottec = (E_W["mottec"]/COEF["mottec_hi"], E_W["mottec"]/COEF["mottec_lo"])
lona_coef = G*HEAD["lona"]/3600*0.80
V["lona"] = E_W["lona"]/lona_coef

# ---- routing (mean year) ----
pumped = PUMP_GWH / PUMP_KWH_M3                       # storage-pump equivalent (upper bound on volume pumped by storage pump)
navi_release = eco["stjean_reach"] - eco["gougra"]
vis_to_river = eco["below_vissoie"] - eco["stjean_reach"]
upper_avail = inflow["moiry"] + inflow["tourt"] + pumped - eco["gougra"] - snow
upper_unturbined = upper_avail - V["mottec"]          # calibration term: spill / uncaptured / model overestimate
mottec_area_avail = inflow["mottec"] - navi_release - irr["roux_stluc"] - pumped
vis_overflow = V["mottec"] + mottec_area_avail - V["vissoie"]   # calibration term at Mottec intake / gallery
mottec_area_to_vis = mottec_area_avail - vis_overflow
reach300_total = eco["stjean_reach"] + upper_unturbined + vis_overflow
recaptured = upper_unturbined + vis_overflow           # river water above the 300 L/s, taken at Vissoie intake
irr_lower = irr["briey"] + irr["niouc"]
vis_area_to_navi = inflow["vissoie"] - vis_to_river - eco["fang"]
lower_avail = V["vissoie"] - irr_lower + recaptured + vis_area_to_navi
vissoie_spill = lower_avail - V["navizence"]          # derived; BGE 150 II 83: ~20 hm3 in 2001
vis_to_navi = V["vissoie"] - irr_lower - vissoie_spill
for k, v in {"upper_unturbined":upper_unturbined, "vis_overflow":vis_overflow, "vissoie_spill":vissoie_spill}.items():
    assert v > -1e-9, (k, v)
rhone = V["navizence"] + eco["below_vissoie"] + vissoie_spill + eco["fang"]
other = snow + irr["roux_stluc"] + irr_lower
assert abs(rhone + other - MEAN_INFLOW) < 1e-6, rhone + other

theor = {k: V[k]*G*HEAD[k]/3600 for k in ("lona","mottec","vissoie","navizence")}
eco_cost = (eco["gougra"]*(COEF["mottec"]+COEF["vissoie"]+COEF["navizence"])
            + navi_release*(COEF["vissoie"]+COEF["navizence"])
            + (vis_to_river+eco["fang"])*COEF["navizence"])

nodes = [
 ("src_moiry","Moiry","catchment incl. Lona",0,"src"),
 ("src_tourt","Tourtemagne","gallery ≤ 8 m³/s",0,"src"),
 ("pump_src","Pumped from Mottec basin","storage pump",0,"pump"),
 ("moiry","Moiry reservoir","77 hm³ live storage",1,"store"),
 ("mottec","Mottec plant","Stage 1",2,"plant"),
 ("snow","Snowmaking","Tsarmette offtake",2,"use"),
 ("src_mottec","Mottec area","Navizence intake + Moulins",2,"src"),
 ("upper_spill","Not turbined at Mottec","spill · uncaptured",2,"spill"),
 ("gougra","Gougra below dam","≥ 90 / 50 L/s",2,"eco"),
 ("vissoie","Vissoie plant","Stage 2",3,"plant"),
 ("irr_up","Bisse Roux + St-Luc","free quota",3,"use"),
 ("pump_sink","To storage pump","3.9 m³/s, back to Moiry",3,"pump"),
 ("reach300","St-Jean–Vissoie reach","≥ 300 L/s + spills",3,"eco"),
 ("src_vissoie","Vissoie area","incl. Fang",3,"src"),
 ("irr_low","Briey + Niouc","≤ 45 / < 60 L/s",4,"use"),
 ("navizence","Navizence plant","Stage 3 · Chippis",4,"plant"),
 ("river_low","Lower Navizence","≥ 470 L/s + Vissoie spill",4,"eco"),
 ("fang","Fang below intake","≥ 50 L/s",4,"eco"),
 ("rhone","Rhône","",5,"sink"),
]
links = [  # source, target, value, kind, uncertain
 ("src_moiry","moiry",inflow["moiry"],"power",False),
 ("src_tourt","moiry",inflow["tourt"],"power",False),
 ("pump_src","moiry",pumped,"pump",True),
 ("moiry","mottec",V["mottec"],"power",False),
 ("moiry","snow",snow,"use",True),
 ("moiry","upper_spill",upper_unturbined,"spill",True),
 ("moiry","gougra",eco["gougra"],"eco",False),
 ("mottec","vissoie",V["mottec"],"power",False),
 ("src_mottec","vissoie",mottec_area_to_vis,"power",False),
 ("src_mottec","irr_up",irr["roux_stluc"],"use",True),
 ("src_mottec","pump_sink",pumped,"pump",True),
 ("upper_spill","reach300",upper_unturbined,"spill",True),
 ("gougra","reach300",eco["gougra"],"eco",False),
 ("src_mottec","reach300",navi_release,"eco",True),
 ("src_mottec","reach300",vis_overflow,"spill",True),
 ("vissoie","irr_low",irr_lower,"use",True),
 ("vissoie","navizence",vis_to_navi,"power",False),
 ("reach300","navizence",recaptured,"power",True),
 ("src_vissoie","navizence",vis_area_to_navi,"power",False),
 ("vissoie","river_low",vissoie_spill,"spill",True),
 ("reach300","river_low",eco["stjean_reach"],"eco",False),
 ("src_vissoie","river_low",vis_to_river,"eco",True),
 ("src_vissoie","fang",eco["fang"],"eco",False),
 ("navizence","rhone",V["navizence"],"power",False),
 ("river_low","rhone",eco["below_vissoie"]+vissoie_spill,"eco",False),
 ("fang","rhone",eco["fang"],"eco",False),
]
DISPLAY_FLOOR = 4.0
r = lambda x, n=2: round(x, n)
mqn_check = {"Moiry dam + Lona": float(mqn["Gougra_Moiry_dam"]["annual_hm3"])+float(mqn["Lona_torrent"]["annual_hm3"]),
             "Turtmänna 1728 m (upper bound)": float(mqn["Turtmaenna_1728m"]["annual_hm3"]),
             "Navisence at Mottec + Moulins (Vuibiesse) + Nava": float(mqn["Navisence_Mottec_intake"]["annual_hm3"])+float(mqn["Moulins_StLuc_intake_Vuibiesse"]["annual_hm3"])+float(mqn["Nava_torrent"]["annual_hm3"]),
             "Fang": float(mqn["Fang_torrent"]["annual_hm3"])}
model = {
 "version": "v2 2026-10-06 mean year",
 "basis": "Mean year: FMG 10-yr mean inflow 265.5 hm³ split by 2025 reporting-area shares; stage volumes calibrated to BFE WASTA expected production ÷ leaflet energy coefficients",
 "inflow": {k: r(v) for k, v in inflow.items()}, "inflow_total": MEAN_INFLOW, "scale_from_2025": r(scale,4),
 "mqn_check_hm3": {k: r(v,1) for k, v in mqn_check.items()},
 "eco_hm3": {k: r(v,3) for k, v in eco.items()}, "navi_release": r(navi_release,3), "vis_to_river": r(vis_to_river,3),
 "irr_hm3": {k: r(v,3) for k, v in irr.items()}, "snow_hm3": r(snow,3), "other_total": r(other,3),
 "pumped_hm3": r(pumped), "pump_GWh": PUMP_GWH, "pump_kWh_m3": r(PUMP_KWH_M3,3),
 "upper_unturbined": r(upper_unturbined), "vis_overflow": r(vis_overflow), "recaptured": r(recaptured), "vissoie_spill": r(vissoie_spill),
 "V_hm3": {k: r(v,1) for k, v in V.items()}, "V_mottec_range": [r(V_range_mottec[0],1), r(V_range_mottec[1],1)],
 "coef": COEF, "head_m": HEAD, "turbine_MW": MW,
 "E_wasta_GWh": E_W, "E_wasta_total": r(sum(E_W.values()),2),
 "E_theor_GWh": {k: r(v,1) for k, v in theor.items()}, "E_theor_total": r(sum(theor.values()),1),
 "eco_cost_GWh": r(eco_cost,1),
 "nodes": [dict(id=a,name=b,sub=c,col=d,kind=e) for a,b,c,d,e in nodes],
 "display_floor": DISPLAY_FLOOR,
 "links": [dict(source=a,target=b,value=r(v,3),display=r(max(v,DISPLAY_FLOOR) if u else v,3),kind=t,uncertain=u) for a,b,v,t,u in links],
}
if __name__ == "__main__":
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "02_outputs/gougra_cascade_energy")
    os.makedirs(out, exist_ok=True)
    json.dump(model, open(os.path.join(out,"cascade_model.json"),"w"), ensure_ascii=False, indent=1)
    tpl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cascade_energy_template.html")
    if os.path.exists(tpl):
        html = open(tpl, encoding="utf-8").read().replace("/*__MODEL__*/null", json.dumps(model, ensure_ascii=False))
        open(os.path.join(out,"index.html"),"w",encoding="utf-8").write(html)
    print(json.dumps({k: model[k] for k in ("inflow","mqn_check_hm3","pumped_hm3","upper_unturbined","vis_overflow","recaptured","vissoie_spill","V_hm3","V_mottec_range","E_theor_GWh","E_theor_total","E_wasta_total","eco_cost_GWh")}, ensure_ascii=False, indent=1))
