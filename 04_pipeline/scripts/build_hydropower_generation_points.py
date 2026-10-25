"""Create minimal hydropower station points and period-specific generation fields."""

import copy
import csv
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '02_outputs/hydropower_generation_points'
POINTS = ROOT / '02_outputs/concession_objects_merged/objects_points_wgs84.geojson'
PERIODS = ROOT / '02_outputs/gougra_period_sankeys/period_models.json'
CASCADE = ROOT / '02_outputs/gougra_cascade_energy/cascade_model.json'
WASTA = ROOT / '02_outputs/flow_diagram_sources/wasta_plants.csv'
FIELD_NOTES = {
    'E_pre1958_theory_GWh_yr': '1958年前（约1950年状态）理论毛年电量；不是历史实测产量',
    'E_1958_1961_design_GWh_yr': '1958–1961投运方案的设计平均年电量，Robert 1962 表2',
    'E_1958_1961_winter_GWh': '同一历史设计方案的平均冬季电量',
    'E_1958_1961_summer_GWh': '同一历史设计方案的平均夏季电量',
    'E_WASTA_2025_expected_GWh_yr': 'WASTA统计日2025-12-31的长期预期年电量；不是2025实际发电量',
    'E_post2039_scenario_GWh_yr': '2039年后图示情景沿用现行预期电量；不是实测值或独立预测',
}
PLANTS = {
    'P01': ('mottec', 'mottec', ['503200']),
    'P02': ('vissoie', 'vissoie', ['503300', '503350']),
    'P03': ('lona', 's_lona', ['503100']),
    'P04': ('navizence', 'chippis', ['503400']),
    'P10': (None, None, []),
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    points, periods, cascade = map(read_json, (POINTS, PERIODS, CASCADE))
    with WASTA.open(encoding='utf-8-sig', newline='') as stream:
        wasta = {row['wasta_id']: row for row in csv.DictReader(stream)}
    station_points = [f for f in points['features']
                      if f['properties'].get('Feature_Type', '').startswith('水电站')]
    assert {f['properties']['Object_ID'] for f in station_points} == set(PLANTS)
    nodes1958 = {n['id']: n for n in periods['post1958']['nodes']}
    nodes2039 = {n['id']: n for n in periods['post2039']['nodes']}
    # Confirm the historical source rather than relying only on diagram labels.
    extracted = read_json(ROOT / '04_pipeline/work/pdfs/extracted.json')
    robert = next(item for item in extracted if item['file'].startswith('Robert_'))
    table_page = robert['pages'][3]
    assert 'Tableau 2.' in table_page and '569' in table_page
    assert re.search(r'1\s+3\s+111\s+8\s+6\s+93\s+92\s+134\s+121', table_page)

    features, evidence, checks = [], [], []
    def record(name, field, value, source, locator, evidence_id, note=''):
        evidence.append(dict(Name=name, field=field, value=value, unit=(
            'GWh/season' if field.endswith(('_winter_GWh', '_summer_GWh')) else 'GWh/year'
        ), source=source, locator=locator, evidence_id=evidence_id, note=note))

    for original in station_points:
        p = original['properties']
        key, historical_id, wasta_ids = PLANTS[p['Object_ID']]
        values = {field: None for field in FIELD_NOTES}
        name = p['Name']
        if key:
            historical = nodes1958[historical_id]
            if key == 'lona':
                match = re.search(r'([\d.]+) GWh', historical['sub'])
                assert match
                annual, winter, summer = float(match[1]), 1.0, 3.0
            else:
                match = re.fullmatch(r'([\d.]+) GWh/yr · W ([\d.]+) / S ([\d.]+)',
                                     historical['energy'])
                assert match, historical['energy']
                annual, winter, summer = map(float, match.groups())
            assert winter + summer == annual
            values.update({
                'E_1958_1961_design_GWh_yr': annual,
                'E_1958_1961_winter_GWh': winter,
                'E_1958_1961_summer_GWh': summer,
            })
            for field in ('E_1958_1961_design_GWh_yr',
                          'E_1958_1961_winter_GWh', 'E_1958_1961_summer_GWh'):
                record(name, field, values[field],
                       '01_sources/hydropower/' + robert['file'], 'PDF p4, printed p251, Table 2',
                       'R01; period_models.post1958.' + historical_id,
                       'Mottec includes Moiry–Mottec and Tourtemagne–Mottec' if key == 'mottec' else '')
            expected = float(sum((Decimal(wasta[i]['production_expected_GWh'])
                                  for i in wasta_ids), Decimal('0')))
            cascade_expected = cascade['E_wasta_GWh'][key]
            if key == 'vissoie':
                cascade_expected += cascade['E_wasta_GWh']['vissoie_aux']
            assert abs(expected - cascade_expected) < 1e-9
            assert all(wasta[i]['date_of_statistic'] == '2025-12-31' for i in wasta_ids)
            values['E_WASTA_2025_expected_GWh_yr'] = expected
            ids = {'mottec': 'E01', 'vissoie': 'E02', 'navizence': 'E03', 'lona': 'E04'}
            note = 'Vissoie main 213.0 + auxiliary 3.1 = 216.1 GWh/year' if key == 'vissoie' else ''
            record(name, 'E_WASTA_2025_expected_GWh_yr', expected,
                   str(WASTA.relative_to(ROOT)), 'WASTA features ' + ', '.join(wasta_ids),
                   ids[key] + '; R10', note)
            if key in ('mottec', 'vissoie', 'navizence'):
                # Labels are rounded; use the checked underlying numeric data.
                label = nodes2039[key]['energy']
                assert label.startswith(f'{expected:.0f} GWh/yr')
                values['E_post2039_scenario_GWh_yr'] = expected
                record(name, 'E_post2039_scenario_GWh_yr', expected,
                       str(PERIODS.relative_to(ROOT)), 'post2039.nodes.' + key,
                       'R10; ' + ids[key],
                       f'Diagram label: {label}; exact value from cascade/WASTA; unchanged-system scenario')
                checks.append(dict(Name=name, check='2039图标签与底层精确值',
                                   diagram_label=label, exact_GWh_per_year=expected, status='通过'))
            if key == 'navizence':
                theoretical = periods['pre1958']['totals']['chippis_theor_GWh']
                label = next(n for n in periods['pre1958']['nodes'] if n['id'] == 'chippis')['energy']
                assert label == f'{theoretical:.0f} GWh/yr theor.'
                values['E_pre1958_theory_GWh_yr'] = theoretical
                record(name, 'E_pre1958_theory_GWh_yr', theoretical,
                       str(PERIODS.relative_to(ROOT)), 'pre1958.totals.chippis_theor_GWh',
                       'MODEL_PRE1958; R01; R11',
                       'Model theoretical gross output; no historical actual production record')
        else:
            checks.append(dict(Name=name, check='图内产量覆盖', diagram_label=None,
                               exact_GWh_per_year=None, status='Bieudron未在Gougra流量图中；保持空值'))
        properties = {'Name': name, **values}
        features.append({'type': 'Feature', 'properties': properties,
                         'geometry': copy.deepcopy(original['geometry'])})

    historic_total = sum(f['properties']['E_1958_1961_design_GWh_yr'] or 0 for f in features)
    assert historic_total == periods['post1958']['totals']['design_GWh'] == 569
    assert sum(f['properties']['E_1958_1961_winter_GWh'] or 0 for f in features) == 347
    assert sum(f['properties']['E_1958_1961_summer_GWh'] or 0 for f in features) == 222
    expected_total = sum(f['properties']['E_WASTA_2025_expected_GWh_yr'] or 0 for f in features)
    assert abs(expected_total - cascade['E_wasta_total']) < 1e-9
    assert all(f['geometry'] == o['geometry'] for f, o in zip(features, station_points))
    assert all(set(f['properties']) == {'Name', *FIELD_NOTES} for f in features)
    assert all(f['geometry']['type'] == 'Point' for f in features)
    layer = {'type': 'FeatureCollection', 'name': 'hydropower_generation_points_wgs84',
             'features': features}
    # RFC 7946 WGS84 positions, no legacy CRS property needed.
    OUT.mkdir(parents=True, exist_ok=True)
    geojson = OUT / 'hydropower_generation_points_wgs84.geojson'
    geojson.write_text(json.dumps(layer, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert read_json(geojson) == layer
    with (OUT / 'generation_evidence.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['Name', 'field', 'value', 'unit',
                                                  'source', 'locator', 'evidence_id', 'note'])
        writer.writeheader()
        writer.writerows(evidence)
    audit = {
        'station_count': len(features), 'source_point_count': len(points['features']),
        'geometry_preserved': True, 'schema_validated': True,
        'historical_design_total_GWh_yr': historic_total,
        'historical_winter_GWh': 347, 'historical_summer_GWh': 222,
        'WASTA_expected_total_GWh_yr': round(expected_total, 2),
        'checks': checks,
        'input_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in (POINTS, PERIODS, CASCADE, WASTA)},
    }
    (OUT / 'validation.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n',
                                         encoding='utf-8')
    table = ['| 电站 | 1958年前理论值 | 1958–1961设计年 | WASTA现行预期年 | 2039后情景年 |',
             '|---|---:|---:|---:|---:|']
    for f in features:
        p = f['properties']
        fields = ['E_pre1958_theory_GWh_yr', 'E_1958_1961_design_GWh_yr',
                  'E_WASTA_2025_expected_GWh_yr', 'E_post2039_scenario_GWh_yr']
        table.append('| ' + ' | '.join([p['Name'], *['—' if p[k] is None else str(p[k]) for k in fields]]) + ' |')
    readme = f'''# 水电站点副本：分时期发电量

`hydropower_generation_points_wgs84.geojson` 从现有点图层筛选全部 5 个 Feature_Type 以“水电站”开头的对象。
保留原点坐标（WGS84）和 Name，只新增数值型产量字段；不保留 ID、类型、建设年代、权属或特许权等其他字段。
原文件没有修改；源坐标中的第三维 0 原样保留，不代表本次核实的真实高程。

产量指发电电量，年度单位 GWh/年，冬夏字段单位 GWh/季节。没有混入功率 MW、水流 m³/s 或过机水量 hm³。

{chr(10).join(table)}

## 字段

{chr(10).join(f'- `{field}`：{note}。' for field, note in FIELD_NOTES.items())}

## 核对与缺项

- 对照三期流量图 `gougra_period_sankeys/period_models.json`、现状 `gougra_cascade_energy/cascade_model.json`、
  `flow_diagram_sources/wasta_plants.csv` 和 Robert 1962 的已提取文本 PDF p4（印刷 p251，表2）。
- 历史设计年总量 569 = Lona 4 + Mottec 125 + Vissoie 185 + Navizence 255；冬季 347、夏季 222。
- Mottec 历史设计值合并 Moiry–Mottec 111 和 Tourtemagne–Mottec 14；冬季 111+8=119，夏季 6。
- 现行预期值合计 653.85，和级联系统底层数据一致。Vissoie 含主机组 213.0 和辅助机组 3.1，合计 216.1。
  主、辅属于同一统计时期和同一电站，因此使用站级合计，不作为两个时期。
- 图中文字将 137.05／216.1／298.7 四舍五入为 137／216／299，副本保留底层精确值。
- Navizence 的 1958年前值 201.761 为模型理论毛电量（图上约202），不是实际历史产量。
  其他站该时期没有对应图示数据，留 null；null 不表示零。
- 2039后是图中的“现行系统与规则不变”情景，不代表真实未来发电量。
  Lona 在2039图中没有独立产量标注，所以该情景字段留空；其现行预期2.0保留在WASTA字段。
- Bieudron 属于原点图层，故保留该点；它未在 Gougra 流量图中提供产量，全部产量字段留 null。
  Turtmann／Oberems／Chippis-Rhône 等没有原点要素，未创建新坐标。
- 没有把全工程实际年产量或多年均值拆给单站，也没有把理论毛电量改称实测产量。
- 权利数据库 quantities 中没有发电电量记录；本次电量证据沿用流量图的 R01/R10/R11 与补充证据 E01–E04。
  `generation_evidence.csv` 在图层外记录每个非空值的证据ID、来源、页码/定位和计算口径；图层保持字段精简。
  `validation.json` 保存输入哈希、总量和标签核对结果。原流量图均未改动。

从项目根目录再生成：`python3 04_pipeline/scripts/build_hydropower_generation_points.py`。
'''
    (OUT / 'README.md').write_text(readme, encoding='utf-8')
    print('\n'.join(table))
    print(f'Validated {len(features)} station points; only Name + six generation fields.')
    print(geojson)


if __name__ == '__main__':
    main()
