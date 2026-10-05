from pathlib import Path
import csv,json,zipfile,xml.etree.ElementTree as ET,math,sys
sys.path.insert(0,'04_pipeline/vendor/qgis_geo_libs')
from shapely.geometry import shape
p=Path('02_outputs/qgis_wgs84_package')
tables={}
for name in ['01_points_wgs84','02_linear_objects','03_no_unique_coordinate']:
    with (p/(name+'.csv')).open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert all(None not in r for r in rows)
    assert len({r['Row_ID'] for r in rows})==len(rows)
    for r in rows:
        for k in ['Value','Year_Min','Year_Max','Source_Year']:
            assert not r[k] or (r[k].isdigit() and 1000<=int(r[k])<=2200),(name,k,r)
    tables[name]=rows
for r in tables['01_points_wgs84']:
    assert 5<float(r['X'])<11 and 45<float(r['Y'])<48 and float(r['Z'])==0 and r['CRS']=='EPSG:4326'
for file,key in [('points_wgs84.geojson','01_points_wgs84'),('lines_wgs84.geojson','02_linear_objects')]:
    obj=json.loads((p/file).read_text()); records={r['Row_ID']:r for r in tables[key]}
    for feature in obj['features']:
        g=shape(feature['geometry']); assert g.is_valid and not g.is_empty
        props=feature['properties']; r=records[props['Row_ID']]
        assert props['Value']==(int(r['Value']) if r['Value'] else None)
        def check(coords):
            if isinstance(coords[0],(int,float)):
                assert len(coords)==3 and all(math.isfinite(x) for x in coords)
                assert 5<coords[0]<11 and 45<coords[1]<48 and coords[2]==0
            else:
                for c in coords:check(c)
        check(feature['geometry']['coordinates'])
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(p/'concession_WGS84_QGIS.xlsx') as z:
    root=ET.fromstring(z.read('xl/workbook.xml'))
    assert len(root.find('s:sheets',ns))==4
    shared=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        shared=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    def value(c):
        t=c.get('t'); v=c.find('s:v',ns)
        if t=='inlineStr': return ''.join(c.find('s:is',ns).itertext())
        if v is None:return ''
        if t=='s':return shared[int(v.text)]
        return v.text or ''
    for i,(key,rows) in enumerate(tables.items(),1):
        tree=ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml'))
        actual=tree.find('s:sheetData',ns).findall('s:row',ns)
        assert len(actual)==len(rows)+1
        headers=list(rows[0]);
        def col_index(ref):
            n=0
            for ch in ref:
                if ch.isalpha(): n=n*26+ord(ch.upper())-64
                else:break
            return n-1
        for xr,expected in zip(actual[1:],rows):
            vals=['']*len(headers)
            for c in xr.findall('s:c',ns):vals[col_index(c.attrib['r'])]=value(c)
            for h,a in zip(headers,vals):
                e=expected[h]
                if h in {'X','Y','Z','Value','Year_Min','Year_Max','Source_Year'} and e:
                    assert abs(float(a)-float(e))<1e-12,(h,a,e)
                else:assert a==e,(key,h,a,e)
        assert tree.find('s:sheetViews/s:sheetView/s:pane',ns) is not None
readme='''# Concession：WGS84 坐标与 QGIS 导入包

本包按已有52条时间线记录和50条关系记录拆分为143个地物／客体。全部已提供的空间坐标均为WGS84（EPSG:4326）；X为经度、Y为纬度，Z统一为0，非实测海拔。

## 文件与规模

|文件|对象数|对象—事件行数|用途|
|---|---:|---:|---|
|01_points_wgs84.csv|11|31|已核定点对象，含X、Y、Z|
|02_linear_objects.csv|39|120|线性对象说明及逐事件年份|
|03_no_unique_coordinate.csv|93|150|面域／集合、非地物权利客体、无个案实例和位置待核定实物|

工作簿含以上三表及字段与导入说明。所有Review初值为“待审理”。对象数不等于独立concession文书数。

## 导入 QGIS

1. 点表：添加“分隔文本图层”，选择01_points_wgs84.csv，编码UTF-8、逗号分隔；X字段选X，Y字段选Y，Z字段选Z，几何坐标系选EPSG:4326。也可直接加载points_wgs84.geojson。
2. 线图层：直接加载lines_wgs84.geojson。它含20个线对象的71条对象—事件要素，保留Value及审理信息。部分对象由多段线组成。
3. 线说明表与无唯一坐标表：以“无几何”方式加载对应CSV。无参考线形的线对象仍保留在线说明表中。
4. 三个同名.csvt请与CSV放在同一目录。Value、Year_Min、Year_Max、Source_Year为整数，X、Y为实数；导入后可检查字段类型。
5. Object_ID连接同一对象的事件，Row_ID唯一标识一条记录。相同对象在不同事件行出现相同几何属正常；可按Value、Event_Status和Review筛选。

## 年份与审理规则

- Value每格只含一个整数年份。多次主要权利／安排变更拆成多行，同年不同事件也分别保留。
- 只有时间区间的记录，Value留空，区间端点分别写入Year_Min和Year_Max；不推定区间内逐年发生变更。
- 来源发表年、权益份额观测年或模板／理论文献年放在Source_Year，不自动充当权利变更年。
- 未来到期、附条件协议、提议、撤回、项目放弃、活动停止及来源差异各有Event_Status；不能将所有Value都解释为已生效授权年。完整状态说明见工作簿。
- 未确定的坐标和年份留空，不用(0,0)或年份0补齐。“未找到可靠坐标”不等于“实物不存在”，表中已区分原因。

## 空间证据与限制

点坐标来自瑞士能源局水电站／蓄水设施官方图层；Moiry餐厅点来自swisstopo建筑名称点。线形来自swissNAMES3D 2026具名线对象，保留相应名称的选定线段。原始LV95几何已转换至WGS84，转换标称精度约1米，小数位数不表示实测精度。

线形是现代地物参考几何，不是concession法律边界，也未重建历史年份的河道或设施位置。历史Value与当前参考几何的结合只用于检索、审理和展示。

20个有线形的线对象中，L09（Barneusaz／Barneuza）及L38（Äbibärgeri／Äbibergeri）仍为名称对应候选，Geometry_Status明确标注；另外18个为参考名称匹配。候选线形应由用户审理后再确认。

每行保留Right_Source、Geo_Source、Geo_ID及范围／备注。原有数据未改写。格式、字段类型、坐标范围、Z值、逐事件Value和CSV／工作簿／GeoJSON一致性已校验；未在QGIS桌面软件中实际打开验证。

官方来源：
- swisstopo：https://www.swisstopo.admin.ch/fr/modele-du-territoire-swissnames3d
- 水电站：https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfe.statistik-wasserkraftanlagen
- 蓄水设施：https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfe.stauanlagen-bundesaufsicht
'''
(p/'README_导入与审理说明.md').write_text(readme,encoding='utf-8')
validation=json.loads((p/'coverage_and_validation.json').read_text())
validation['export_checks']={'csv_xlsx_values_match':True,'geojson_values_match_csv':True,'all_geometries_valid':True,'all_exported_coordinates_wgs84_and_z0':True,'qgis_desktop_tested':False}
(p/'coverage_and_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
files=[f for f in p.iterdir() if f.suffix in {'.csv','.csvt','.geojson','.xlsx','.md','.json'}]
with zipfile.ZipFile(p/'QGIS_WGS84_导入包.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(files):z.write(f,f.name)
print(json.dumps({'status':'PASS','files_in_zip':len(files),'table_rows':{k:len(v) for k,v in tables.items()}},ensure_ascii=False))
