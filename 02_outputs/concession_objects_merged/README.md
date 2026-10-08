# 地物合并图层（WGS84）

- `objects_points_wgs84.geojson`：11 个点地物（电站、坝、餐厅）
- `objects_lines_wgs84.geojson`：20 个线地物（河流、溪流、灌渠、攀岩路线）

由 `qgis_wgs84_package/` 原有的点、线 GeoJSON（含两个 classified 版本）按 Object_ID 合并而来，一个地物一条要素，几何未改动。两个文件字段相同。由 `04_pipeline/scripts/build_merged_objects.py` 生成，2026-10-08。

原来的 4 个 GeoJSON（`points_wgs84`、`lines_wgs84` 及其 `_classified`）已删除，以本目录两个文件代替；需要时可从 git 提交 `8e39105` 取回，脚本在文件缺失时会自动从该提交读取。

## 字段

| 字段 | 内容 |
|---|---|
| Object_ID, Name | 同原图层 |
| Feature_Type | 建筑／地物类型：水电站、坝体（注明坝型）、餐厅建筑、河流、溪流、灌渠（bisse／Suone）、攀岩路线 |
| Category, Transition_Year | 取自原 classified 图层，原样保留 |
| Built_Year | 建成年份（整数）。老灌渠取最早文字记载年（建成不晚于此）；天然河流为空 |
| Built_Year_Note | 年份口径、施工期、改建等说明 |
| Built_Year_Basis | 联网／文献／联网+文献／推测／不适用／未知 |
| Built_Year_Source | 网页或文献（含页码） |
| Concession_1…8 | 原 `Value` 字段：每次 concession／权利安排事件单独一个年份字段，按年份排序 |
| Concession_n_Event | 对应事件、Event_Status、timeline 记录号。只有区间的事件，年份字段为空，区间写在本字段开头 |
| Geometry_Status, CRS | 同原图层 |

## 使用注意

- Concession_n 不全是特许权授予：包括期限届满（future）、提议（proposal）、取消（cancelled）、供水协议等，需看 `_Event` 中的状态。供水协议不等于特许权转让。
- 推测值：Restaurant Lac de Moiry（1958，坝施工期木板房改作餐厅，1989 年雪崩后重建）、Bisse de Niouc（1908，依赖 AIAG 的 Vissoie–Niouc 隧洞）、Bisse de Ricard（约 1500，“15 世纪／约 500 年前”）。Äbibärgeri 只知 1922 年前已存在，留空。
