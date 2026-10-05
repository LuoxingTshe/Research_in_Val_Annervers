import json,urllib.request,urllib.parse
from pathlib import Path
root=Path(__file__).resolve().parents[2] / '03_reference_data/geodata_resources/queries'
for q in ['Mottec','Vissoie','Navizence','Lona','Bieudron','Veytaux','Cleuson','Moiry','Mauvoisin']:
    p={'layer':'ch.bfe.statistik-wasserkraftanlagen','searchField':'name','searchText':q,'contains':'true','geometryFormat':'geojson','returnGeometry':'true','sr':4326,'lang':'fr'}
    url='https://api3.geo.admin.ch/rest/services/ech/MapServer/find?'+urllib.parse.urlencode(p)
    data=json.load(urllib.request.urlopen(url,timeout=30))
    (root/('power_'+q.lower()+'.json')).write_text(json.dumps({'url':url,'retrieved_on':'2026-10-04','response':data},ensure_ascii=False,indent=2))
    print(q,json.dumps(data,ensure_ascii=False)[:2500],flush=True)
