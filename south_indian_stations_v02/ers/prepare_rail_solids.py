"""Geometric union of running rail heads, with genuine wheel-flange channels.
Offline preprocessing: Python3 + Shapely2. Use generated JSON in Blender, so Blender has no dependency.
Approximate visual turnout construction from mapped centrelines, not engineered switch design.
"""
import sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parent
try:import shapely
except ImportError:sys.path.insert(0,str(R.parent/'tvc'/'.builddeps'))
from shapely.geometry import LineString,Point,Polygon,box
from shapely.ops import unary_union,triangulate,substring
from shapely import make_valid,constrained_delaunay_triangles
raw=json.loads((R/'references/osm_rail.json').read_text())
def xy(p):
 e=(p[0]-76.29105)*109640;n=(p[1]-9.9693)*111195;return(n*.981-e*.194,e*.981+n*.194+14)
def smooth(pp):
 out=[]
 for i in range(len(pp)-1):
  a=pp[max(0,i-1)];b=pp[i];c=pp[i+1];d=pp[min(len(pp)-1,i+2)];nn=max(3,min(24,int(math.dist(b,c)/5)))
  for j in range(nn):
   t=j/nn;out.append(tuple(.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in range(2)))
 out.append(pp[-1]);return out
ways=[]
for w in raw:
 if w['tags'].get('railway')!='rail':continue
 seg=[];segs=[]
 for p in w['points']:
  p=xy(p)
  if -510<p[0]<850 and -30<p[1]<155:seg.append(p)
  else:
   if len(seg)>1:segs.append(seg)
   seg=[]
 if len(seg)>1:segs.append(seg)
 for pp in segs:
  pp=smooth(pp);ways.append({'id':w['id'],'xy':pp,'nodes':[str(tuple(round(v,6) for v in p)) for p in pp],'tags':w['tags']})
clip=box(-510,-30,850,155)
heads=[];webs=[];feet=[];flanges=[];offsets=[]
for w in ways:
 p=LineString(w['xy'])
 if p.is_empty:continue
 for sg in (-1,1):
  run=p.offset_curve(sg*.868,join_style=2);flange=p.offset_curve(sg*.8155,join_style=2)
  heads.append(run.buffer(.030,cap_style=2,join_style=2));webs.append(run.buffer(.012,cap_style=2,join_style=2));feet.append(run.buffer(.075,cap_style=2,join_style=2));flanges.append(flange.buffer(.0225,cap_style=2,join_style=2));offsets.append((w['id'],sg,run))
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
  run=ln.offset_curve(sg*.868,join_style=2);ll=run.length
  if ll<.5:continue
  left=[];right=[]
  for ii in range(25):
   t=ii/24;dist=t*ll;p=run.interpolate(dist);a=run.interpolate(max(0,dist-.02));b=run.interpolate(min(ll,dist+.02));d=unit((b.x-a.x,b.y-a.y));n=(-d[1],d[0]);hw=.003+.027*t;shift=-sg*.006*(1-t);left.append((p.x+n[0]*(shift+hw),p.y+n[1]*(shift+hw)));right.append((p.x+n[0]*(shift-hw),p.y+n[1]*(shift-hw)))
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
  if p.area<1e-7:continue
  for t in constrained_delaunay_triangles(p).geoms:
   if not p.covers(t.representative_point()):continue
   xyz=list(t.exterior.coords)[:-1];f.append([idx(x,y,z1) for x,y in xyz]);f.append([idx(x,y,z0) for x,y in reversed(xyz)])
  for ring in [p.exterior,*p.interiors]:
   xy=list(ring.coords)
   for (a,b),(c,d) in zip(xy,xy[1:]):f.append([idx(a,b,z0),idx(c,d,z0),idx(c,d,z1),idx(a,b,z1)])
 return {'vertices':v,'faces':f,'polygon_parts':len(polygons(g))}
frogs=[]
for i,(wid,sg,a) in enumerate(offsets):
 for wid2,sg2,b in offsets[i+1:]:
  if wid==wid2:continue
  inter=a.intersection(b)
  if inter.geom_type=='Point':frogs.append({'xy':[inter.x,inter.y],'ways':[wid,wid2]})
O={'method':'Union of mapped running rail footprints, subtract0.045m flange channels centred0.8155m either side of track centre. Railhead centres±0.868m,width0.060m:1.676m nominal gauge. Floatprecision6decimalmetres. Visual rather than engineering turnout geometry.','blade':meshdata(blades,.5975,.643),'blade_nodes':blade_nodes,'head':meshdata(head,.5975,.6425),'web':meshdata(web,.49,.60),'foot':meshdata(foot,.46,.49),'crossing_points':frogs,'flangeway_width_m':.045}
(R/'geometry/rail_solids.json').write_text(json.dumps(O,separators=(',',':')))
(R/'geometry/mapped_routes.json').write_text(json.dumps(ways,separators=(',',':')))
print('head',len(O['head']['vertices']),'faces',len(O['head']['faces']),'crossings',len(frogs),'cuts_area',head_union.area-head.area)

# True planar geometry proof from the generated polygons; no render substitution.
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(1600,850),'#faf7ef');draw=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
center=(549.84625,39.75377);full=unary_union([head,blades])
for x0,spanx,spany,title in [(30,20,10,'Mapped physical crossing / metres'),(830,3,2,'Actual 45 mm flange channels / close detail')]:
 win=box(center[0]-spanx/2,center[1]-spany/2,center[0]+spanx/2,center[1]+spany/2)
 sx=740/spanx;sy=740/spany;scale=min(sx,sy)
 def pix(p):return(x0+370+(p[0]-center[0])*scale,440-(p[1]-center[1])*scale)
 for poly in polygons(full.intersection(win)):
  draw.polygon([pix(p) for p in poly.exterior.coords],fill='#516d78')
  for ring in poly.interiors:draw.polygon([pix(p) for p in ring.coords],fill='#faf7ef')
 draw.text((x0,25),title,font=font,fill='#203b3c')
 draw.text((x0,780),'ERS node 1008213472 • routes 285881585 / 49015817',font=font,fill='#203b3c')
im.save(R/'renders/14_Physical_rail_geometry.png')
