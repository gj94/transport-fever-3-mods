import xml.etree.ElementTree as E,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];root=E.parse(R/'research_only/osm.xml').getroot();pos={};adj={};use={}
for n in root.findall('node'):
 lo,la=float(n.attrib['lon']),float(n.attrib['lat']);xx=(lo-77.4433)*110185-90;yy=(la-8.1737)*111320-10;pos[n.attrib['id']]=(xx*.306-yy*.952+45,xx*.952+yy*.306)
for w in root.findall('way'):
 tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
 if tags.get('railway')!='rail':continue
 ns=[n.attrib['ref'] for n in w.findall('nd')]
 for a,b in zip(ns,ns[1:]):adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a);use.setdefault(a,set()).add(w.attrib['id']);use.setdefault(b,set()).add(w.attrib['id'])
r=[]
for n,nb in adj.items():
 if len(nb)<3:continue
 p=pos[n];ang=[math.degrees(math.atan2(pos[b][1]-p[1],pos[b][0]-p[0])) for b in nb]
 if 100<p[0]<500 and 25<p[1]<100:r.append({'node':n,'position':p,'ways':sorted(use[n]),'angles':ang,'neighbors':[(b,pos[b]) for b in nb]})
(R/'references/turnout_source_nodes.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
