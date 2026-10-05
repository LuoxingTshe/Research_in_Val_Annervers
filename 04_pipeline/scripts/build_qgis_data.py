import sys,json,sqlite3,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'04_pipeline/vendor/qgis_geo_libs'))
from pyproj import Transformer
from shapely import from_wkb,force_2d,force_3d,to_geojson
from shapely.ops import transform
from shapely.geometry import MultiLineString,mapping

OUT=ROOT/'02_outputs/qgis_wgs84_package'
OUT.mkdir(parents=True,exist_ok=True)
GEO=ROOT/'03_reference_data/geodata_resources'
review=json.loads((ROOT/'02_outputs/concession_review/concession_地物与客体_审理数据.json').read_text())
R={r['id']:r for r in review['timeline_assessments']}
REL={r['id']:r for r in review['relation_assessments']}
gn=sqlite3.connect('file:'+str(GEO/'data/swissnames3d_2026.sqlite')+'?mode=ro',uri=True);gn.row_factory=sqlite3.Row
gp=sqlite3.connect('file:'+str(GEO/'data/swissnames3d_2026_2056.gpkg')+'?mode=ro',uri=True);gp.row_factory=sqlite3.Row
tr=Transformer.from_crs(2056,4326,always_xy=True)
OFFICIAL='https://data.geo.admin.ch/ch.swisstopo.swissnames3d/swissnames3d_2026/swissnames3d_2026_2056.gpkg'
objs={};geoms={};events=[]

def obj(id,name,typ,group,note='',names=None,source='',geoid='',xy=None,status=None):
    assert id not in objs
    objs[id]={'Object_ID':id,'Name':name,'Type':typ,'Table':group,'Object_Note':note,'Official_Name':'; '.join(names or []),
        'Geo_Source':source,'Geo_ID':geoid,'X':xy[0] if xy else None,'Y':xy[1] if xy else None,'Z':0 if xy else None,
        'Geometry_Status':status or ('已核对官方设施点' if xy else '无唯一点位'),'Geometry_Scope':'工程设施定位点' if xy else '',
        'Geometry_File':'points_wgs84.geojson' if xy else None}
    return objs[id]

def bfe(id,query,official,name,typ='水电站',kind='power',note=''):
    p=json.loads((GEO/f'queries/{kind}_{query}.json').read_text())
    key='name' if kind=='power' else 'damname'
    matches=[x for x in p['response']['results'] if x['properties'][key]==official]
    assert len(matches)==1,(query,official)
    f=matches[0]; geom=f['geometry']; xy=geom['coordinates']
    if geom['type']=='MultiPoint':
        assert len(xy)==1;xy=xy[0]
    else: assert geom['type']=='Point'
    o=obj(id,name,typ,'points',note,[official],p['url'],str(f['featureId']),xy)
    o['Geo_Layer']=f['layerBodId']

bfe('P01','mottec','Mottec','Centrale de Mottec')
bfe('P02','vissoie','Vissoie','Centrale de Vissoie',note='主电站；未用同名村庄或辅助机组点。')
bfe('P03','lona','Lona','Centrale de Lona',note='设施投运与特许权期限起点不同；不把整体历史授权回填为本设施已建。')
bfe('P04','navizence','Navizence','Centrale de Navizence')
bfe('P05','moiry','Moiry','Barrage de Moiry','坝体','dam','采用官方坝体点；不代表整个水库。')
bfe('P06','turtmann','Turtmann','Barrage de Tourtemagne / Turtmann','坝体','dam','Tourtemagne为文献法文名称；官方设施名Turtmann，与流域和工程一致。')
bfe('P07','cleuson','Cleuson','Barrage de Cleuson','坝体','dam')
bfe('P08','hongrin','Hongrin Nord','Barrage de l’Hongrin Nord','坝体','dam')
bfe('P09','hongrin','Hongrin Sud','Barrage de l’Hongrin Sud','坝体','dam')
bfe('P10','bieudron','Bieudron','Centrale de Bieudron')

def decode(blob):
    assert blob[:2]==b'GP'
    code=(blob[3]>>1)&7
    return from_wkb(blob[8+{0:0,1:32,2:48,3:48,4:64}[code]:])

# Actual named building point, transformed from the original point geometry.
rr=gp.execute("SELECT * FROM swissnames3d_pkt WHERE name=?",('Restaurant Lac de Moiry',)).fetchall()
rr=[r for r in rr if decode(r['geom']).x>2600000]
assert len(rr)==1
p=transform(tr.transform,force_2d(decode(rr[0]['geom'])))
obj('P11','Restaurant Lac de Moiry','房屋','points','建筑只是转租链关联对象；土地租赁标的另列。',['Restaurant Lac de Moiry'],OFFICIAL,rr[0]['uuid'],[round(p.x,7),round(p.y,7)],'已核对官方建筑点')

def line(id,name,names=None,note='',candidate=False,types=('Fliessgewaesser',)):
    o=obj(id,name,'河流／灌渠' if types==('Fliessgewaesser',) else '线性设施','lines',note,names,status='线形未核定')
    if not names:return
    parts=[];ids=[]
    for n in names:
        for r in gp.execute('SELECT * FROM swissnames3d_lin WHERE name=?',(n,)):
            if r['objektart'] not in types:continue
            g=decode(r['geom'])
            if not (2530000 < g.centroid.x < 2650000 and 1080000 < g.centroid.y < 1170000):continue
            if r['uuid'] in ids:continue
            ids.append(r['uuid']);parts.append(force_3d(transform(tr.transform,force_2d(g)),z=0))
    if not parts:
        o['Geometry_Status']='具名地物未找到匹配线形';return
    geom=MultiLineString(parts)
    assert geom.is_valid and not geom.is_empty
    geoms[id]=geom
    o.update({'Geo_Source':OFFICIAL,'Geo_ID':';'.join(ids),'Geometry_File':'lines_wgs84.geojson',
        'Geometry_Status':'候选名称线形，需审理同一性' if candidate else '已核对具名地物参考线形',
        'Geometry_Scope':'官方现状名称对应线形；未按特许权或历史年代裁切'})

line('L01','La Gougra',['La Gougra'])
line('L02','Navizence / La Navisence',['La Navisence'],'同一河流的上段与下段事件分别标注；几何不替代特许段界线。')
line('L03','Turtmänna',['Turtmänna'],'各市镇历史授权段界线未核定。')
line('L04','Rhône：Turtmann–Chippis引水相关河段',note='全河线形不能代替授权引水段；须明确起止断面后裁切。')
line('L05','Brändjibach',['Brändjibach'])
line('L06','Nebenbach',note='文献范围已列名，未找到可确认的同名线形。')
line('L07','Torrent des Mayens',note='文献与Lona名称关系有待核对，不能匹配异地Ruisseau des Mayens。')
line('L08','Torrent des Moulins',['Torrent des Moulins'])
line('L09','Torrent de Barneusaz',['Torrent de Barneuza'],'文献Barneusaz与地图Barneuza为同流域候选拼写，尚待你确认。',True)
line('L10','Torrent de Nava',['Torrent de Nava'])
line('L11','Torrent du Frilitälli / Frilibach',note='地图上的Frilitälli是山谷；未用山谷点代替溪流。')
line('L12','Torrent de Fang',['Torrent de Fang'])
line('L13','Bisse de Niouc',['Bisse de Niouc'])
line('L14','Bisse de Briey',['Bisse de Briey'])
line('L15','Bisse Roux',['Bisse de Lâcher-Roux'],'Bisses du Valais的Roux条目明确列别名Bisse de Lâcher-Roux。')
line('L16','Grand bisse de St-Luc',['Grand Bisse de Saint-Luc'])
line('L17','Bisse de Ricard',['Bisse de Ricard'],'未混入以道路记录的Ancien Bisse de Ricard。')
line('L18','Bisse de Granges',note='材料确认供水与维护安排；官方名称库未找到同名灌渠。')
line('L19','Ancien bisse des Sarrasins',note='旧渠为Briey争议背景；现存渠线未确认。')
line('L20','Galerie Vissoie–Niouc',note='现有引水隧洞与拟建压力隧洞需工程图分离，不能以两端直线代替。')
line('L21','Galerie sous pression Vissoie–Niouc（拟议）',note='拟建工程的批准设计线未取得；不与既有隧洞合并。')
line('L22','Moiry–Mottec压力输水设施',note='输水廊道和地下段精确线形尚缺工程图。')
line('L23','Moiry坝脚至Bendolla造雪管道',note='供水关系确定，管线走向未核定。')
line('L24','Nava供水管道及接入支线',note='私人取水和Grand-Praz接水对应不同支线，须核对工程图。')
line('L25','Via ferrata de Moiry',['Via ferrata de Moiry'],'官方记录为道路类线段；仅路线参考，不代表免费使用土地宗地。',types=('Strasse',))
line('L26','Bisse de Saxon',['Grand Bisse de Saxon'],'按灌渠线形提取，未混入旧渠旅游道路。')
line('L27','La Printse',['La Printse'],'包括上游与下游命名线段；授权／治理段未裁切。')
line('L28','Tortin Ouest',note='原文已注明两支Tortin的准确范围未明；历史权利不硬配现代支流。')
line('L29','Cleuson-Dixence地下引水隧洞',note='地下工程线形未取得。')
line('L30','Tracouet–Bieudron压力竖井',note='不能用Tracouet地点到Bieudron电站的直线代替竖井。')
line('L31','Bouillets–SEBA供水连接管线',note='源头和接入端点尚未核定。')
line('L32','Cleuson–Pra Mounet供水管道',note='材料有设施链，未取得全线工程坐标。')
line('L33','La Dixence',['La Dixence'])
line('L34','L’Hongrin',["L'Hongrin"],'生态放水事件对应坝下段；参考几何含该名称下全部已提取河段。')
line('L35','Le Petit Hongrin',['Le Petit Hongrin'])
line('L36','Hongrin–Veytaux引水及抽水管线',note='地下引水线与压力井需工程资料。')
line('L37','Hongrin–Leysin／Les Mosses拟议造雪管线',note='项目曾撤回；没有已建成管线可定位。')
line('L38','Äbibärgeri',['Äbibergeri'],'原文历史拼写与官方现名的对应仍列为候选；不把同音视为已审定。',True)
line('L39','Niouc悬索桥上的Briey输水管','' or None,'桥上输水管是线性构件；桥的位置不能代替整条管线。')

# Areas and networks have no unique XY; official label points are deliberately not used.
areas=[
('A01','Lac de Moiry','水库水面','湖面准入／蓄水用途；不能与Moiry坝体点互换。'),
('A02','Lac de Lona','湖泊','上段授权水体，面积对象无唯一点位。'),
('A03','Retenue de Tourtemagne / Turtmannsee','水库','与坝体分开。'),
('A04','Plats de la Lée / Les Plats de la Lé','生态修复区','修复地块边界需项目图；未用同名公交站点。'),
('A05','Niouc喷灌网络','灌溉网络','分散设施集合，不能以灌渠定位点代替。'),
('A06','Ayer／Anniviers旧灌渠与替代喷灌体系','灌溉网络','记录未逐一列出全部渠、支管与地块。'),
('A07','Sorebois–Singlinaz造雪受益区','雪场','供水用途范围；非单一点。'),
('A08','Bendolla造雪受益区','雪场','供水用途范围；非单一点。'),
('A09','Alpage de Moiry湖左岸租赁土地','牧场宗地集合','市镇→Moiry牧场；宗地号未列。'),
('A10','Alpage de Château-Pré湖右岸租赁土地','牧场宗地集合','FMG→餐厅→Château-Pré牧场；不以餐厅房屋坐标替代土地。'),
('A11','Moiry Via Ferrata使用土地','土地使用范围','攀登路线另列；合同涉及的地籍范围未核定。'),
('A12','Lac de Cleuson','水库水面／库容','库容、储水与购水用途无唯一点位。'),
('A13','Nendaz–Veysonnaz造雪系统','供水及用水网络','付款链明确；分布式用水系统不是一座建筑。'),
('A14','Lac de l’Hongrin','水库水面','与Hongrin两座坝体分别记录。'),
('A15','Lac Léman','湖泊','抽水水源为湖水，具体抽水口另列。'),
('A16','Leysin造雪受益区','雪场','关联拟议造雪供水项目。'),
('A17','Les Mosses造雪受益区','雪场','关联拟议造雪供水项目。'),
('A18','Hongrin应急供水受益高山牧场','未具名牧场集合','受益地分散且未具名。'),
('A19','Sarine流域','流域','物种传播风险的受影响范围，不是固定取水点。'),
('A20','Gougra上段涉水资产集合','工程资产集合','完整回归资产清册未取得。'),
('A21','Gougra上段干式设施集合','工程资产集合','补偿对应资产集合，不能只取某座电站坐标。'),
('A22','Navizence下段工程集合','工程资产集合','工程参与权益不等于特定建筑物产权。'),
('A23','Mauvoisin替代供水设施集合','供水设施集合','Saxon供水替代路径未具体化到某一电站或取水口。'),
('A24','SEBA原有水源集合','水源集合','原文没有逐一具名。'),
('A25','Cleuson-Dixence保护补偿地点','未确定补偿地物','补偿地点尚未列明；不能用Bieudron替代补偿地块。'),
('A26','Mottec调节池','水体','与同名电站分开。'),
('A27','Vissoie调节池','水体','与电站和坝体分开，面积对象。'),
('A28','Grand-Praz废弃物处理站用地','设施用地区域','州文件给出用地约略位置；没有把用地中心当作供水接入口。'),
]
for id,n,t,note in areas:obj(id,n,t,'nonunique',note,status='面域／集合无唯一XY')
unknown=[
('U01','Vissoie–Niouc隧洞18号取水窗口','取水口','未取得窗口本体坐标；不以Niouc村或灌渠点代替。'),
('U02','Vuibiesse取水设施','取水口','Narèt de Vuibiesse泉与瀑布名称不能证明同一设施。'),
('U03','Tsarmette造雪泵站','泵站','同名地名散布不同市镇；未找到可确认的泵站设施点。'),
('U04','Tsarmette调压井','调压井','与泵站关联但不预设两者坐标完全相同。'),
('U05','Nava取水设施','取水口','已找到Torrent de Nava；取水设施本体坐标未核定。'),
('U06','Chippis饮用水取水口（Navizence电站下游）','取水口','下游取水口不能用电站点代替。'),
('U07','Zinal两座公共喷泉','未具名点对象集合','数量为两座；分别名称和位置未知，不能制造两组坐标。'),
('U08','受损私人水源及替代接水点','泉源／接水点','原文只记供水受损，未具名；两处位置均待核。'),
('U09','Source des Bouillets取水设施','泉源／取水设施','原文确认水源，未取得可确认的设施点。'),
('U10','Hongrin能源补偿的锯木厂','房屋／工业设施','工厂未具名；不能直接认定就是L’Etivaz锯木厂。'),
('U11','Grand-Praz废弃物站供水接入点','供水接入点','州文件只有废弃物站用地约略位置，不是供水接入点。'),
('U12','Veytaux II地下电站','地下电站','官方水电统计给出Veytaux合并设施点，未据此拆成I、II两个精确点。'),
('U13','Veytaux I地下电站','地下电站','合并设施点不证明单个地下厂房位置。'),
('U14','Veytaux的Léman抽水口','取水口','湖泊和合并电站点均不能代替抽水口。'),
('U15','Bisse de Ricard取水口','取水口','约略高程及峡谷位置不足以确认设施坐标。'),
('U16','Bisse de Granges取水口','取水口','材料只指Chippis平原供水段。'),
('U17','Moiry湖皮划艇告示牌','未具名点对象集合','告示牌数量与逐牌坐标未列。'),
]
for id,n,t,note in unknown:obj(id,n,t,'nonunique',note,status='实物存在或被记载，坐标尚未核定')

rights=[
('N01','Niouc喷灌设施定额资助','金钱给付'),('N02','Briey历史水权及免费性争议和解','权利／程序义务'),
('N03','Roux／St-Luc超额供水费','金钱给付'),('N04','Zinal造雪供水费','金钱给付'),('N05','Grimentz造雪供水费','金钱给付'),
('N06','Gougra上段回归补偿款','金钱给付'),('N07','Gougra现代化残值补偿','金钱给付'),('N08','ACC-FMG39协调安排','组织／协调关系'),
('N09','未来上段新concession','待授权利'),('N10','未来地方造雪／消防保留水量','拟议用水权'),
('N11','Bornet既有及剩余权利','未细分权利'),('N12','Bornet权利转让对价电力','电力给付'),
('N13','EOS对FMM的Saxon替代供水补偿','给付义务'),('N14','Cleuson-Dixence撤诉与保护补偿义务','程序／补偿义务'),
('N15','Bouillets水源接管及连接费用偿还','金钱给付'),('N16','Nendaz购水及公共费用安排','金钱／税费义务'),
('N17','NVRM经市镇支付的造雪水费','金钱给付'),('N18','Hongrin锯木厂补偿能源','电力给付'),
('N19','Hongrin年度鱼类配额或等值现金','可移动实物／金钱给付'),('N20','未来FMV股权／股东身份','未定股权'),
('N21','FMV回归准备专业支持','服务／支持关系'),('N22','Gougra年度水力费','金钱给付'),
('N23','下段工程51%参与权益','工程参与权益'),('N24','下段公共方取得FMG公司10%股权','公司股权'),
]
for id,n,t in rights:obj(id,n,t,'nonunique','客体是权益或给付，不把付款方／受款方办公地点当作其坐标。',status='非地物客体')
for n in range(42,49):obj(f'N{n}',R[f'R{n:03d}']['semantic_object'],'模板／制度客体','nonunique',R[f'R{n:03d}']['assessment_note'],status='无具体地物实例')
for n in [50,51,52]:obj(f'N{n}',R[f'R{n:03d}']['semantic_object'],'制度／理论客体','nonunique',R[f'R{n:03d}']['assessment_note'],status='无具体地物实例')

def event(ids,record,year,title,status='documented',rels=(),scope='',date=None,precision=None,lo=None,hi=None,source_year=None,note='',extra_source=''):
    if isinstance(ids,str):ids=ids.split()
    if isinstance(rels,str):rels=rels.split()
    assert all(i in objs for i in ids)
    assert year is None or type(year)==int
    assert all(x in REL for x in rels)
    rid=f'R{record:03d}' if isinstance(record,int) else record
    if rid:
        r=R[rid]; right_source=r['source_filename']+' PDF '+r['source_pdf_pages']
        if source_year is None:
            source_year=2022 if r['source_filename'].startswith('Bagnoud') else 2025 if r['source_filename'].startswith('Savoy') else None
    else:right_source='；'.join(sorted(set(e for x in rels for e in REL[x]['evidence_ids'])))
    if extra_source:right_source+='；'+extra_source
    # Source date is not silently promoted to the year of the right change.
    events.append({'ids':ids,'Record_ID':rid or '', 'Value':year,'Event':title,'Event_Status':status,'Relation_ID':';'.join(rels),
        'Right_Scope':scope,'Event_Date':date,'Year_Status':precision or ('year' if year is not None else 'unknown'),
        'Year_Min':lo,'Year_Max':hi,'Source_Year':source_year,'Right_Source':right_source,'Event_Note':note})

event('L13 U01',1,2004,'Niouc灌溉保留配额纳入下段授权',rels='N2004')
event('L13 U01',1,2009,'下段授权的州核准',date='2009-01-28',precision='day',note='核准与授权起点分开。')
event('L13 A05 N01',1,2008,'减量换喷灌设施资助协议',rels='N2008 Nfund',date='2008-03-18',precision='day')
for year,title in [(1912,'公证灌溉取水安排'),(1979,'灌溉权流量及季节修改'),(2004,'原灌溉额度纳入下段授权')]:event('L14 U01',2,year,title,rels='B2004' if year==2004 else ())
event('L14 L19 L39 U01 N02',2,2017,'灌溉权争议和解并重定供水额度',rels='B2017 Bsettle',date='2017-06-13',precision='day',note='旧Sarrasins渠仅为争议关联对象。',extra_source='Savoy PDF81')
event('L15 L08 U02 N03',3,2018,'Roux免费供水额度及超额付费协议',rels='W_roux DIST_roux W_excess',extra_source='Savoy PDF81–82；https://bisses-valais.ch/bisses/bisse-de-lacher-roux/')
event('L16 L08 U02 N03',4,2018,'St-Luc免费供水额度及超额付费协议',rels='W_grand_st_luc DIST_grand_st_luc W_excess',extra_source='Savoy PDF81–82')
event('A06',5,None,'旧渠维护及供水改为管道接入／喷灌安排',precision='approximate',lo=2000,note='仅知年代和相对时间，不据此填写某个确定变更年。')
event('L20 L21 A04',6,2016,'工程不反对与生态修复出资安排载入州决定',date='2016-10-19',precision='day')
event('L01 L02 L03',7,2016,'跨流域生态治理和剩余流量折衷',date='2016-10-19',precision='day',scope='上段整体治理；河段未裁切')
for year,title,status,rels in [(2004,'Navizence下段授权续期','documented','L_grant'),(2009,'Navizence下段授权州核准','documented',''),(2084,'Navizence下段授权届满','future','L2084')]:
    event('L02 L12 L20 P04 A22',8,year,title,status,rels,scope='Vissoie电站出水口至Rhône回水口，含Fang',date='2009-01-28' if year==2009 else None,precision='day' if year==2009 else None)
event('U03 U04 L22 A07 N04',9,2006,'Zinal造雪有偿供水协议',rels='SN_zinal_lifts PAY_zinal_lifts')
event('L23 A08 N05',9,2007,'Grimentz造雪有偿供水协议',rels='SN_grimentz_lifts PAY_grimentz_lifts')
event('A07 A08',9,None,'合并公司RMGZ供水现状',rels='SN_rmgz',precision='observation_not_change',note='公司合并时间及供水权变更时间未核实。')
event('A01',10,2021,'市镇同意湖面皮划艇活动',precision='month_range',note='材料仅列夏季两个月，未补造具体日期。')
event('A01 U17',10,2022,'皮划艇活动规则与安全责任安排',date='2022-06-24',precision='day')
event('A01',10,2023,'皮划艇经营活动停止',status='ceased',note='停止的是该活动；不推定整个湖面的法律禁令改变。')
event('A21 N06',11,2022,'上段回归补偿协议获批准',rels='VAL22',note='金额采用原关系包并列口径；本表不重新估值。')
event('A21 N06',11,2039,'上段回归补偿约定支付时点',status='future_obligation',rels='VAL22')
event('P01 P02 N07',12,2022,'现代化增值／残值补偿纳入约定',rels='VAL22')
event('P01 P02 N07',12,2039,'现代化补偿约定结算时点',status='future_obligation',rels='VAL22')
event('P05 P06 A01 A03 A20 L22',13,2039,'上段涉水资产回归安排',status='future',rels='RETURN39',note='工程关联；最终移交边界以资产清册为准。')
event('L01',14,1943,'Grimentz与Ayer分别授予私人水力权',rels='H43_grimentz H43_ayer',scope='两历史市镇各自范围')
event('L01',14,None,'私人向Isotherme转让',rels='H_private',precision='bounded_unknown',lo=1943,hi=1953,note='只保存事件前后界限，不把端点当成转让年份。')
event('L03',14,1951,'Oberems向Isotherme授予水力权',rels='H_oberems',scope='Oberems历史授权段')
event('L03',14,1952,'Ergisch向Isotherme授予水力权',rels='H_ergisch',scope='Ergisch历史授权段')
event('L03',14,1952,'Turtmann向Isotherme授予水力权',rels='H_turtmann',scope='Turtmann历史授权段')
event('L01 L03',14,1953,'Isotherme向FMG转让已汇集的特许权',rels='H53',note='完整转让清单未披露，仅映射已知水体。')
upper='L01 L02 L03 L04 L05 L06 L07 L08 L09 L10 L11 A02'
event(upper,14,None,'上段各项分立授权文书',precision='interval_unknown',lo=1950,hi=1957,note='未将区间内各年生成为独立事件。',scope='上段授权组')
event(upper+' P01 P02 P05 P06 A01 A03',14,1959,'上段特许权期限起点',rels='U_grant',scope='上段授权组')
event(upper+' P01 P02 P03 P05 P06 A01 A03',14,2039,'上段特许权期限届满',status='future',rels='U_grant',scope='上段授权组')
event('N08',15,2021,'ACC-FMG39成立并协调续权准备',note='组织安排，不是新特许权授予。')
event('N09',15,2039,'新上段concession待决定',status='undetermined',rels='FUT_GRANT',note='接收方、期限、额度均未确定。')
event('N10',15,2039,'地方造雪／消防等预留用水设想',status='proposal',rels='FUT_RESERVE')
event('P05',16,2021,'Moiry加高列入圆桌优先项目',status='proposal',note='既有坝体定位；加高尚不视为已建。')
event('P05 N07',16,None,'拟议加高投资补偿待谈',status='proposal',precision='unknown',note='不把报道日期当成签约年份。')
event('U07',17,1959,'安装喷泉并移交团体的协议')
event('U08',18,1968,'水源受损后的替代供水协议')
event('L17 U15',19,2003,'Ricard设施产权与流量协议')
event('L18 U16',19,1902,'Granges初始设施协议')
event('L18 U16',19,2004,'Granges设施产权与维护新协议')
event('L25 A11',20,None,'Via Ferrata免费使用土地及责任协议',precision='interval_unknown',lo=2005,hi=2006,note='来源以期间列出多份协议，未确定每份具体签约年。')
event('U06',21,2014,'Chippis饮用水取水协议')
event('U05 L24',21,2017,'Nava私人非饮用水接管协议')
event('U05 L24 U11 A28',21,2018,'Grand-Praz废弃物站供水接入协议')
event('A09 A10 P11',22,None,'牧场租赁及右岸餐厅转租链',note='餐厅仅为转租链关联建筑，土地标的另列。')
event('N11 N12',23,1951,'Bornet权利转让并换取电力给付')
event('N11',23,1971,'后继权利人向EOS转让剩余权利')
event('L26 A23',24,1963,'Saxon与EOS供水协议',date='1963-09',precision='month')
event('L26 A23 N13',24,1963,'EOS与FMM替代供水及补偿协议',date='1963-10',precision='month')
event('L28',25,1966,'EOS放弃Tortin Ouest水力开发',status='renounced',date='1966-03-23',precision='day')
event('L27 L28',26,1986,'Basse-Printse开发授权获授',scope='下部水系含Tortin Ouest')
event('L27 L28',26,1986,'Basse-Printse项目放弃',status='abandoned',scope='下部水系含Tortin Ouest',note='不推定法定撤销日。')
for yr,title,status in [(1987,'Cleuson-Dixence项目协议','documented'),(1989,'Cleuson-Dixence议定安排','documented'),(2021,'追加折旧协议（表格年份口径）','source_conflict'),(2022,'追加折旧协议（正文年份口径）','source_conflict'),(2045,'表格记载的折旧期末','future')]:
    event('P10 L29 L30',27,yr,title,status,note='两处追加协议年份互有差异；保留而不视为已证实两份不同追加合同。' if yr in [2021,2022] else '工程关联位置；早期协议时设施可能尚未建成。')
event('A25 N14',28,1992,'WWF撤诉及保护补偿三方协议')
event('U09 A24 L31',29,1989,'州决定要求保障并接通Bouillets水源',date='1989-12-20',precision='day')
event('U09 A24 L31 N15',29,1990,'水源保障及条件出售／费用偿还三方协议',date='1990-05-18',precision='day',note='实际出售完成日期未据此推定。')
event('U09',29,2031,'受访者所述水源使用权终期',status='future_reported',note='期限来源为访谈，待核合同。')
event('A12 L32 N16',30,2000,'市镇储水、备用购水及费用协议',date='2000-09-08',precision='day')
event('A12 L32 N16',30,2013,'供水协议续期')
event('A12 L32 A13 N17',31,2000,'市镇工业用水／造雪供水框架协议',note='框架日期不能代替市镇与NVRM之间安排的具体日期。')
event('A13 N17',31,None,'NVRM经市镇付款的具体安排',note='是否书面合同在访谈中有分歧。')
event('L27',32,1945,'Haute-Printse授权保留充足灌溉供水',extra_source='Savoy PDF24、36')
event('L27',32,2031,'相关既有Printse授权终期',status='future',extra_source='Savoy PDF24、41')
event('P07 L27',32,None,'按需请求增加灌溉下泄',note='访谈年份仅为观测日期；没有固定的逐次权利变更年份。')
event('L33',33,2016,'决定实施Dixence人工洪水')
event('L33',33,2018,'试验洪水取消并调整治理安排',status='cancelled')
event('L27 L33',33,2023,'Printse替代修复方案提交',status='proposal',date='2023-03',precision='month')
hongrin='L34 L35 L36 A14 A15 U13 U14'
event(hongrin,34,1963,'跨州水力及Léman抽水授权',note='现状设施坐标不表示授权时设施已建。')
event(hongrin+' P08 P09',34,1971,'资料记载的运行起算／授权期限起点',date='1971-10-01',precision='day',extra_source='Savoy PDF58',note='仅采用研究对特许期限起算的口径，不替换设备投运统计。')
event(hongrin+' P08 P09',34,2051,'资料记载的授权终期',status='future',date='2051-09',precision='month',extra_source='Savoy PDF58')
event('U10 N18',35,1961,'锯木厂能源补偿合同')
event('N19',36,1963,'授权中规定年度鱼类增殖补偿')
event('N19',36,1981,'鱼类实物配额或等值现金协议')
event('U12',37,2011,'Hongrin-Léman Plus新增设施折旧协议',note='涉及拟增建设施；不表示当年已经投运。')
event('A14 L34',38,2022,'生态放水延期并承诺后续补放',status='documented')
event('A14 L34',38,2023,'前期延期水量的约定补放时点',status='scheduled_performance',note='只确认约定，不确认实际已履行。')
event('A14 A16 A17 L37',39,2023,'造雪取水／报酬／返水附条件协议',status='conditional',note='生效以另获州抽水授权为条件，获批未证实。')
event('A14 A16 A17 L37',39,2024,'造雪项目撤回',status='withdrawn')
event('A14 A18',40,2018,'干旱期间直升机应急免费取水')
event('A14 A15 A19 L34',41,2024,'防止外来物种传播而取消年度洪水',status='cancelled')
for n in range(42,49):event([f'N{n}'],n,None,'通用条款／制度说明，无已识别个案变更年',precision='not_applicable',source_year=2025 if n<48 else None)
event('L38',49,1922,'回忆所述市镇收购灌渠',status='historical_recollection',precision='reported_year')
for n,sy in [(50,1946),(51,2023),(52,2017)]:event([f'N{n}'],n,None,'制度／理论记录，未识别个案权利变更',precision='not_applicable',source_year=sy)

# Relations without a unique timeline transaction remain explicitly represented.
for rid,r in REL.items():
    if rid.startswith('G_'):
        oid='G_'+rid[2:];obj(oid,r['subject_name']+'的上段已授水力份额','水力授予份额','nonunique','份额不对应可唯一分割的河段或土地。',status='非地物客体')
        event([oid],None,None,'公共授予份额观测，变更年未披露',rels=[rid],precision='observation_not_change',source_year=2022)
    if rid.startswith('EQ_'):
        oid=rid;obj(oid,r['subject_name']+'持有的FMG股权','公司股权','nonunique','不以公司总部坐标代替股权客体。',status='非地物客体')
        event([oid],None,None,'公司股权比例观测，取得／变更年未披露',rels=[rid],precision='observation_not_change',source_year=2025)
event('N22',None,None,'上段年度水力费义务',rels='U_fees',note='具体设立或变更年未披露。')
event('N21',None,None,'FMV提供回归准备专业支持的记载',rels='FMV_support',precision='observation_not_change',source_year=2026)
event('N20',None,None,'FMV被描述为未来股东',status='future',rels='FMV_future',precision='unknown',source_year=2026)
event('N23 A22',None,2004,'研究报告所述下段51%参与时点',status='source_conflict',rels='LOWER51old',source_year=2025)
event('N23 A22',None,2039,'官方访谈所述下段51%参与时点',status='future',rels='LOWER51new',source_year=2026)
event('N24',None,2004,'研究报告所述公共方取得FMG公司股权',rels='LOWER10',source_year=2025)

# Add documented associated engineering objects without inventing their change dates.
event('A26 A27',14,2039,'上段工程期限终点关联的调节设施',status='future',note='关联设施，不替代逐项资产回归清册。',extra_source='Savoy PDF78')

used={i for e in events for i in e['ids']}
assert used==set(objs),('Uncovered objects',set(objs)-used)
assert {e['Record_ID'] for e in events if e['Record_ID']}==set(R)
assert {i for e in events for i in e['Relation_ID'].split(';') if i}==set(REL)

tables={'points':[],'lines':[],'nonunique':[]}
for ei,e in enumerate(events,1):
    for oid in e['ids']:
        o=objs[oid];group=o['Table']
        row={'Row_ID':f'{oid}_E{ei:03d}','Object_ID':oid,'Name':o['Name'],'Type':o['Type'],'Value':e['Value'],
            'X':round(o['X'],7) if o['X'] is not None else None,'Y':round(o['Y'],7) if o['Y'] is not None else None,'Z':o['Z'],
            'CRS':'EPSG:4326','Event':e['Event'],'Event_Status':e['Event_Status'],'Year_Status':e['Year_Status'],
            'Event_Date':e['Event_Date'],'Year_Min':e['Year_Min'],'Year_Max':e['Year_Max'],'Source_Year':e['Source_Year'],
            'Record_ID':e['Record_ID'],'Relation_ID':e['Relation_ID'],'Right_Scope':e['Right_Scope'],
            'Geometry_Status':o['Geometry_Status'],'Geometry_Scope':o['Geometry_Scope'],
            'Geometry_File':o['Geometry_File'],'Official_Name':o['Official_Name'],'Geo_ID':o['Geo_ID'],
            'Geo_Source':o['Geo_Source'],'Right_Source':e['Right_Source'],
            'Note':'；'.join(x for x in [o['Object_Note'],e['Event_Note']] if x),'Review':'待审理'}
        tables[group].append(row)
for group,rows in tables.items():rows.sort(key=lambda r:(r['Object_ID'],r['Value'] is None,r['Value'] or 0,r['Row_ID']))

# Event-level geometry layers retain one scalar Value per feature and Z=0.
for group in ['points','lines']:
    features=[]
    for row in tables[group]:
        if group=='points':geometry={'type':'Point','coordinates':[row['X'],row['Y'],0]}
        elif row['Object_ID'] in geoms:
            geometry=mapping(geoms[row['Object_ID']])
        else:continue
        props={k:v for k,v in row.items() if k not in ['X','Y','Z']}
        features.append({'type':'Feature','id':row['Row_ID'],'properties':props,'geometry':geometry})
    (OUT/f'{group}_wgs84.geojson').write_text(json.dumps({'type':'FeatureCollection','name':group+'_rights_events_WGS84','features':features},ensure_ascii=False,separators=(',',':')))

point_headers=['Row_ID','Object_ID','Name','Type','Value','X','Y','Z','CRS','Event','Event_Status','Year_Status','Event_Date','Year_Min','Year_Max','Source_Year','Record_ID','Relation_ID','Geometry_Status','Right_Scope','Geo_ID','Geo_Source','Right_Source','Note','Review']
line_headers=['Row_ID','Object_ID','Name','Type','Value','Geometry_Status','Geometry_File','Right_Scope','Event','Event_Status','Year_Status','Event_Date','Year_Min','Year_Max','Source_Year','Record_ID','Relation_ID','CRS','Geometry_Scope','Official_Name','Geo_ID','Geo_Source','Right_Source','Note','Review']
none_headers=['Row_ID','Object_ID','Name','Type','Value','Geometry_Status','Event','Event_Status','Year_Status','Event_Date','Year_Min','Year_Max','Source_Year','Record_ID','Relation_ID','CRS','Right_Source','Note','Review']
specs=[{'key':'points','sheet':'点对象','file':'01_points_wgs84.csv','headers':point_headers},
       {'key':'lines','sheet':'线性对象','file':'02_linear_objects.csv','headers':line_headers},
       {'key':'nonunique','sheet':'无唯一坐标及待核定','file':'03_no_unique_coordinate.csv','headers':none_headers}]
for s in specs:s['rows']=[[r.get(h) for h in s['headers']] for r in tables[s['key']]]
summary={'object_count':len(objs),'event_count':len(events),'row_counts':{k:len(v) for k,v in tables.items()},
    'object_counts':dict(Counter(o['Table'] for o in objs.values())),'line_objects_with_geometry':len(geoms),
    'line_event_features':sum(r['Object_ID'] in geoms for r in tables['lines']),
    'candidate_line_objects':[o['Object_ID'] for o in objs.values() if o['Geometry_Status'].startswith('候选')],
    'input_timeline_coverage':len(R),'input_relation_coverage':len(REL),'crs':'EPSG:4326','point_z':0,
    'coordinate_transform':tr.description,'transform_accuracy_m':tr.accuracy}
payload={'specs':specs,'summary':summary,'objects':list(objs.values()),'events':events}
(ROOT/'04_pipeline/work/qgis_workbook_data.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
(OUT/'coverage_and_validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))

for r in tables['points']:
    assert r['Z']==0 and 5 < r['X'] < 11 and 45 < r['Y'] < 48.5
for r in [r for rs in tables.values() for r in rs]:
    assert r['Value'] is None or (type(r['Value'])==int and 1800<r['Value']<2200)
    assert r['Value'] is None or not r['Event_Date'] or int(r['Event_Date'][:4])==r['Value']
    if r['Year_Status'] in ['observation_not_change','not_applicable']:assert r['Value'] is None
for g in geoms.values():
    assert g.has_z
    for part in g.geoms:assert all(z==0 and 5<x<11 and 45<y<48.5 for x,y,z in part.coords)
assert len({r['Row_ID'] for rs in tables.values() for r in rs})==sum(len(rs) for rs in tables.values())
print(json.dumps(summary,ensure_ascii=False,indent=2))
