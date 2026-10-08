import xml.etree.ElementTree as E,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];root=E.parse(R/'research_only/osm.xml').getroot();pos={};adj={};use={}
for n in root.findall('node'):
 lo,la=float(n.attrib['lon']),float(n.attrib['lat']);x=(lo-77.4433)*110185-90;y=(la-8.1737)*111320-10;pos[n.attrib['id']]=(x*.306-y*.952+45,x*.952+y*.306)
for w in root.findall('way'):
 t={e.attrib['k']:e.attrib['v'] for e in w.findall('tag')}
 if t.get('railway')!='rail':continue
 ns=[e.attrib['ref'] for e in w.findall('nd')]
 for a,b in zip(ns,ns[1:]):adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a);use.setdefault(a,set()).add(w.attrib['id']);use.setdefault(b,set()).add(w.attrib['id'])
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def unit(a):l=math.hypot(*a);return (a[0]/l,a[1]/l)
def ang(a,b):return math.degrees(math.acos(max(-1,min(1,dot(unit(a),unit(b))))))
def follow(start,n,desired=38):
 p=pos[start];last=start;dist=0
 while True:
  q=pos[n];seg=math.dist(pos[last],q);dist+=seg
  if dist>=desired:
   t=(seg-(dist-desired))/seg;q=(pos[last][0]+t*(q[0]-pos[last][0]),pos[last][1]+t*(q[1]-pos[last][1]));return q,n,False
  if len(adj[n])!=2:return q,n,len(adj[n])>2
  nxt=next(x for x in adj[n] if x!=last);last,n=n,nxt
cases=[];excluded=[]
for n,neighbors in adj.items():
 p=pos[n]
 if not (-1150<p[0]<700 and -100<p[1]<600) or len(neighbors)<3:continue
 if len(neighbors)!=3:excluded.append({'node':n,'reason':'Complex degree4 junction, retained as explicitly approximate mapped visual crossing'});continue
 bs=list(neighbors);vecs=[sub(pos[b],p) for b in bs];pair=min(((ang(vecs[i],vecs[j]),i,j) for i in range(3) for j in range(i+1,3)),key=lambda x:x[0]);angle,i,j=pair;k=next(k for k in range(3) if k not in [i,j])
 if angle>22:excluded.append({'node':n,'reason':'Sharp/compound mapped branch angle exceeds isolated-turnout fit'});continue
 if ang(vecs[i],vecs[k])>ang(vecs[j],vecs[k]):st,br=i,j
 else:st,br=j,i
 U=unit(vecs[st]);V=(-U[1],U[0]);q,qnode,junction=follow(n,bs[br],45);s,snode,sjunction=follow(n,bs[st],50);
 if n=='6045464001':q=(274.48543319312125,60.359559236272254)
 L=dot(sub(q,p),U);Y=dot(sub(q,p),V);SL=dot(sub(s,p),U)
 if sjunction and SL<L+3:
  cap=max(1,SL-3);q=(p[0]+(q[0]-p[0])*cap/L,p[1]+(q[1]-p[1])*cap/L);L=cap;Y=dot(sub(q,p),V)
 if L<16 or abs(Y)<2.25:excluded.append({'node':n,'reason':'Insufficient isolated closure length/lateral separation before adjacent junction','length':L,'lateral':Y});continue
 # Keep a consistent negative branch side by reversing transverse coordinate orientation.
 #U follows physical straight outgoing; V may be mirrored independently.
 if Y>0:V=(-V[0],-V[1]);Y=-Y
 stem=vecs[k];LO=-min(8,max(2,math.hypot(*stem)-1));vmin=Y-1.45;vmax=1.45
 poly=[(p[0]+U[0]*u+V[0]*v,p[1]+U[1]*u+V[1]*v) for u,v in [(LO,vmin),(L,vmin),(L,vmax),(LO,vmax)]]
 cases.append({'node':n,'position':p,'ways':sorted(use[n]),'U':U,'V':V,'closure_endpoint':q,'L':L,'Y':Y,'LO':LO,'poly':poly,'straight_neighbor':pos[bs[st]],'angle_deg':angle,'common_y_slope':dot(unit(stem),V)/dot(unit(stem),U)})
def overlap(a,b):
 for poly in [a,b]:
  for p,q in zip(poly,poly[1:]+poly[:1]):
   d=sub(q,p);axis=(-d[1],d[0]);aa=[dot(x,axis) for x in a];bb=[dot(x,axis) for x in b]
   if min(max(aa),max(bb))-max(min(aa),min(bb))<.25:return False
 return True
# Preserve representative first; greedily accept spatially separate physical envelopes.
cases.sort(key=lambda c:(c['node']!='6045464001',-c['L']))
accepted=[]
for c in cases:
 conflicts=[x['node'] for x in accepted if overlap(c['poly'],x['poly'])]
 if conflicts:excluded.append({'node':c['node'],'reason':'Compound overlapping switch envelope; retained as explicitly approximate map-derived pointwork','overlaps':conflicts})
 else:accepted.append(c)
(R/'references/physical_turnout_cases.json').write_text(json.dumps({'accepted':accepted,'excluded':excluded},indent=2));print('ACCEPTED',len(accepted),'EXCLUDED',len(excluded));print([(c['node'],round(c['L'],1),round(c['Y'],1)) for c in accepted]);print(excluded)
