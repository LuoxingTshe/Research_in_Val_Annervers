import csv,json,sqlite3,unicodedata
from pathlib import Path

root=Path(__file__).resolve().parents[2] / '03_reference_data/geodata_resources'
db=root/'data/swissnames3d_2026.sqlite'
conn=sqlite3.connect(db)
conn.execute('CREATE TABLE IF NOT EXISTS names (row_id INTEGER PRIMARY KEY,uuid TEXT,name TEXT,name_normalized TEXT,source_geometry_class TEXT,object_type TEXT,object_class TEXT,e_lv95 REAL,n_lv95 REAL,z_ln02 REAL,source_file TEXT)')
assert conn.execute('SELECT count(*) FROM names').fetchone()[0]==0, 'Index already populated; leave existing index unchanged'
counts={}
for path in sorted((root/'data').glob('*.csv')):
    rows=[]
    kind=path.stem.rsplit('_',1)[-1]
    for r in csv.DictReader(path.open(encoding='utf-8-sig'),delimiter=';'):
        norm=''.join(c for c in unicodedata.normalize('NFKD',r['NAME'].casefold()) if not unicodedata.combining(c))
        def number(s):
            try:return float(s)
            except (ValueError,TypeError):return None
        rows.append((r['UUID'],r['NAME'],norm,kind,r['OBJEKTART'],r['OBJEKTKLASSE_TLM'],number(r['E']),number(r['N']),number(r['Z']),path.name))
    conn.executemany('INSERT INTO names (uuid,name,name_normalized,source_geometry_class,object_type,object_class,e_lv95,n_lv95,z_ln02,source_file) VALUES (?,?,?,?,?,?,?,?,?,?)',rows)
    counts[path.name]=len(rows)
conn.execute('CREATE INDEX IF NOT EXISTS name_idx ON names(name_normalized)')
conn.execute('CREATE INDEX IF NOT EXISTS uuid_idx ON names(uuid)')
conn.commit()
assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
summary={'counts':counts,'total_records':sum(counts.values()),'coordinate_system':'EPSG:2056 (LV95) / LN02','unique_object_uuids':conn.execute('SELECT count(DISTINCT uuid) FROM names').fetchone()[0]}
(root/'data/index_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
for q in ['naviz','navis','tsarmette','plats','abibergeri']:
    print(q,conn.execute('SELECT name,object_type,e_lv95,n_lv95 FROM names WHERE name_normalized LIKE ? LIMIT 12',('%'+q+'%',)).fetchall())
