# 研究日志

按日期倒序记录每次工作的结果和下一步目标。详细数据与口径见各 `02_outputs/<topic>/README.md`。

## 下一次研究目标：泵水策略与水量的数值考察

目标：把 Moiry–Mottec 的抽水和蓄水从“等效估算”推进到有依据的数值，回答抽多少水、何时抽、值多少钱。

待解决的问题：
1. **抽水量拆分**。WASTA 记载 Mottec 每年抽水电耗 30.2 GWh（2025 年实际 28 GWh）。目前只按“全部用蓄能泵”折算为约 15 hm³（617 m 扬程、效率 85 %，约 1.98 kWh/m³）。需要拆分两台泵：
   - 蓄能泵：Navizence 水抽往 Moiry，扬程 570–664 m，最大 3.9 m³/s，23–24 MW；
   - 虹吸泵：Tourtemagne 水送往 Moiry，扬程 0–126 m，最大 6 m³/s，6.75 MW。
2. **Tourtemagne 来水的去向**。年均约 65 hm³ 中，多少直接经 Mottec 发电（水头约 613 m），多少重力或抽水进入 Moiry；以 Moiry 水位相对 Tourtemagne 补偿池（2177 m）的高低划分时段。
3. **逐月水量模型**。用 BAFU MQN 月流量形状和 Moiry 有效库容 77 hm³ 建逐月蓄放模型，检验冬季发电占 52 %（2014 年介绍册）能否由库容和抽水解释。
4. **收益的数值考察**。用 ENTSO-E 小时电价代替月均价，估计抽水的实际购电价（2025 年报推算约 49 CHF/MWh）、蓄能泵的保本冬季电价，以及 Moiry 加高 9 m 方案（新增库容 12 hm³ 以上、40–50 GWh 夏转冬、配新泵）的增量。
5. **校准项的验证**。v2 桑基图中 Mottec 未发电约 21 hm³（区间 13–28）、Vissoie 溢流约 13 hm³（2001 年约 20 hm³）都是平衡项，需要找证据确认去向。

需要的数据：Moiry 逐日或逐月水位与库容、逐月发电与抽水量（2025 年报第 8 页柱状图没有数值）、2016–2023 年 FMG 年报、ENTSO-E 小时价格、两台泵的运行时数。

起点文件：`02_outputs/gougra_cascade_energy/`（v2 模型与 `cascade_model.json`）、`02_outputs/flow_diagram_sources/`（`wasta_plants.csv`、`mqn_points.csv`、`evidence_additions.csv` 中的 Q06、Q07、S02）、`04_pipeline/scripts/build_cascade_energy.py`。

## 2026-10-08
- 新增 `02_outputs/valley_economic_narrative/`：河谷产业演变叙事（农牧→旅游、水电与多用途景观），供景观设计作业使用，主要依据 Viallon 第 8 章和 Savoy 2025。“战略引导”和“可持续”作为设计目标，不写成现状判断。
- `00_index/reference_list.csv` 改为唯一书目：用原文献标题，不再记录 PDF 文件名；并入原总阅读清单的内容（R01–R29 文献、W01–W07 网站、P01–P13 图片与 GIS 门户）。
- 原文（`01_sources/`、总阅读清单 PDF、`source_catalog.csv`、moiry_flow 的 3 份 PDF、web_sources 全文）移出 git，仅保留本地副本。之前的提交里仍可找到这些原文。

## 2026-10-06
- 新增 `02_outputs/flow_diagram_sources/`：BFE WASTA 逐站统计、BAFU MQN 天然月流量（13 个断面）、24 条新证据和交叉核对；两份新原件（瓦莱州 Convention 2022 咨文、FMG 2014 介绍册）。
- `gougra_cascade_energy` 升级为 v2：改为近十年平均年（来水 265.5 hm³），各级过水量用 WASTA 预期发电量除以能量系数校准（Mottec 95.3、Vissoie 216.0、Navizence 233.9 hm³；预期合计 653.9 GWh/年）。新增抽水（约 15 hm³）、Mottec 未发电、Vissoie 溢流、Vissoie 取水口回收等流带；生态留水少发电量修正为约 33 GWh/年。网页和 SVG/PDF 矢量图已重新生成。

## 2026-10-05
- 项目重组，建立编号目录结构。
- 新建 `gougra_cascade_energy` v1：2025 年来水的梯级桑基图、各级理论发电量、生态留水机制、冬夏抽水/发电收益计算器；之后转为英文，并导出可编辑矢量文件。
