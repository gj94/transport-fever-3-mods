"""Cut real canopy openings for both footbridge flights and test their swept body clearance."""
import bpy,sys,os,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,os.environ.get('NCJ_SHAPELY_PATH',str(Path(__file__).resolve().parents[1]/'.build_deps/shapely')))
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
import shapely
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
slots=unary_union([box(-91.8,y-1.45,-74.8,y+1.45) for y in [15.5,34.5]])
C=bpy.data.collections.new('42_CLEAR_FOOTBRIDGE_STAIR_OPENINGS');s.collection.children.link(C);C['scope']='Reconstructed canopy openings for continuous footbridge stair circulation; clear-body ray checks across flight width.'
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for q in g.geoms for p in polys(q)] if hasattr(g,'geoms') else []
cutfaces=0
for o in list(s.objects):
 if not o.name.startswith('Corrugated zinc canopy sheets') or o.type!='MESH':continue
 old=o.data;world=[o.matrix_world@v.co for v in old.vertices];vs=[];fs=[]
 for face in old.polygons:
  pts=[world[i] for i in face.vertices];poly=Polygon([(p.x,p.y) for p in pts]);normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]);constant=normal.dot(pts[0])
  if not poly.intersects(slots):k=len(vs);vs.extend(pts);fs.append(tuple(k+j for j in range(len(pts))));continue
  cutfaces+=1
  for part in polys(poly.difference(slots)):
   for tri in shapely.constrained_delaunay_triangles(part).geoms:
    coords=list(tri.exterior.coords)[:3];k=len(vs);vs.extend([(x,y,(constant-normal.x*x-normal.y*y)/normal.z)for x,y in coords]);fs.append((k,k+1,k+2))
 d=bpy.data.meshes.new(o.name+' with stair opening');d.from_pydata(vs,[],fs);d.update()
 for m in old.materials:d.materials.append(m)
 o.data=d;o.matrix_world.identity()
def beam(n,a,b,r,m):
 a,b=Vector(a),Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1)))
 if v.length<.01:v=u.cross(Vector((0,1,0)))
 v.normalize();w=u.cross(v);N=12;vs=[p+r*(v*math.cos(i*2*math.pi/N)+w*math.sin(i*2*math.pi/N))for p in [a,b]for i in range(N)];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)];d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(m)
trimmed=0
for o in list(s.objects):
 if o.type!='MESH' or not o.name.startswith(('Roof transverse tie','Roof sloped top chord','Roof diagonal web','Roof longitudinal purlin')):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];N=len(pts)//2
 if N<3:continue
 a=sum(pts[:N],Vector())/N;b=sum(pts[N:],Vector())/N;line=LineString([(a.x,a.y),(b.x,b.y)])
 if not line.intersects(slots.buffer(.08)):continue
 remaining=line.difference(slots.buffer(.08));segments=list(remaining.geoms)if hasattr(remaining,'geoms')else[remaining];mat=o.data.materials[0];radius=(pts[0]-a).length;length=line.length
 for piece in segments:
  if piece.is_empty or piece.geom_type!='LineString' or piece.length<.02:continue
  ends=[]
  for p in [piece.coords[0],piece.coords[-1]]:
   t=LineString([(a.x,a.y),p]).length/max(.00001,length);ends.append((p[0],p[1],a.z+(b.z-a.z)*t))
  beam('Trimmed canopy member at stair opening',ends[0],ends[1],radius,mat)
 bpy.data.objects.remove(o,do_unlink=True);trimmed+=1
# Roof-side longitudinal trims sit OUTSIDE the full stair-and-handrail width.
metal=bpy.data.materials['Railway blue painted steel']
for yy in [15.5,34.5]:
 for dy in [-1.49,1.49]:beam('Stair roof opening edge trim',(-91.8,yy+dy,5.42),(-74.8,yy+dy,5.42),.04,metal)
# Ground-level reconstructed blocks need actual bearing plinths below their floor slabs.
def solid_box(n,p,dim,m):
 x,y,z=[q/2 for q in dim];vs=[(p[0]+a,p[1]+b,p[2]+c)for a,b,c in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]];fs=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(m)
concrete=bpy.data.materials['Weathered concrete'];plinths=[]
entries={'STATION MANAGER':(-52.4,3.1,.68),'PARCEL OFFICE':(-43.75,3.1,.68),'TOILETS':(-68,1,.68),'ELECTRICAL / STAFF':(27,1,.68),'COACH MAINTENANCE':(-314,119,.35),'GOODS SHED':(-510,-20,.4)}
for name,(dx,dy,top) in entries.items():
 floor=bpy.data.objects.get(name+' floor')
 if floor:
  pts=[floor.matrix_world@Vector(v)for v in floor.bound_box];x0,x1=min(p.x for p in pts),max(p.x for p in pts);y0,y1=min(p.y for p in pts),max(p.y for p in pts);bottom=min(p.z for p in pts)
  solid_box(name+' supporting plinth',((x0+x1)/2,(y0+y1)/2,(bottom-.16)/2),(x1-x0+.08,y1-y0+.08,bottom+.16),concrete);plinths.append(name)
  count=max(2,round((top+.10)/.156))
  for j in range(count):
   ztop=-.10+(top+.10)*(j+1)/count;yy=dy-.15-(count-1-j)*.30
   solid_box(name+' entrance threshold step',(dx,yy,(ztop-.16)/2),(1.5,.32,ztop+.16),concrete)
# Reconcile the site grade with the original zero-metre forecourt datum so fences,
#formation and OHE feet bear on the ground instead of floating above an underset terrain slab.
for ob in s.objects:
 if ob.type=='MESH' and ob.name.startswith('Full metre-scale site ground'):
  for v in ob.data.vertices:
   if abs(v.co.z+.105)<.0002:v.co.z=0.0
 if ob.type=='MESH' and ob.name.startswith('Mapped platform '):
  for v in ob.data.vertices:
   if abs(v.co.z-.05)<.0002:v.co.z=0.0
 if ob.type=='MESH' and ob.name.startswith('Water tower support'):
  solid_box('Water tower bearing pad',(ob.location.x,ob.location.y,.11),(.75,.75,.22),concrete)
# Dedicated working-side kiosk composition; no platform geometry is altered.
cam=bpy.data.objects['05_PLATFORM_DETAIL'];cam.location=(51,10.3,2.9);cam.rotation_euler=(Vector((43,15.5,2.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=34
# Test sloping body-clear paths across both complete flights, not just landing/end points.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();tests=[]
for y in [15.5,34.5]:
 for off in [-.88,0,.88]:
  for height in [.40,1.0,1.8]:
   a=Vector((-75.6,y+off,1.428+height));b=Vector((-86.7,y+off,7.644+height));v=b-a;hit=s.ray_cast(deps,a,v.normalized(),distance=v.length)
   tests.append({'platform_stair_y':y,'lateral_offset_m':off,'body_height_m':height,'clear':not hit[0],'hit':hit[4].name if hit[0]else None})
report={'roof_faces_cut':cutfaces,'roof_members_trimmed':trimmed,'opening_bounds':[-91.8,-74.8],'opening_clear_width_m':2.9,'flight_width_m':2.2,'swept_body_rays':tests,'all_clear':all(t['clear']for t in tests),'ground_floor_plinths_added':plinths}
(R/'QA_STAIR_CANOPY_CLEARANCE.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
assert report['all_clear'],'Stair flight still has a physical obstruction; inspect hit names'
s['footbridge_clearance']='Both full stair flights have canopy openings and trimmed roof members;18 sloping body-clearance rays across flight width passed.'
# Review-only labels must not cast doubled-looking annotation shadows.
labels=bpy.data.collections.get('91_REVIEW_LABELS_NOT_PHYSICAL')
if labels:
 for o in labels.objects:
  if hasattr(o,'visible_shadow'):o.visible_shadow=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True)
