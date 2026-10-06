# 流量图补充资料（2026-10-06 联网检索）

目的：为把 `gougra_cascade_energy/` 和 `moiry_flow_allocation/` 的流量图细化到“逐取水口、逐月、逐级电站”提供新证据。本文件夹只登记资料和交叉核对，**没有改动**已有模型和图。

由 `04_pipeline/scripts/build_flow_sources.py` 生成（在项目根目录运行）。原始网页／PDF 文本抽取保存在 `04_pipeline/work/web_sources/`。

## 文件
- `evidence_additions.csv`：24 条新证据，列与 `moiry_flow_allocation/flow_evidence.csv` 相同（N＝拓扑，Q＝能力／设计，E＝电量，H＝来水，S＝溢流／蓄量，L＝权利）。
- `mqn_points.csv`：BAFU 天然平均流量（MQN）在 13 个断面的年值及 12 个月值，并给出 10–3 月占比。
- `wasta_plants.csv`：BFE 水电站统计（WASTA，统计日 2025-12-31）中 Gougra 各站的水头、功率、预期年发电量，以及按能量系数反推的过机水量。
- `crosscheck.json`：新资料与现有模型的交叉核对结果。

## 新来源及其对流量图的作用

| 代号 | 来源 | 带来的新内容 | 流量图中的用途 |
|---|---|---|---|
| BFE_WASTA | [BFE 水电站统计，geo.admin API 图层 ch.bfe.statistik-wasserkraftanlagen](https://api3.geo.admin.ch/rest/services/api/MapServer/ch.bfe.statistik-wasserkraftanlagen/503100,503200,503300,503350,503400?returnGeometry=false)；[数据集说明](https://www.bfe.admin.ch/bfe/en/home/supply/digitalization-and-geoinformation/geoinformation/geodata/water/hydropower-plants-statistics.html) | 官方逐站预期年发电量：Mottec 137.05、Vissoie 213.0（另有辅助机组 3.1）、Navizence 298.7、Lona 2.0 GWh；水头 640／437／591／319 m；Mottec 抽水功率 87 MW、抽水电耗 30.2 GWh | 每级电站的长期平均发电量，补上年报未公开的分站数据 |
| BAFU_MQN | [BAFU“平均流量及流态”图层 ch.bafu.mittlere-abfluesse](https://api3.geo.admin.ch/rest/services/api/MapServer/ch.bafu.mittlere-abfluesse) | 各河段天然（未调节）年均流量和 12 个月流量，模型值 | 每条支流、每个取水口的入流宽度，以及冬季／夏季两张图 |
| VS_CONV2022 | [瓦莱州政府致大议会咨文及 Convention 2022（2023-05，93 页）](https://parlement.vs.ch/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBOS84QWc9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--b8c46a9d24249ef4099244cb161e7e042e738570/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdCem9MWm05eWJXRjBPZ2h3WkdZNkRIRnlYMnhwYm10cEEvL25BZz09IiwiZXhwIjpudWxsLCJwdXIiOiJ2YXJpYXRpb24ifX0=--3a9540a08a58bf71367b4d8b3dbc950d96975573/2023.05_Ech%C3%A9ance%20des%20concessions%20Gougra%20en%202039_MES_CE.pdf) | 上段 concession 的范围；各授权方所占水力份额；附件资产清单列出全部取水口、隧洞、补偿池、泵、饮用水池，以及“经 RMGZ 管网向 Moiry 下游放生态水”（2021 年） | 完整的节点清单；按授权方拆分水力份额；生态放水与造雪管网相连 |
| BGE_150_II_83 | [联邦法院 BGE 150 II 83（9C_739/2022，2024-01-05）](https://www.bger.ch/ext/eurospider/live/fr/php/clir/http/index.php?highlight_docid=atf://150-II-83:fr&lang=fr&type=show_document) | 因 Vissoie–Niouc 隧洞过水能力不足，夏季约 2000 万 m³ 水溢流、未发电（2001 年交还报告）；判定这部分溢流水不计入特别税的计税基础 | 新增一条 **Vissoie 溢流** 流带，与生态留水分开画 |
| LEPORELLO2014 | [FMG/Alpiq 介绍册 2014](https://www.visinand.ch/Refuges/Turtmann/2015_07/Gougra_leporello_2014_FR_WEB_tcm116-98658.pdf)（第三方网站转存） | Tourtemagne 隧洞 8 m³/s；Mottec 取水口 12（最大 18）m³/s；补偿池 15／5 万 m³；溢洪道 60、底孔 55 m³/s；三级能量系数 1.324–1.551／0.986／1.277 kWh/m³；年毛发电 650 GWh，其中冬季 52 % | 隧洞和取水口的容量上限；电量与水量互换；冬夏比例 |
| FMG_RG2025 | [FMG 2025 年报](https://www.alpiq.com/fileadmin/ALPIQ/energy/assets/gougra/fmg_rapport_gestion_2025.pdf)（已在 `moiry_flow_allocation/sources/`）第 5–10 页 | 此前未用到的数据：2024 年来水 203.7 hm³、近十年均值 265.5 hm³；2024 年发电 607 GWh、近十年均值约 675 GWh；Moiry–Mottec 段因 RCT 工程停运 6 个月；年末库容 36.47 hm³；2025 年各授权方理论功率份额 | 把 2025 年模型换算到平均年；解释 2025 年发电量偏低 |
| VS_STRAT_EAU, BLICK2026 | [瓦莱州水战略：Moiry 坝加高](https://www.vs.ch/web/strategie-eau/w/rehaussement-du-barrage-de-moiry)；[Blick 2026](https://www.blick.ch/fr/suisse/moiry-ce-barrage-pourrait-bientot-gagner-9m-de-hauteur-id21967647.html) | 加高 9 m，新增库容 1200 万 m³ 以上，可把 40–50 GWh 从夏季移到冬季；造价 1.2 亿瑞郎；Mottec 将配新泵 | 情景图层，不属于现状 |
| ALPIQ_PAGE | [Alpiq Gougra 介绍页](https://www.alpiq.com/fr/energie/amenagements/energie-hydraulique/centrale-a-accumulation-de-gougra) | 能量系数与介绍册一致；年均 643 GWh | 核对用 |
| HYDROSCOPE42 | [HYDROscope 第 42 期（2024-05）](https://www.hydro.ch/data/documents/Hydroscope/Hydroscopeno42mai2024web-1.pdf) | Mottec 负责 Tourtemagne 水的发电和抽水调度；RCT、RCB 两项改造（2024–2027） | 停运期背景 |

## 交叉核对结果（`crosscheck.json`）
1. **各级过机水量相互吻合。** 用 WASTA 预期年发电量除以能量系数，得到长期过机水量：Mottec 88–104、Vissoie 216、Navizence 234 hm³。现有模型的 2025 年数值除以 2025 年来水指数 0.73 后为 101、237、242 hm³。两组数差距在 10 % 以内，说明模型的结构没有问题；2025 年发电量偏低主要来自枯水年和停运。
2. **天然来水与年报吻合。** 按 MQN 计算：Moiry 坝址约 37 hm³，Mottec 取水口约 127 hm³，Turtmänna 在 1728 m 处约 64 hm³（2025 年报的 Tourtemagne 分区为 47.56 hm³，除以 0.73 约为 65）。各分区相加量级与近十年均值 265.5 hm³ 一致。
3. **季节错位。** 各断面天然径流只有 11–17 % 出现在 10–3 月（Fang 为 24 %），而 2014 年介绍册给出的发电量冬季占 52 %。Moiry 有效库容 77 hm³，约等于年均来水的 29 %，这就是冬夏转移的规模上限，加高后再增约 12 hm³。
4. **Chippis 断面的水量差额。** Navisence 天然来水约 251 hm³，加上 Turtmänna 来水（上限 64），共约 315 hm³；Navizence 过机水量约 234 hm³，差额约 81 hm³。差额可分为：生态留水（模型约 26）、Vissoie 溢流（2001 年约 20）、灌溉、取水口以下未截取的侧向来水，以及 Turtmänna 取值偏高（1728 m 断面在取水口下游）。这个差额是细化流量图时需要拆分的“未发电”部分。

## 使用注意
- MQN 是全国模型给出的**天然**平均流量，参考期较早，不包含冰川近年的后退，也不是实测或调节后的流量。只能用来拆分来水宽度和季节形状，绝对量应以 FMG 年报为准、按比例缩放。
- 联邦水文站网在 Navisence、Gougra、Turtmänna 上没有测站（hydrodaten.admin.ch 站点列表最近的只有 Rhône–Sion 和 Rhône–Brig），所以这些河段没有公开的实测流量。
- WASTA 的“预期发电量”是长期平均值，不是某一年的实际值。Mottec 的数值包含抽水后再发的电。
- 约 2000 万 m³ 的 Vissoie 溢流是 2001 年的估计值；新的 15 m³/s 隧洞（GVN）截至 2025 年报仍在审批。
- 介绍册地图上的流域面积标签（6.2／29.3／41.1／107.6／67.5 km²）对应哪个流域无法确定，其中 67.5 km² 标在相邻工程 Illsee（ARGESA）旁边。暂不使用。
- WASTA 中的 Turtmann（502800）和 Chippis-Rhône（503000）不属于 FMG，列出只为说明 Turtmänna 下游和 Chippis 还有其他用水户。

## 尚未取得
- 2016 年治理决定附表、2004 年 Navizence concession 原文、2008／2017／2018 年灌溉协议。
- Moiry 逐日或逐月库容、各站逐月发电量（2025 年报第 8 页 2016–2025 年柱状图没有数值文字）。
- Tourtemagne 来水中直接发电与抽水入库的比例。
- 2016–2023 年的 FMG 年报（Alpiq 只公开了 2025 年版）。

## 原件状态
2026-10-06 已下载并核对 SHA-256，存入 `01_sources/` 并登记到 `00_index/source_catalog.csv`：
- `01_sources/concessions/Conseil d’État du Valais_Message concernant la Convention 2022 en vue de l’échéance des concessions Gougra en 2039.pdf`（93 页，7 145 302 字节，SHA-256 `ce2aa903…b2fc4822`）
- `01_sources/hydropower/Forces Motrices de la Gougra_Un aménagement aux confins des vallées d’Anniviers et de Tourtemagne.pdf`（10 页，449 421 字节，SHA-256 `532018e0…87182a81`）

联邦法院判决只有网页版，正文保存在 `04_pipeline/work/web_sources/bger_150_II_83_fr.txt`；geo.admin 数据保存为该文件夹中的 JSON。FMG 2025 年报原件已在 `moiry_flow_allocation/sources/` 中。
