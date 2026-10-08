"""Geometric union of running rail heads, with genuine wheel-flange channels.
Offline preprocessing: Python3 + Shapely2. Use generated JSON in Blender, so Blender has no dependency.
Approximate visual turnout construction from mapped centrelines, not engineered switch design.
"""
import sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.builddeps'))
from shapely.geometry import LineString,Point,Polygon,box
from shapely.ops import unary_union,triangulate,substring
from shapely.geometry.polygon import orient
from shapely import make_valid,constrained_delaunay_triangles
D=json.loads((R/'source/mapped_geometry.json').read_text());ways=[w for w in D['ways'] if w['tags'].get('railway')=='rail'];clip=box(-820,-300,820,350)
heads=[];webs=[];feet=[];flanges=[];offsets=[];ballast_shapes=[]
for w in ways:
 p=LineString(w['xy']).intersection(clip)
 if p.is_empty:continue
 ballast_shapes.append(p.buffer(1.8,cap_style=2,join_style=2))
 for sg in (-1,1):
  run=p.offset_curve(sg*.872,join_style=2);flange=p.offset_curve(sg*.8155,join_style=2)
  heads.append(run.buffer(.034,cap_style=2,join_style=2));webs.append(run.buffer(.012,cap_style=2,join_style=2));feet.append(run.buffer(.075,cap_style=2,join_style=2));flanges.append(flange.buffer(.0225,cap_style=2,join_style=2));offsets.append((w['id'],sg,run))
head_union=unary_union(heads);channels=unary_union(flanges)
head=make_valid(head_union.difference(channels));web=make_valid(unary_union(webs).difference(channels));foot=make_valid(unary_union(feet))
# Separate tapered moving tongue meshes from the unioned running rail, preserving
# shared boundaries rather than laying duplicated rail pairs over one another.
nodes={};adj={}
for w in ways:
 for nd,p in zip(w['nodes'],w['xy']):nodes[nd]=p
 for a,b in zip(w['nodes'],w['nodes'][1:]):adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
def unit(p):
 l=math.hypot(*p);return(p[0]/l,p[1]/l)
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
blade_shapes=[];blade_nodes=[]
for nd,ns in adj.items():
 if len(ns)!=3:continue
 ns=list(ns);q=nodes[nd];vv=[unit((nodes[n][0]-q[0],nodes[n][1]-q[1])) for n in ns];_,i,j=max((dot(vv[i],vv[j]),i,j) for i in range(3) for j in range(i+1,3));k=next(z for z in range(3) if z not in(i,j));branch=i if dot(vv[i],vv[k])>dot(vv[j],vv[k]) else j;bn=ns[branch];route=None
 for w in ways:
  for ii,(a,b) in enumerate(zip(w['nodes'],w['nodes'][1:])):
   if a==nd and b==bn:route=w['xy'][ii:];break
   if b==nd and a==bn:route=list(reversed(w['xy'][:ii+2]));break
  if route:break
 if not route or len(route)<2:continue
 ln=substring(LineString(route),0,min(12,LineString(route).length));length=ln.length
 for sg in (-1,1):
  run=ln.offset_curve(sg*.872,join_style=2);ll=run.length
  if ll<.5:continue
  left=[];right=[]
  for ii in range(25):
   t=ii/24;dist=t*ll;p=run.interpolate(dist);a=run.interpolate(max(0,dist-.02));b=run.interpolate(min(ll,dist+.02));d=unit((b.x-a.x,b.y-a.y));n=(-d[1],d[0]);hw=.003+.031*t;shift=-sg*.006*(1-t);left.append((p.x+n[0]*(shift+hw),p.y+n[1]*(shift+hw)));right.append((p.x+n[0]*(shift-hw),p.y+n[1]*(shift-hw)))
  blade_shapes.append(Polygon(left+list(reversed(right))))
 blade_nodes.append(nd)
blades=make_valid(unary_union(blade_shapes).intersection(head));head=make_valid(head.difference(blades))

# This operation produces runninghead cut-outs, wing rails and pointed crossing noses;
# not additional intersecting coplanar rail pairs.
def polygons(g):
 if g.geom_type=='Polygon':return [g]
 return [p for gg in getattr(g,'geoms',[]) for p in polygons(gg)]
def meshdata(g,z0,z1):
 v=[];f=[];index={}
 def idx(x,y,z):
  k=(round(x,6),round(y,6),z)
  if k not in index:index[k]=len(v);v.append(k)
  return index[k]
 for p in polygons(g):
  p=orient(p,sign=1.0)
  if p.area<1e-7:continue
  for t in constrained_delaunay_triangles(p).geoms:
   if not p.covers(t.representative_point()):continue
   xyz=list(t.exterior.coords)[:-1]
   signed=sum(xyz[i][0]*xyz[(i+1)%3][1]-xyz[(i+1)%3][0]*xyz[i][1] for i in range(3))
   if signed<0:xyz.reverse()
   if abs(signed)<1e-10:continue
   f.append([idx(x,y,z1) for x,y in xyz]);f.append([idx(x,y,z0) for x,y in reversed(xyz)])
  for ring in [p.exterior,*p.interiors]:
   xy=list(ring.coords)
   for (a,b),(c,d) in zip(xy,xy[1:]):f.append([idx(a,b,z0),idx(c,d,z0),idx(c,d,z1),idx(a,b,z1)])
 filtered=[]
 for face in f:
  if len(set(face))<3:continue
  a=v[face[0]];area=0
  for j in range(1,len(face)-1):
   b=v[face[j]];c=v[face[j+1]];u=[b[k]-a[k] for k in range(3)];w=[c[k]-a[k] for k in range(3)];cross=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];area+=sum(q*q for q in cross)
  if area>1e-20:filtered.append(face)
 return {'vertices':v,'faces':filtered,'polygon_parts':len(polygons(g))}
frogs=[]
for i,(wid,sg,a) in enumerate(offsets):
 for wid2,sg2,b in offsets[i+1:]:
  if wid==wid2:continue
  inter=a.intersection(b)
  if inter.geom_type=='Point':frogs.append({'xy':[inter.x,inter.y],'ways':[wid,wid2]})
O={'method':'Union of mapped running rail footprints, subtract0.045m flange channels centred0.8155m either side of track centre. Railhead centres±0.872m,width0.068m:1.676m nominal gauge. Floatprecision6decimalmetres. Visual rather than engineering turnout geometry.','ballast':meshdata(unary_union(ballast_shapes),-.36,-.08),'blade':meshdata(blades,.125,.179),'blade_nodes':blade_nodes,'head':meshdata(head,.125,.178),'web':meshdata(web,.012,.135),'foot':meshdata(foot,-.015,.012),'crossing_points':frogs,'flangeway_width_m':.045}
(R/'source/running_rails_mesh.json').write_text(json.dumps(O,separators=(',',':')))
print('head',len(O['head']['vertices']),'faces',len(O['head']['faces']),'crossings',len(frogs),'cuts_area',head_union.area-head.area)
# Diagnostic true geometry plot at first interior crossing away from station platforms.
import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,2,figsize=(15,7));candidates=[q for q in frogs if -420<q['xy'][0]<-250 and q['xy'][1]>60]
c=candidates[0] if candidates else frogs[0];x,y=c['xy'];window=box(x-18,y-5,x+18,y+5)
for ax,win in [(axs[0],window),(axs[1],box(x-2,y-.65,x+2,y+.65))]:
 for p in polygons(unary_union([head,blades]).intersection(win)):
  xx,yy=p.exterior.xy;ax.fill(xx,yy,color='#536c75')
  for h in p.interiors:xx,yy=h.xy;ax.fill(xx,yy,color='white')
 ax.set_aspect('equal');ax.grid(alpha=.3);ax.set_xlabel('metres along station');ax.set_ylabel('metres into yard')
axs[0].set_title('Actual generated running-rail head geometry');axs[1].set_title('Frog nose / wing rails / 45 mm flangeways')
fig.suptitle('TVC mapped crossing '+', '.join(c['ways']));fig.tight_layout();fig.savefig(R/'renders/rail_geometry_diagnostic.png',dpi=160)
(R/'source/turnout_review_target.json').write_text(json.dumps(c,indent=2))
