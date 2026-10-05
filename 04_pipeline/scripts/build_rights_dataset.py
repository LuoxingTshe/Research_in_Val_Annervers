from pathlib import Path
import json, sqlite3, hashlib, zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'02_outputs/anniviers_rights_dataset'
OUT.mkdir(parents=True,exist_ok=True)
tables={k:[] for k in ['entities','sources','evidence','events','relations','quantities','relation_evidence','snapshots','snapshot_relations','discrepancies']}
def row(table,**kw): tables[table].append(kw); return kw['id']
def entity(i,name,kind,zh):return row('entities',id=i,name=name,entity_type=kind,description_zh=zh)
for x in [
 ('anniviers','Commune d’Anniviers','municipality','2009年合并成立；主要公共水力授予方'),
 ('ayer','Commune d’Ayer','historical_municipality','Anniviers前身市镇'),
 ('grimentz','Commune de Grimentz','historical_municipality','Anniviers前身市镇'),
 ('st_jean','Commune de St-Jean','historical_municipality','Anniviers前身市镇'),
 ('chandolin','Commune de Chandolin','historical_municipality','Anniviers前身市镇'),
 ('st_luc','Commune de St-Luc','historical_municipality','Anniviers前身市镇；2008年代表Niouc团体'),
 ('vissoie','Commune de Vissoie','historical_municipality','Anniviers前身市镇'),
 ('ergisch','Commune d’Ergisch','municipality','上段公共授予方'),
 ('turtmann','Commune de Turtmann','historical_municipality','1952年授权者；2013年合并前名称'),
 ('turtmann_unterems','Commune de Turtmann-Unterems','municipality','上段公共授予方'),
 ('oberems','Commune d’Oberems','municipality','上段公共授予方'),
 ('chippis','Commune de Chippis','municipality','上、下段公共授予方'),
 ('chalais','Commune de Chalais','municipality','上、下段公共授予方'),
 ('valais','Canton du Valais','canton','上段授予方及批准当局；下段身份在来源间表述不同'),
 ('sierre','Commune de Sierre','municipality','FMG股东，不能据此推定为上段授予方'),
 ('private_1943','Two unnamed private holders','unnamed_group','1943年Gougra concession受让者；原文未具名'),
 ('isotherme','Isotherme SA','company','1953年向FMG转让各项特许权'),
 ('fmg','Forces Motrices de la Gougra SA','company','直接特许经营权持有人'),
 ('alpiq','Alpiq SA','company','FMG控股股东；不等于直接承接公共水权'),
 ('rhonewerke','Rhonewerke AG','company','FMG股东'),
 ('oiken','Oiken','company','FMG股东'),
 ('fmv','Forces Motrices Valaisannes','company','公共方专业支持者；2026年来源称未来股东'),
 ('upper_grantors','Upper Gougra public grantors','analytical_group','六市镇加Valais州的集合，不是新增法人'),
 ('lower_grantors','Lower Navizence municipal grantors','analytical_group','Anniviers、Chalais、Chippis及相应历史前身；组名不裁定州的法律身份'),
 ('acc_fmg39','ACC-FMG39','association','公共授予方协调协会；不等于未来特许经营公司'),
 ('niouc','Niouc irrigation consortium','irrigation_consortium','灌溉供水权利人'),
 ('briey','Briey irrigation consortium','irrigation_consortium','既有权源及免费性曾存在争议'),
 ('roux','Bisse Roux','irrigation_system','灌渠及其供水用途；不是法人'),
 ('grand_st_luc','Grand bisse de St-Luc','irrigation_system','灌渠及其供水用途；不是法人'),
 ('zinal_lifts','Remontées mécaniques de Zinal','historical_company','2006年造雪协议方'),
 ('grimentz_lifts','Remontées mécaniques de Grimentz','historical_company','2007年造雪协议方'),
 ('rmgz','Remontées mécaniques Grimentz-Zinal','company','前述两家缆车公司合并后的公司'),
 ('future_operator','Future upper-stage concession holder','undetermined_role','未在已核对资料中确定法律实体，不能填成FMV或Alpiq'),
 ('future_structure','Future operating structure','undetermined_role','未来持股结构占位项；不推定与未来concession持有人为同一实体'),
 ('upper_assets','Upper Gougra hydroelectric assets','asset_scope','Moiry／Tourtemagne等上段设施'),
 ('lower_stage','Lower Navizence stage','asset_scope','下段工程；工程参与比例与FMG公司股权不同'),
]:entity(*x)

SAV='Savoy_Analyse de la gouvernance de la multifonctionnalité.pdf'
BAG='Bagnoud_Val d’Anniviers-on prépare déjà l’échéance de la concession des Forces motrices de la Gougra en 2039.pdf'
def source(i,title,date,kind,path=None,url=None):
 p=ROOT/path if path else None
 return row('sources',id=i,title=title,publication_date=date,source_type=kind,local_filename=path,url=url,checked_on='2026-10-04' if p else None,sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p else None,access_note='用户提供的原始PDF' if p else '沿用前一轮已核对的官方网页；核对日未单独记录。本数据包保存引用及摘录，不含网页全文')
source('S','Andréa Savoy, Analyse de la gouvernance de la multifonctionnalité…, Working paper 6','2025-07','research_report',SAV)
source('B','Florent Bagnoud, Val d’Anniviers: on prépare déjà l’échéance de la concession des Forces motrices de la Gougra en 2039','2022-12-22','newspaper',BAG)
source('C','Chalais Info no. 6, Convention 2022 en vue de l’échéance des concessions Gougra en 2039','2022-12','official_municipal_bulletin',url='https://www.chalais.ch/data/documents/WEB_JournalChalaisInfoDecembre2022.pdf')
source('A','Alpiq, La centrale hydroélectrique de Mottec optimisée pour un avenir énergétique durable','2025-05-26','official_company_release',url='https://www.alpiq.com/fr/newsroom/communiques-de-presse/la-centrale-hydroelectrique-de-mottec-optimisee-pour-un-avenir-energetique-durable')
source('F','FMV, Gougra 2039 : Un modèle construit dans la sérénité','2026-03-16','official_company_interview',url='https://fmv.ch/concessions/concession-gougra-2039/')
def ev(i,s,pages,printed,quote,summary):return row('evidence',id=i,source_id=s,pdf_pages=pages,printed_pages=printed,original_excerpt=quote,summary_zh=summary)
ev('EV01','S','77-78','76-77','La société Isotherme SA transfère en 1953 ses diverses concessions à la société des Forces motrices de la Gougra.','1943年Grimentz/Ayer授予两名私人，之后转Isotherme；Oberems1951、Ergisch/Turtmann1952授予Isotherme；1953转FMG。')
ev('EV02','S','78','77','Ces concessions arriveront à échéance en 2039.','上段2039年、下段2004年续至2084年；历史授权不可按现有市镇名称回填。')
ev('EV03','S','83-84','82-83','devenant partenaires à 51% de l’aménagement du palier inférieur jusqu’en 2084.','研究报告将下段51%参与与2004年回归联系；另记三市镇获得10%公司股本。与2026年来源的时间口径有差异。')
ev('EV04','S','100','99','Ils s’accordent ainsi sur le paiement d’un montant forfaitaire par les FMG pour le développement du réseau d’irrigation par aspersion','2004年Niouc配额120 L/s；2008-03-18以削减超过50%换FMG定额设施资助。金额未披露。')
ev('EV05','S','100-101','99-100','Cette convention fixe les débits pour le bisse de Briey à 45 l/s, avec possibilité de les augmenter sur demande jusqu’à 70 l/s en cas de sécheresse exceptionnelle.','1979及2004年70 L/s；2017-06-13和解通常45，特殊干旱可请求最高70。')
ev('EV06','S','101','100',"Bisse Roux : prélèvement maximal de 50 litres par seconde, pour un volume annuel maximal de 120'000 m³ utilisable entre le 1er mai et le 30 septembre.",'2018年Roux年额120000 m³、St-Luc32000 m³；各最高50 L/s；5月1日至9月30日；超额按未生产kWh价值购水。摘录统一了原PDF的换行和上标。')
ev('EV07','S','102-103','101-102','vous devez d’abord avoir le OK de la commune.','2006及2007造雪供水协议；需要市镇同意；水能特许权不等于任意用途售水权。')
ev('EV08','S','111','110','Nous, on a à peu près 55% de la force.','Anniviers受访者称拥有约55%的水力，不能当成FMG持股超过50%。')
ev('EV09','S','112-113','111-112','c’est nous qui négocions le prix de l’eau à facturer aux remontées mécaniques','有关2039造雪、消防预留水量及定价的访谈设想；不是已授配额。')
ev('EV10','B','3-5','3-5','Aujourd’hui, cette convention stipule uniquement le prix à payer','新闻记载1500万总额（干式1400万、现代化100万）；未来授权另作决定；湿式设施免费回归。')
ev('EV11','C','12-14','12-14','Anniviers : 55.4% ; 15.05 millions de francs','两处短摘录以分号分隔：上段Anniviers55.4%；2022年协议1505万；其余公共份额及年度费用见同页段。')
ev('EV12','A',None,None,'Alpiq 54%','2025年公告股权：Alpiq54、Rhonewerke27.5、Anniviers7.71、Sierre7.5、Chippis1.79、Chalais0.5、Oiken1.0。')
ev('EV13','F',None,None,'les trois communes concédantes Anniviers, Chalais et Chippis prendront 51% du palier inférieur.','在2039年到期的语境下称三市镇将接收下段51%；与研究报告时间表述不同。')
ev('EV14','F',None,None,'une mise à jour annuelle de la valeur de la partie sèche','回归协议有年度干式资产估值更新；FMV被称作未来股东，不构成其已取得新concession的证据。')

def event(i,date,end,title,status='documented',note=None):return row('events',id=i,date_start=date,date_end=end,date_precision='day' if date and len(date)==10 else 'year',title=title,status=status,note_zh=note)
event('E1943','1943',None,'Gougra grants to private holders')
event('E1951','1951','1952','Tourtemagne grants to Isotherme')
event('E1953','1953',None,'Assignment from Isotherme to FMG')
event('E1959','1959',None,'Upper-stage concession term','documented','来源另有1950—1957年分项授权口径；1959为官方公告及新闻所述上段期限起点。')
event('E2004','2004',None,'Lower-stage concession renewal')
event('E2009','2009-01-28',None,'Approval of the 2004 concession')
event('E2006','2006',None,'Zinal snowmaking agreement')
event('E2007','2007',None,'Grimentz snowmaking agreement')
event('E2008','2008-03-18',None,'Niouc irrigation settlement')
event('E2017','2017-06-13',None,'Briey irrigation settlement')
event('E2018','2018',None,'Bisse Roux and St-Luc agreements')
event('E2022','2022',None,'Upper-stage compensation agreement','documented','12月大会批准；精确签约日未核实。')
event('E2025','2025-05-26',None,'Published FMG shareholding observation')
event('E2026','2026-03-16',None,'Official update on the 2039 return')
event('E2039','2039',None,'Scheduled upper-stage concession expiry','future')
event('E2084','2084',None,'Scheduled lower-stage concession expiry','future')

def rel(i,a,p,b,scope,e,evs,start=None,end=None,status='documented',level='source_statement',note=None):
 row('relations',id=i,subject_id=a,predicate=p,object_id=b,scope=scope,event_id=e,valid_from=start,valid_to=end,status=status,evidence_level=level,note_zh=note)
 for v in evs:row('relation_evidence',id=i+'_'+v,relation_id=i,evidence_id=v)
 return i
def q(i,r,measure,val,unit,operator='eq',denom=None,qualifier=None,evidence=None):
 return row('quantities',id=i,relation_id=r,measure=measure,value=val,unit=unit,operator=operator,denominator=denom,qualifier_zh=qualifier,evidence_id=evidence)

for a in ['grimentz','ayer']:
 rel('H43_'+a,a,'grants_concession_to','private_1943','Gougra','E1943',['EV01'],'1943')
rel('H_private','private_1943','assigns_concession_to','isotherme','Gougra',None,['EV01'],note='日期未披露；在1943授权之后及1953转让之前。')
for a,y in [('oberems','1951'),('ergisch','1952'),('turtmann','1952')]:
 rel('H_'+a,a,'grants_concession_to','isotherme','Turtmaenna','E1951',['EV01'],y)
rel('H53','isotherme','assigns_concession_to','fmg','multiple_historical_concessions','E1953',['EV01'],'1953',note='价格和权利总量未披露。')
rel('U_grant','upper_grantors','grants_concession_to','fmg','upper_Gougra','E1959',['EV02','EV11'],'1959','2039')
rel('L_grant','lower_grantors','grants_concession_to','fmg','lower_Navizence','E2004',['EV02'],'2004','2084',note='2009-01-28核准；该关系不裁定州是否也是直接授予人。')
q('Q_term','L_grant','term',80,'year',evidence='EV02')
rel('U_fees','fmg','pays_annual_water_fee_to','upper_grantors','upper_Gougra',None,['EV11'],note='金额未披露；与公司分红、售电收益分开。')
q('Q_fee','U_fees','annual_fee',None,'CHF/year',operator='unknown',evidence='EV11')
for a,v in [('anniviers',55.4),('ergisch',18.1),('turtmann_unterems',11.9),('oberems',9.4),('valais',2.4),('chippis',2.2),('chalais',0.6)]:
 r=rel('G_'+a,a,'holds_granting_share_in','upper_grantors','upper_Gougra',None,['EV11'],note='2022官方分配表；当前结构沿用已知最新该类数据，未声称2026重新测量。')
 q('QG_'+a,r,'granted_hydraulic_force_share',v,'percent',denom='upper_Gougra_total_granted_hydraulic_force',evidence='EV11')
for a,v in [('alpiq',54),('rhonewerke',27.5),('anniviers',7.71),('sierre',7.5),('chippis',1.79),('chalais',.5),('oiken',1)]:
 r=rel('EQ_'+a,a,'owns_equity_in','fmg','FMG_company','E2025',['EV12'],note='2025-05-26观测值；股权不等于水力授予份额。')
 q('QE_'+a,r,'equity_share',v,'percent',denom='FMG_total_share_capital',evidence='EV12')
rel('N2004','fmg','owes_reserved_irrigation_supply_to','niouc','lower_Navizence','E2004',['EV04'],'2004',note='2004授权额度；2008协议另降低实际约定量，不写成全部授权条文被正式修改。')
q('QN120','N2004','concession_flow',120,'L/s',evidence='EV04')
rel('N2008','niouc','accepts_reduced_allocation_from','fmg','Niouc_irrigation','E2008',['EV04'],'2008-03-18')
q('QNcut','N2008','allocation_reduction',50,'percent',operator='gt',denom='previous_120_L_per_s',evidence='EV04')
rel('Nfund','fmg','funds_irrigation_infrastructure_for','niouc','Niouc_irrigation','E2008',['EV04'],'2008-03-18')
q('QNfund','Nfund','lump_sum',None,'CHF',operator='unknown',evidence='EV04')
rel('B2004','fmg','owes_reserved_irrigation_supply_to','briey','lower_Navizence','E2004',['EV05'],'2004',note='70 L/s可追溯至1979文书；2017年出现后续和解，但旧权利正式消灭日期未确定。')
q('QB70','B2004','ordinary_flow',70,'L/s',evidence='EV05')
rel('B2017','fmg','agrees_irrigation_supply_to','briey','Briey_irrigation','E2017',['EV05'],'2017-06-13')
q('QB45','B2017','ordinary_flow',45,'L/s',evidence='EV05')
q('QBdrought','B2017','exceptional_drought_flow',70,'L/s',operator='lte',qualifier='须请求；不是全年常规额度',evidence='EV05')
rel('Bsettle','briey','settles_rights_dispute_with','fmg','Briey_irrigation','E2017',['EV05'],'2017-06-13',note='双方避免不确定诉讼，不推定付款或一切历史权利转让。')
for who,vol in [('roux',120000),('grand_st_luc',32000)]:
 r=rel('W_'+who,'fmg','agrees_free_supply_with','anniviers',who,'E2018',['EV06'],'2018',note='市镇为协议方；灌渠是用途，不是接收concession的法人。')
 q('QV_'+who,r,'annual_volume',vol,'m3/year',operator='lte',evidence='EV06')
 q('QF_'+who,r,'flow',50,'L/s',operator='lte',qualifier='每年05-01至09-30',evidence='EV06')
 rel('DIST_'+who,'anniviers','arranges_irrigation_supply_for',who,who,'E2018',['EV06'],'2018',level='analytical_representation',note='表达协议受益用途，不代表材料证明了独立的二次权利转让。')
rel('W_excess','anniviers','pays_excess_water_charge_to','fmg','Roux_and_StLuc','E2018',['EV06'],'2018',note='按未生产kWh的价值计费；单价未披露。')
for who,e,y in [('zinal_lifts','E2006','2006'),('grimentz_lifts','E2007','2007')]:
 rel('SN_'+who,'fmg','agrees_paid_water_supply_to',who,'snowmaking',e,['EV07'],y,note='市镇须同意用途；供水协议不是水电concession转让。')
 rel('PAY_'+who,who,'pays_water_charge_to','fmg','snowmaking',e,['EV07'],y)
 q('QS_'+who,'SN_'+who,'volume',None,'m3',operator='unknown',evidence='EV07')
rel('SN_rmgz','fmg','supplies_water_to','rmgz','snowmaking',None,['EV07'],level='source_statement',note='合并后的现状名称；具体合并日期未在此数据集核实。')
rel('VAL22','upper_grantors','agrees_future_compensation_to','fmg','upper_Gougra','E2022',['EV10','EV11','EV14'],'2022',status='agreed_future_obligation',note='约定2039支付；2022金额不是最终固定结算额。')
q('QCofficial','VAL22','agreed_2022_compensation',15050000,'CHF',qualifier='官方报告金额；覆盖约定资产及项目范围，存在更新机制',evidence='EV11')
q('QCpress','VAL22','reported_rounded_compensation',15000000,'CHF',qualifier='新闻口径；与官方金额是并列证据，不相加',evidence='EV10')
q('QCpressdry','VAL22','reported_dry_asset_component',14000000,'CHF',qualifier='新闻分项；属于报道总额，不能另加',evidence='EV10')
q('QCpressmodern','VAL22','reported_modernization_component',1000000,'CHF',qualifier='新闻分项；属于报道总额，不能另加',evidence='EV10')
rel('RETURN39','fmg','returns_assets_to','upper_grantors','upper_Gougra','E2039',['EV10','EV14'],'2039',status='future',note='湿式资产无偿；有偿部分及现代化依协议，不能解释为将旧concession出售给市镇。')
q('QWet','RETURN39','wet_asset_return_price',0,'CHF',evidence='EV10')
rel('FUT_GRANT','upper_grantors','may_grant_new_concession_to','future_operator','upper_Gougra','E2039',['EV09','EV10','EV14'],'2039',status='undetermined',note='新主体、期限和配额未证实；不得据FMV未来股东身份填充受让人。')
rel('FUT_RESERVE','upper_grantors','may_reserve_local_water_for','anniviers','upper_Gougra','E2039',['EV09'],'2039',status='proposal',note='造雪、消防等地方用水保留为设想，无已确认数量。')
rel('FMV_support','fmv','supports_return_preparation_for','upper_grantors','upper_Gougra','E2026',['EV14'],status='documented')
rel('FMV_future','fmv','is_described_as_future_shareholder_of','future_structure','future_operating_structure','E2026',['EV14'],status='future',level='role_mapping',note='对象为待定经营结构占位角色；不认定该公司已设立或与未来特许持有人为同一主体；比例未披露。')
rel('LOWER51old','lower_grantors','is_reported_as_partner_in','lower_stage','lower_Navizence','E2004',['EV03'],'2004','2084',status='source_conflict',note='研究报告时间口径；不可当作无争议当前值。')
q('QL51old','LOWER51old','stage_participation',51,'percent',denom='lower_Navizence_stage',evidence='EV03')
rel('LOWER51new','lower_grantors','is_expected_to_take_participation_in','lower_stage','lower_Navizence','E2039',['EV13'],'2039',status='future',note='2026官方访谈的时间口径；与旧研究并列保存。')
q('QL51new','LOWER51new','stage_participation',51,'percent',denom='lower_Navizence_stage',evidence='EV13')
rel('LOWER10','lower_grantors','receives_equity_in','fmg','FMG_company','E2004',['EV03'],'2004',note='研究报告记载的10%公司股本；不得与工程51%相加。')
q('QL10','LOWER10','equity_received',10,'percent',denom='FMG_total_share_capital',evidence='EV03')
rel('L2084','fmg','reaches_concession_expiry_with','lower_grantors','lower_Navizence','E2084',['EV02'],'2084',status='future',note='到期日期，不表示已决定新经营人或已确定接收全部资产的价格。')

snapshots=[
 ('T1953','1943','1953','Historical concentration of concessions',[r['id'] for r in tables['relations'] if r['id'].startswith('H')]),
 ('T2009','2004','2009','Lower-stage renewal and reserved irrigation',['L_grant','N2004','N2008','Nfund','B2004','LOWER10','LOWER51old']),
 ('T2018','2017','2018','Quantified local water agreements',['U_grant','L_grant','B2017','Bsettle','W_roux','W_grand_st_luc','DIST_roux','DIST_grand_st_luc','W_excess','SN_zinal_lifts','SN_grimentz_lifts']),
 ('TCURRENT','2025','2026','Latest documented structure, not a real-time registry',[r['id'] for r in tables['relations'] if r['id'].startswith(('G_','EQ_'))]+['U_grant','L_grant','B2017','W_roux','W_grand_st_luc','W_excess','SN_rmgz','VAL22','FMV_support']),
 ('T2039','2039',None,'Future return and separate new licensing',['RETURN39','VAL22','FUT_GRANT','FUT_RESERVE','FMV_future','LOWER51new','L_grant','L2084']),
]
for i,start,end,title,rels in snapshots:
 row('snapshots',id=i,period_start=start,period_end=end,title=title,selection_rule='Analyst-curated relations; includes historical instruments relevant to the displayed period. Not a legal registry or automatic validity determination.')
 for r in rels:row('snapshot_relations',id=i+'_'+r,snapshot_id=i,relation_id=r)
for x in [
 ('D01','Water-force share versus equity','EV08,EV11,EV12','55%／55.4%指上段已授水力；Alpiq54%、Anniviers7.71%指FMG股本。','按分母分开存储；不生成综合最大权利排名。'),
 ('D02','Lower-stage 51% timing','EV03,EV13','Savoy将51%参与关联2004回归；FMV2026称2039将接收51%。','保留两个关系；旧口径标source_conflict，未来图优先使用2026说明。'),
 ('D03','Compensation amount and updating','EV10,EV11,EV14','新闻1500万及1400万+100万；官方1505万；另有年度估值更新。','官方1505万作为2022协议口径；未来结算数未知；分项与并列金额禁止相加。'),
 ('D04','Upper-concession dates','EV01,EV02,EV11','历史多份授权及1953转让，与1959上段期限起点不是同一事件。','分项事件分别保存；不将1959回填为1953转让日期。'),
 ('D05','Canton in lower-stage granting community','EV02,EV03,EV10','研究及2026说明突出下段三市镇；新闻将州也列入下段授予共同体。','lower_grantors仅定义市镇集合；不将州排除或纳入作为裁定。'),
 ('D06','Water agreements versus concession transfers','EV04,EV05,EV06,EV07','供水、历史灌溉主张、股权、资产回归、concession各不相同。','仅历史私人→Isotherme→FMG使用assigns_concession_to；供水边不编码为转让。'),
]:row('discrepancies',id=x[0],topic=x[1],evidence_ids=x[2],issue_zh=x[3],treatment_zh=x[4])

metadata={'schema_version':'1.0.0','created_on':'2026-10-04','language':'English identifiers; Chinese interpretive notes; original French excerpts','geographic_scope':'Anniviers / Gougra / Navizence system, including connected Tourtemagne upper-stage grantors','scope_note_zh':'结构化上一轮权利关系总结及关键时间点，不等于此前52条跨河谷记录的全量重编；原CSV保持不变。','current_note_zh':'目前指已核对的2025—2026公开记载；比例可能来自较早公布的仍被引用资料，不代表2026年实时登记。','date_rules':'ISO 8601 partial dates: YYYY, YYYY-MM, YYYY-MM-DD. Never expand a year into an invented exact date. Null = not established.','direction_rules':'subject -> predicate -> object; payment and right transfer are separate relations. A tree position does not create a legal assignment.','quantity_rules':'All values numeric or null. Percentages use 0–100. gt/lte/eq/unknown preserve bounds. Each percentage has a denominator. Multiple observations must not be summed without checking measure and evidence.','source_priority':'Keep conflicting observations. Prefer primary documents for the same claim and explicit dates, without silently overwriting the research report.','limitations_zh':['未认定金融债权出售或债转股。','未穷尽所有河谷水权及私人权利。','未来经营者是占位角色，不是已成立或已获授权实体。','快照是分析选编，不是法律有效期查询结果。']}
payload={'metadata':metadata,**tables}
(OUT/'rights_dataset.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Derived SQLite database: keys and references retained; no inputs are modified.
db=OUT/'rights_dataset.sqlite'
if db.exists(): db.unlink()
con=sqlite3.connect(db);con.execute('PRAGMA foreign_keys=ON')
refs_fk={'evidence':{'source_id':('sources','id')},'relations':{'subject_id':('entities','id'),'object_id':('entities','id'),'event_id':('events','id')},'quantities':{'relation_id':('relations','id'),'evidence_id':('evidence','id')},'relation_evidence':{'relation_id':('relations','id'),'evidence_id':('evidence','id')},'snapshot_relations':{'snapshot_id':('snapshots','id'),'relation_id':('relations','id')}}
for table,records in tables.items():
 keys=list(records[0]);defs=[]
 for k in keys:
  typ='REAL' if table=='quantities' and k=='value' else 'TEXT'
  spec=f'"{k}" {typ}'+(' PRIMARY KEY' if k=='id' else '')
  if k in refs_fk.get(table,{}):target,col=refs_fk[table][k];spec+=f' REFERENCES "{target}"("{col}")'
  defs.append(spec)
 con.execute(f'CREATE TABLE "{table}" ({", ".join(defs)})')
 con.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" for _ in keys)})',[[r.get(k) for k in keys] for r in records])
con.execute('CREATE TABLE metadata (key TEXT PRIMARY KEY, value_json TEXT NOT NULL)')
con.executemany('INSERT INTO metadata VALUES (?,?)',[(k,json.dumps(v,ensure_ascii=False)) for k,v in metadata.items()])
con.execute('''CREATE VIEW relation_details AS SELECT r.*, s.name AS subject_name,o.name AS object_name,q.measure,q.value,q.unit,q.operator,q.denominator,q.qualifier_zh,q.evidence_id AS quantity_evidence_id FROM relations r JOIN entities s ON s.id=r.subject_id JOIN entities o ON o.id=r.object_id LEFT JOIN quantities q ON q.relation_id=r.id''')
con.execute('''CREATE VIEW evidence_links AS SELECT re.relation_id,e.id AS evidence_id,e.pdf_pages,e.printed_pages,e.original_excerpt,e.summary_zh,s.id AS source_id,s.title,s.publication_date,s.url,s.local_filename FROM relation_evidence re JOIN evidence e ON e.id=re.evidence_id JOIN sources s ON s.id=e.source_id''')
con.commit()
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not con.execute('PRAGMA foreign_key_check').fetchall()
assert abs(sum(x['value'] for x in tables['quantities'] if x['measure']=='equity_share')-100)<1e-8
assert abs(sum(x['value'] for x in tables['quantities'] if x['measure']=='granted_hydraulic_force_share')-100)<1e-8
assert len({r['id'] for r in tables['relations']})==len(tables['relations'])
con.close()
print(json.dumps({k:len(v) for k,v in tables.items()},ensure_ascii=False))
