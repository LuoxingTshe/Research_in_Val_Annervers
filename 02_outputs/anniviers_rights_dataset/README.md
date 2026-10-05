# Anniviers / Gougra 权利关系分析数据包

整理日期：2026-10-04。版本：1.0.0。

本包保存已有研究结果，便于后续筛选、比较、绘图和追溯原文。详细结构化部分覆盖 Anniviers / Gougra / Navizence 及相连的 Tourtemagne 上段授予方；此前52条跨河谷研究记录另按原样保存，不宣称已全部转换为关系数据库。

## 从哪个文件开始

- `relations_readable.csv`：一行一条 A → B 关系，含数量、状态、时间及证据编号，适合直接阅读。
- `rights_dataset.json`：主数据；10张关联表及整体解释规则。
- `rights_dataset.sqlite`：相同数据的数据库；可在SQLite工具、Python或R中查询。
- `csv/`：10张分表，UTF-8 BOM，适合Excel、R、Python导入。
- `data_dictionary.json`：各字段定义、实际枚举值及外键。
- `snapshots/`：5个英文Mermaid关系图源文件，可修改及重新绘图。图中证据编号对应evidence表，再连接sources表。
- `prior_outputs/`：先前52条研究CSV、材料筛选表、英文时间线PNG和SVG。属于历史输出，未覆盖更新；遇到口径差异，以本包明确的证据与差异记录为准。
- `manifest.json`：文件清单及SHA-256，用于版本校验。

原始PDF没有复制进数据包。`sources.local_filename` 保存相对于项目根目录的材料路径；迁移到其他电脑后，将这些原文件放入对应的 `01_sources/` 子目录即可。网络来源保存链接与短摘录，不保存网页全文。

## 核心内容

Anniviers 是已核对上段公共授予方中份额最大者：55.4%，分母是上段已授水力。FMG 是直接concession持有人；上段至2039年，下段至2084年。Alpiq 持FMG股权54%，Anniviers持7.71%，该分母是公司股本。三种角色不能合并排名。

历史concession由私人／Isotherme汇集至FMG。后续地方灌溉与造雪主要体现供水额度、用水同意及付款安排，不编码成concession再次转让。Niouc以削减超过50%的120 L/s原配额换取灌溉设施资助；Briey2017年通常45 L/s，特殊干旱可申请最高70 L/s；Roux和St-Luc分别最多120,000与32,000 m³/年，各最高50 L/s，使用期5月1日至9月30日，超额按未生产kWh价值支付。

2039年安排分为资产回归、补偿和另行授予新concession。未来concession接收主体未在已核对资料中确定；FMV未来股东身份不能填充这一空白。没有证据认定为金融债权出售或债转股。

## 表与连接

| 表 | 用途 |
|---|---|
| entities | 市镇、公司、团体、工程和明确标注的分析集合／待定角色 |
| sources | 5项原始来源及定位信息 |
| evidence | 14项证据摘录、页码和摘要 |
| events | 16个历史／未来事件 |
| relations | 50条有向关系：subject → predicate → object |
| quantities | 36项带单位、界限及分母的数值观测 |
| relation_evidence | 关系与证据的多对多连接 |
| snapshots | 5个选编时间快照 |
| snapshot_relations | 快照包含哪些关系 |
| discrepancies | 6项来源差异或解释边界 |

主要连接：`relations.subject_id/object_id → entities.id`；`relations.event_id → events.id`；`quantities.relation_id → relations.id`；`relation_evidence → relations/evidence`；`evidence.source_id → sources.id`。

SQLite另含`metadata`及两个视图：`relation_details`（主体名称与量）、`evidence_links`（每条关系的来源）。一个关系可有多个数值或证据，因此视图不是“一行一关系”；不要按视图行数统计关系数。

## 日期、状态与数量

- 年份、年月、日期分别保留YYYY、YYYY-MM、YYYY-MM-DD，未知为空。不要把年份自动改成1月1日。
- `event`记录事件日期；`valid_from/to`记录材料明确起终点，交易关系还须结合动词理解。空的终期不表示永久有效；历史供水条款也不自动表示仍适用。
- “目前”是截至已核对2025—2026公开记载的分析；55.4%的授予份额来源发表于2022年，股权来源发表于2025年，并非实时登记。
- `documented`仅表示有来源记载；`agreed_future_obligation`是约定的未来义务；`future`是未来安排；`proposal`是提议；`undetermined`是尚未确定；`source_conflict`是来源存在差异。
- `evidence_level=analytical_representation/role_mapping`表示为绘图或分析建立的映射，不能作为额外法律转让。
- null/CSV空白不等于0；`operator`保存eq、gt、lte、unknown。百分数以0—100记录。
- 金额为来源所记CHF名义数值；流量L/s和年度体积m³/year不得在缺乏时间假设时互换。
- 百分比须查看`denominator`。股权、水力份额、工程参与比例禁止混算。
- 同一关系的多条金额不一定可加总：2022官方1505万、新闻1500万及其1400万+100万分项是并列／从属口径，不是四笔应付款；2039最终结算额还受更新机制影响。
- 下段51%：研究报告关联2004年；2026年官方访谈说2039年取得。两者并列保存，不能直接声称当前已持51%。
- 快照为人工选编，包含展示期相关的较早协议，不是自动有效期查询，也不是完整法律登记。未来图中包含2084年下段终期作为背景。

## 后续分析例子

直接查询最大上段公共授予方：

```sql
SELECT subject_name, value, unit, denominator
FROM relation_details
WHERE measure = 'granted_hydraulic_force_share'
ORDER BY value DESC;
```

查看2017—2018快照的关系与数量：

```sql
SELECT d.* FROM relation_details d
JOIN snapshot_relations sr ON sr.relation_id = d.id
WHERE sr.snapshot_id = 'T2018';
```

追溯一条关系的证据：

```sql
SELECT * FROM evidence_links WHERE relation_id = 'VAL22';
```

用Python读取JSON：

```python
import json
from pathlib import Path
p = json.loads(Path('rights_dataset.json').read_text(encoding='utf-8'))
relations = p['relations']
```

更新时先修改主JSON，保留ID、增加新证据和观测，再同步SQLite与CSV；不要只修改其中一个导出版本。新的法律文书应保留来源和有效期，不静默覆盖旧值。
