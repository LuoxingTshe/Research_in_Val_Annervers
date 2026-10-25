# Anniviers / Turtmann 输水网络分类副本

源文件：`/Volumes/luoxie_ethz/Annivers/SHP/JahrRecord/Water_Anniviers_Turtmann_pipes.geojson`。共 603 个 MultiLineString；保留原坐标、高程和 CRS，不改写原文件。
全部 16 个 GeoJSON 已精简为仅含可视化所需的 5 个属性字段，原编号、制图日期、来源、权属、特许权、备注等均从图层属性删除。
源文件 SHA-256：`69d02c378ac5a184cee5634e7106a19b723761255d513d26d9222a2b11f5f8f4`。

## 文件与数量

三个类别目录各有 `all.geojson` 和四个互斥年代子类；空子类仍输出有效的空 FeatureCollection。
`all_classified.geojson` 汇总全部要素；`layer_index.csv` 列出所有图层；`unknown_year_review.csv` 列出年代待核实段。
父层与子层有意重复：在 QGIS 中选择三个 `all.geojson`，或选择十二个年代子类，避免同时叠加重复绘制。

| 类别 | 1958年前 | 1958–2000年 | 2000年后修复 | 年代未知 | 合计 |
|---|---:|---:|---:|---:|---:|
| 地上水渠 | 33 | 0 | 21 | 304 | 358 |
| 地上管道 | 14 | 2 | 0 | 0 | 16 |
| 地下输水段 | 44 | 17 | 11 | 157 | 229 |
| 合计 | 91 | 19 | 32 | 461 | 603 |

## 物理类型规则

- 源 `VERLAUF=Oberirdisch/Bruecke`：地上，桥上输水段也归地上。
- 地上 `OBJEKTART=Bisse Suone`：地上水渠；该名称并不单独证明每段都是明渠。
- 地上 `Druckleitung einfach/mehrfach`：地上压力管道。
- 源 `Unterirdisch bestimmt/unbestimmt`：地下输水段；地下位置不确定的段仍在其中，源标记可在原文件核实。
- 地下类型通过 `CLASS_SUBTYPE` 区分；源数据不足以把地下 Bisse 精确拆成管道、涵洞或隧洞，故不强行细分。

- 地下水渠段（管道／涵洞／隧洞形式未细分）：195 段。
- 地下压力隧洞：33 段。
- 地下压力管道：1 段。

## 年代规则与限制

按原 `BAU_JAHR`（建造／首次记载年）和 `SAN_JAHR`（修复年）中较晚的已知工程事件分类；相同年份优先修复。
1958年前为 <1958；1958–2000年为 1958≤年≤2000；2000年后修复为 SAN_JAHR>2000。
图层只保留最终分期及采用年份，原建造年、修复年、年份依据和精度信息均可回查未修改的源文件。
未知修复年不代表从未修复。源属性文字中只有模糊修复描述或多个事件，未自动补入 SAN_JAHR。

`BAU_GENAU=首次记载/推测` 的年份仅作为带有该不确定性的历史分类依据，不提升为确切建造年。
`ERSTELL_J`、`HERKUNFT_J`、`REVISION_J`、`DATUM_ERST`、`DATUM_AEND` 等制图日期均不作为工程年代。
修复子类沿用 Grand Bisse de St-Jean 的 2012 年和 Grand Bisse de Saint-Luc 的 2020 年源属性，
仅表示这些段被源文件标注了修复年份，不证明每段全部重建，也不提供精确修复施工边界。本次未独立核验历史来源。

## 图层仅保留以下字段

- `Name`：原 NAME，若为空则取设施名称 ANLAGE；均为空时保留 null。
- `CLASS_GROUP`：地上水渠／地上管道／地下输水段。
- `CLASS_SUBTYPE`：输水形式；保留不能细分的情况。
- `CLASS_PERIOD`：最终年代子类，用于分期着色与筛选。
- `CLASS_YEAR`：分类采用的工程事件年份；未知为 null。

坐标存于 geometry，不重复新增坐标属性。图层不含特许权属性。
`unknown_year_review.csv` 是图层外的核查清单，保留源编号与来源信息，供后续补充未知年代。

## 导入和再生成

坐标沿用源文件 EPSG:2056（水平，米）及 EPSG:5728（高程），适用于 QGIS。
这些文件保留源 GeoJSON 的投影 CRS 扩展，并非 RFC 7946 的经纬度 GeoJSON；不要强制指定 EPSG:4326。
已校验所有输出图层的坐标、几何和 CRS 无改动，属性严格仅含上述五个字段；
内部按源 UUID 校验十二个年代子类合计无遗漏、无重复，但 UUID 不导出到 GeoJSON。

从项目根目录运行：
`python3 04_pipeline/scripts/build_water_network_subclasses.py`
可用 `--source`、`--output` 指定输入和输出目录。压缩包含上述图层和说明。
