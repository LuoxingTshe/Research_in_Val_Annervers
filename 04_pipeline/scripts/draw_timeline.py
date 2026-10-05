from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html,json,re

OUT=Path('02_outputs/negotiation_concession'); OUT.mkdir(exist_ok=True)
W=1600
regular='/System/Library/Fonts/Supplemental/Arial.ttf'
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
fonts={}
def font(size,weight=False):
 key=(size,weight)
 if key not in fonts:fonts[key]=ImageFont.truetype(bold if weight else regular,size)
 return fonts[key]
measure=ImageDraw.Draw(Image.new('RGB',(1,1)))
def wrap(t,width,size=24,weight=False):
 lines=[]
 for p in t.split('\n'):
  line=''
  for word in p.split():
   test=(line+' '+word).strip()
   if line and measure.textlength(test,font=font(size,weight))>width:lines.append(line);line=word
   else:line=test
  lines.append(line)
 return lines
events=[
('1951','Cleuson · Rights for electricity',1,'The Bornet estate transfers rights to EOS in return for electricity supply. Remaining rights are transferred in 1971.','event'),
('1963','Saxon · Substitute water supply',2,'FMM supplies Saxon through its facilities instead of Cleuson. EOS compensates FMM; Saxon’s existing claim is 350 L/s.','event'),
('1948–1963','Hongrin · Shared concession authority',3,'Fribourg contests Vaud’s proposal to license alone and compensate diverted water. The two cantons jointly grant the concession in 1963.','event'),
('18 May 1990','Bouillets · Water-source access and cost repayment',4,'Nendaz, EOS and SEBA agree on a replacement source. With no source disruption, SEBA acquires access and reimburses EOS’s connection costs.','event'),
('1992','Cleuson-Dixence · Appeals exchanged for a settlement',5,'WWF, EOS and Valais agree on compensation measures under Federal Court auspices. WWF’s appeals count as withdrawn when the agreement takes effect.','event'),
('2000','Nendaz · Storage and water purchases',6,'EOS allows municipal water storage and purchases when needed. Municipal water fees exclude supplied volumes; the canton still levies its special tax.','event'),
('2004 / 2009','Navizence · Relicensing and an unsuccessful objection',7,'The lower-stage concession is renewed in 2004 and approved in 2009. WWF’s late objection is rejected; the new term runs to 2084.','event'),
('2006–2007','Gougra · Paid access for snowmaking',8,'Zinal and Grimentz lift companies obtain water from FMG facilities with municipal consent. Water payments replace part of the value of hydropower use.','event'),
('18 Mar 2008','Niouc · Less water for irrigation investment',9,'The irrigation consortium accepts a cut of more than 50% from 120 L/s. FMG contributes a lump sum to the sprinkler network.','event'),
('2013–2016','Gougra · No appeal in return for restoration funding',10,'WWF agrees not to appeal the Vissoie–Niouc tunnel project; FMG helps fund Plats de la Lée restoration. The agreement enters the 19 October 2016 decision.','event'),
('13 Jun 2017','Briey · A quantified settlement',11,'The consortium and FMG settle disputed irrigation rights at 45 L/s, with requests up to 70 L/s in exceptional drought. Both avoid uncertain litigation.','event'),
('2018','Bisse Roux and St-Luc · Free quotas, paid excess',11,'FMG grants seasonal quotas of 120,000 and 32,000 m³/year, respectively, each capped at 50 L/s. Anniviers pays for excess water at foregone electricity value.','event'),
('2021','Cleuson and Gougra · Public parties organize for expiry',12,'Public authorities create Dixence Cleuson 2031 and ACC-FMG39 to prepare concession returns. Future water reservations and ownership remain negotiation issues.','event'),
('2022','Gougra · A price agreed now, payment due in 2039',13,'After roughly two years of talks, public grantors and FMG fix CHF 15 million: CHF 14 million for “dry” assets plus CHF 1 million for modernization value.','event'),
('2022 → 2023','Hongrin · Deferred ecological release',14,'Vaud and Fribourg accept FMHL’s 2022 flood-release postponement for winter energy reserves. Fribourg requires the withheld volume as an extra release in 2023.','event'),
('2023–2024','Hongrin · Conditional snowmaking agreement',15,'FMHL and TLML sign terms for withdrawals, payment and return flows, conditional on a cantonal pumping concession. The project is withdrawn in 2024.','event'),
('28 Feb 2025','Valais · Model terms for future bargaining',16,'The template provides free reserved water, compensated additional withdrawals, unencumbered asset return and retention of compensation for omitted maintenance.','template'),
('2031','Cleuson / First Dixence · Scheduled concession expiry',12,'A future window to renegotiate water allocation and infrastructure arrangements. The materials do not establish the terms of a completed new concession.','future'),
('2039','Upper Gougra · Scheduled return and compensation',13,'“Wet” assets are to return without charge; the agreed CHF 15 million concerns compensated assets and modernization. The future concession is a separate decision.','future'),
('2084','Lower Navizence · Scheduled end of the renewed term',7,'The 2004 concession for the lower stage reaches its stated expiry. This is separate from the upper Gougra return in 2039.','future'),
]
# Range events are placed by their outcome date, rather than their first negotiation date.
details=[
 'Bornet estate → EOS: rights (quantity not specified).\nEOS → Bornet estate: electricity (kWh not specified).',
 'FMM → Saxon: substitute supply for an existing 350 L/s entitlement.\nEOS → FMM: compensation (amount not specified).',
 'Vaud + Fribourg → FMHL: joint hydropower concession (1963).\nFMHL → cantons: financial terms not specified in this passage.',
 'Nendaz → SEBA: Bouillets source use until 2031 (interview account).\nSEBA → EOS: connection-cost reimbursement (amount not specified).',
 'WWF → EOS / Valais: withdrawal of appeals.\nEOS / Valais → environmental protection: settlement measures (amount not specified).',
 'EOS → Nendaz: storage + water supply (volume not specified).\nNendaz → EOS: water payments (amount not specified).',
 'Public grantors → FMG: 80-year concession, 2004–2084.\nFMG → rivers: Navizence 470 L/s; Fang 50 L/s residual flows.',
 'FMG → Zinal / Grimentz lift companies: snowmaking water (volume not specified).\nLift companies → FMG: water payments (rate not specified).',
 'Niouc consortium → FMG: irrigation allocation cut >50% from 120 L/s.\nFMG → sprinkler network: lump-sum funding (amount not specified).',
 'WWF → FMG: no appeal against the Vissoie–Niouc tunnel.\nFMG → Plats de la Lée: restoration funding (amount not specified).',
 'Briey consortium → FMG: standard allocation reduced from 70 to 45 L/s.\nFMG → Briey: 45 L/s; up to 70 L/s on exceptional-drought request.',
 'FMG → Anniviers: Roux 120,000; St-Luc 32,000 m³/year; each ≤50 L/s.\nAnniviers → FMG: excess water paid at foregone kWh value (May–September use).',
 'Public grantors → joint bodies: preparation for 2031 / 2039 returns.\nWater quotas / payments: not yet specified.',
 'Public grantors → FMG: CHF 15m due in 2039 (dry assets 14m + modernization 1m).\nFMG → public grantors: assets at concession expiry in 2039.',
 'Vaud + Fribourg → FMHL: permission to defer the 2022 flood release.\nFMHL → Hongrin: extra 2023 release = withheld 2022 volume (m³ not specified).',
 'FMHL → TLML: proposed 160,000–200,000 m³/year; pumping licence required.\nTLML → FMHL: payment (rate not specified); ≈80% expected return to reservoir.\nProject withdrawn in 2024.',
 'Operator → municipality: reserved water free of charge (quota to be set).\nMunicipality → operator: extra withdrawals paid at foregone energy production cost.',
 'Alpiq → public grantors: concession expiry in 2031.\nNew allocation / payments: not specified.',
 'FMG → public grantors: “wet” assets free of charge + compensated assets.\nPublic grantors → FMG: CHF 15m agreed in 2022 (not an additional payment).',
 'FMG → public grantors: lower-stage concession expiry in 2084.\nNew allocation / payments: not specified.',
]
events=[(d,t,r,details[i],k) for i,(d,t,r,_,k) in enumerate(events)]
refs=[
('S · PDF 36 / printed p. 35','“Cession des droits de l’Hoirie Bornet au profit d’EOS, avec une contrepartie de fourniture d’électricité”'),
('S · PDF 36, 46 / printed pp. 35, 45','“Une contrepartie d’EOS est prévue pour dédommager les FMM.”'),
('S · PDF 57 / printed p. 56','“Le canton de Fribourg manifeste toutefois son désaccord” / “L’octroi de la concession hydraulique […] advient finalement en 1963”'),
('S · PDF 47–48 / printed pp. 46–47','“la commune vendra la source des Bouillets à la SEBA qui remboursera à EOS les frais engendrés par le raccordement”'),
('S · PDF 37 / printed p. 36','“les recours déposés par le WWF sont considérés comme retirés dès l’entrée en force de la convention.”'),
('S · PDF 41–43 / printed pp. 40–42','“stocker de l’eau dans la retenue de Cleuson […] et d’acheter de l’eau à Alpiq en cas de besoin.”'),
('S · PDF 94, 104 / printed pp. 93, 103; B · PDF 5','“La concession des FMG a été renouvelée en 2004. Elle court jusqu’en 2084.” [B]'),
('S · PDF 102–103 / printed pp. 101–102','“le mètre-cube est bien payé, et puis pour nous […] ça nous évite d’aller faire une retenue collinaire sur une piste”'),
('S · PDF 100 / printed p. 99; agreement dated 18 March 2008','“paiement d’un montant forfaitaire par les FMG pour le développement du réseau d’irrigation par aspersion […] contre une diminution des débits”'),
('S · PDF 81, 104–105 / printed pp. 80, 103–104','“Une renaturation des Plats de la Lée pour le WWF contre une absence d’opposition contre le projet de galerie d’amenée”'),
('S · PDF 100–101 / printed pp. 99–100','“45 l/s, avec possibilité de les augmenter sur demande jusqu’à 70 l/s” / “chaque m³ d’eau supplémentaire sera acheté aux FMG”'),
('S · PDF 24–25, 37, 96 / printed pp. 23–24, 36, 95','“les communes […] créent une société simple pour gérer ce retour, qui adviendra en 2031” / “gérer le retour de concession de 2039”'),
('B · PDF 2–5; published 22 December 2022','“cette convention stipule uniquement le prix à payer” / “14 millions de francs […] l’indemnité équitable” / “le million de francs restant”'),
('S · PDF 71 / printed p. 70','“les quantités prévues pour la crue de 2022 soient relâchées pendant la crue de 2023.”'),
('S · PDF 69–70 / printed pp. 68–69','“conditionnant sa validité à l’obtention par TLML d’une concession de pompage” / “le projet a finalement été retiré en 2024.”'),
('K · PDF 4–5, 9–10; Articles 2–4, 13bis–14','“die den Gestehungskosten der entzogenen Energie entspricht” / “nach dem Heimfall lastenfrei” / “zurückbehalten”'),
]
# Earlier grants and transfers recovered from the source passages.
early_refs=[
('S · PDF 77 / printed p. 76', '“une concession des eaux de la Navizence […] octroyée par la commune d’Ayer à des privés” / “La commune de St-Jean fait de même […] en 1902”'),
('S · PDF 94 / printed p. 93', '“Le consortage du bisse de Granges avait déjà signé une première convention en 1902 avec la centrale d’électricité Chippis-Sierre.”'),
('S · PDF 77 / printed p. 76', '“En 1905, l’Aluminium Industrie Aktien Gesellschaft (AIAG) […] obtient une concession […] pour une durée de 99 ans.”'),
('S · PDF 77 / printed p. 76', '“un transfert de ces deux concessions aux Services industriels de Sierre (SIS) en 1908.”'),
('S · PDF 36 / printed p. 35', '“1908 Concession à un particulier de la force hydraulique de la Printse entre Beuson et Aproz par la commune de Nendaz.”'),
('S · PDF 100 / printed p. 99', '“En 1912, un acte notarié autorise le prélèvement de 120 l/s, du 1er juin au 31 août de chaque année, pour l’irrigation de Briey.”'),
('L · PDF 6 / printed p. 139; retrospective account', '“En 1922, la commune a racheté le bisse et probablement aussi pris à sa charge le salaire du gardien.”'),
('S · PDF 77 / printed p. 76', '“En 1943, les communes de Grimentz et d’Ayer concèdent les eaux de la Gougra […] à deux privés. Ces concessions ont ensuite été cédées à la société Isotherme SA.”'),
('S · PDF 36, 44 / printed pp. 35, 43', '“1945 Concession à EOS des eaux de la Haute-Printse et de ses affluents par la commune de Nendaz.”'),
('S · PDF 78 / printed p. 77', '“La société Isotherme SA transfère en 1953 ses diverses concessions à la société des Forces motrices de la Gougra.”'),
]
base=len(refs)
early_events=[
('Late 1800s / 1902','Navizence · Initial concession grants',1,'Ayer (late 1800s) + St-Jean (1902) → private holders: water-power concessions.\nVolumes / payments: not specified.','event'),
('1902','Granges · An early agreement',2,'Granges consortium ↔ Chippis-Sierre power station: first agreement.\nRights transferred / quantities / payments: not specified for the 1902 agreement.','event'),
('1905','Lower Navizence · A 99-year concession',3,'Seven municipalities → AIAG: Vissoie–Chippis water-power concession, 99 years.\nVolumes / payments: not specified.','event'),
('1908','Navizence · Two concessions transferred',4,'Private concession holders → Sierre industrial services (SIS): 2 concessions.\nTransfer price / water volumes: not specified.','event'),
('1908','Lower Printse · Initial concession grant',5,'Nendaz → a private holder: water-power use between Beuson and Aproz.\nLater holder → Lonza: subsequent transfer; date / price not specified.','event'),
('1912','Briey · Notarized irrigation entitlement',6,'Notarial deed → Briey irrigation: 120 L/s, 1 June–31 August each year.\nEntitlement documented; a transfer between holders is not established.','event'),
('1922','Stalden · Municipal purchase of a bisse',7,'Previous holders → Stalden municipality: irrigation-channel asset (recollection).\nMunicipality → seller(s): purchase price not specified; water-right scope unclear.','event'),
('1943','Gougra · Grants followed by an undated transfer',8,'Grimentz + Ayer → 2 private holders: Gougra water-power concessions.\nPrivate holders → Isotherme SA: later transfer; year / price not specified.\nThe later transfer cannot be dated to before 1950 from this passage.','event'),
('1945','Haute-Printse · Concession to EOS',9,'Nendaz → EOS: Haute-Printse and tributary water-power concession.\nVolumes / payments: not specified; existing irrigation supply is reserved.','event'),
]
early_events=[(d,t,base+r,s,k) for d,t,r,s,k in early_events]
events=early_events+[events[0]]+[
('1953','Gougra · Concessions transferred before dam construction',base+10,'Isotherme SA → FMG: its various water-power concessions.\nTransfer price / water volumes: not specified.','event')
]+events[1:]
refs.extend(early_refs)
# Number source notes by first appearance in the expanded timeline.
order=list(dict.fromkeys(e[2] for e in events))
renumber={old:i+1 for i,old in enumerate(order)}
refs=[refs[old-1] for old in order]
events=[(d,t,renumber[r],s,k) for d,t,r,s,k in events]
ink='#172D36'; muted='#51636B'; line='#CFD9DA'; blue='#246779'; amber='#936B20'; bg='#FFFFFF'
ops=[]
def text(x,y,t,size=24,weight=False,color=ink):ops.append(('text',x,y,t,size,weight,color))
def rule(x1,y1,x2,y2,col=line,width=2):ops.append(('line',x1,y1,x2,y2,col,width))
def dot(x,y,col=blue,hollow=False,square=False):ops.append(('dot',x,y,col,hollow,square))
def lines(x,y,t,width,size=24,weight=False,color=ink,step=None):
 step=step or round(size*1.34)
 ls=wrap(t,width,size,weight)
 for z in ls:text(x,y,z,size,weight,color);y+=step
 return y

text(70,55,'Negotiation, concessions & rights exchange',45,True)
text(70,117,'Selected milestones in Cleuson, Gougra, Hongrin-Léman and Valais irrigation',26,False,muted)
text(70,163,'Chronological sequence; spacing is not proportional. Date ranges are placed by their outcome.',20,False,muted)
dot(81,219);text(103,204,'Documented event',21)
dot(375,219,amber,square=True);text(397,204,'Model terms',21)
dot(630,219,blue,hollow=True);text(652,204,'Future expiry / obligation',21)
text(1080,204,'Superscripts → source notes',21,False,muted)
y=277; spine=264
sup=lambda n:str(n).translate(str.maketrans('0123456789','⁰¹²³⁴⁵⁶⁷⁸⁹'))
positions=[]
for date,title,ref,desc,kind in events:
 start=y; positions.append((start,kind))
 lines(70,y+2,date,168,22,True)
 title_end=lines(303,y,title+sup(ref),1210,27,True)
 bottom=lines(303,title_end+8,desc,1210,23,False,muted,31)
 y=bottom+30
for i,(start,kind) in enumerate(positions):
 if i<len(positions)-1:rule(spine,start+15,spine,positions[i+1][0]+15)
 dot(spine,start+15,amber if kind=='template' else blue,kind=='future',kind=='template')

y+=4;rule(70,y,1530,y);y+=28
text(70,y,'Source notes and original-language excerpts',31,True);y+=52
source_intro=[
('S','Andréa Savoy (July 2025). Analyse de la gouvernance de la multifonctionnalité à l’échelle des aménagements hydroélectriques : les cas de Cleuson (Valais), de l’Hongrin-Léman (Vaud) et de la Gougra (Valais). Working paper 6, Université de Lausanne.'),
('B','Florent Bagnoud (22 December 2022). Val d’Anniviers : on prépare déjà l’échéance de la concession des Forces motrices de la Gougra en 2039. Le Nouvelliste.'),
('K','Kanton Wallis / DEWK (28 February 2025). Mustervorlage Wasserrechtskonzession. Model water-rights concession; not an executed contract.'),
('L','Bellwald. Les cabanes de gardiens de bisses. Supplied extract, PDF page 6 / printed page 139; Medard Gsponer’s retrospective account.'),
]
for tag,t in source_intro:
 text(70,y,tag,21,True,blue);y=lines(108,y,t,1420,21,False,ink,28)+13
y+=9
colwidth=700; left=70; right=835
for i in range(0,len(refs),2):
 bottoms=[]
 for idx,x in [(i,left),(i+1,right)]:
  if idx>=len(refs):continue
  loc,quote=refs[idx]
  end=lines(x,y,f'{sup(idx+1)}  {loc}',colwidth,20,True,ink,27)
  end=lines(x,end+7,quote,colwidth,20,False,muted,27)
  bottoms.append(end)
 y=max(bottoms)+23
y+=3;rule(70,y,1530,y);y+=24
notes='Reading notes: grants, transfers, entitlement confirmations and agreements are distinguished in each entry. Undated follow-on transfers are grouped with their dated origin; their position does not establish a pre-1950 transfer. Moiry was built in 1954–1958 (S, PDF 78 / printed p. 77), so “before 1950” differs from “before dam completion.” The 1922 purchase is outside the Gougra case and rests on a retrospective account. Evidence reflects the supplied publications, not a live status update. “Concession” means a water-power licence where applicable; these sources do not establish a transfer of financial debt claims. The Bouillets source is described as a sale in the narrative and as exclusive use until 2031 in an interview. The 2023 compensating release is a requirement, not verified completion.'
y=lines(70,y,notes,1460,20,False,muted,27)
H=y+60
im=Image.new('RGB',(W,H),bg);dr=ImageDraw.Draw(im)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="{bg}"/>','<title>Negotiation, concessions and rights exchange: selected milestones and original sources</title>']
# Draw lines first so the chronological spine never crosses event markers.
for op in sorted(ops,key=lambda v:0 if v[0]=='line' else 1):
 if op[0]=='text':
  _,x,z,t,size,weight,col=op
  cursor=x
  for part in re.split(r'([⁰¹²³⁴⁵⁶⁷⁸⁹]+)',t):
   is_sup=bool(part) and all(c in '⁰¹²³⁴⁵⁶⁷⁸⁹' for c in part)
   label=part.translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹','0123456789')) if is_sup else part
   ps=round(size*.7) if is_sup else size
   py=z-3 if is_sup else z
   dr.text((cursor,py),label,font=font(ps,weight),fill=col)
   baseline=z+size*.91-(size*.36 if is_sup else 0)
   svg.append(f'<text x="{cursor:.2f}" y="{baseline:.2f}" fill="{col}" font-family="Arial, sans-serif" font-size="{ps}" font-weight="{700 if weight else 400}">{html.escape(label)}</text>')
   cursor+=measure.textlength(label,font=font(ps,weight))
 elif op[0]=='line':
  _,x,z,x2,z2,col,width=op;dr.line((x,z,x2,z2),fill=col,width=width)
  svg.append(f'<line x1="{x}" y1="{z}" x2="{x2}" y2="{z2}" stroke="{col}" stroke-width="{width}"/>')
 else:
  _,x,z,col,hollow,square=op;r=7
  if square:
   dr.rectangle((x-r,z-r,x+r,z+r),fill=col)
   svg.append(f'<rect x="{x-r}" y="{z-r}" width="14" height="14" fill="{col}"/>')
  else:
   dr.ellipse((x-r,z-r,x+r,z+r),fill=bg if hollow else col,outline=col,width=2)
   svg.append(f'<circle cx="{x}" cy="{z}" r="{r}" fill="{bg if hollow else col}" stroke="{col}" stroke-width="2"/>')
svg.append('</svg>')
im.save(OUT/'negotiation_concession_timeline.png')
(OUT/'negotiation_concession_timeline.svg').write_text('\n'.join(svg))
# Preview at readable size, in two sections.
split=positions[-1][0]+160
im.crop((0,0,W,min(split,H))).resize((1000,round(min(split,H)*1000/W))).save('04_pipeline/work/timeline_events_preview.png')
im.crop((0,min(split,H),W,H)).resize((1100,round((H-min(split,H))*1100/W))).save('04_pipeline/work/timeline_sources_preview.png')
print('Timeline:',len(events),'milestones;',len(refs),'source notes;',W,'x',H)
