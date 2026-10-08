import xml.etree.ElementTree as E,math,json,matplotlib.pyplot as plt
from pathlib import Path
R=Path(__file__).resolve().parents[1];r=E.parse(R/'references/osm.xml').getroot();ns={n.attrib['id']:(float(n.attrib['lat']),float(n.attrib['lon'])) for n in r.findall('node')}
def xy(p):return ((p[1]-76.952)*111320*math.cos(math.radians(8.486)),(p[0]-8.486)*111320)
fig,ax=plt.subplots(figsize=(14,15))
for w in r.findall('way'):
 t={v.attrib['k']:v.attrib['v'] for v in w.findall('tag')};p=[xy(ns[n.attrib['ref']]) for n in w.findall('nd')];xs,ys=zip(*p)
 if t.get('railway')=='rail':ax.plot(xs,ys,'k-',lw=1);ax.text(xs[len(xs)//2],ys[len(xs)//2],w.attrib['id'][-5:],fontsize=5,color='red')
 elif t.get('railway')=='platform':ax.fill(xs,ys,color='gold');ax.text(sum(xs)/len(xs),sum(ys)/len(ys),t.get('ref','P?'),fontsize=9)
 elif 'building' in t:ax.fill(xs,ys,color='silver',alpha=.5);name=t.get('name','');ax.text(sum(xs)/len(xs),sum(ys)/len(ys),name,fontsize=5)
 elif t.get('highway') in ('primary','secondary','tertiary'):ax.plot(xs,ys,'b-',lw=2)
ax.axis('equal');ax.set_xlim(-450,450);ax.set_ylim(-650,650);ax.grid();fig.savefig(R/'references/mapped_layout.png',dpi=140)
