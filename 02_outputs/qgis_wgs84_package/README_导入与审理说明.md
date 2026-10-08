# Concession：WGS84 坐标与 QGIS 导入包

> 2026-10-08：本包的 4 个 GeoJSON（points_wgs84、lines_wgs84 及其 _classified）已删除，改用 `../concession_objects_merged/` 中按地物合并的点、线两个文件。下文提到这些 GeoJSON 的地方以那里为准；原文件可从 git 提交 8e39105 取回。

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
