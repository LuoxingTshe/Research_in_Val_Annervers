"""Merge the QGIS point/line GeoJSON layers into one object-level layer.

Reads 02_outputs/qgis_wgs84_package/{points,lines}_wgs84{,_classified}.geojson
(one feature per object-event) and writes one feature per object to
02_outputs/concession_objects_merged/objects_{points,lines}_wgs84.geojson, with:
  - Feature_Type and the existing Category / Transition_Year
  - Built_Year (+ note, basis, source), researched 2026-10-08 (table below)
  - Owner (+ note, basis, source), researched 2026-10-08 (table below)
  - Concession_Relation / Scope / Grantor / Holder / Term / End / Note / Source,
    per 00_index/concession_field_protocol.md
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


# Object_ID: (Owner, Owner_Note, Owner_Basis, Owner_Source), researched 2026-10-08.
# Owner = who owns the physical object (plant, dam, channel, land) or, for natural
# watercourses, who holds the water (in Valais the communes, except the Rhône; in Vaud
# and Fribourg the canton). Owner ≠ shareholder ≠ operator ≠ granting commune.
FMG_UPPER = ("Forces Motrices de la Gougra SA（FMG）",
             "上段（Gougra）特许权资产，1959–2039；2039年湿式资产无偿归还上段授予方（六市镇+Valais州）。"
             "FMG股东（Alpiq等）不是资产所有人；运营由Alpiq／Hydro Exploitation承担",
             "文献", "rights_dataset：U_grant、RETURN39；Bagnoud 2026 p5；Savoy 2025 p78、p84")
WATER_VS = "Valais州内地表水归市镇所有（Rhône、Léman除外）；授予水力特许权不转移水体所有权"
OWNER = {
    "P01": FMG_UPPER,
    "P02": FMG_UPPER,
    "P03": FMG_UPPER,
    "P04": ("Forces Motrices de la Gougra SA（FMG）",
            "下段（Navizence）特许权资产，2004–2084；下段授予方（Anniviers、Chippis、Chalais）"
            "对下段工程的51%参与在来源间口径不一，且不同于其在FMG的10%股本",
            "文献", "rights_dataset：L_grant、LOWER51old、LOWER51new、LOWER10；Savoy 2025 p86"),
    "P05": FMG_UPPER,
    "P06": FMG_UPPER,
    "P07": ("Alpiq Suisse SA",
            "EOS（今Alpiq Suisse）1945年获Haute-Printse特许权并建坝；Alpiq为现特许权人和运营方。"
            "2031年特许权届满，授予市镇组成“Dixence Cleuson 2031”；2024年新设Dixence-Cleuson SA，持股未核实",
            "联网+文献", "Savoy 2025 p24–25；Hérémence 2021新闻稿（Dix-Cl-31）；Alpiq《DIX Rapport annuel 2024-25》"),
    "P08": ("Forces Motrices Hongrin-Léman SA（FMHL）",
            "Vaud与Fribourg两州1963年共同授予FMHL；FMHL股东：Romande Energie 41.14%、Alpiq 39.29%、"
            "Groupe E 13.14%、Lausanne市6.43%（股东≠资产所有人）；技术运营Hydro Exploitation",
            "文献", "Savoy 2025 p57、p60（引fmhl.ch 2024）"),
    "P10": ("Cleuson-Dixence（société simple）：Grande Dixence SA 15/22、Alpiq Suisse SA 7/22",
            "1992年为建设和运营Cleuson-Dixence设立的简单合伙；Grande Dixence SA本身由Alpiq 60%、"
            "Axpo、BKW、IWB各13⅓%持有；运营Hydro Exploitation",
            "联网", "grande-dixence.ch（Cleuson-Dixence手册；2023年报）；alpiq.com（Cleuson-Dixence）"),
    "P11": ("土地：FMG；建筑：未知",
            "FMG将其Moiry湖右岸土地租给坝区餐厅，餐厅再转租Château-Pré牧场；餐厅建筑本身归属材料未载",
            "文献", "R022；Savoy 2025 p96"),
    "L01": ("municipal", "Commune d'Anniviers（原Grimentz、Ayer）；" + WATER_VS + "；1943年由Grimentz与Ayer分别授出", "文献",
            "Savoy 2025 p57注61；rights_dataset：H43_grimentz、H43_ayer"),
    "L02": ("municipal", "Commune d'Anniviers，下游段Chippis、Chalais；" + WATER_VS + "；按河段分属沿岸市镇", "文献",
            "Savoy 2025 p57注61；rights_dataset：lower_grantors"),
    "L03": ("municipal", "Oberems、Ergisch、Turtmann-Unterems；" + WATER_VS + "；1951–1952年三市镇分别向Isotherme授出", "文献",
            "Savoy 2025 p57注61；rights_dataset：H_oberems、H_ergisch、H_turtmann"),
    "L05": ("municipal", "Turtmann谷市镇（Oberems／Ergisch／Turtmann-Unterems），具体所属未逐条核实；" + WATER_VS, "文献（推定）",
            "Savoy 2025 p57注61、p78"),
    "L08": ("municipal", "Commune d'Anniviers；" + WATER_VS, "文献", "Savoy 2025 p57注61、p78"),
    "L09": ("municipal", "Commune d'Anniviers；" + WATER_VS, "文献", "Savoy 2025 p57注61、p78"),
    "L10": ("municipal", "Commune d'Anniviers；" + WATER_VS, "文献", "Savoy 2025 p57注61、p78"),
    "L12": ("municipal", "Commune d'Anniviers；" + WATER_VS + "；属下段Navizence特许权范围", "文献（推定）", "Savoy 2025 p57注61、p78"),
    "L13": ("Niouc灌溉团体（consortage d'irrigation de Niouc）",
            "团体为灌渠与供水权利人；2008年协议由St-Luc市镇议会代表团体签署", "文献", "rights_dataset：niouc、N2008；Savoy 2025 p84、p95"),
    "L14": ("Briey灌溉团体（consortage d'irrigation de Briey）", "团体为灌渠与供水权利人；历史权源曾有争议，2017年和解", "文献",
            "rights_dataset：briey、Bsettle；Savoy 2025 p84"),
    "L15": ("municipal（管理）", "修复后由Commune d'Anniviers管理；材料只写“gère”，产权未明载", "文献", "Savoy 2025 p84；R003"),
    "L16": ("municipal（管理）", "修复后由Commune d'Anniviers管理；材料只写“gère”，产权未明载", "文献", "Savoy 2025 p84；R004"),
    "L17": ("Ricard灌渠团体（consortage du bisse de Ricard）与FMG分有设施",
            "2003年协议划分各设施产权并定流量，未说明哪段归哪方", "文献", "R019；Savoy 2025 p84、p93"),
    "L25": ("土地：FMG；路线：Anniviers Tourisme负责",
            "FMG为土地所有人并免费提供；项目全部责任由Grimentz/St-Jean Tourisme（今Anniviers Tourisme）承担", "文献", "R020；Savoy 2025 p94"),
    "L26": ("municipal（取水权）；渠道产权未知",
            "Saxon市镇享有Printse 350 L/s取水权；1963年起改由FMM设施供水，原渠道停用", "文献", "R024；Savoy 2025 p27、p36"),
    "L27": ("municipal", "Commune de Nendaz；" + WATER_VS + "；1906、1945年由Nendaz授出", "文献", "Savoy 2025 p22–23、p57注61"),
    "L33": ("municipal", "Commune d'Hérémence；" + WATER_VS + "；Dixence水力授予方以Hérémence为主（62%）", "文献", "Savoy 2025 p24、p57注61"),
    "L34": ("kantonal", "Canton de Vaud（Fribourg共同授予）；Vaud与Fribourg地表水归州所有；Hongrin引水涉及Fribourg水量，1963年两州共同授予FMHL", "文献",
            "Savoy 2025 p57注61"),
    "L38": ("municipal", "Commune de Stalden；1922年由市镇从原共有权利人手中收购（访谈回忆）", "文献", "R049；Bellwald p.139"),
}
OWNER["P09"] = OWNER["P08"]
OWNER["L35"] = OWNER["L34"]


# Concession fields, following 00_index/concession_field_protocol.md (researched 2026-10-08).
# Object_ID: (Relation, Scope, Grantor, Holder, Term, End, Note, Source)
# Multiple concessions on one object: Scope/Grantor/Holder/Term aligned with " | ".
NA = "不适用"
RELATIONS = {"特许权", "特许权条款受益", "供水协议", "土地使用协议", "无"}
PUBLIC = {"municipal", "kantonal", "municipal + kantonal"}
UPPER_GRANTORS = "上段授予方：Anniviers、Ergisch、Turtmann-Unterems、Oberems、Chippis、Chalais六市镇 + Valais州"
LOWER_GRANTORS = "下段授予方：Anniviers、Chalais、Chippis（州是否也是直接授予人，来源表述不一）"
DIX7 = "授予方：Hérémence（62%）、Nendaz（29%）、Vex、Mont-Noble、Saint-Martin、Sion、Valais州"
UPPER = ("上段Gougra", "municipal + kantonal",
         "Forces Motrices de la Gougra SA（FMG）", "1959–2039")
LOWER = ("下段Navizence", "municipal",
         "Forces Motrices de la Gougra SA（FMG）", "2004–2084")
UPPER_SRC = "rights_dataset：U_grant、G_*、RETURN39；Bagnoud 2026 p5；Savoy 2025 p78"
LOWER_SRC = "rights_dataset：L_grant、L2084；Savoy 2025 p78、p100"
HONGRIN = ("Hongrin-Léman", "kantonal",
           "Forces Motrices Hongrin-Léman SA（FMHL）", "1971–2051")
HONGRIN_NOTE = "授予方：Vaud、Fribourg两州政府共同授予；1963-03-22授予；1971-10-01投运起算80年，至2051年9月底"


def upper(note=""):
    return ("特许权", *UPPER, 2039, "；".join(filter(None, [UPPER_GRANTORS, note])), UPPER_SRC)


CONCESSION = {
    "P01": upper("上段特许权资产；2039年湿式资产无偿归还授予方"),
    "P02": upper("上段特许权资产；2039年湿式资产无偿归还授予方"),
    "P03": upper("上段特许权资产（Lona引水及小电站）"),
    "P04": ("特许权", *LOWER, 2084, LOWER_GRANTORS + "；下段特许权资产；旧Navizence特许权2004年届满后重新授予，2009年核准", LOWER_SRC),
    "P05": upper("上段特许权资产；2039年湿式资产无偿归还授予方"),
    "P06": upper("上段特许权资产；Turtmänna水经此泵送入Moiry"),
    "P07": ("特许权", "Haute-Printse", "municipal", "Alpiq Suisse SA（前EOS）", "1945–2031", 2031,
            "授予方：Commune de Nendaz；1945-12-07授予EOS；2031年届满，授予方已组成“Dixence Cleuson 2031”准备回归",
            "Savoy 2025 p23–25；R027"),
    "P08": ("特许权", *HONGRIN, 2051, HONGRIN_NOTE, "Savoy 2025 p57–58、p60；R034"),
    "P10": ("特许权", "Grande Dixence | Haute-Printse", "municipal + kantonal | municipal",
            "Grande Dixence SA | Alpiq Suisse SA", "?–2031 | 1945–2031", 2031,
            DIX7 + " | 授予方：Commune de Nendaz；Cleuson-Dixence未新授特许权，沿用既有特许权；新设施折旧和回归按协议，其他流域的特许权2031–2044年间届满",
            "Savoy 2025 p24–25；R027；Hérémence 2021新闻稿（Dix-Cl-31）"),
    "P11": ("土地使用协议", NA, NA, NA, NA, None,
            "FMG把Moiry湖右岸土地租给餐厅，餐厅转租Château-Pré牧场；另有供水供电协议（FMG）", "R022；Savoy 2025 p96"),
    "L01": upper("1943年Grimentz与Ayer分别授予两名私人，经Isotherme于1953年转给FMG"),
    "L02": ("特许权", UPPER[0] + " | " + LOWER[0], UPPER[1] + " | " + LOWER[1],
            UPPER[2] + " | " + LOWER[2], UPPER[3] + " | " + LOWER[3], 2039,
            UPPER_GRANTORS + " | " + LOWER_GRANTORS + "；上段（Mottec以上及Vissoie段）与下段（Vissoie–Chippis）分属两套特许权", UPPER_SRC + "；" + LOWER_SRC),
    "L03": upper("1951–1952年Oberems、Ergisch、Turtmann分别授予Isotherme，1953年转给FMG"),
    "L05": upper(),
    "L08": upper(),
    "L09": upper(),
    "L10": upper(),
    "L12": ("特许权", *LOWER, 2084, LOWER_GRANTORS, LOWER_SRC),
    "L13": ("特许权条款受益；供水协议", *LOWER, 2084,
            LOWER_GRANTORS + "；下段特许权为Niouc保留120 L/s；2008年与FMG协议降至一半以下，FMG出资建喷灌网",
            "rights_dataset：N2004、N2008、Nfund；R001"),
    "L14": ("特许权条款受益；供水协议", *LOWER, 2084,
            LOWER_GRANTORS + "；下段特许权为Briey保留70 L/s；2017年与FMG和解，通常45 L/s，特别干旱时最高70 L/s",
            "rights_dataset：B2004、B2017；R002"),
    "L15": ("供水协议", NA, NA, NA, NA, None, "2018年Anniviers市镇与FMG协议：免费限额，超额按未发电量付费", "rights_dataset：W_roux；R003"),
    "L16": ("供水协议", NA, NA, NA, NA, None, "2018年Anniviers市镇与FMG协议：免费限额，超额按未发电量付费", "rights_dataset：W_grand_st_luc；R004"),
    "L17": ("供水协议", NA, NA, NA, NA, None, "2003年灌渠团体与FMG协议：划分设施产权并定流量", "R019"),
    "L25": ("土地使用协议", NA, NA, NA, NA, None, "2005–2006年FMG免费提供土地，旅游机构承担全部责任", "R020"),
    "L26": ("供水协议", NA, NA, NA, NA, None,
            "Saxon市镇原有Printse取水权350 L/s；1963年EOS–Saxon、EOS–FMM两份协议改由FMM设施供水", "R024；Savoy 2025 p36"),
    "L27": ("特许权", "Haute-Printse", "municipal", "Alpiq Suisse SA（前EOS）", "1945–2031", 2031,
            "授予方：Commune de Nendaz；1945年特许权保留充足灌溉水；下游段1906年授出的特许权已于1966年由Lonza放弃",
            "Savoy 2025 p23–24；R032"),
    "L33": ("特许权", "Grande Dixence", "municipal + kantonal", "Grande Dixence SA", "?–2031", 2031,
            DIX7 + "（“Dixence Cleuson 2031”七方），按河流分属未核实；起始年未查到",
            "Savoy 2025 p25；Hérémence 2021新闻稿（Dix-Cl-31）"),
    "L34": ("特许权", *HONGRIN, 2051, HONGRIN_NOTE, "Savoy 2025 p57–58；R034"),
    "L38": ("无", NA, NA, NA, NA, None, "1922年由Stalden市镇收购（访谈回忆），未见特许权或供水协议", "R049"),
}
CONCESSION["P09"] = CONCESSION["P08"]
CONCESSION["L35"] = CONCESSION["L34"]


def check_concession(oid, c):
    relation, scope, grantor, holder, term, end, _, source = c
    assert set(relation.split("；")) <= RELATIONS, oid
    has = "特许权" in relation.split("；") or "特许权条款受益" in relation.split("；")
    if has:
        n = scope.count(" | ")
        assert NA not in (scope, grantor, holder, term) and isinstance(end, int), oid
        assert grantor.count(" | ") == holder.count(" | ") == term.count(" | ") == n, oid
        assert set(grantor.split(" | ")) <= PUBLIC, oid
    else:
        assert (scope, grantor, holder, term, end) == (NA, NA, NA, NA, None), oid
    assert source, oid


def check_owner(oid, owner):
    """Public owners are written only as municipal / kantonal (protocol §4 rule 8)."""
    head = owner.split("（")[0].split("；")[0]
    assert not any(w in head for w in ("Commune", "Canton", "市镇", "州")), oid
    if head.startswith(("municipal", "kantonal")):
        assert head in PUBLIC, oid


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
    assert set(objects) == set(OWNER), set(objects) ^ set(OWNER)
    assert set(objects) == set(CONCESSION), set(objects) ^ set(CONCESSION)
    for oid, c in CONCESSION.items():
        check_concession(oid, c)
    for oid, o in OWNER.items():
        check_owner(oid, o[0])
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
        props["Owner"], props["Owner_Note"], props["Owner_Basis"], props["Owner_Source"] = OWNER[oid]
        props.update(zip(["Concession_Relation", "Concession_Scope", "Concession_Grantor", "Concession_Holder",
                          "Concession_Term", "Concession_End", "Concession_Note", "Concession_Source"],
                         CONCESSION[oid]))
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
