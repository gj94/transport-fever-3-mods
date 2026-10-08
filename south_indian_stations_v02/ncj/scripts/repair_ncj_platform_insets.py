"""Remove mapped platform mass/markings from reconstructed ground-room footprints.
Rail-facing boundaries and full platform lengths are preserved; building insets are inferred.
"""
import bpy,sys,os,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,os.environ.get('NCJ_SHAPELY_PATH',str(Path(__file__).resolve().parents[1]/'.build_deps/shapely')))
import shapely
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
names=['TOILETS','STATION MANAGER','PARCEL OFFICE','ELECTRICAL / STAFF','WAITING HALL'];footprints={}
for name in names:
 o=bpy.data.objects.get(name+' floor')
 if not o:continue
 pts=[o.matrix_world@Vector(v)for v in o.bound_box];footprints[name]=box(min(v.x for v in pts)-.13,min(v.y for v in pts)-.13,max(v.x for v in pts)+.13,max(v.y for v in pts)+.13)
cut=unary_union(list(footprints.values()));F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
C=bpy.data.collections.new('43_PLATFORM_BUILDING_INSETS');s.collection.children.link(C);C['scope']='Inferred building insets in mapped platform mass, preserving rail-facing edges and total spans.'
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for h in g.geoms for p in polys(h)] if hasattr(g,'geoms')else[]
def append(g,z0,z1,vs,fs,surface=False):
 for p in polys(g):
  for tri in shapely.constrained_delaunay_triangles(p).geoms:
   xy=list(tri.exterior.coords)[:3];k=len(vs)
   if surface:vs.extend([(x,y,z1)for x,y in xy]);fs.append((k,k+1,k+2))
   else:vs.extend([(x,y,z)for z in [z0,z1]for x,y in xy]);fs.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
  if surface:continue
  for ring in [p.exterior]+list(p.interiors):
   pp=list(ring.coords)
   for a,b in zip(pp,pp[1:]):k=len(vs);vs.extend([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)]);fs.append((k,k+1,k+2,k+3))
def replace(o,vs,fs):
 old=o.data;d=bpy.data.meshes.new(o.name+' inset cleared');d.from_pydata(vs,[],fs);d.update()
 for m in old.materials:d.materials.append(m)
 o.data=d;o.matrix_world.identity()
areas={};cleared_tiles=0;cleared_coping=0
for o in list(s.objects):
 if o.type!='MESH':continue
 if o.name.startswith(('Mapped platform ','Terrazzo platform surface ')):
  pts=[o.matrix_world@v.co for v in o.data.vertices];z0=min(v.z for v in pts);z1=max(v.z for v in pts);top=[v for v in pts if abs(v.z-z1)<.00001];p=Polygon([(v.x,v.y)for v in top])
  if not p.is_valid:p=p.buffer(0)
  if not p.intersects(cut):continue
  left=p.difference(cut);vs=[];fs=[];append(left,z0,z1,vs,fs,o.name.startswith('Terrazzo'))
  if o.name.startswith('Mapped'):areas[o.name]={'removed_under_buildings_m2':p.area-left.area,'original_bounds':list(p.bounds),'final_bounds':list(left.bounds),'intersections':[n for n,poly in footprints.items()if p.intersects(poly)]}
  replace(o,vs,fs)
 elif o.name.startswith(('Platform paving jointed tiles','Edge weathered fascia coping')):
  vv=[o.matrix_world@v.co for v in o.data.vertices]
  if len(vv)%8:continue
  vs=[];fs=[]
  for i in range(0,len(vv),8):
   q=vv[i:i+8];p=Polygon([(q[j].x,q[j].y)for j in [0,4,6,2]])
   if not p.is_valid:p=p.buffer(0)
   if not p.intersects(cut):k=len(vs);vs.extend(q);fs.extend(tuple(k+j for j in f)for f in F);continue
   if o.name.startswith('Platform paving'):cleared_tiles+=1
   else:cleared_coping+=1
   append(p.difference(cut),min(v.z for v in q),max(v.z for v in q),vs,fs)
  replace(o,vs,fs)
marks=0
for o in list(s.objects):
 if o.type!='CURVE' or not o.name.startswith('Platform yellow safety edge'):continue
 pts=[o.matrix_world@Vector(p.co[:3])for sp in o.data.splines for p in sp.points]
 if len(pts)<2:continue
 line=LineString([(p.x,p.y)for p in pts])
 if not line.intersects(cut.buffer(.08)):continue
 remaining=line.difference(cut.buffer(.08));parts=list(remaining.geoms)if hasattr(remaining,'geoms')else[remaining]
 for p in parts:
  if p.is_empty or p.geom_type!='LineString':continue
  d=bpy.data.curves.new('Platform safety edge outside buildings','CURVE');d.dimensions='3D';d.bevel_depth=o.data.bevel_depth;d.bevel_resolution=o.data.bevel_resolution;sp=d.splines.new('POLY');sp.points.add(len(p.coords)-1)
  for v,xy in zip(sp.points,p.coords):v.co=(xy[0],xy[1],pts[0].z,1)
  ob=bpy.data.objects.new(d.name,d);C.objects.link(ob)
  for m in o.data.materials:d.materials.append(m)
 bpy.data.objects.remove(o,do_unlink=True);marks+=1
# Confirm no platform mass remains above the toilet floor at representative cubicle points.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();tests=[]
for x in [-74.7,-72.4,-70.1,-65.9,-63.6,-61.3]:
 a=Vector((x,10.4,1.6));hit=s.ray_cast(deps,a,Vector((0,0,-1)),distance=1.1)
 tests.append({'xy':[x,10.4],'hit':hit[4].name if hit[0]else None,'height':hit[1].z if hit[0]else None,'platform_conflict':bool(hit[0]and hit[4].name.startswith(('Mapped platform','Terrazzo platform','Platform paving','Platform safety edge')))})
report={'platform_insets':areas,'paving_components_cleared':cleared_tiles,'coping_components_cleared':cleared_coping,'safety_lines_clipped':marks,'cubicle_floor_checks':tests,'rail_facing_edges_and_lengths_preserved':all(a['original_bounds']==a['final_bounds']for a in areas.values())}
(R/'QA_PLATFORM_BUILDING_INSETS.json').write_text(json.dumps(report,indent=2));assert not any(t['platform_conflict']for t in tests),'Platform still intrudes into toilet floor';assert report['rail_facing_edges_and_lengths_preserved']
s['platform_building_insets']='Mapped platform bodies cut around inferred toilet/annex room footprints; source total spans and track-facing boundary remain unchanged.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True);print('PLATFORM_INSETS_CLEARED',json.dumps(report),flush=True)
