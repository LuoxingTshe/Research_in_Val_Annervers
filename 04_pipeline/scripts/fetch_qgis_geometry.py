import json,urllib.request,hashlib,time
from pathlib import Path
root=Path(__file__).resolve().parents[2] / '03_reference_data/geodata_resources'
manifest=[]
catalog=json.loads((root/'data/swissnames3d_catalog.json').read_text())
a=next(x for x in catalog['features'] if x['id']=='swissnames3d_2026')['assets']['swissnames3d_2026_2056.gpkg']
target=root/'data/swissnames3d_2026_2056.gpkg'
if not target.exists():
    temp=target.with_suffix('.download')
    h=hashlib.sha256(); total=0
    with urllib.request.urlopen(a['href'],timeout=60) as r, temp.open('wb') as f:
        while True:
            block=r.read(1024*1024)
            if not block: break
            f.write(block); h.update(block);total+=len(block)
            if total%(50*1024*1024)==0:print('Downloaded MB',total//(1024*1024),flush=True)
    assert '1220'+h.hexdigest().upper()==a['file:checksum'].upper()
    temp.rename(target)
    print('Verified geometry database',total,flush=True)
manifest.append({'file':str(target.relative_to(root)),'url':a['href'],'sha256':a['file:checksum'][4:].lower()})
url='https://api3.geo.admin.ch/rest/services/ech/MapServer?lang=fr'
p=json.load(urllib.request.urlopen(url,timeout=30))
(root/'data/geoadmin_layers_fr.json').write_text(json.dumps(p,ensure_ascii=False))
layers=[x for x in p['layers'] if any(t in (str(x.get('id',''))+' '+str(x.get('name',''))).lower() for t in ['wasserkraft','stauanlagen','hydro','bisse'])]
print(json.dumps([{'id':x.get('id'),'name':x.get('name')} for x in layers],ensure_ascii=False),flush=True)
(root/'data/geometry_download_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
