"""Merge the QGIS point/line GeoJSON layers into one object-level layer.

Reads 02_outputs/qgis_wgs84_package/{points,lines}_wgs84{,_classified}.geojson
(one feature per object-event) and writes one feature per object to
02_outputs/concession_objects_merged/objects_{points,lines}_wgs84.geojson, with:
  - Feature_Type and the existing Category / Transition_Year
  - Built_Year (+ note, basis, source), researched 2026-10-08 (table below)
  - Concession_1..N: every event year (old `Value` field) kept in its own field,
    with Concession_n_Event describing it (event, status, record ID).

The four input files were deleted from the working tree on 2026-10-08; when they
are missing they are read from git commit SRC_COMMIT.

Run from the project root: python3 04_pipeline/scripts/build_merged_objects.py
"""
import json
import subprocess
from pathlib import Path

SRC = Path("02_outputs/qgis_wgs84_package")
SRC_COMMIT = "8e39105"
OUT = Path("02_outputs/concession_objects_merged")

# Object_ID: (Feature_Type, Built_Year, Built_Year_Note, Built_Year_Basis, Built_Year_Source)
# Built_Year = first construction / commissioning year of the feature (or first written
# mention for old bisses). Basis: 联网 = web, 文献 = project sources, 推测 = inferred.
BUILT = {
    "P01": ("水电站", 1958, "1958年12月两组机组投运；2018–2025年改造（69→87 MW）", "联网+文献",
            "Alpiq新闻稿（Mottec, first commissioned 1958）；Mottier 1959 p3；Savoy 2025 p79"),
    "P02": ("水电站", 1958, "1958年5–6月三组机组相继投运；2025年前后改造", "联网+文献",
            "Alpiq新闻（Vissoie commissioned 1958）；Mottier 1959 p3"),
    "P03": ("水电站（小型自动电站）", 1961, "Lona引水1958年才决定，工程1961年完工；1000 kW自动电站", "文献",
            "Robert 1962 p2；Hoeffleur 1962 p10"),
    "P04": ("水电站", 1908, "AIAG（后Alusuisse）Chippis厂1905年购得Navizence水权，1908年投产；1954/55年为Gougra改造", "联网+文献",
            "HLS《Alusuisse》；Robert 1962 p3"),
    "P05": ("坝体（拱坝）", 1958, "1954–1958年建设；1960年首次蓄满", "联网+文献",
            "swissdams.ch；Savoy 2025 p78；Stucky 1962 p6"),
    "P06": ("坝体（拱坝）", 1958, "1957–1958年建设", "联网+文献",
            "swissdams.ch（Tourtemagne）；HLS；Savoy 2025 p78"),
    "P07": ("坝体（空腹重力坝）", 1950, "1947年开工，1950年完工（swissdams）；Savoy记1948/49起分期投用、1952年最终完工", "联网+文献",
            "swissdams.ch（Cleuson）；Savoy 2025 p24–25"),
    "P08": ("坝体（拱坝）", 1969, "坝体1969年建成；Veytaux电站1971年投运（1966–1971年施工）", "联网",
            "Lausanne SiL（Barrage de l'Hongrin）；alpesvaudoises.ch"),
    "P09": ("坝体（拱坝）", 1969, "同Hongrin北坝：1969年建成，1971年投运", "联网",
            "Lausanne SiL（Barrage de l'Hongrin）；alpesvaudoises.ch"),
    "P10": ("水电站", 1998, "1993–1998年建设，1998年投运（1999年落成）；2000年压力井破裂停运，约2010年恢复", "联网+文献",
            "nendaz.ch（Bieudron）；Savoy 2025 p24"),
    "P11": ("餐厅建筑", 1958, "估计值：由Moiry坝施工期（1954–1958）木板房改作餐厅，改用年份不详；1989年雪崩损毁后以砖石重建", "推测",
            "Savoy 2025 p86（访谈11）"),
    "L01": ("河流", None, "天然河流", "不适用", ""),
    "L02": ("河流", None, "天然河流", "不适用", ""),
    "L03": ("河流", None, "天然河流", "不适用", ""),
    "L05": ("溪流", None, "天然溪流", "不适用", ""),
    "L08": ("溪流", None, "天然溪流", "不适用", ""),
    "L09": ("溪流", None, "天然溪流", "不适用", ""),
    "L10": ("溪流", None, "天然溪流", "不适用", ""),
    "L12": ("溪流", None, "天然溪流", "不适用", ""),
    "L13": ("灌渠（bisse）", 1908, "推测：其水源和水权依赖Vissoie–Niouc隧洞（AIAG Navizence工程，1908年投产），不属旧有水权；喷灌网1988、2003、2008年分期建成", "推测",
            "Savoy 2025 p82、p95、p100；bisses-valais.ch（Bisse de Niouc）"),
    "L14": ("灌渠（bisse）", 1922, "现线路：取水口20世纪初移至对岸，经1922年落成的Niouc悬索输水桥过峡谷；前身Bisse des Sarrasins约15世纪", "联网+文献",
            "fr.wikipedia（Pont suspendu de Niouc）；bisses-valais.ch（Bisse de Briey）；Savoy 2025 p81、p100"),
    "L15": ("灌渠（bisse）", 1578, "最早见于1578年档案（建成不晚于此）；1825年大修，1939年部分改管", "文献",
            "Commune d'Anniviers 2017 bisse清单 §9.1"),
    "L16": ("灌渠（bisse）", 1593, "最早见于1593年记载（建成不晚于此）", "文献",
            "Commune d'Anniviers 2017 bisse清单 §8.1"),
    "L17": ("灌渠（bisse）", 1500, "估计值：旅游资料称起源于15世纪，2026年徒步报告称约500年前凿岩而成", "联网（推测取值）",
            "lacote-tourisme.ch（Bisse de Ricard）；cas-diablerets.ch 2026"),
    "L25": ("攀岩路线（via ferrata）", 2005, "2005年建成；悬索桥2009年增设", "联网+文献",
            "sac-cas.ch（Moiry via ferrata）；Savoy 2025 p94（2005–06协议）"),
    "L26": ("灌渠（bisse）", 1876, "1865年开工，诉讼中断后1874年复工，1876年通水；1964/1966年停用", "联网+文献",
            "HLS《Saxon》；nendaz.ch（Bisse de Saxon）；Savoy 2025 p27"),
    "L27": ("河流", None, "天然河流", "不适用", ""),
    "L33": ("河流", None, "天然河流", "不适用", ""),
    "L34": ("河流", None, "天然河流", "不适用", ""),
    "L35": ("河流", None, "天然河流", "不适用", ""),
    "L38": ("灌渠（Suone）", None, "未知：仅知1922年前已存在（当年由Stalden市镇收购）；网上未查到建成年份", "未知",
            "Bellwald p.139（访谈回忆）"),
}


def load(name):
    path = SRC / name
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = subprocess.run(["git", "show", f"{SRC_COMMIT}:{path.as_posix()}"],
                              capture_output=True, check=True).stdout.decode("utf-8")
    return json.loads(text)["features"]


def event_text(p):
    if p["Value"] is None and p["Year_Min"] is not None:
        when = f"{p['Year_Min']}–{p['Year_Max']} "
    elif p["Value"] is None:
        when = "年份不详 "
    else:
        when = ""
    return f"{when}{p['Event']}（{p['Event_Status']}；{p['Record_ID']}）"


def sort_key(p):
    year = p["Value"] if p["Value"] is not None else p["Year_Min"]
    return (year is None, year or 0)


def main():
    objects = {}
    for raw, classified in [("points_wgs84.geojson", "points_wgs84_classified.geojson"),
                            ("lines_wgs84.geojson", "lines_wgs84_classified.geojson")]:
        for f, c in zip(load(raw), load(classified), strict=True):
            p, cp = f["properties"], c["properties"]
            assert p["Name"] == cp["Name"] and f["geometry"] == c["geometry"]
            obj = objects.setdefault(p["Object_ID"], {"geometry": f["geometry"], "p": p, "c": cp, "events": []})
            assert obj["geometry"] == f["geometry"], p["Row_ID"]
            obj["events"].append(p)

    assert set(objects) == set(BUILT), set(objects) ^ set(BUILT)
    n_max = max(len(o["events"]) for o in objects.values())

    features = []
    for oid, o in objects.items():
        ftype, year, note, basis, source = BUILT[oid]
        props = {
            "Object_ID": oid,
            "Name": o["p"]["Name"],
            "Feature_Type": ftype,
            "Category": o["c"]["Category"],
            "Built_Year": year,
            "Built_Year_Note": note,
            "Built_Year_Basis": basis,
            "Built_Year_Source": source,
            "Transition_Year": o["c"]["Transition_Year"],
        }
        events = sorted(o["events"], key=sort_key)
        for i in range(n_max):
            e = events[i] if i < len(events) else None
            props[f"Concession_{i + 1}"] = e["Value"] if e else None
            props[f"Concession_{i + 1}_Event"] = event_text(e) if e else None
        props["Geometry_Status"] = o["p"]["Geometry_Status"]
        props["CRS"] = o["p"]["CRS"]
        features.append({"type": "Feature", "properties": props, "geometry": o["geometry"]})

    OUT.mkdir(exist_ok=True)
    for kind, geom_type in [("points", "Point"), ("lines", "MultiLineString")]:
        subset = [f for f in features if f["geometry"]["type"] == geom_type]
        name = f"objects_{kind}_wgs84"
        out = {"type": "FeatureCollection", "name": name,
               "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
               "features": subset}
        path = OUT / f"{name}.geojson"
        path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print(f"{path}: {len(subset)} objects, Concession_1..{n_max}")


if __name__ == "__main__":
    main()
