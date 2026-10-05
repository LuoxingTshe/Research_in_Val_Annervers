# 运行数据获取登记

本登记对应项目下一阶段的年度／日尺度水量平衡工作。它区分了已经取得的公开统计、可以通过官方门户查询的数据，以及尚未公开或尚未取得的FMG工程内部运行序列。

## 当前结论

- FMG 2025 年报已经提供 Mottec、Tourtemagne、Moiry、Vissoie 四个工程统计分区的年度来水量；现有配水研究已使用这组数据。
- 瑞士联邦环境局（BAFU）`hydrodaten.admin.ch`公开实时和历史河流、湖泊水文数据，并说明可通过LINDAS获取机器可读数据。
- 本轮检索未确认Gougra、Moiry、Mottec、Vissoie取水口、灌渠取水口或电站过机流量的公开逐日工程运行序列。
- 因此目前不能把BAFU下游河流站数据直接当作FMG各用途的取水或过机数据，也不能据此闭合Moiry—Navizence配水表。

## 已核验入口

| 数据源 | 可用范围 | 当前处理 |
|---|---|---|
| BAFU Hydrologische Daten und Vorhersagen | 瑞士公开河流、湖泊及部分水文站历史／实时数据 | 作为候选外部校验源；需先确认站点是否位于研究断面及是否受水电调度影响 |
| BAFU LINDAS数据服务 | 机器可读的公开水文测站数据 | 作为后续批量下载接口；本轮未将非Gougra站点混入项目数据 |
| FMG Rapport de gestion 2025 | 四个工程分区年度来水、发电和抽水摘要 | 已纳入`moiry_flow_allocation`与`gougra_cascade_energy` |
| Valais州公开水面水资料页 | Navisence、Turtmänna等水质和水文相关报告索引 | 作为生态流量和水文背景补证入口 |

## 仍需向FMG、州或市镇索取

1. Moiry库容及日库水位／入流／出流；
2. Mottec、Vissoie、Navizence各级电站逐日或小时过机流量；
3. Tourtemagne跨流域引水、抽水及回灌记录；
4. Roux、St-Luc、Briey、Niouc、Ricard、Granges等取水口的计量记录；
5. 2016治理决定附表及2004、2008、2017、2018协议的后续修订。

登记来源：

- https://www.hydrodaten.admin.ch/de/
- https://www.hydrodaten.admin.ch/de/aktuelle-hydrologische-daten-beziehen
- https://www.vs.ch/fr/web/sen/documents-eaux-de-surface
- https://www.alpiq.com/fr/energie/amenagements/energie-hydraulique/centrale-a-accumulation-de-gougra
