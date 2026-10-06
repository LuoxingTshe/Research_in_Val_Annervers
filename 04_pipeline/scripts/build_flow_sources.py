#!/usr/bin/env python3
"""Build 02_outputs/flow_diagram_sources/ from web extracts in 04_pipeline/work/web_sources/.

Run from the project root:  python3 04_pipeline/scripts/build_flow_sources.py
Inputs (saved 2026-10-06, see README of the output folder):
  bafu_mqn_points_gougra.json   BAFU "Mittlere Abflüsse und Regime" (MQN, natural) at chosen points
  bfe_wasta_gougra_2025-12-31.json  BFE WASTA statistic for the Gougra plants
Outputs: mqn_points.csv, wasta_plants.csv, evidence_additions.csv, crosscheck.json
"""
import csv, json, os

SRC = "04_pipeline/work/web_sources"
OUT = "02_outputs/flow_diagram_sources"
os.makedirs(OUT, exist_ok=True)
SEC_PER_YEAR = 365.25 * 86400
MONTHS = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "dez"]
DAYS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
WINTER = {"okt", "nov", "dez", "jan", "feb", "mar"}

# Which river segment to keep at each sampled point (largest discharge in the box,
# except where a tributary is meant). Points chosen from swissNAMES3D / WASTA coordinates.
POINT_NOTES = {
    "Gougra_Moiry_dam": ("Gougra at Moiry dam (natural, whole Moiry catchment)", "max"),
    "Lona_torrent": ("Torrent de Lona below Lac de Lona (diverted to Moiry via Lona plant)", "max"),
    "Navisence_Mottec_intake": ("Navisence at Mottec intake (Navizence PE, 12 m3/s nominal)", "max"),
    "Navisence_StJean_label": ("Navisence near St-Jean (above Moulins confluence)", "max"),
    "Nava_torrent": ("Torrent de Nava (PE de Nava, Vissoie stage)", "max"),
    "Moulins_StLuc_intake_Vuibiesse": ("Torrent des Moulins at Vuibiesse (PE Moulins à St-Luc)", "max"),
    "Moulins_lower_Vissoie": ("Torrent des Moulins near Vissoie (tributary segment)", "min"),
    "Navisence_Vissoie": ("Navisence at Vissoie (above Vissoie intake)", "max"),
    "Fang_torrent": ("Torrent de Fang (lower-stage concession, 50 L/s residual)", "max"),
    "Navisence_Chippis": ("Navisence above Rhône at Chippis (natural, no Tourtemagne water)", "max"),
    "Turtmaenna_Turtmannsee": ("Turtmänna at Turtmann dam (glacier catchment only)", "max"),
    "Turtmaenna_1728m": ("Turtmänna at 1728 m, below Brändji/Blüomatt/Frili confluences", "max"),
    "Turtmaenna_Turtmann": ("Turtmänna at Turtmann village (natural, valley outlet)", "max"),
}

mqn = json.load(open(f"{SRC}/bafu_mqn_points_gougra.json"))
rows = []
for key, (label, pick) in POINT_NOTES.items():
    hits = mqn["sites"].get(key, {}).get("hits", [])
    if not hits:
        continue
    h = (max if pick == "max" else min)(hits, key=lambda x: x["mqn_jahr"])
    vol = {m: h["mqn_" + m] * d * 86400 / 1e6 for m, d in zip(MONTHS, DAYS)}
    annual = sum(vol.values())
    winter = sum(v for m, v in vol.items() if m in WINTER)
    rows.append({
        "point": key, "description": label, "segment_id": h["id"],
        "lv95_e": mqn["sites"][key]["lv95"][0], "lv95_n": mqn["sites"][key]["lv95"][1],
        "mqn_year_m3s": round(h["mqn_jahr"], 3), "annual_hm3": round(annual, 1),
        "winter_Oct_Mar_hm3": round(winter, 1), "winter_share": round(winter / annual, 3),
        "regime": h["regimetyp"],
        **{f"q_{m}_m3s": round(h["mqn_" + m], 3) for m in MONTHS},
    })
with open(f"{OUT}/mqn_points.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
Q = {r["point"]: r for r in rows}

# Energy coefficients (kWh/m3) from the Gougra leaflet 2014 / Alpiq plant page.
COEF = {"Mottec": (1.324, 1.551), "Vissoie": (0.986, 0.986), "Navizence": (1.277, 1.277)}
wasta = json.load(open(f"{SRC}/bfe_wasta_gougra_2025-12-31.json"))["data"]["features"]
wrows = []
for ft in wasta:
    a = ft["attributes"]
    name = a["name"]
    c = COEF.get(name)
    wrows.append({
        "wasta_id": ft["id"], "name": name, "location": a["location"],
        "type_fr": a["hydropowerplanttype_fr"], "status_fr": a["hydropowerplantoperationalstatus_fr"],
        "start": a["beginningofoperation"], "fall_height": a["fallheight"],
        "turbine_max_MW": a["performanceturbinemaximum"], "generator_max_MW": a["performancegeneratormaximum"],
        "production_expected_GWh": a["productionexpected"], "pump_input_max_MW": a["pumpspowerinputmaximum"],
        "motor_energy_GWh": a["enginepowerdemand"], "date_of_statistic": a["dateofstatistic"],
        "implied_turbined_hm3": (f"{a['productionexpected']/c[1]:.1f}–{a['productionexpected']/c[0]:.1f}"
                                 if c and c[0] != c[1] else (round(a["productionexpected"] / c[0], 1) if c else "")),
        "lv95": ft["geometry"]["points"][0] if "geometry" in ft else "",
    })
with open(f"{OUT}/wasta_plants.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(wrows[0].keys()))
    w.writeheader(); w.writerows(wrows)
W = {r["name"]: r for r in wrows}

gougra_sum = sum(W[n]["production_expected_GWh"] for n in ["Lona", "Mottec", "Vissoie", "Vissoie groupe auxiliaire", "Navizence"])
model_2025 = {"Mottec": 73.6, "Vissoie": 172.7, "Navizence": 176.5}  # gougra_cascade_energy README, hm3
hydraulicity_2025 = 0.73  # FMG RG 2025 p.6
check = {
    "wasta_expected_production_sum_GWh": round(gougra_sum, 2),
    "wasta_motor_energy_Mottec_GWh": W["Mottec"]["motor_energy_GWh"],
    "published_mean_production_GWh": {"Alpiq page": 643, "leaflet 2014 gross": 650, "FMG decadal mean (RG 2025)": 675},
    "stage_volume_hm3": {
        n: {"wasta_implied": W[n]["implied_turbined_hm3"],
            "cascade_model_2025": model_2025[n],
            "cascade_model_2025_div_hydraulicity": round(model_2025[n] / hydraulicity_2025, 1)}
        for n in model_2025},
    "natural_runoff_hm3": {
        "Navisence_Chippis": Q["Navisence_Chippis"]["annual_hm3"],
        "Turtmaenna_1728m_upper_bound_of_transfer": Q["Turtmaenna_1728m"]["annual_hm3"],
        "Gougra_Moiry_dam": Q["Gougra_Moiry_dam"]["annual_hm3"],
        "Navisence_Mottec_intake": Q["Navisence_Mottec_intake"]["annual_hm3"],
        "FMG_decadal_mean_inflow": 265.5, "FMG_2024": 203.7, "FMG_2025": 194.9},
    "winter_share_natural_runoff": {k: v["winter_share"] for k, v in Q.items()},
    "production_winter_share_leaflet_2014": 0.52,
    "moiry_live_storage_share_of_mean_inflow": round(77 / 265.5, 3),
    "balance_at_Chippis_hm3": {
        "natural_Navisence_plus_Turtmaenna_1728m": round(Q["Navisence_Chippis"]["annual_hm3"] + Q["Turtmaenna_1728m"]["annual_hm3"], 1),
        "minus_Navizence_turbined_wasta_implied": round(W["Navizence"]["production_expected_GWh"] / 1.277, 1),
        "note": "remainder = residual flows + Vissoie spill (~20 hm3/yr in 2001, BGE 150 II 83) + irrigation + uncaptured lateral runoff + overestimate of Turtmänna transfer (1728 m point lies below the intakes)",
    },
}
check["balance_at_Chippis_hm3"]["remainder"] = round(
    check["balance_at_Chippis_hm3"]["natural_Navisence_plus_Turtmaenna_1728m"]
    - check["balance_at_Chippis_hm3"]["minus_Navizence_turbined_wasta_implied"], 1)
json.dump(check, open(f"{OUT}/crosscheck.json", "w"), ensure_ascii=False, indent=1)

# Curated evidence additions (same columns as moiry_flow_allocation/flow_evidence.csv, plus url).
EV = [
 ("N01", "topology", "Tourtemagne intakes", "Galerie Tourtemagne–Barneusa → Mottec", "Brändji, Frili, Blüomatt, Nebenbach L/R, Turtmänna; Barneusa PE on the gallery", "list", "", "current assets 2021", "documented", "VS_CONV2022", "PDF 19–21 (asset inventory)", "Intakes as asset lines 0301A–F; gallery Tourtemagne–Barneusa 0303A004"),
 ("N02", "topology", "Moiry", "Mottec", "Galerie de Moiry–Tsarmette + puits blindé", "list", "", "current", "documented", "VS_CONV2022; FMG_RG2025", "PDF 19–21; RG p.4–5", "Tsarmette = name of the Moiry–Mottec fall (RCT rehab, back in service June 2025)"),
 ("N03", "topology", "Vissoie-stage intakes", "Bassin de Vissoie", "PE Nava; PE Moulins à St-Luc; PE Moulins à Vissoie; PE St-Jean (groupe aux.); PE Navizence (Vissoie) with dotation", "list", "", "current", "documented", "VS_CONV2022", "PDF 20–21", "PE Navizence (Vissoie) dotation asset dated 2017-01-01; galerie Mottec–Biolec"),
 ("N04", "ecology", "Moiry", "Gougra", "Dotation de Moiry par le réseau des RMGZ", "asset", "", "since 2021-01-01", "documented", "VS_CONV2022", "PDF 20 (0332A008)", "Residual-flow release routed through the Grimentz-Zinal ski-lift (snowmaking) network; links ecology and snowmaking nodes"),
 ("Q01", "capacity", "Tourtemagne", "Mottec", 8, "max", "m3/s", "design", "documented", "LEPORELLO2014", "PDF 7", "Galerie 4,700 m, Ø2.2 m"),
 ("Q02", "capacity", "Navisence intake at Mottec", "Bassin de Mottec", 12, "nominal (max 18)", "m3/s", "design", "documented", "LEPORELLO2014", "PDF 9", ""),
 ("Q03", "storage", "Bassin de compensation", "Mottec", 0.15, "capacity", "hm3", "design", "documented", "LEPORELLO2014", "PDF 9", "Vissoie basin 0.05 hm3 (PDF 10)"),
 ("Q04", "capacity", "Moiry", "Gougra (spillway / bottom outlet)", "60 / 55", "max", "m3/s", "design", "documented", "LEPORELLO2014", "PDF 7", "Flood/emptying paths for the Sankey; no annual volumes published"),
 ("Q05", "energy_coef", "Moiry–Mottec / Mottec–Vissoie / Vissoie–Chippis", "", "1.324–1.551 / 0.986 / 1.277", "coefficient", "kWh/m3", "design", "documented", "LEPORELLO2014; ALPIQ_PAGE", "PDF 8–10", "Converts stage energy ↔ turbined volume"),
 ("Q06", "pump", "Navisence (Mottec basin)", "Moiry", 3.9, "max", "m3/s", "design", "documented", "LEPORELLO2014", "PDF 8", "Storage pump, 3 stages, head 570–664 m, 23 MW"),
 ("Q07", "pump", "Tourtemagne", "Moiry", 6, "max", "m3/s", "design", "documented", "LEPORELLO2014", "PDF 8", "Siphon (back-pressure) pump, head 0–126 m, 6.75 MW"),
 ("E01", "energy", "Mottec", "", 137.05, "expected", "GWh/yr", "WASTA 2025-12-31", "official_statistic", "BFE_WASTA", "feature 503200", "Head 640 m; turbine 102 MW; pump input 87 MW; motor energy 30.2 GWh/yr"),
 ("E02", "energy", "Vissoie", "", 213.0, "expected", "GWh/yr", "WASTA 2025-12-31", "official_statistic", "BFE_WASTA", "feature 503300", "Head 437 m; 57 MW turbine; status 'en transformation'; aux. group 3.1 GWh (503350)"),
 ("E03", "energy", "Navizence", "", 298.7, "expected", "GWh/yr", "WASTA 2025-12-31", "official_statistic", "BFE_WASTA", "feature 503400", "Head 591 m; 71.1 MW turbine"),
 ("E04", "energy", "Lona", "", 2.0, "expected", "GWh/yr", "WASTA 2025-12-31", "official_statistic", "BFE_WASTA", "feature 503100", "Head 319 m"),
 ("E05", "energy", "Gougra total", "", "650 (52 % winter); net 570; pumping 30", "gross", "GWh/yr", "c. 2014", "documented", "LEPORELLO2014", "PDF 3", "Only published winter/summer split found"),
 ("E06", "energy", "Gougra total", "", "2024: 607; decadal mean ~675", "turbined", "GWh/yr", "2024 / 2016–2025", "documented", "FMG_RG2025", "PDF 10", "Moiry–Mottec stopped 6 months in 2024–25 (RCT)"),
 ("H01", "inflow", "Gougra system", "", "2024: 203.7; decadal mean 265.5", "natural inflow", "hm3/yr", "2024 / 10-yr", "documented", "FMG_RG2025", "PDF 8", "Lets the 2025 model be scaled to a mean year (2025 hydraulicity 73 %)"),
 ("H02", "inflow", "sub-catchments", "", "see mqn_points.csv", "natural mean monthly", "m3/s", "MQ-CH reference period", "modelled", "BAFU_MQN", "layer ch.bafu.mittlere-abfluesse", "Natural (unregulated) monthly means per river segment; basis for a seasonal Sankey"),
 ("S01", "spill", "Bassin de Vissoie", "Navisence (not turbined)", "≈20", "summer spill", "hm3/yr", "2001 return report", "court_finding", "BGE_150_II_83", "facts A", "Vissoie–Niouc gallery under-sized; new 15 m3/s gallery (GVN) still in permitting (RG 2025)"),
 ("S02", "storage", "Moiry raising (RBM)", "", "+9 m; >12 hm3; 40–50 GWh shifted summer→winter; new pump at Mottec", "project", "", "2026 status", "project", "VS_STRAT_EAU; BLICK2026; FMG_RG2025", "", "Scenario layer, not current state"),
 ("L01", "rights", "Upper-stage concessions (2039)", "", "Anniviers 55.4; Ergisch 18.1; Turtmann-Unterems 11.9; Oberems 9.4; Canton 2.4; Chippis 2.2; Chalais 0.6", "share of conceded hydraulic power", "%", "estimate for 2039", "documented", "VS_CONV2022", "PDF 3", "Allows attributing theoretical power to Tourtemagne vs Anniviers waters"),
 ("L02", "rights", "All FMG concessions", "", "Anniviers 59.7; Ergisch 14.5; Turtmann-Unterems 9.4; Oberems 7.5; Chippis 5.5; Etat 1.9; Chalais 1.5", "share of theoretical power (water fees 2025)", "%", "2025", "documented", "FMG_RG2025", "PDF 5", ""),
 ("L03", "rights", "Navizence concession (2004–2084)", "", "spilled water not part of 'débits utilisables'", "legal", "", "2024-01-05", "court_ruling", "BGE_150_II_83", "consid. 7.5.3", "Fiscal basis differs from physical flow: keep spill as its own Sankey band"),
]
cols = ["id", "category", "source_node", "target_node", "value", "operator", "unit", "period", "status", "source_ref", "pdf_page", "note"]
with open(f"{OUT}/evidence_additions.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(cols); w.writerows(EV)
print(json.dumps(check, ensure_ascii=False, indent=1))
