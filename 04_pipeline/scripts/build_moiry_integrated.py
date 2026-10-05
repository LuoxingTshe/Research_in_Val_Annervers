from pathlib import Path
from html import escape
import json
from PIL import ImageFont

OUT=Path(__file__).resolve().parents[2] / '02_outputs/moiry_flow_allocation'
W,H=3700,2240
C={'hydro':'#287bb1','river':'#19887e','ag':'#b57922','pump':'#805aab','other':'#be626b','unknown':'#7b8793'}
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
'<rect width="100%" height="100%" fill="#fff"/>',
'<style>text{font-family:Arial,Helvetica,sans-serif;fill:#203247} .body{font-size:20px} .small{font-size:19px} .title{font-size:25px;font-weight:600}</style>',
'<title>Moiry–Gougra–Navizence integrated water-allocation Sankey schematic</title>',
'<desc>One connected multi-stage network combining reservoirs, hydropower, pumping, ecological river releases, irrigation, snowmaking and downstream returns. Band widths are schematic, not quantitative.</desc>']
nodes={}; edges=[]
font_path='/System/Library/Fonts/Supplemental/Arial.ttf'
def wrap(line,width,size):
 font=ImageFont.truetype(font_path,size); out=[]; current=''
 for word in line.split():
  candidate=(current+' '+word).strip()
  if current and font.getlength(candidate)>width:out.append(current);current=word
  else:current=candidate
 if current:out.append(current)
 return out
def txt(x,y,text,size=20,color='#203247',anchor='start',weight=400):
 parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(text)}</text>')
def node(k,x,y,title,lines,kind='hydro',w=250):
 lines=[t for line in lines for t in wrap(line,w-36,20)]
 title_size=24
 while ImageFont.truetype(font_path,title_size).getlength(title)>w-35 and title_size>18:title_size-=1
 nodes[k]=dict(x=x,y=y,w=w,h=63+27*len(lines),title=title,title_size=title_size,lines=lines,kind=kind)
def pt(k,side='r',offset=0):
 n=nodes[k];x,y,w,h=n['x'],n['y'],n['w'],n['h']
 return {'r':(x+w,y+h/2+offset),'l':(x,y+h/2+offset),'t':(x+w/2+offset,y),'b':(x+w/2+offset,y+h)}[side]
def link(a,b,kind='hydro',sa='r',sb='l',via=None,dash=False,width=23):
 p=pt(a,sa);q=pt(b,sb)
 if via:
  d=f'M {p[0]} {p[1]} '+via.format(x=p[0],y=p[1],X=q[0],Y=q[1])
 elif sa in ('t','b') and sb in ('t','b'):
  m=(p[1]+q[1])/2;d=f'M {p[0]} {p[1]} C {p[0]} {m} {q[0]} {m} {q[0]} {q[1]}'
 else:
  m=(p[0]+q[0])/2;d=f'M {p[0]} {p[1]} C {m} {p[1]} {m} {q[1]} {q[0]} {q[1]}'
 edges.append(dict(source=a,target=b,category=kind,schematic=True))
 color=C[kind]
 parts.append(f'<path d="{d}" fill="none" stroke="white" stroke-width="{width+7}" stroke-linecap="round"/>')
 parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{3 if dash else width}" opacity="{0.8 if dash else 0.38}" stroke-linecap="round"'+(' stroke-dasharray="8 7"' if dash else '')+'/>')
 # Arrow heads indicate direction; their size does not encode quantity.
 x,y=q
 if sb=='l': points=f'{x-13},{y-7} {x},{y} {x-13},{y+7}'
 elif sb=='r': points=f'{x+13},{y-7} {x},{y} {x+13},{y+7}'
 elif sb=='t': points=f'{x-7},{y-13} {x},{y} {x+7},{y-13}'
 else: points=f'{x-7},{y+13} {x},{y} {x+7},{y+13}'
 parts.append(f'<polygon points="{points}" fill="{color}" opacity="0.8"/>')

txt(65,72,'MOIRY–GOUGRA–NAVIZENCE',51,weight=600)
txt(65,116,'Integrated water-allocation network | multi-stage Sankey schematic | evidence reviewed 05 October 2026',27)
txt(65,157,'BAND WIDTHS ARE SCHEMATIC. Labels distinguish flow requirements, allocation limits, equipment capacities and annual reporting-area inflows.',23)
for x,t in [(65,'CATCHMENTS & STORAGE'),(1230,'UPPER GENERATION'),(1910,'MIDDLE STAGE'),(2610,'LOWER CONVEYANCE'),(3280,'USES & RETURNS')]:
 txt(x,208,t,20,weight=600)
parts.append('<path d="M65 225H3635" stroke="#d9e0e5"/>')

node('lona',65,290,'Lona / Mayens',['Captured stream','Separate residual quota: NR [S1]'],w=290)
node('lona_h',440,290,'Lona power plant',['~1 MW; turbine flow NR','Water transferred to Moiry [S1]'],w=290)
node('moiry_in',440,535,'Moiry catchment',['Glacier and lateral inflows','A2025 reporting area:','28.45 hm³ [S2]'],w=290)
node('moiry',850,745,'MOIRY RESERVOIR',['Storage: 77 hm³','Generation / ecological release','Snowmaking / pumped storage'],w=290)
node('turt_in',65,770,'Upper Tourtemagne',['Turtmänna and captured tributaries:','Blumattbach, Brändjibach,','Frilibach, Nebenbach [S1]'],w=310)
node('turt',440,805,'TOURTEMAGNE',['Reservoir: 0.78 hm³','A2025 reporting area:','47.56 hm³ [S2]'],w=290)
node('barneusa',440,1045,'Barneusaz',['Captured tributary; Q NR','No separate residual quota [S1]'],w=290)
node('junction',850,1010,'Upper transfer network',['Tourtemagne + Barneusaz','To Mottec / transfer to Moiry','Individual flow split: NR'],w=290)
node('mottec',1270,745,'MOTTEC',['CAP: 15 m³/s','Upgraded from 12 m³/s','87 MW [S2, S3]'],w=245)
node('pool_m',1630,745,'Mottec balance basin',['Turbine tailwater + river intake','To Vissoie or pumping','Mottec area A2025: 106.50 hm³'],w=275)
node('vissoie',1990,745,'VISSOIE',['CAP: 12 → 15 m³/s','Upgrade target; full completion','not verified [S2, S4]'],w=250)
node('pool_v',2330,745,'Vissoie balance basin',['Tailwater + river abstraction','Vissoie area A2025:','12.00 hm³ [S2]'],w=250)
node('gallery',2660,745,'Vissoie–Niouc tunnel',['CAP: ~10.8 m³/s, existing','15 m³/s tunnel: proposed','Not treated as operational [S7]'],w=250)
node('navplant',2980,745,'NAVIZENCE / CHIPPIS',['Turbine CAP: 15 m³/s','Supply constrained by the','~10.8 m³/s tunnel [S7]'],w=270)
node('pump',1270,290,'Mottec pumping modes',['Storage pump CAP: ≤3.9 m³/s','Siphon pump CAP: ≤6 m³/s','Alternative modes; do not add [S3]'],kind='pump',w=325)
node('bendolla',850,480,'Bendolla snowmaking',['Moiry dam-foot supply','Actual withdrawal: NR [S1]'],kind='other',w=290)
node('sorebois',1270,520,'Sorebois–Singlinaz',['Tsarmette penstock offtake','Snowmaking; withdrawal NR [S1]'],kind='other',w=325)
node('moulins',1630,495,'Torrent des Moulins',['Captured at Vuibiesse','No separate residual quota [S1]'],w=275)
node('vuibiesse',1990,460,'Vuibiesse intake',['Hydropower / irrigation split','Two free annual quotas:','152,000 m³ combined [S1]'],w=250)
node('roux',2330,285,'Bisse Roux',['ALLOC: ≤50 L/s','Free quota: ≤120,000 m³/yr','1 May–30 Sep; excess paid [S1]'],kind='ag',w=270)
node('stluc',2330,495,'Grand bisse de St-Luc',['ALLOC: ≤50 L/s','Free quota: ≤32,000 m³/yr','1 May–30 Sep; excess paid [S1]'],kind='ag',w=270)
node('briey',2840,285,'Briey irrigation',['ALLOC: 45 L/s normally','≤70 L/s on drought request','2017 settlement [S1]'],kind='ag',w=315)
node('niouc',2840,495,'Niouc irrigation / bisse',['ALLOC: <60 L/s inferred','2008: >50% cut from 120 L/s','Tourism channel ~25 L/s','Relationship to total unresolved [S1]'],kind='ag',w=370)
node('drinking',3320,990,'Chippis drinking water',['Downstream plant offtake','2014 agreement; Q NR [S1]'],kind='other',w=305)
node('eco',1160,1170,'Moiry release turbine',['~130 kW; over-turbine Q NR','Ecological water reused for','generation, then river release [S5]'],kind='river',w=310)
node('gougra',1530,1170,'Gougra river',['ECO: 90 L/s Apr–Sep','ECO: 50 L/s Oct–Mar','Conditional Lona alternative [S1]'],kind='river',w=295)
node('lona_release',440,1370,'Conditional Lona release',['All Lona flow as the alternative','specified for Gougra dotation','Not an extra fixed allocation [S1]'],kind='river',w=350)
node('navup',850,1430,'Upper Navizence',['Zinal glacier and tributaries','Plats de la Lée → Mottec','Actual abstraction: NR'],kind='river',w=290)
node('mintake',1270,1430,'Mottec river intake',['Captured water to balance basin','Uncaptured water stays in river','Site-specific minimum: NR'],kind='river',w=305)
node('stjean',1700,1450,'St-Jean / river junction',['Gougra joins Navizence','ECO: 300 L/s along the reach','from St-Jean to Vissoie [S1]'],kind='river',w=310)
node('vintake',2330,1450,'Vissoie river intake',['Abstraction to lower scheme','ECO: 470 L/s downstream','2004 / 2009 concession [S1]'],kind='river',w=285)
node('fang',2330,1180,'Torrent de Fang',['Hydropower diversion','ECO: 50 L/s downstream [S1]'],kind='river',w=285)
node('lower',2770,1450,'Lower Navizence',['River flow + Fang residual','Natural lateral inflows / spills','Actual combined flow: NR'],kind='river',w=290)
node('rhone',3370,1430,'RHÔNE',['Navizence river discharge','Hydropower tailwater','Tourtemagne river discharge'],kind='river',w=260)
node('ricard',2840,1740,'Ricard irrigation',['HISTORIC right: 265 L/s','2008 text: 20 Apr–20 Sep*','Actual supply below entitlement','after intake damage [S1, S6]'],kind='ag',w=350)
node('granges',3300,1740,'Granges irrigation',['Navizence supply at Chippis','Entitlement / actual flow: NR [S1]'],kind='ag',w=330)
node('aux',2330,1740,'Vissoie auxiliary unit',['Restarted Sep 2025 [S2]','Turbine Q / outlet routing: NR','Return path not assigned'],w=340)
node('turt_down',440,1730,'Lower Turtmänna',['No residual-flow allocation','reported for this basin [S1]','Does NOT mean zero river flow'],kind='river',w=350)

# Long river corridor and pumping loops are routed first, behind local branches.
link('turt','turt_down','river',sa='l',sb='l',via='C 390 {y} 390 {Y} {X} {Y}',width=19)
link('turt_down','rhone','river',sa='b',sb='b',via='C {x} 2000 3500 2000 {X} {Y}',width=19)
link('pool_m','pump','pump',sa='t',sb='r',via='C 1960 730 1960 600 1960 450 C 1960 260 1720 240 {X} {Y}',width=19)
link('junction','pump','pump',sa='t',sb='b',via='C 1170 940 1190 490 {X} {Y}',width=17)
link('pump','moiry','pump',sa='l',sb='t',via='C 1190 385 1200 680 {X} {Y}',width=19)
link('lona','lona_release','river',sa='l',sb='l',via='C 20 {y} 20 {Y} {X} {Y}',dash=True)
link('lona_release','gougra','river',via='C 960 {y} 1180 1340 {X} {Y}',dash=True)
for a,b in [('lona','lona_h'),('lona_h','moiry'),('moiry_in','moiry'),('turt_in','turt'),('turt','junction'),('barneusa','junction'),('junction','mottec'),('moiry','mottec'),('mottec','pool_m'),('pool_m','vissoie'),('vissoie','pool_v'),('pool_v','gallery'),('gallery','navplant')]:link(a,b)
link('moiry','bendolla','other',sa='t',sb='b',width=15)
link('moiry','sorebois','other',sa='r',sb='b',via='C 1190 {y} 1190 690 {X} {Y}',width=15)
for a,b in [('moulins','vuibiesse')]:link(a,b)
link('vuibiesse','vissoie',sa='b',sb='t')
link('vuibiesse','roux','ag',width=17)
link('vuibiesse','stluc','ag',width=17)
link('gallery','briey','ag',sa='t',sb='l',via='C {x} 600 2700 360 {X} {Y}',width=17)
link('gallery','niouc','ag',sa='r',sb='b',via='C 2940 {y} 2940 680 {X} {Y}',width=17)
link('navup','mintake','river')
link('mintake','pool_m',sa='t',sb='b',via='C 1500 1375 1915 1410 1930 1360 C 1960 1160 1950 1060 {X} {Y}')
link('moiry','eco','river',sa='b',sb='l',via='C 1240 940 1270 1090 {X} {Y}',width=19)
link('eco','gougra','river',width=19)
link('gougra','stjean','river',sa='b',sb='t',width=19)
link('mintake','stjean','river')
link('stjean','vintake','river')
link('vintake','pool_v',sa='t',sb='b',via='C 2230 1380 2240 1030 {X} {Y}')
link('vintake','lower','river',width=19)
link('pool_v','lower','river',sa='b',sb='t',via='C {x} 1070 2915 1120 {X} {Y}',width=17)
link('fang','gallery',sa='r',sb='b')
link('fang','lower','river',sa='b',sb='t',width=19)
link('lower','rhone','river')
link('lower','ricard','ag',sa='b',sb='t',width=17)
link('lower','granges','ag',sa='r',sb='l',via='C 3180 {y} 3190 {Y} {X} {Y}',width=17)
link('vintake','aux',sa='b',sb='t',dash=True)
link('navplant','rhone',sa='r',sb='t',via='C 3530 {y} 3570 1230 {X} {Y}')
link('navplant','drinking','other',sa='r',sb='l',width=15)

for k,n in nodes.items():
 x,y,w,h=n['x'],n['y'],n['w'],n['h'];col=C[n['kind']]
 parts.append(f'<g id="{k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="white" stroke="#d9e0e5"/><rect x="{x}" y="{y}" width="8" height="{h}" fill="{col}"/>')
 txt(x+19,y+34,n['title'],n['title_size'],weight=600)
 for i,line in enumerate(n['lines']):txt(x+19,y+65+i*27,line,20)
 parts.append('</g>')

# Evidence and unresolved quantities remain annotations, not invented physical flows.
txt(850,1640,'Annual inflow annotations refer to reporting areas,',21)
txt(850,1670,'not volumes passing through individual plants.',21)
txt(2660,1110,'Spill / bypass: Q NR',21)
txt(850,1780,'ADDITIONAL CAPTURE / SUPPLY INFORMATION [S1]',21,weight=600)
txt(850,1815,'Nava: upper-scheme intake; exact connection not resolved here.',21)
txt(850,1846,'Private non-potable allocation: 10 m³/yr (2017 agreement).',21)
txt(850,1877,'Moulins, Lona/Mayens, Barneusaz and Nava: no separate',21)
txt(850,1908,'residual-flow measures reported under scheme-wide rehabilitation.',21)

parts.append('<rect x="65" y="2010" width="3570" height="215" fill="#f3f6f8"/>')
xx=88
for kind,label in [('hydro','Hydropower conveyance'),('river','River / ecological release'),('ag','Irrigation allocation'),('pump','Pumping / storage return'),('other','Other water use')]:
 parts.append(f'<path d="M{xx} 2040h46" stroke="{C[kind]}" stroke-width="15" opacity="0.6"/>');txt(xx+60,2048,label,22);xx+=590
txt(88,2081,'Q = flow; NR = not reported; CAP = equipment capacity; ALLOC = allocation limit; ECO = reach-specific release requirement; A2025 = annual natural inflow in 2025; 1 hm³ = 1 million m³.',21)
txt(88,2113,'Dashed links: conditional route or unresolved detail. Crossings are not junctions. Ecological releases and serial turbine flows must not be summed as independent consumption.',21)
txt(88,2145,'2025 inflows: component sum 194.51 hm³; reported total 194.9 hm³ (0.39 hm³ discrepancy). No missing flow is invented. Agricultural return flows and storage changes are not quantified.',21)
txt(88,2177,'Sources: S1 Savoy 2025, pp. 78–81, 95, 100–105 (PDF); S2 FMG Annual Report 2025; S3 Alpiq Mottec 2025; S4 HYDROscope 44; S5 HYDRO 2022; S6 Ricard 2008*; S7 Alpiq 14 Mar 2025.',20)
txt(88,2209,'*Ricard: seasonal dates differ within the 2008 source; the node quotes its main text. Upper concessions expire in 2039; the lower Navizence concession expires in 2084.',20)
parts.append('</svg>')
(OUT/'moiry_integrated_sankey_en.svg').write_text('\n'.join(parts))
(OUT/'integrated_network_en.json').write_text(json.dumps({'width_basis':'schematic_not_quantitative','nodes':nodes,'links':edges},indent=2))
print(len(nodes),'nodes,',len(edges),'links')
