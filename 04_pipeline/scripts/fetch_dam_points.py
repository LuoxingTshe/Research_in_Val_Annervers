import json,urllib.request,urllib.parse
from pathlib import Path
root=Path(__file__).resolve().parents[2] / '03_reference_data/geodata_resources/queries'
for q in ['Moiry','Turtmann','Tourtemagne','Cleuson','Hongrin','Mottec','Vissoie']:
    p={'layer':'ch.bfe.stauanlagen-bundesaufsicht','searchField':'damname','searchText':q,'contains':'true','geometryFormat':'geojson','returnGeometry':'true','sr':4326,'lang':'fr'}
    url='https://api3.geo.admin.ch/rest/services/ech/MapServer/find?'+urllib.parse.urlencode(p)
    data=json.load(urllib.request.urlopen(url,timeout=30))
    (root/('dam_'+q.lower()+'.json')).write_text(json.dumps({'url':url,'retrieved_on':'2026-10-04','response':data},ensure_ascii=False,indent=2))
    print(q,json.dumps([{'id':x['id'],'name':x['properties'].get('damname'),'geometry':x['geometry']} for x in data['results']],ensure_ascii=False),flush=True)
