from pathlib import Path
import csv,json,sqlite3,hashlib,shutil,zipfile
root=Path(__file__).resolve().parents[2]
out=root/'02_outputs/anniviers_rights_dataset'
p=json.loads((out/'rights_dataset.json').read_text())
tables={k:v for k,v in p.items() if k!='metadata'}
(out/'csv').mkdir(exist_ok=True)
for name,rows in tables.items():
 with (out/'csv'/f'{name}.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
entities={r['id']:r for r in p['entities']}
quantities={r['id']:[] for r in p['relations']}
evidence={r['id']:[] for r in p['relations']}
for q in p['quantities']:quantities[q['relation_id']].append(q)
for e in p['relation_evidence']:evidence[e['relation_id']].append(e['evidence_id'])
ops={'eq':'','gt':'>','lte':'≤','unknown':''}
def qtext(q):
 value='unknown' if q['value'] is None else f"{q['value']:g}"
 return f"{q['measure']}: {ops[q['operator']]}{value} {q['unit']}"
flat=[]
for r in p['relations']:
 a,b=entities[r['subject_id']]['name'],entities[r['object_id']]['name']
 flat.append(dict(relation_id=r['id'],A=a,relation=r['predicate'],B=b,arrow=f'{a} → {b}',scope=r['scope'],event_id=r['event_id'],valid_from=r['valid_from'],valid_to=r['valid_to'],status=r['status'],quantities=' | '.join(map(qtext,quantities[r['id']])),evidence_ids=';'.join(evidence[r['id']]),note_zh=r['note_zh']))
with (out/'relations_readable.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)

# Machine-readable dictionary: types, meanings, and actual controlled vocabulary.
meanings={
'id':'本表稳定唯一标识；跨表连接使用 *_id 字段', 'name':'主体原名或明确标为分析角色的名称', 'entity_type':'主体类型；集合、用途及占位角色不得视为法律实体', 'description_zh':'主体说明',
'title':'来源、事件或快照标题','publication_date':'来源发表日期；允许年月或年份','source_type':'来源类别','local_filename':'相对原始材料目录的文件名；原PDF未复制入包','url':'原始来源链接','checked_on':'本次已核对本地文件日期；未记录网页核对日则为空','sha256':'本地原始文件SHA-256；用于检验是否同一版本','access_note':'来源保存和核对范围',
'source_id':'引用 sources.id','pdf_pages':'PDF阅读器页序，从1开始；区间用连字符','printed_pages':'原文印刷页码，与PDF页序区分','original_excerpt':'原文短摘录；可能统一换行和上标，不是完整支撑段落','summary_zh':'相关页段的中文归纳；可能覆盖摘录之外的内容',
'date_start':'事件起始或发生日期，允许YYYY / YYYY-MM / YYYY-MM-DD','date_end':'事件区间结束日期；空值不推定','date_precision':'事件日期精度','status':'事实状态；不是法律意见','note_zh':'条件、限制、解读说明',
'subject_id':'箭头起点，引用 entities.id','predicate':'关系类别，动词方向必须结合主体与客体理解','object_id':'箭头终点，引用 entities.id','scope':'权利、工程、公司或用途范围','event_id':'关联 events.id；空值表示尚无对应事件','valid_from':'材料记载的起点；也可能是交易或未来行动日期，须结合predicate/status','valid_to':'材料明确终期；空值不意味着永久有效','evidence_level':'直接来源陈述或分析映射标志',
'relation_id':'引用 relations.id','measure':'量的含义；不同measure不可直接相加','value':'数值；未知为空而不是0；百分数采用0—100','unit':'单位','operator':'eq 等于、gt 大于、lte 不超过、unknown 未知','denominator':'百分比对应分母；不同分母不可比较或加总','qualifier_zh':'适用条件和不可加总提示','evidence_id':'引用 evidence.id；数值有独立证据指向',
'period_start':'展示期起点','period_end':'展示期终点；空值不表示永久有效','selection_rule':'快照选取规则，人工分析选编','snapshot_id':'引用 snapshots.id','topic':'差异或解释边界主题','evidence_ids':'涉及的 evidence.id，逗号分隔','issue_zh':'来源差异或不可混同点','treatment_zh':'在数据中的处理原则'}
fks={'evidence':{'source_id':'sources.id'},'relations':{'subject_id':'entities.id','object_id':'entities.id','event_id':'events.id'},'quantities':{'relation_id':'relations.id','evidence_id':'evidence.id'},'relation_evidence':{'relation_id':'relations.id','evidence_id':'evidence.id'},'snapshot_relations':{'snapshot_id':'snapshots.id','relation_id':'relations.id'}}
dictionary={'schema_version':'1.0.0','canonical_file':'rights_dataset.json','null_rule':'JSON/SQLite null = 未知或不适用；CSV为空。按measure/operator/note区分。','tables':{}}
for t,rows in tables.items():
 cols={}
 for k in rows[0]:
  c={'type':'number' if t=='quantities' and k=='value' else 'string','nullable':k!='id','description_zh':meanings[k]}
  if k in fks.get(t,{}):c['references']=fks[t][k]
  if k in ['predicate','status','evidence_level','operator','entity_type','source_type','date_precision','unit','measure']:c['observed_values']=sorted({r[k] for r in rows if r[k] is not None})
  cols[k]=c
 dictionary['tables'][t]={'primary_key':'id','row_count':len(rows),'columns':cols}
(out/'data_dictionary.json').write_text(json.dumps(dictionary,ensure_ascii=False,indent=2)+'\n')

# Reproducible graph sources: relation-level references keep arrows traceable.
(out/'snapshots').mkdir(exist_ok=True)
rels={r['id']:r for r in p['relations']}
for snap in p['snapshots']:
 selected=[rels[x['relation_id']] for x in p['snapshot_relations'] if x['snapshot_id']==snap['id']]
 used=sorted({x[k] for x in selected for k in ['subject_id','object_id']})
 lines=['%% '+snap['title'],'%% References: evidence IDs resolve through evidence.csv to sources.csv.','%% Dotted arrows indicate future / proposal / undetermined or disputed relations.','flowchart TD']
 for key in used:lines.append(f'  {key}["{entities[key]["name"]}"]')
 for r in selected:
  label=r['predicate'].replace('_',' ')+'<br/>'+'; '.join(map(qtext,quantities[r['id']]))
  label+=' ['+', '.join(evidence[r['id']])+']'
  label=label.replace('"',"'")
  arrow='-.->' if r['status'] in ['future','proposal','undetermined','source_conflict','agreed_future_obligation'] else '-->'
  lines.append(f'  {r["subject_id"]} {arrow}|"{label}"| {r["object_id"]}')
 (out/'snapshots'/f'{snap["id"]}.mmd').write_text('\n'.join(lines)+'\n')

prior=out/'prior_outputs';prior.mkdir(exist_ok=True)
for name in ['negotiation_concession_分析.csv','材料阅读与筛选清单.csv','negotiation_concession_timeline.png','negotiation_concession_timeline.svg']:
 shutil.copy2(root/'02_outputs/negotiation_concession'/name,prior/name)
readme='''# Anniviers / Gougra 权利关系分析数据包

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
'''
(out/'README.md').write_text(readme,encoding='utf-8')
# Final checks across each representation.
con=sqlite3.connect(out/'rights_dataset.sqlite')
for name,rows in tables.items():
 assert con.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0]==len(rows)
 with (out/'csv'/f'{name}.csv').open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==len(rows)
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
assert len(flat)==50
con.close()
manifest={'version':'1.0.0','created_on':'2026-10-04','counts':{k:len(v) for k,v in tables.items()},'files':[]}
for f in sorted(out.rglob('*')):
 if f.is_file() and f.name!='manifest.json':manifest['files'].append({'path':str(f.relative_to(out)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive=root/'02_outputs/anniviers_rights_dataset.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(out.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(out.parent))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'files':len(manifest['files'])+1,'zip_bytes':archive.stat().st_size,'validation':'JSON/SQLite/CSV counts match; database integrity and foreign keys pass; ZIP passes'},ensure_ascii=False))
