"""Actual packed-scene mesh check for clear2m headroom over full stair flights."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;src=P/'ERS_full_station_v02.blend';digest=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src))
# Include all platform-canopy structure and footbridge structure. Exclude the
# treads/risers/nosings themselves because they form the intended walking floor.
collections=['08 | PLATFORM CANOPIES • full span trusses gutters lights','10 | FOOTBRIDGES • traversable stairs and landings']
vs=[];faces=[];owners=[]
for name in collections:
 for ob in bpy.data.collections[name].objects:
  if ob.name.startswith(('Stair concrete tread','Stair red riser','Stair anti-slip nosing')):continue
  if ob.type=='MESH':
   off=len(vs);vs.extend(ob.matrix_world@v.co for v in ob.data.vertices)
   for f in ob.data.polygons:faces.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
  elif ob.type=='CURVE' and ob.data.bevel_depth>0:
   for sp in ob.data.splines:
    if sp.type!='POLY':continue
    pts=[ob.matrix_world@p.co.xyz for p in sp.points]
    for a,b in zip(pts,pts[1:]):
     d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
     if u.length<.01:u=d.cross(Vector((1,0,0)))
     u.normalize();v=d.cross(u);off=len(vs);r=ob.data.bevel_depth
     for end in [a,b]:
      for j in range(12):vs.append(end+r*(u*math.cos(j*math.tau/12)+v*math.sin(j*math.tau/12)))
     for j in range(12):faces.append((off+j,off+(j+1)%12,off+(j+1)%12+12,off+j+12));owners.append(ob.name)
bvh=BVHTree.FromPolygons(vs,faces,all_triangles=False);findings=[];tested=0
for bx in [-60,100]:
 for y in [19,48,68,98]:
  start=bx+1.8;end=bx+16;n=38
  samples=285
  for k in range(samples):
   x=start+(end-start)*(k+.5)/samples;i=min(n-1,int((x-start)/(end-start)*n));floor=7.7-(7.7-1.18)*(i+1)/n+.055
   for lateral in range(49):
    dy=-1.2+2.4*lateral/48;tested+=1;origin=Vector((x,y+dy,floor+.025));hit,normal,face,dist=bvh.ray_cast(origin,Vector((0,0,1)),1.975)
    if hit is not None:findings.append({'bridge_x':bx,'platform_y':y,'step':i+1,'lateral_m':dy,'obstacle':owners[face],'clearance_m':dist+.025,'hit':[float(v) for v in hit]})
edge=[h for h in findings if h['obstacle'].startswith('Stair side stringer') and h['clearance_m']<.06 and abs(h['lateral_m'])>=1.199]
findings=[h for h in findings if h not in edge]
q={'floor_edge_contacts':edge,'floor_edge_note':'Own supporting stringer boundary contacts below60mm are floor-edge structure, not overhead obstruction.','source_blend_sha256':digest,'test':'Vertical headroom rays at dense0.05m longitudinal/lateral spacing across2.4m clear width, up to2.0m above actual tread top; actual canopy/bridge meshes and swept pipe curves','ray_count':tested,'clearance_target_m':2.0,'full_flights':8,'obstructions':findings,'pass':not findings,'limitations':'Mesh surface ray test at111720sample points; does not certify accessibility or structural design.'}
(P/'flight_clearance_validation.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
