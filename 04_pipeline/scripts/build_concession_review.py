import csv
import json
import hashlib
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '02_outputs/concession_review'
OUT.mkdir(exist_ok=True)
timeline_path = ROOT / '02_outputs/negotiation_concession/negotiation_concession_分析.csv'
dataset_path = ROOT / '02_outputs/anniviers_rights_dataset/rights_dataset.json'
timeline = list(csv.DictReader(timeline_path.open(encoding='utf-8-sig')))
dataset = json.loads(dataset_path.read_text())

# One assessment for every existing timeline record. Supplemental page numbers
# refer to the already available Savoy PDF extraction, not to new web research.
# status, geographical referent, semantic object, qualification, extra Savoy pages
M = {
1: ('具名地物', 'Bisse de Niouc；Niouc喷灌网络；Vissoie–Niouc引水隧洞18号窗口', '灌溉供水额度、减量承诺、喷灌设施投资给付', '约25 L/s是旅游渠保水，不能代替全部灌溉额度；资金本身另属非地物客体。', '81–82,95'),
2: ('具名地物', 'Bisse de Briey；Vissoie–Niouc隧洞18号窗口；Niouc悬索桥上的输水管；争议另涉及旧Bisse des Sarrasins', '历史灌溉权、免费性、和解后的流量请求权', '2017年常态45 L/s，特殊干旱可申请最高70 L/s；旧Sarrasins渠为争议关联地物，不推定仍供水。', '81,95'),
3: ('具名地物', 'Bisse Roux；torrent des Moulins；Vuibiesse取水设施', '季节性免费灌溉水量及超额水费', '50 L/s、120000 m³/年，5月1日至9月30日；渠不是接收特许权的法人。', '81–82'),
4: ('具名地物', 'Grand bisse de St-Luc；torrent des Moulins；Vuibiesse取水设施', '季节性免费灌溉水量及超额水费', '50 L/s、32000 m³/年，5月1日至9月30日；与Roux共享取水来源但各有协议额度。', '81–82'),
5: ('地物未细定', 'Ayer／Anniviers旧灌渠、FMG管道上的接水点及替代喷灌网络', '旧渠供水及维护义务调整、管道接入、设施出资', '只能定位到体系；各渠、地块及接水点未逐一具名，不可直接用六条已知bisses填满本条。', '99'),
6: ('具名地物', 'Vissoie–Niouc拟建压力引水隧洞；Plats de la Lée冲积地与河道修复区', '不反对工程／放弃申诉、生态修复出资', '工程地点与补偿地点是两个不同地物；拟建隧洞不当作已建成。', '104–105'),
7: ('具名地物', 'Turtmänna河及其流域；Anniviers侧Gougra与Navizence上段', '跨流域生态治理与剩余流量让步', '不是河流或特许权的转让；治理尺度是工程整体，逐支流对应交换量未列。', '80–81,104'),
8: ('具名地物', 'Navizence下段：Vissoie电站出水口至Rhône回水口；torrent de Fang', '下段水力利用特许权及环境流量条件', '2004—2084，2009年核准；470和50 L/s是生态下泄，不能写成特许开发流量。', '78,80'),
9: ('具名地物', 'Tsarmette调压井上的泵站、Moiry–Mottec压力输水设施→Sorebois–Singlinaz雪场；Moiry坝脚管道→Bendolla雪场', '有偿造雪供水、市镇用途同意及水费', '2006 Zinal、2007 Grimentz；供水合同不等于水电特许权再转让。', '79–80,95'),
10: ('具名地物', 'Lac de Moiry湖面及许可航线、岸边告示牌', '皮划艇活动准入、安全责任、保险及告示费用', 'Savoy PDF104明确称活动于2023年底停止；历史许可不表示目前仍开展。', '96,104'),
11: ('具名地物', 'Gougra上段工程的干式设施资产集合', '2039年回归补偿及未来支付义务', '并非单一地物清单；旧时间线1500万为新闻口径，关系包官方2022口径1505万且有更新机制。', ''),
12: ('具名地物', 'Centrale de Mottec；Centrale de Vissoie及现代化设备', '投资残值／增值补偿、补助与出资分担', '投资金额不等于2039应付补偿额；设备逐项清单未提供。', '79'),
13: ('具名地物', 'Gougra上段涉水设施集合，关联Moiry、Tourtemagne坝库及输水设施', '湿式资产无偿回归请求权／移交义务', '具体回归资产边界须资产清册确认；R013原表“干式补偿见R010”为错误交叉引用，应参照R011。', '78–79'),
14: ('具名地物', 'Gougra特许权组覆盖水体：Gougra、Navizence上段、Turtmänna、Lac de Lona、Rhône的Turtmann–Chippis引水段及具名支流', '各项水力利用特许权及私人→Isotherme→FMG转让', '是一组分立授权，不是单份concession；1943、1951/1952、1953、1950—1957与1959期限起点须分开。', '77–78,94'),
15: ('具名地物', 'Gougra上段既有水体与工程范围；未来具体保留取水点未定', '新特许权授予决定、地方水量保留、未来持股安排', '2039安排；接收主体、期限、额度未确定；ACC-FMG39是协调协会，不能填成地物。', ''),
16: ('具名地物', 'Barrage de Moiry既有坝体及拟议加高部分', '加高项目许可、补助及期末投资残值补偿', '既有坝真实存在；8—10米加高为材料中的设想，不属于已存在的新地物。', ''),
17: ('地物未细定', 'Zinal两座公共喷泉', '喷泉设施所有权及安装／公共供水义务', '数量2座可确认；具体名称、位置及现存状况未确认。', ''),
18: ('地物未细定', '一处供给遭破坏的未具名水源；替代供水接入点未具名', '私人替代供水请求权', '不能认定该泉已物理消失；原文仅指供水受毁损。以请求权作审理客体，地物位置待补。', ''),
19: ('具名地物', 'Bisse de Ricard及Navizence峡谷约700米高程取水口；Bisse de Granges及Chippis平原取水段', '渠与设施产权、取水流量和维护义务', '两条渠、两个协议应分别审理；Ricard取水设施有2018洪灾损坏记录。', '81'),
20: ('具名地物', 'Moiry Via Ferrata所使用的FMG土地与攀登路线', '免费土地使用许可与项目责任', '路线范围可识别，地籍宗地和界线未给。', ''),
21: ('具名地物', 'Navizence电站下游Chippis饮用水取水点；Nava取水管道；Grand-Praz废弃物处理站供水接入', '饮用／非饮用取水及接管许可', '三个子安排须区分；10 m³/年仅对应Nava私人2017协议。', '95–96'),
22: ('具名地物', 'Moiry湖左岸Alpage de Moiry土地；右岸Alpage de Château-Pré土地；Moiry坝旁餐厅为转租链一方', '土地租赁、转租及租金请求权', '左岸市镇→Moiry牧场；右岸FMG→餐厅→Château-Pré牧场。宗地号未给。', '96'),
23: ('未识别地物', '', 'Hoirie Bornet及后继人的既有／剩余权利；EOS实物电力给付', '权利内容未细分，不能仅因Cleuson案例背景便指认具体湖、泉、渠或宗地。', ''),
24: ('具名地物', 'Bisse de Saxon；Printse水源；Cleuson原供水设施与Mauvoisin替代供水设施', 'Saxon灌溉供水及EOS对FMM补偿义务', '替代路线端点和全部管线未逐项列明；350 L/s为原Printse取水权。', ''),
25: ('具名地物', 'Tortin Ouest水流／流域', '1966年放弃的水力利用特许权及在先灌溉负担', '原文明示Tortin两个分支确切范围不详；保留历史名称，不硬配现代河段。', '24'),
26: ('具名地物', 'Basse-Printse下部水系，含Tortin Ouest', '已授而后放弃的开发权与项目支持', '自然水体存在；放弃的开发项目不当作已建水电设施。', ''),
27: ('具名地物', 'Cleuson-Dixence工程：Bieudron电站、地下引水隧洞、Tracouet–Bieudron压力竖井', '新增设施折旧、回归和残值补偿', '原文称不新增水权；2021／2022补充协议年份差异保留。', '24'),
28: ('未识别地物', '', 'WWF撤诉／不再维持申诉及EOS、州接受的保护补偿义务', 'Cleuson-Dixence为关联工程；具体补偿地块或修复河段未列，不能以工程代填补偿地物。', ''),
29: ('具名地物', 'Source des Bouillets；SEBA原有水源（未逐一具名）；连接SEBA的供水管线', '水源保障／购买、使用权和连接费用偿还', '2031排他期限为访谈记载；原水源与Bouillets替代水源分别保留。', ''),
30: ('具名地物', 'Retenue de Cleuson水库及市镇储水／供水接入设施', '可用库容、备用水购买及税费安排', '库容使用是权利客体；水库是承载地物，非水库所有权转让。', ''),
31: ('具名地物', 'Cleuson供水设施及Nendaz–Veysonnaz造雪系统', 'Alpiq→市镇→NVRM供水与付款链', 'Bieudron仅为替代发电价值计价参照；不等于造雪取水位置，具体分支管线未列。', ''),
32: ('具名地物', 'Cleuson大坝下泄设施；Printse河及其灌渠取水系统', '1945授权保留的充足灌溉用水及按需下泄请求', '200 L/s为访谈举例，不能当成所有时段固定配额。', ''),
33: ('具名地物', 'Dixence河床；Printse拟修复河段', '人工洪水、河床监测及替代生态修复义务', '具体Printse修复段界线未在原记录列明；大坝下游桥梁为风险背景。', ''),
34: ('具名地物', 'Hongrin／Petit Hongrin水系、Lac de l’Hongrin、Lac Léman；Hongrin南北双坝与Veytaux水电系统', '跨州水力特许使用权，包含Léman抽水', '1963授权；材料记1971-10-01运行起计至2051年9月底；完整支流与取水口仍须特许附件确认。', '57–58,67'),
35: ('地物未细定', 'Hongrin案例的一家未具名锯木厂', '能源补偿／电力给付请求权', 'PDF57另提L’Etivaz锯木厂，但不能据此确认其与1961合同工厂同一；审理以能源给付为客体。', '57,67'),
36: ('非地物客体', '', '年度鱼类实物配额，或等值货币的鱼群补充给付', '鱼是可移动实物，款项是金钱客体；具体放流地点未列，不以Hongrin地名代替给付客体。', ''),
37: ('具名地物', 'Hongrin-Léman Plus新增设施，核心为Veytaux II地下抽水蓄能电站', '新增设施折旧与特许期末安排', 'PDF58将Veytaux II明确对应Plus项目；合同覆盖的全部设备仍未逐项列出。', '58'),
38: ('具名地物', 'Lac de l’Hongrin蓄水；Hongrin下游生态洪水河段', '2022生态放水延期及2023额外补放义务', '只确认约定，未在本数据内核实2023实际补放履行。', '58'),
39: ('具名地物', 'Lac de l’Hongrin；Leysin与Les Mosses雪场；拟议17 km输水管线', '有条件造雪供水、报酬、融雪返水及另行抽水授权', '2024撤回项目；拟建管线不计为已存在地物，州抽水授权是否已获未证实。', ''),
40: ('具名地物', 'Lac de l’Hongrin直升机取水水面；受益高山牧场未具名', '2018干旱应急免费取水许可', '约40 m³是当次应急取水，不能扩成常设特许额度。', ''),
41: ('具名地物', 'Lac Léman→Lac de l’Hongrin→Hongrin河→Sarine流域的水文路径', '生态洪水取消／延期执行决定与物种传播风险控制', '不是设施产权转移；未证实新增补放承诺。', ''),
42: ('模板无个案地物', '', '免费保留水量、追加取水及能源成本补偿', '模板水量、位置待填，不能生成真实concession地物。', ''),
43: ('模板无个案地物', '', '待授水力利用权、首次费与年度水力费', '通用授权条款；无具体河段、设施或成交授权。', ''),
44: ('模板无个案地物', '', '湿式／干式设施回归及合理补偿', '资产类别存在于模板概念中，个案资产未填。', ''),
45: ('模板无个案地物', '', '权利负担清理、维护履行及补偿款留置', '不是已识别宗地上的负担；未做维护金额为待计算客体。', ''),
46: ('模板无个案地物', '', '回购权、股份、利润、董事席位与优先购买权', '公司治理和财产权益；无具体公司或资产可匹配。', ''),
47: ('模板无个案地物', '', '第三方取水权、消灭后的权利归属、特许权转让审批', '权利规则，非已发生转让；无指定水体。', ''),
48: ('制度无个案地物', '', '共有牧场／灌溉体系中的使用份额、继承和买卖资格', '牧场和灌渠只是地物类型，未列可逐一对应的真实个案。', ''),
49: ('具名地物', 'Äbibärgeri灌渠', '灌渠资产及市镇接管后的管理责任', '1922为回忆记载；精确渠线及与现代地图名称的对应仍待确认。', ''),
50: ('制度无个案地物', '', '传统bisses轮灌资格、按土地分配的水权、水费和维护义务', '这条摘录是一般制度说明，不能自动对应任一具体bisse。', ''),
51: ('制度无个案地物', '', '有期限水力利用权、年度授权费及涉水设施回归请求权', '瑞士制度概述，不是新的一份concession；不据此增加地物或个案计数。', ''),
52: ('理论无个案地物', '', '景观使用价值、文化身份、存在／内在价值及保护利益', '理论对象，未识别具体景观或已成交交换。', ''),
}

UPPER_WATER = ['Navizence supérieure', 'Turtmänna（Tourtemagne）', 'Gougra', 'Lac de Lona', 'Rhône：Turtmann至Chippis的引水相关河段', 'Brändjibach', 'Nebenbach', 'torrent des Mayens', 'torrent des Moulins', 'torrent de Barneusaz', 'torrent de Nava', 'torrent du Frilitälli']
UPPER = '；'.join(UPPER_WATER)
LOWER = 'Navizence下段（Vissoie电站出水口至Rhône回水口）及torrent de Fang；工程关联Vissoie–Niouc隧洞与Navizence电站'
GROUPS = [
 {'id':'C01','name':'1943 Gougra授权及后续转给Isotherme','record_ids':['R014'],'relation_ids':['H43_grimentz','H43_ayer','H_private'],'time':'1943；转让日期未披露（在1953之前）','features':'Gougra河在原Grimentz、Ayer范围内的水体','object':'水力利用特许权','note':'两市镇、两名未具名私人及Isotherme是主体；后来的Moiry坝不是1943已存在的授权地物。','source':'Savoy PDF77–78；EV01'},
 {'id':'C02','name':'Tourtemagne历史授权','record_ids':['R014'],'relation_ids':['H_oberems','H_ergisch','H_turtmann'],'time':'Oberems 1951；Ergisch与Turtmann 1952','features':'Turtmänna河有关市镇河段','object':'水力利用特许权','note':'原授权逐段界线未提供；现有市镇边界不能回填历史界线。','source':'Savoy PDF77–78；EV01'},
 {'id':'C03','name':'Isotherme向FMG转让多项特许权','record_ids':['R014'],'relation_ids':['H53'],'time':'1953','features':'已知Gougra、Turtmänna有关水体','object':'多项历史特许权集合','note':'“diverses concessions”没有逐件清单；不能认定完整覆盖后来上段的全部水体。','source':'Savoy PDF77–78；EV01'},
 {'id':'C04','name':'Gougra上段特许权组','record_ids':['R014','R015'],'relation_ids':['U_grant','FUT_GRANT'],'time':'历史各项授权1950—1957；数据包期限口径1959—2039；2039新授待定','features':UPPER,'object':'各具名水体的水力利用权；2039以后新特许权尚待确定','note':'分立文书组成的组，不是12份已证实独立特许权。关联Moiry／Tourtemagne坝库、Mottec／Vissoie及Lona电站等设施；完整资产归属及回归范围未据此确认。Frilitälli与另一段Frilibach拼写不强制合并。','source':'Savoy PDF78–79、94；EV02、EV10–11、EV14'},
 {'id':'C05','name':'Navizence下段特许权组','record_ids':['R008'],'relation_ids':['L_grant','L2084'],'time':'2004—2084；2009-01-28核准','features':LOWER,'object':'下段水力利用权','note':'FMG是直接持有人；Navizence 470 L/s、Fang 50 L/s是剩余流量要求。','source':'Savoy PDF78、80、94、104；EV02'},
 {'id':'C06','name':'Haute-Printse／Cleuson既有授权背景','record_ids':['R025','R032','R027'],'relation_ids':[],'time':'1945；材料记相关既有水权2031到期','features':'Haute-Printse及支流Femine、Tortin Est／Sud、Tortin Ouest（后放弃）；关联Cleuson坝库','object':'水力利用权及保留灌溉用水','note':'从既有R025、R032的原文核出授权背景；Tortin Ouest已于1966放弃，不能继续列作当前可用授权。Femine为历史名称；Tortin分支确切范围不详。','source':'Savoy PDF24、45–46'},
 {'id':'C07','name':'Tortin Ouest放弃授权','record_ids':['R025'],'relation_ids':[],'time':'1966-03-23放弃','features':'Tortin Ouest水流／流域','object':'被放弃的水力开发权','note':'是C06的历史变化事件，不能重复计算为另一份当前有效concession。','source':'Savoy PDF24'},
 {'id':'C08','name':'Basse-Printse开发授权','record_ids':['R026'],'relation_ids':[],'time':'1986授权，同年底项目放弃','features':'Basse-Printse水系，含Tortin Ouest','object':'已授而未开发的水力利用权','note':'承接项目公司Nendaz-Electricité SA；不是已存在的电站，不推断法定撤销日期。','source':'Savoy PDF24'},
 {'id':'C09','name':'Hongrin-Léman跨州授权','record_ids':['R034'],'relation_ids':[],'time':'1963授权；1971-10-01起运行；至2051年9月底（材料记载）','features':'Hongrin及汇水系统、Lac de l’Hongrin、Lac Léman；关联双坝、Veytaux电站与输水／抽水设施','object':'水力利用权及Léman抽水许可','note':'汇水系统的完整八个取水口和支流范围未在本轮逐个落实；不把授权水体与工程所有权合并。','source':'Savoy PDF57–58、67'},
 {'id':'C10','name':'Hongrin造雪另行抽水授权条件','record_ids':['R039'],'relation_ids':[],'time':'2023协议；2024项目撤回','features':'Lac de l’Hongrin取水水体；Leysin、Les Mosses雪场；拟建输水管线','object':'协议生效所需的州抽水特许权／许可','note':'取得授权未获证实；不得列作既成或当前有效concession。','source':'Savoy PDF69–70'},
]

links = {
1:['N2004','N2008','Nfund'],2:['B2004','B2017','Bsettle'],3:['W_roux','DIST_roux','W_excess'],4:['W_grand_st_luc','DIST_grand_st_luc','W_excess'],
8:['L_grant'],9:['SN_zinal_lifts','PAY_zinal_lifts','SN_grimentz_lifts','PAY_grimentz_lifts','SN_rmgz'],11:['VAL22'],12:['VAL22'],13:['RETURN39'],
14:['H43_grimentz','H43_ayer','H_private','H_oberems','H_ergisch','H_turtmann','H53','U_grant'],
15:['FUT_GRANT','FUT_RESERVE','FMV_support','FMV_future'],
}
records=[]
for r in timeline:
    n=int(r['编号'][1:]); status,features,obj,note,pages=M[n]
    records.append({'id':r['编号'],'title':r['案例或主题'],'classification':status,'physical_features':features or None,
        'semantic_object':obj,'assessment_note':note,'time':r['事件或谈判时间'],'source_state':r['结果或状态（截至材料记载）'],
        'source_filename':r['来源文件'],'source_pdf_pages':r['PDF页码（从1起）'],'supplemental_savoy_pdf_pages':pages or None,
        'relation_ids':links.get(n,[]),'review_status':'待审理','review_decision':None,'review_note':None,'original_record':r})

entities={e['id']:e for e in dataset['entities']}
quantities=dataset['quantities']; evidence_by_rel={}
for x in dataset['relation_evidence']:
    evidence_by_rel.setdefault(x['relation_id'],[]).append(x['evidence_id'])

def map_relation(r):
    rid=r['id']; scope=r['scope']; pred=r['predicate']
    if rid.startswith('H43') or rid=='H_private': return 'Gougra河（历史授权段）','水力利用特许权','历史水体；不回填Moiry后建工程。'
    if rid in ['H_oberems','H_ergisch','H_turtmann']: return 'Turtmänna河（历史授权段）','水力利用特许权','逐件授权河段边界未给。'
    if rid=='H53': return '已知Gougra及Turtmänna授权水体','多项历史特许权集合','完整转让标的清单未知。'
    if rid.startswith('EQ_') or rid=='LOWER10': return None,'FMG公司股权','客体为公司股本权益；不对应可分割的特定坝、渠或土地。'
    if rid=='FMV_future': return None,'待定未来经营结构中的股权／股东身份','经营结构和持股比例未定；不能填成未来特许权持有人。'
    if rid in ['LOWER51old','LOWER51new']: return LOWER,'下段工程51%参与权益','工程为承载对象；51%不是河段面积或公司股本，时点有来源差异。'
    if rid in ['N2004','N2008','Nfund']:
        obj={'N2004':'保留灌溉供水120 L/s','N2008':'灌溉供水额度削减超过50%','Nfund':'喷灌设施一次性资助给付'}[rid]
        return M[1][1],obj,M[1][3]
    if rid in ['B2004','B2017','Bsettle']: return M[2][1],{'B2004':'原70 L/s灌溉供水','B2017':'45 L/s常态及干旱最高70 L/s供水','Bsettle':'历史权源／免费性争议和解'}[rid],M[2][3]
    if scope in ['roux','grand_st_luc']:
        m=M[3 if scope=='roux' else 4]; return m[1],m[2],m[3]
    if rid=='W_excess': return 'Bisse Roux；Grand bisse de St-Luc','超额供水费，按未生产kWh价值计算','灌渠为计费用途关联地物；直接给付是金钱。'
    if scope=='snowmaking':
        f=M[9][1]
        if 'zinal_lifts' in rid: f='Tsarmette泵站、Moiry–Mottec输水设施→Sorebois–Singlinaz雪场'
        if 'grimentz_lifts' in rid: f='Moiry坝脚管道→Bendolla雪场'
        return f,('造雪水费给付' if rid.startswith('PAY') else '造雪供水'),M[9][3]
    if scope=='upper_Gougra':
        obj={'U_grant':'上段水力利用特许权','U_fees':'年度水力费给付','VAL22':'2039补偿的未来金钱给付','RETURN39':'湿式及约定有偿部分资产回归','FUT_GRANT':'2039以后待授新特许权','FUT_RESERVE':'地方造雪／消防等预留用水设想','FMV_support':'回归准备的专业支持'}
        if rid.startswith('G_'): return UPPER,'上段已授水力份额','份额的分母为已授水力；不能以该百分比切割任一地物。'
        assert rid in obj,rid
        f=UPPER
        if rid in ['VAL22','RETURN39']: f=M[11 if rid=='VAL22' else 13][1]
        return f,obj[rid],r.get('note_zh') or '以特许权组为范围；不是逐件资产清册。'
    if scope=='lower_Navizence': return LOWER,('2084特许权到期事项' if rid=='L2084' else '下段水力利用特许权'),r.get('note_zh') or ''
    raise ValueError(rid)

relations=[]
for r in dataset['relations']:
    features,obj,note=map_relation(r)
    mapping_pages = set()
    for record in records:
        if r['id'] in record['relation_ids'] and record['supplemental_savoy_pdf_pages']:
            mapping_pages.add(record['supplemental_savoy_pdf_pages'])
    if r['scope'] in ['upper_Gougra','lower_Navizence'] or r['id'].startswith('H'):
        mapping_pages.add('77–82')
    relations.append({**r,'subject_name':entities[r['subject_id']]['name'],'relation_object_name':entities[r['object_id']]['name'],
       'physical_features':features,'semantic_object':obj,'mapping_note':note,'evidence_ids':evidence_by_rel.get(r['id'],[]),
       'supplemental_mapping_source':('Savoy PDF '+', '.join(sorted(mapping_pages))) if mapping_pages else None,
       'quantities':[q for q in quantities if q['relation_id']==r['id']], 'review_status':'待审理','review_decision':None,'review_note':None})

assert {x['id'] for x in records}=={f'R{i:03d}' for i in range(1,53)}
assert len(relations)==50 and len({x['id'] for x in relations})==50
assert {x['id'] for x in relations}=={x['id'] for x in dataset['relations']}
assert all(r['semantic_object'] for r in records+relations)
assert all(i in {r['id'] for r in relations} for ids in links.values() for i in ids)

counts=dict(Counter(r['classification'] for r in records))
payload={'prepared_on':'2026-10-04','scope':'现有52条时间线与50条关系的地物／客体审理映射；非实时特许权登记或地籍清册',
 'rules':['原关系object_id保持不变；物理地物与权利／给付客体另列。','地物未识别不等于地物不存在。','具名地物不等于已核定GIS几何。','历史、已放弃、已撤回与未来安排分别保留，不能统称当前有效。','同一权利的事件及多条关系不重复计为多份独立concession。'],
 'counts':counts,'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [timeline_path,dataset_path]},
 'concession_groups_and_events':GROUPS,'timeline_assessments':records,'relation_assessments':relations,
 'source_tables':{'sources':dataset['sources'],'evidence':dataset['evidence'],'discrepancies':dataset['discrepancies']}}
(OUT/'concession_地物与客体_审理数据.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))

def esc(s): return str(s or '—').replace('|','／').replace('\n',' ')
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(esc(x) for x in row)+' |' for row in rows])
source_short={'Savoy':'Savoy','Bagnoud':'Bagnoud','Kanton':'Valais模板','Louvin':'Louvin & Calvo','Bellwald':'Bellwald','Stevensson':'Stevensson','Flaminio':'Flaminio & Reynard','Gerber':'Gerber & Hess'}
def source(r):
    short=next((v for k,v in source_short.items() if r['source_filename'].startswith(k)),r['source_filename'])
    txt=short+' PDF '+r['source_pdf_pages']
    if r['supplemental_savoy_pdf_pages']: txt+='；补查Savoy PDF '+r['supplemental_savoy_pdf_pages']
    return txt

lines=['# Concession 对应地物与客体审理清单','',
'整理日期：2026-10-04。范围为已有52条时间线记录与50条关系记录，已逐条覆盖。“目前”指现有数据中的全部记录，不表示全部权利在今日有效。本轮使用现有结构化数据及本地原文提取，未作实时法律登记查询。','',
'原表同时收录水力特许权、谈判让步、供水协议和制度材料。以下先列严格意义的特许权及其变化事件，再列全部52条记录，以便决定保留范围。公司、市镇、协会是行为主体；原关系表的object_id常为接收方，不应改写成地物。','',
'**判读规则：**“具名地物”仅指名称和关系可核对，未必已有准确坐标或地籍边界。没有足够证据指认地物时，保留权利、份额、金钱、实物或履行义务作为客体。所有条目均为待审理，尚未回写原数据。','',
'## 一、严格特许权及历史／未来变化','',
'以下10行是审理分组和变化事件，不是10份独立有效concession。Gougra／Navizence各为文书组；C07是C06的历史放弃事件，C10仅为未证实获批的授权条件。','',
table(['编号／事项','时间','实际地物／承载范围','权利客体及边界','原记录／证据'],[(g['id']+' '+g['name'],g['time'],g['features'],g['object']+'。'+g['note'],', '.join(g['record_ids']+g['relation_ids'])+'；'+g['source']) for g in GROUPS]),'',
'**Gougra上段水体逐名核对：** '+ '；'.join(UPPER_WATER)+'。上述12个名称／范围来自Savoy PDF78的上段范围列举，不能据名称个数推算法律文书数量。','',
'## 二、全部时间线记录：地物或替代客体','',
'分类计数：'+ '；'.join(f'{k} {v}条' for k,v in counts.items())+'。同一条可含多个地物以及非地物给付，计数只表示该条能否落实具名地物。','']

for title,subset in [('Anniviers／Gougra（R001—R022）',records[:22]),('Cleuson／Printse（R023—R033）',records[22:33]),('Hongrin（R034—R041）',records[33:41]),('模板、制度及其他案例（R042—R052）',records[41:])]:
    lines += ['### '+title,'',table(['原编号／事项','地物判定及实际地物','权利／给付客体','审理注意事项','来源'],[(r['id']+' '+r['title'],r['classification']+'：'+(r['physical_features'] or '无可确定的个案地物'),r['semantic_object'],r['assessment_note'],source(r)) for r in subset]),'']

lines += ['## 三、优先待审项目','',
'1. **R023 Bornet权利：** 原权利内容未分解，暂以既有／剩余权利与电力给付为客体，待合同或权利清单。',
'2. **R028保护补偿：** 具体补偿地块、河段未识别，暂以撤诉与保护补偿义务为客体。',
'3. **R005、R017、R018、R035：** 有实物或设施线索，但未落实独立地物名称／位置。尤其R035不能直接认定就是L’Etivaz锯木厂。',
'4. **R036：** 客体为鱼类或等值现金，属于实物／金钱给付，不是固定地物。',
'5. **R042—R048、R050—R052：** 模板、制度或理论材料缺少个案地物，建议由你决定是否留在concession个案表之外。',
'6. **EQ_*、LOWER10、FMV_future：** 对应公司股权或未来股东角色；LOWER51*对应工程参与权益。不能将百分比解释为某一坝、河段或地块的比例。',
'7. **历史与项目状态：** R010皮划艇活动于2023年底停止；R025授权于1966放弃；R026项目1986放弃；R039项目2024撤回；未来新授及预留水量仍待定。',
'8. **资产回归与金额：** 原资产清册缺失；保留1500万新闻口径与1505万官方2022口径及年度更新差异。不得将补偿数值当成地物，或把上段所有设施直接认定全部回归。','',
'## 四、50条关系的客体校正对照','',
'此处“原箭头终点”保留原关系语义。“实际地物”可能是权利的承载物、供水设施或给付关联地点，并不意味着该地物所有权被转移。证据编号可在原数据包evidence表或随附JSON中查回来源。','',
table(['关系ID','原箭头（主体 → 接收方／原客体）','实际地物／关联范围','本条权利或给付客体','依据／限制'],[(r['id'],r['subject_name']+' → '+r['relation_object_name'],r['physical_features'] or '无独立地物；以右列权益／角色为客体',r['semantic_object'],', '.join(r['evidence_ids'])+'；'+(r['supplemental_mapping_source'] or '')+'；'+r['mapping_note']) for r in relations]),'',
'## 五、审理填写与来源','',
'随附JSON保留原时间、状态、记录全文、关系主体与终点、数量和证据外键，并为每条设置review_status、review_decision、review_note。可按“确认／修改／排除／补证”记录决定；当前全部为“待审理”。','',
'原始输入：','',f'- [52条时间线](<{timeline_path}>)',f'- [50条关系主数据](<{dataset_path}>)',f'- [本次可回写审理数据](<{OUT / "concession_地物与客体_审理数据.json"}>)','',
'出处均采用PDF阅读器页序（从1起），不是印刷页码。补查细节来自已有Savoy原文提取。外部网页来源只沿用原包保存的证据，不表示本轮重新访问验证。','']
for fn in sorted({r['source_filename'] for r in records}):
    matches = list((ROOT / '01_sources').rglob(fn))
    target = matches[0] if matches else (ROOT / '01_sources' / fn)
    lines.append(f'- [{fn}](<{target}>)')
(OUT/'concession_地物与客体_审理清单.md').write_text('\n'.join(lines))
print(json.dumps({'timeline_count':len(records),'relation_count':len(relations),'classification_counts':counts,'outputs':[str(p) for p in OUT.iterdir()]},ensure_ascii=False,indent=2))
