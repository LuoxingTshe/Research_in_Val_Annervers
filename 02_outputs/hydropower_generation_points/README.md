# 水电站点副本：分时期发电量

`hydropower_generation_points_wgs84.geojson` 从现有点图层筛选全部 5 个 Feature_Type 以“水电站”开头的对象。
保留原点坐标（WGS84）和 Name，只新增数值型产量字段；不保留 ID、类型、建设年代、权属或特许权等其他字段。
原文件没有修改；源坐标中的第三维 0 原样保留，不代表本次核实的真实高程。

产量指发电电量，年度单位 GWh/年，冬夏字段单位 GWh/季节。没有混入功率 MW、水流 m³/s 或过机水量 hm³。

| 电站 | 1958年前理论值 | 1958–1961设计年 | WASTA现行预期年 | 2039后情景年 |
|---|---:|---:|---:|---:|
| Centrale de Mottec | — | 125.0 | 137.05 | 137.05 |
| Centrale de Vissoie | — | 185.0 | 216.1 | 216.1 |
| Centrale de Lona | — | 4.0 | 2.0 | — |
| Centrale de Navizence | 201.761 | 255.0 | 298.7 | 298.7 |
| Centrale de Bieudron | — | — | — | — |

## 字段

- `E_pre1958_theory_GWh_yr`：1958年前（约1950年状态）理论毛年电量；不是历史实测产量。
- `E_1958_1961_design_GWh_yr`：1958–1961投运方案的设计平均年电量，Robert 1962 表2。
- `E_1958_1961_winter_GWh`：同一历史设计方案的平均冬季电量。
- `E_1958_1961_summer_GWh`：同一历史设计方案的平均夏季电量。
- `E_WASTA_2025_expected_GWh_yr`：WASTA统计日2025-12-31的长期预期年电量；不是2025实际发电量。
- `E_post2039_scenario_GWh_yr`：2039年后图示情景沿用现行预期电量；不是实测值或独立预测。

## 核对与缺项

- 对照三期流量图 `gougra_period_sankeys/period_models.json`、现状 `gougra_cascade_energy/cascade_model.json`、
  `flow_diagram_sources/wasta_plants.csv` 和 Robert 1962 的已提取文本 PDF p4（印刷 p251，表2）。
- 历史设计年总量 569 = Lona 4 + Mottec 125 + Vissoie 185 + Navizence 255；冬季 347、夏季 222。
- Mottec 历史设计值合并 Moiry–Mottec 111 和 Tourtemagne–Mottec 14；冬季 111+8=119，夏季 6。
- 现行预期值合计 653.85，和级联系统底层数据一致。Vissoie 含主机组 213.0 和辅助机组 3.1，合计 216.1。
  主、辅属于同一统计时期和同一电站，因此使用站级合计，不作为两个时期。
- 图中文字将 137.05／216.1／298.7 四舍五入为 137／216／299，副本保留底层精确值。
- Navizence 的 1958年前值 201.761 为模型理论毛电量（图上约202），不是实际历史产量。
  其他站该时期没有对应图示数据，留 null；null 不表示零。
- 2039后是图中的“现行系统与规则不变”情景，不代表真实未来发电量。
  Lona 在2039图中没有独立产量标注，所以该情景字段留空；其现行预期2.0保留在WASTA字段。
- Bieudron 属于原点图层，故保留该点；它未在 Gougra 流量图中提供产量，全部产量字段留 null。
  Turtmann／Oberems／Chippis-Rhône 等没有原点要素，未创建新坐标。
- 没有把全工程实际年产量或多年均值拆给单站，也没有把理论毛电量改称实测产量。
- 权利数据库 quantities 中没有发电电量记录；本次电量证据沿用流量图的 R01/R10/R11 与补充证据 E01–E04。
  `generation_evidence.csv` 在图层外记录每个非空值的证据ID、来源、页码/定位和计算口径；图层保持字段精简。
  `validation.json` 保存输入哈希、总量和标签核对结果。原流量图均未改动。

从项目根目录再生成：`python3 04_pipeline/scripts/build_hydropower_generation_points.py`。
