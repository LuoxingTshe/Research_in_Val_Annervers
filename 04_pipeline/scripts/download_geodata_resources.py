import json, hashlib, urllib.request, urllib.parse, zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2] / '03_reference_data/geodata_resources'
ROOT.mkdir(exist_ok=True)
for folder in ['docs','data','queries']:
    (ROOT/folder).mkdir(exist_ok=True)
manifest=[]
def fetch(url,relative):
    dest=ROOT/relative
    req=urllib.request.Request(url,headers={'User-Agent':'ResearchGeodata/1.0'})
    with urllib.request.urlopen(req,timeout=60) as response:
        data=response.read()
    dest.write_bytes(data)
    entry={'path':relative,'url':url,'downloaded_utc':datetime.now(timezone.utc).isoformat(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    manifest.append(entry)
    print(relative,len(data),flush=True)
    return data

catalog=json.loads(fetch('https://data.geo.admin.ch/api/stac/v1/collections/ch.swisstopo.swissnames3d/items?limit=100','data/swissnames3d_catalog.json'))
item=next(i for i in catalog['features'] if i['id']=='swissnames3d_2026')
asset=item['assets']['swissnames3d_2026_2056.csv.zip']
raw=fetch(asset['href'],'data/swissnames3d_2026_2056.csv.zip')
assert '1220'+hashlib.sha256(raw).hexdigest().upper()==asset['file:checksum'].upper()
manifest[-1]['official_checksum_verified']=True
with zipfile.ZipFile(ROOT/'data/swissnames3d_2026_2056.csv.zip') as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.lower().endswith('.csv'):
            (ROOT/'data'/Path(name).name).write_bytes(z.read(name))
    print('ARCHIVE',z.namelist(),flush=True)
docs={
 'geoadmin_search.html':'https://docs.geo.admin.ch/access-data/search.html',
 'geoadmin_find_features.html':'https://docs.geo.admin.ch/access-data/find-features.html',
 'geoadmin_identify_features.html':'https://docs.geo.admin.ch/access-data/identify-features.html',
 'geoadmin_stac_overview.html':'https://docs.geo.admin.ch/download-data/stac-api/overview.html',
 'swissnames3d_product.html':'https://www.swisstopo.admin.ch/fr/modele-du-territoire-swissnames3d',
 'swissNAMES3D_2026_information_FR.pdf':'https://www.swisstopo.admin.ch/dam/fr/sd-web/lXacsGJI7k9t/2026%20swissNAMES3D_ProdInfo-FR.pdf',
}
errors=[]
for filename,url in docs.items():
    try:
        data=fetch(url,'docs/'+filename)
        if filename.endswith('.pdf'): assert data.startswith(b'%PDF')
    except Exception as e: errors.append({'url':url,'error':str(e)})
queries=['Lac de Moiry','Gougra','Navizence','Turtmänna','Lac de Lona','Bisse de Niouc','Bisse de Briey','Bisse Roux','Grand Bisse de St-Luc','Vuibiesse','Tsarmette','Plats de la Lée','Lac de Cleuson','Lac de l’Hongrin','Bieudron','Mottec','Vissoie','Äbibärgeri']
results=[]
for i,q in enumerate(queries,1):
    url='https://api3.geo.admin.ch/rest/services/ech/SearchServer?'+urllib.parse.urlencode({'searchText':q,'type':'locations','origins':'gazetteer','sr':4326,'limit':10,'lang':'fr'})
    try:
        data=json.loads(fetch(url,f'queries/query_{i:02d}.json'))
        candidates=[]
        for result in data.get('results',[]):
            a=result['attrs']
            candidates.append({'label':a.get('label'),'objectclass':a.get('objectclass'),'longitude':a.get('lon'),'latitude':a.get('lat'),'bounding_box_raw':a.get('geom_st_box2d'),'detail':a.get('detail'),'status':'候选，尚未确认与研究对象同一'})
        results.append({'query':q,'url':url,'raw_file':f'queries/query_{i:02d}.json','candidate_count':len(candidates),'candidates':candidates})
    except Exception as e: errors.append({'query':q,'error':str(e)})
(ROOT/'coordinate_search_examples.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
(ROOT/'download_manifest.json').write_text(json.dumps({'downloads':manifest,'errors':errors},ensure_ascii=False,indent=2))
print(json.dumps({'download_count':len(manifest),'query_count':len(results),'errors':errors},ensure_ascii=False),flush=True)
