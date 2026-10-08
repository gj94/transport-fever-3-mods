import xml.etree.ElementTree as ET,json,math
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];root=ET.parse(r/'research_only/osm.xml').getroot();nodes={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in root.findall('node')};out=[]
for w in root.findall('way'):
 t={x.attrib['k']:x.attrib['v'] for x in w.findall('tag')}
 if t.get('railway') in ['rail','platform'] or t.get('public_transport')=='platform' or t.get('building')=='train_station':
  ll=[nodes[x.attrib['ref']] for x in w.findall('nd') if x.attrib['ref'] in nodes];coords=[((lo-77.4433)*110185,(la-8.1737)*111320) for lo,la in ll];out.append({'id':w.attrib['id'],'tags':t,'lonlat':ll,'coords':coords})
(r/'references/map_geometry.json').write_text(json.dumps(out,indent=2));im=Image.new('RGB',(1500,1900),'white');d=ImageDraw.Draw(im)
for w in out:
 p=[(750+x*.72,1050-y*.72) for x,y in w['coords']];d.line(p,fill='red' if w['tags'].get('railway')=='platform' else 'black',width=2);a=p[len(p)//2];d.text(a,w['id'],fill='blue')
im.save(r/'references/map_trace.png');print('ways',len(out));print([(w['id'],w['tags']) for w in out if w['tags'].get('railway')=='platform'])
