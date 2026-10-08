import json,math,csv,os
os.environ['MPLCONFIGDIR']='/tmp/tvc_mpl'
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
R=Path(__file__).resolve().parents[1];D=json.loads((R/'source/mapped_geometry.json').read_text());rails=[w for w in D['ways'] if w['tags'].get('railway')=='rail'];records=[]
fig,ax=plt.subplots(figsize=(25,8.6));fig.patch.set_facecolor('#f7f5ef');ax.set_facecolor('#f7f5ef')
colors={'yard':'#6d607f','siding':'#ab5a33','crossover':'#ad344b','main':'#1e6a77','rail':'#465154'}
occupied=[]
def clipped(pts):
 out=[]
 for a,b in zip(pts,pts[1:]):
  if min(a[0],b[0])>820 or max(a[0],b[0])<-820:continue
  aa=list(a);bb=list(b)
  for p,q in ((aa,bb),(bb,aa)):
   if abs(p[0])>820:
    xx=math.copysign(820,p[0]);t=(xx-p[0])/(q[0]-p[0]);p[1]+=t*(q[1]-p[1]);p[0]=xx
  if not out or math.dist(out[-1],aa)>.01:out.append(aa)
  out.append(bb)
 return out
for i,w in enumerate(rails):
 label='R%02d'%(i+1);p=clipped(w['xy']);typ=w['tags'].get('service',w['tags'].get('usage','rail'));cc=colors.get(typ,'#465154');x,y=zip(*p);ax.plot(x,y,color=cc,lw=1.1,zorder=3)
 length=sum(math.dist(a,b) for a,b in zip(p,p[1:]));target=length*(.25+.11*(i%5));run=0;mid=p[len(p)//2]
 for a,b in zip(p,p[1:]):
  ll=math.dist(a,b)
  if run+ll>=target:
   t=(target-run)/ll;mid=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t);break
  run+=ll
 labelpos=mid
 for dy in (0,4,-4,8,-8):
  found=False
  for dx in (0,20,-20,40,-40,60,-60,80,-80):
   q=(mid[0]+dx,mid[1]+dy)
   if -815<q[0]<815 and all(abs(q[0]-a)>27 or abs(q[1]-b)>8 for a,b in occupied):labelpos=q;found=True;break
  if found:break
 occupied.append(labelpos)
 if math.dist(labelpos,mid)>2:ax.plot([labelpos[0],mid[0]],[labelpos[1],mid[1]],color=cc,lw=.5,zorder=4)
 ax.text(*labelpos,label,color='white',fontsize=8.4,ha='center',va='center',bbox={'facecolor':cc,'edgecolor':'none','pad':1.4},zorder=5)
 records.append({'review_label':label,'osm_way_id':w['id'],'mapped_class':typ,'rendered_length_m':round(length,2),'operational_road_number':'unverified'})
for w in D['ways']:
 if w['tags'].get('railway')=='platform':
  p=w['xy'];ax.add_patch(Polygon(p,facecolor='#e5cf9a',edgecolor='#aa8b4d',linewidth=.8,zorder=1))
  ref=w['tags'].get('ref','1').replace(';',' / ').replace('|',' / ');xx=sum(p[0] for p in p)/len(p);yy=sum(p[1] for p in p)/len(p);ax.text(xx+30,yy,'PLATFORM '+ref,fontsize=9,color='#4a391e',ha='center',zorder=6)
ax.add_patch(Polygon([(-77,0),(59,0),(59,14),(-77,14)],facecolor='#427768',edgecolor='#284c45',zorder=2));ax.text(-9,-9,'HERITAGE + FURNISHED ROOMS',ha='center',fontsize=8,color='#284c45')
ax.add_patch(Polygon([(90,-7),(136,-7),(136,13),(90,13)],facecolor='#76a393',edgecolor='#284c45',zorder=2));ax.text(160,-20,'RECONSTRUCTED BOOKING BLOCK',fontsize=8,color='#284c45',ha='center')
for x in (-105,178):ax.plot([x,x],[13,74],color='#374446',lw=3);ax.text(x,80,'FOB',fontsize=8,ha='center')
for x,y in [(350,120),(-250,130),(-300,145)]:ax.add_patch(Polygon([(x-12,y-6),(x+12,y-6),(x+12,y+6),(x-12,y+6)],facecolor='#9c9b8d',edgecolor='#66665b'))
ax.text(-310,158,'RECONSTRUCTED\nSERVICE WORKSHOPS',ha='right',fontsize=9,color='#555')
ax.text(80,222,'MAPPED COACHING / SERVICE FAN',ha='center',fontsize=11,color='#6d607f')
ax.plot([-760,-660],[225,225],color='#293a3b',lw=4);ax.text(-710,232,'100 m',ha='center',fontsize=10)
ax.set_aspect('equal');ax.set_xlim(-840,840);ax.set_ylim(-45,250);ax.set_xlabel('Local metres along station: positive X toward WNW',fontsize=10);ax.set_ylabel('Local metres toward SSW / yard',fontsize=10);ax.grid(alpha=.13)
fig.suptitle('TVC | FULL-SCALE TRACK & COVERAGE REGISTER',fontsize=22,color='#193b3b',x=.125,ha='left',y=.93)
fig.text(.125,.855,'46 mapped railway ways • 3 physical platforms / 5 faces • full-node junction graph • no trains',fontsize=12,color='#506567')
fig.text(.125,.16,'R labels are review identifiers, NOT verified operational road numbers. Heritage:2022 photographs. Rail XY: mixed-date OSM extract retrieved2026-10-08.',fontsize=10,color='#5a6060')
fig.text(.125,.13,'Unknown room plans, signal locations, supports and service workshop positions are explicit visual reconstructions. Not an engineering survey. Mainlines cropped at ±820m.',fontsize=10,color='#5a6060')
fig.text(.125,.10,'© OpenStreetMap contributors. Geographic extract under ODbL1.0. https://www.openstreetmap.org/copyright',fontsize=9,color='#5a6060')
fig.savefig(R/'renders/00_Labelled_yard_coverage.png',dpi=170,bbox_inches='tight');fig.savefig(R/'TVC_track_coverage_plan.pdf',bbox_inches='tight')
with open(R/'TRACK_REGISTER.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
(R/'source/route_review_labels.json').write_text(json.dumps(records,indent=2))
