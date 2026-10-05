"""Gougra cascade: theoretical water routing & energy model (2025 inflows + current residual-flow rules).
Run from project root: python3 04_pipeline/scripts/build_cascade_energy.py
Writes 02_outputs/gougra_cascade_energy/cascade_model.json and index.html (from template)."""
import json, os, sys
G = 9.81
SEC_S = 183*86400   # Apr-Sep
SEC_W = 182*86400   # Oct-Mar
def hm3(ls_s, ls_w=None):
    ls_w = ls_s if ls_w is None else ls_w
    return (ls_s/1000*SEC_S + ls_w/1000*SEC_W)/1e6
def kwh_per_m3(h): return G*h/3600

# ---- inputs (sources in comments) ----
inflow = {"moiry":28.45, "tourt":47.56, "mottec":106.50, "vissoie":12.00}  # FMG RG 2025 p.9 (hm3)
H = {"lona":331, "mottec":685, "mottec_tourt":2177-1564, "vissoie":439, "navizence":590}  # Robert 1962 p2-3; Mottier p3; Savoy p79
eco = {"gougra": hm3(90,50), "stjean_reach": hm3(300), "below_vissoie": hm3(470), "fang": hm3(50)}  # Savoy p80-81
irr = {"roux_stluc":0.152,                      # 120k+32k m3 free quota, Savoy p101
       "briey":45/1000*139*86400/1e6,           # 45 L/s, 30 Apr-15 Sep (season of 1979 deed; 2017 season unconfirmed)
       "niouc":60/1000*139*86400/1e6}           # <60 L/s upper bound, season assumed = Briey
snow = 0.0011*sum(inflow.values())              # 0.11 % of catchment water, Savoy p90
ETA = 0.85
lona_share = 6.2/35.5                           # Lona catchment share of Moiry group (Robert Tab.1)

# ---- routing ----
navi_release = eco["stjean_reach"] - eco["gougra"]        # extra release at Mottec intake (upper bound)
vis_to_river = eco["below_vissoie"] - eco["stjean_reach"]  # Vissoie-area water left in river
up = inflow["moiry"] + inflow["tourt"]
mottec_q = up - eco["gougra"] - snow
moiry_part = inflow["moiry"] - eco["gougra"] - snow
mottec_area_to_vis = inflow["mottec"] - navi_release - irr["roux_stluc"]
vissoie_q = mottec_q + mottec_area_to_vis
irr_lower = irr["briey"] + irr["niouc"]
vis_area_to_navi = inflow["vissoie"] - vis_to_river - eco["fang"]
navi_q = vissoie_q - irr_lower + vis_area_to_navi
other = snow + irr["roux_stluc"] + irr_lower
rhone = navi_q + eco["below_vissoie"] + eco["fang"]
assert abs(rhone + other - sum(inflow.values())) < 1e-6

E = {
 "lona": inflow["moiry"]*lona_share*kwh_per_m3(H["lona"]),
 "mottec": moiry_part*kwh_per_m3(H["mottec"]) + inflow["tourt"]*kwh_per_m3(H["mottec_tourt"]),
 "vissoie": vissoie_q*kwh_per_m3(H["vissoie"]),
 "navizence": navi_q*kwh_per_m3(H["navizence"]),
}
# eco cost upper bound (net): what the released water would have produced
k = {s: kwh_per_m3(H[s])*ETA for s in ("mottec","vissoie","navizence")}
eco_cost = (eco["gougra"]*(k["mottec"]+k["vissoie"]) + navi_release*k["vissoie"]
            + (vis_to_river+eco["fang"])*k["navizence"])

nodes = [
 ("src_moiry","Moiry","catchment incl. Lona",0,"src"),
 ("src_tourt","Tourtemagne","inter-basin transfer",0,"src"),
 ("moiry","Moiry reservoir","77 hm³ live storage",1,"store"),
 ("mottec","Mottec plant","Stage 1",2,"plant"),
 ("snow","Snowmaking","Tsarmette offtake",2,"use"),
 ("src_mottec","Mottec area","upper Navizence + Moulins",2,"src"),
 ("gougra","Gougra below dam","≥ 90 / 50 L/s",2,"eco"),
 ("vissoie","Vissoie plant","Stage 2",3,"plant"),
 ("irr_up","Bisse Roux + St-Luc","free quota",3,"use"),
 ("src_vissoie","Vissoie area","incl. Fang",3,"src"),
 ("reach300","St-Jean–Vissoie reach","≥ 300 L/s",3,"eco"),
 ("irr_low","Briey + Niouc","≤ 45 / < 60 L/s",4,"use"),
 ("navizence","Navizence plant","Stage 3 · Chippis",4,"plant"),
 ("fang","Fang below intake","≥ 50 L/s",4,"eco"),
 ("reach470","Below Vissoie intake","≥ 470 L/s",4,"eco"),
 ("rhone","Rhône","",5,"sink"),
]
# (source, target, value, kind, uncertain)
links = [
 ("src_moiry","moiry",inflow["moiry"],"power",False),
 ("src_tourt","moiry",inflow["tourt"],"power",False),
 ("moiry","mottec",mottec_q,"power",False),
 ("moiry","snow",snow,"use",True),
 ("moiry","gougra",eco["gougra"],"eco",False),
 ("mottec","vissoie",mottec_q,"power",False),
 ("src_mottec","vissoie",mottec_area_to_vis,"power",False),
 ("src_mottec","irr_up",irr["roux_stluc"],"use",True),
 ("src_mottec","reach300",navi_release,"eco",True),
 ("gougra","reach300",eco["gougra"],"eco",False),
 ("vissoie","irr_low",irr_lower,"use",True),
 ("vissoie","navizence",vissoie_q-irr_lower,"power",False),
 ("src_vissoie","navizence",vis_area_to_navi,"power",False),
 ("src_vissoie","fang",eco["fang"],"eco",False),
 ("src_vissoie","reach470",vis_to_river,"eco",True),
 ("reach300","reach470",eco["stjean_reach"],"eco",False),
 ("navizence","rhone",navi_q,"power",False),
 ("fang","rhone",eco["fang"],"eco",False),
 ("reach470","rhone",eco["below_vissoie"],"eco",False),
]
DISPLAY_FLOOR = 4.0   # hm³: minimum drawn width for uncertain / bound values (not to scale)
r = lambda x,n=2: round(x,n)
model = {
 "basis":"FMG 2025 inflow areas + current residual-flow rules; all remaining water assumed to pass every downstream stage (theoretical upper bound)",
 "inflow":inflow, "inflow_total":r(sum(inflow.values())),
 "eco_hm3":{k_:r(v,3) for k_,v in eco.items()}, "navi_release":r(navi_release,3), "vis_to_river":r(vis_to_river,3),
 "irr_hm3":{k_:r(v,3) for k_,v in irr.items()}, "snow_hm3":r(snow,3), "other_total":r(other,3),
 "stage_hm3":{"lona_est":r(inflow["moiry"]*lona_share),"mottec":r(mottec_q),"vissoie":r(vissoie_q),"navizence":r(navi_q)},
 "E_gross_GWh":{k_:r(v,1) for k_,v in E.items()}, "E_gross_total":r(sum(E.values()),1),
 "E_net_GWh_eta":ETA, "E_net_total":r(sum(E.values())*ETA,1),
 "eco_cost_net_GWh_upper":r(eco_cost,1),
 "nodes":[dict(id=a,name=b,sub=c,col=d,kind=e) for a,b,c,d,e in nodes],
 "display_floor":DISPLAY_FLOOR,
 "links":[dict(source=a,target=b,value=r(v,3),display=r(max(v,DISPLAY_FLOOR) if u else v,3),kind=t,uncertain=u) for a,b,v,t,u in links],
}
if __name__=="__main__":
    out = sys.argv[1] if len(sys.argv)>1 else "02_outputs/gougra_cascade_energy"
    os.makedirs(out, exist_ok=True)
    json.dump(model, open(os.path.join(out,"cascade_model.json"),"w"), ensure_ascii=False, indent=1)
    tpl = os.path.join(os.path.dirname(os.path.abspath(__file__)),"cascade_energy_template.html")
    if os.path.exists(tpl):
        html = open(tpl,encoding="utf-8").read().replace("/*__MODEL__*/null", json.dumps(model,ensure_ascii=False))
        open(os.path.join(out,"index.html"),"w",encoding="utf-8").write(html)
    print(json.dumps({k_:model[k_] for k_ in ("stage_hm3","E_gross_GWh","E_gross_total","E_net_total","eco_hm3","navi_release","vis_to_river","irr_hm3","snow_hm3","eco_cost_net_GWh_upper")},ensure_ascii=False,indent=1))
