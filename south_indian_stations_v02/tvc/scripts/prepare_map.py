import xml.etree.ElementTree as E,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];r=E.parse(R/'references/osm.xml').getroot();ns={n.attrib['id']:(float(n.attrib['lat']),float(n.attrib['lon'])) for n in r.findall('node')}
def xy(p):
 e=(p[1]-76.9526)*111320*math.cos(math.radians(8.487));n=(p[0]-8.48708)*111320
 return [-.976296*e+.21644*n,-.21644*e-.976296*n]
ways=[]
for w in r.findall('way'):
 t={v.attrib['k']:v.attrib['v'] for v in w.findall('tag')};nd=[v.attrib['ref'] for v in w.findall('nd')];p=[xy(ns[i]) for i in nd]
 if t.get('railway') in ('rail','platform') or t.get('building') or t.get('highway') or t.get('landuse')=='railway':
  if min(v[0] for v in p)>900 or max(v[0] for v in p)<-900 or min(v[1] for v in p)>290 or max(v[1] for v in p)<-160:continue
  ways.append({'id':w.attrib['id'],'tags':t,'nodes':nd,'xy':p})
(R/'source/mapped_geometry.json').write_text(json.dumps({'attribution':'© OpenStreetMap contributors; ODbL 1.0 https://www.openstreetmap.org/copyright','retrieved':'2026-10-08','origin':[8.48708,76.9526],'coordinate_note':'Station-local metres, X WNW, Y SSW. Local equirectangular projection, approximate.','ways':ways},indent=2))
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(18,5))
for w in ways:
 p=w['xy'];x,y=zip(*p);t=w['tags']
 if t.get('railway')=='rail':ax.plot(x,y,'k-',lw=.6)
 elif t.get('railway')=='platform':ax.fill(x,y,color='gold');ax.text(sum(x)/len(x),sum(y)/len(y),t.get('ref','1'),fontsize=9)
 elif 'building' in t:ax.fill(x,y,color='silver',alpha=.4)
ax.invert_yaxis();ax.set_aspect('equal');ax.set_xlim(-800,800);ax.set_ylim(220,-100);ax.grid();fig.savefig(R/'references/local_layout.png',dpi=150)
for w in ways:
 if w['tags'].get('railway')=='platform' or w['id']=='478308341':print(w['id'],w['xy'])
