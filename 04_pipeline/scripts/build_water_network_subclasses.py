"""Split the supplied water network by position/type and recorded chronology.

Run from the project root. Preserve geometry; export only visualization properties.
"""

import argparse
import copy
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = Path(
    '/Volumes/luoxie_ethz/Annivers/SHP/JahrRecord/'
    'Water_Anniviers_Turtmann_pipes.geojson'
)
GROUPS = {
    '01_surface_channels': '地上水渠',
    '02_surface_pipes': '地上管道',
    '03_underground_conveyance': '地下输水段',
}
PERIODS = {
    '01_before_1958': '1958年前',
    '02_1958_2000': '1958–2000年（含端点）',
    '03_after_2000_restored': '2000年后修复',
    '04_unknown': '年代未知',
}
VISUAL_FIELDS = ('Name', 'CLASS_GROUP', 'CLASS_SUBTYPE', 'CLASS_PERIOD', 'CLASS_YEAR')


def year(value):
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        raise ValueError(f'Invalid year: {value!r}')
    number = int(value)
    if str(number) != str(value) or not 1 <= number <= 9999:
        raise ValueError(f'Invalid year: {value!r}')
    return number


def year_period(value):
    if value is None:
        return '未知'
    if value < 1958:
        return '1958年前'
    if value <= 2000:
        return '1958–2000年'
    return '2000年后'


def classify(feature):
    result = copy.deepcopy(feature)
    p = result['properties']
    kind, location = p.get('OBJEKTART'), p.get('VERLAUF')
    if location in ('Oberirdisch', 'Bruecke'):
        if kind == 'Bisse Suone':
            group, subtype = '01_surface_channels', '地上水渠（断面形式未细分）'
        elif kind in ('Druckleitung einfach', 'Druckleitung mehrfach'):
            group, subtype = '02_surface_pipes', '地上压力管道'
        else:
            raise ValueError(f'Unmapped surface type: {kind!r}')
    elif location in ('Unterirdisch bestimmt', 'Unterirdisch unbestimmt'):
        group = '03_underground_conveyance'
        if kind == 'Druckstollen':
            subtype = '地下压力隧洞'
        elif kind in ('Druckleitung einfach', 'Druckleitung mehrfach'):
            subtype = '地下压力管道'
        elif kind == 'Bisse Suone':
            subtype = '地下水渠段（管道／涵洞／隧洞形式未细分）'
        else:
            raise ValueError(f'Unmapped underground type: {kind!r}')
    else:
        raise ValueError(f'Unmapped location: {location!r}')

    build, repair = year(p.get('BAU_JAHR')), year(p.get('SAN_JAHR'))
    # A repair is an event on an older asset: retain both dates and bases.
    selected = max(v for v in (build, repair) if v is not None) if (
        build is not None or repair is not None
    ) else None
    basis = 'SAN_JAHR' if repair is not None and repair == selected else (
        'BAU_JAHR' if build is not None else None
    )
    if selected is None:
        period = '04_unknown'
    elif selected < 1958:
        period = '01_before_1958'
    elif selected <= 2000:
        period = '02_1958_2000'
    elif basis == 'SAN_JAHR':
        period = '03_after_2000_restored'
    else:
        # Do not mislabel a newly built structure as a restoration.
        raise ValueError('Post-2000 construction needs its own category')
    notes = []
    if location == 'Bruecke':
        notes.append('桥上段计入地上；保留原VERLAUF与STUFE')
    if location == 'Unterirdisch unbestimmt':
        notes.append('地下位置不确定；不得视为精确实测线位')
    if kind == 'Bisse Suone' and group == '03_underground_conveyance':
        notes.append('源数据未区分管道、涵洞或隧洞')
    if p.get('BAU_GENAU') == '首次记载':
        notes.append('BAU_JAHR为首次记载年，不是确切建造年')
    elif p.get('BAU_GENAU') == '推测':
        notes.append('BAU_JAHR为推测年份')
    if repair is not None:
        notes.append('修复年沿用源属性；精确修复范围未独立核验')
    if selected is None:
        notes.append('缺少工程年代；制图创建/更新/修订年不用于工程分类')
    added = {
        'CLASS_GROUP': GROUPS[group],
        'CLASS_SUBTYPE': subtype,
        'CLASS_PERIOD': PERIODS[period],
        'CLASS_YEAR': selected,
        'CLASS_YEAR_FIELD': basis,
        'CLASS_BUILD_PERIOD': year_period(build),
        'CLASS_REPAIR_PERIOD': year_period(repair),
        'CLASS_BUILD_CERTAINTY': p.get('BAU_GENAU'),
        'CLASS_NOTE': '；'.join(notes) or None,
    }
    if set(added) & set(p):
        raise ValueError('Classification would overwrite source properties')
    p.update(added)
    return result, group, period


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--output', type=Path,
                        default=ROOT / '02_outputs/water_network_subclasses')
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    data = json.loads(source_bytes)
    assert data['type'] == 'FeatureCollection'
    rows = [classify(feature) for feature in data['features']]
    features = [row[0] for row in rows]
    uuids = [feature['properties']['UUID'] for feature in features]
    assert len(set(uuids)) == len(uuids), 'Duplicate source UUIDs'
    for original, annotated in zip(data['features'], features):
        assert original['geometry'] == annotated['geometry']
        assert all(annotated['properties'][k] == v
                   for k, v in original['properties'].items())
    args.output.mkdir(parents=True, exist_ok=True)
    inventory = []
    written = []

    def write_layer(relative, chosen, label):
        layer = copy.deepcopy({k: v for k, v in data.items() if k != 'features'})
        layer['name'] = label
        visual_features = []
        for feature in chosen:
            p = feature['properties']
            properties = {
                'Name': p.get('NAME') or p.get('ANLAGE'),
                **{field: p[field] for field in VISUAL_FIELDS if field != 'Name'},
            }
            visual_features.append({
                'type': 'Feature', 'properties': properties,
                'geometry': copy.deepcopy(feature['geometry']),
            })
        layer['features'] = visual_features
        path = args.output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(layer, ensure_ascii=False, indent=2) + '\n',
                        encoding='utf-8')
        reread = json.loads(path.read_text(encoding='utf-8'))
        assert reread['features'] == visual_features
        assert all(set(f['properties']) == set(VISUAL_FIELDS) for f in reread['features'])
        assert all(f['geometry'] == source['geometry']
                   for f, source in zip(reread['features'], chosen))
        assert reread.get('crs') == data.get('crs')
        written.append(path)
        inventory.append({'file': relative, 'category': label,
                          'feature_count': len(chosen)})

    write_layer('all_classified.geojson', features, '全部输水段（含分类字段）')
    leaf_uuids = []
    counts = Counter((group, period) for _, group, period in rows)
    for group, group_label in GROUPS.items():
        chosen = [f for f, g, _ in rows if g == group]
        write_layer(f'{group}/all.geojson', chosen, group_label)
        for period, period_label in PERIODS.items():
            chosen = [f for f, g, p in rows if g == group and p == period]
            write_layer(f'{group}/{period}.geojson', chosen,
                        f'{group_label} — {period_label}')
            leaf_uuids.extend(f['properties']['UUID'] for f in chosen)
    assert Counter(leaf_uuids) == Counter(uuids), 'Omitted or repeated leaf feature'

    with (args.output / 'layer_index.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['file', 'category', 'feature_count'])
        writer.writeheader()
        writer.writerows(inventory)
    unknown = [f['properties'] for f, _, p in rows if p == '04_unknown']
    with (args.output / 'unknown_year_review.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        fields = ['UUID', 'NAME', 'ANLAGE', 'OBJEKTART', 'VERLAUF',
                  'CLASS_GROUP', 'CLASS_SUBTYPE', 'BAU_JAHR', 'SAN_JAHR', 'BAU_QUELLE']
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(unknown)

    table = ['| 类别 | 1958年前 | 1958–2000年 | 2000年后修复 | 年代未知 | 合计 |',
             '|---|---:|---:|---:|---:|---:|']
    for group, label in GROUPS.items():
        values = [counts[group, period] for period in PERIODS]
        table.append('| ' + ' | '.join([label, *map(str, values), str(sum(values))]) + ' |')
    totals = [sum(counts[g, p] for g in GROUPS) for p in PERIODS]
    table.append('| 合计 | ' + ' | '.join(map(str, [*totals, sum(totals)])) + ' |')
    subtype_counts = Counter(f['properties']['CLASS_SUBTYPE'] for f in features)
    underground = '\n'.join(f'- {k}：{v} 段。' for k, v in subtype_counts.items() if k.startswith('地下'))
    readme = f'''# Anniviers / Turtmann 输水网络分类副本

源文件：`{args.source}`。共 {len(features)} 个 MultiLineString；保留原坐标、高程和 CRS，不改写原文件。
全部 16 个 GeoJSON 已精简为仅含可视化所需的 5 个属性字段，原编号、制图日期、来源、权属、特许权、备注等均从图层属性删除。
源文件 SHA-256：`{hashlib.sha256(source_bytes).hexdigest()}`。

## 文件与数量

三个类别目录各有 `all.geojson` 和四个互斥年代子类；空子类仍输出有效的空 FeatureCollection。
`all_classified.geojson` 汇总全部要素；`layer_index.csv` 列出所有图层；`unknown_year_review.csv` 列出年代待核实段。
父层与子层有意重复：在 QGIS 中选择三个 `all.geojson`，或选择十二个年代子类，避免同时叠加重复绘制。

{chr(10).join(table)}

## 物理类型规则

- 源 `VERLAUF=Oberirdisch/Bruecke`：地上，桥上输水段也归地上。
- 地上 `OBJEKTART=Bisse Suone`：地上水渠；该名称并不单独证明每段都是明渠。
- 地上 `Druckleitung einfach/mehrfach`：地上压力管道。
- 源 `Unterirdisch bestimmt/unbestimmt`：地下输水段；地下位置不确定的段仍在其中，源标记可在原文件核实。
- 地下类型通过 `CLASS_SUBTYPE` 区分；源数据不足以把地下 Bisse 精确拆成管道、涵洞或隧洞，故不强行细分。

{underground}

## 年代规则与限制

按原 `BAU_JAHR`（建造／首次记载年）和 `SAN_JAHR`（修复年）中较晚的已知工程事件分类；相同年份优先修复。
1958年前为 <1958；1958–2000年为 1958≤年≤2000；2000年后修复为 SAN_JAHR>2000。
图层只保留最终分期及采用年份，原建造年、修复年、年份依据和精度信息均可回查未修改的源文件。
未知修复年不代表从未修复。源属性文字中只有模糊修复描述或多个事件，未自动补入 SAN_JAHR。

`BAU_GENAU=首次记载/推测` 的年份仅作为带有该不确定性的历史分类依据，不提升为确切建造年。
`ERSTELL_J`、`HERKUNFT_J`、`REVISION_J`、`DATUM_ERST`、`DATUM_AEND` 等制图日期均不作为工程年代。
修复子类沿用 Grand Bisse de St-Jean 的 2012 年和 Grand Bisse de Saint-Luc 的 2020 年源属性，
仅表示这些段被源文件标注了修复年份，不证明每段全部重建，也不提供精确修复施工边界。本次未独立核验历史来源。

## 图层仅保留以下字段

- `Name`：原 NAME，若为空则取设施名称 ANLAGE；均为空时保留 null。
- `CLASS_GROUP`：地上水渠／地上管道／地下输水段。
- `CLASS_SUBTYPE`：输水形式；保留不能细分的情况。
- `CLASS_PERIOD`：最终年代子类，用于分期着色与筛选。
- `CLASS_YEAR`：分类采用的工程事件年份；未知为 null。

坐标存于 geometry，不重复新增坐标属性。图层不含特许权属性。
`unknown_year_review.csv` 是图层外的核查清单，保留源编号与来源信息，供后续补充未知年代。

## 导入和再生成

坐标沿用源文件 EPSG:2056（水平，米）及 EPSG:5728（高程），适用于 QGIS。
这些文件保留源 GeoJSON 的投影 CRS 扩展，并非 RFC 7946 的经纬度 GeoJSON；不要强制指定 EPSG:4326。
已校验所有输出图层的坐标、几何和 CRS 无改动，属性严格仅含上述五个字段；
内部按源 UUID 校验十二个年代子类合计无遗漏、无重复，但 UUID 不导出到 GeoJSON。

从项目根目录运行：
`python3 04_pipeline/scripts/build_water_network_subclasses.py`
可用 `--source`、`--output` 指定输入和输出目录。压缩包含上述图层和说明。
'''
    (args.output / 'README.md').write_text(readme, encoding='utf-8')
    archive = args.output / 'Water_Anniviers_Turtmann_subclasses.zip'
    files = [*written, args.output / 'README.md', args.output / 'layer_index.csv',
             args.output / 'unknown_year_review.csv']
    with ZipFile(archive, 'w', ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(args.output))
    with ZipFile(archive) as bundle:
        assert bundle.testzip() is None
    print('\n'.join(table))
    print(f'Validated {len(features)} features in {len(written)} GeoJSON files.')
    print(f'Output: {args.output}')
    print(f'Archive: {archive}')


if __name__ == '__main__':
    main()
