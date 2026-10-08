"""Path-following maintenance pits; original straight-chord obstructions removed.
Pit assignments are explicitly reconstructed. Clear segments avoid all mapped switch nodes.
"""
import bpy,sys,os,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,os.environ.get('NCJ_SHAPELY_PATH',str(Path(__file__).resolve().parents[1]/'.build_deps/shapely')))
import shapely
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
for o in list(s.objects):
 if o.name.startswith(('Inspection pit dark invert','Pit reinforced concrete retaining wall','Maintenance side walkway','Depot water riser','Depot watering hose')):bpy.data.objects.remove(o,do_unlink=True)
C=bpy.data.collections.new('41_PATH_FOLLOWING_MAINTENANCE_PITS');s.collection.children.link(C);C['scope']='Five inferred maintenance assignments, true mapped path normals and all-track collision filtering; no surveyed NCJ pit-number claim.'
raw=json.loads((R/'references/local_geometry.json').read_text());all_lines={w['id']:LineString([(x+45,y) for x,y in w['local']]) for w in raw if w['tags'].get('railway')=='rail'};allunion=unary_union(list(all_lines.values()));junctions=[Point(p) for p in json.loads((R/'references/junction_node_positions.json').read_text()).values()]
GREY=bpy.data.materials['Weathered concrete'];DARK=bpy.data.materials['Deep interior shadow'];BLUE=bpy.data.materials['Railway blue painted steel'];METAL=bpy.data.materials['Polished stainless fixtures'];BLACK=bpy.data.materials['Tyre rubber and vinyl'];B=bpy.data.materials['Angular granite ballast'];batches={}
F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def box(n,p,sz,m,theta=0):
 vs,fs=batches.setdefault((n,m.name),([],[]));k=len(vs);u=Vector((math.cos(theta),math.sin(theta),0));v=Vector((-u.y,u.x,0));p=Vector(p)
 vs.extend([p+u*(a*sz[0]/2)+v*(b*sz[1]/2)+Vector((0,0,c*sz[2]/2)) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]);fs.extend(tuple(k+j for j in f) for f in F)
def tube(n,pts,r,m):
 d=bpy.data.curves.new(n,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=0;sp=d.splines.new('POLY');sp.points.add(len(pts)-1)
 for a,b in zip(sp.points,pts):a.co=(*b,1)
 o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(m)
pitdomains=[];report=[];walkclear=[];riserclear=[]
for wid in ['514385386','514385387','514385388','1302623382','1302623383']:
 line=all_lines[wid];accepted=[];length=0;segments=0
 for j in range(int((line.length-140)/3)):
  d=70+j*3;a=line.interpolate(d);b=line.interpolate(min(line.length-70,d+3));mid=line.interpolate(d+1.5)
  if any(mid.distance(p)<60 for p in junctions):continue
  # No inspection pit through any unrelated centreline or turnout throat.
  others=[l for k,l in all_lines.items() if k!=wid]
  if min(mid.distance(l) for l in others)<2.2:continue
  ax,ay=a.x,a.y;bx,by=b.x,b.y;theta=math.atan2(by-ay,bx-ax);nx,ny=-math.sin(theta),math.cos(theta);L=math.hypot(bx-ax,by-ay);mx,my=(ax+bx)/2,(ay+by)/2
  seg=LineString([(ax,ay),(bx,by)]);pitdomains.append(seg.buffer(.57,cap_style='flat',join_style='mitre'));length+=L;segments+=1
  box('Open inspection pit bottom '+wid,(mx,my,-.55),(L+.012,1.14,.12),DARK,theta)
  for side in [-1,1]:
   wx,wy=mx+nx*side*.66,my+ny*side*.66;box('Curved path pit retaining wall '+wid,(wx,wy,-.06),(L+.01,.18,.88),GREY,theta)
   wx,wy=mx+nx*side*1.75,my+ny*side*1.75
   pp=Point(wx,wy);clear=min(pp.distance(l) for l in all_lines.values())
   if clear>1.33:
    box('Collision-cleared maintenance walk '+wid,(wx,wy,.30),(L+.01,.48,.20),GREY,theta);walkclear.append(clear)
   if j%4==0 and clear>1.3:
    tube('Rail-clear depot watering riser',[(wx,wy,.32),(wx,wy,1.0)],.022,BLUE);tube('Rail-clear watering hose',[(wx,wy,1),(wx+nx*.12,wy+ny*.12,1.08),(wx+nx*.25,wy+ny*.25,.47)],.025,BLACK);riserclear.append(clear)
  if j%30==0:
   for side in [-1,1]:tube('Pit access ladder stile',[(mx+nx*side*.2,my+ny*side*.2,-.5),(mx+nx*side*.2,my+ny*side*.2,.38)],.022,METAL)
   for zz in [-.3,0,.3]:tube('Pit ladder rung',[(mx-nx*.2,my-ny*.2,zz),(mx+nx*.2,my+ny*.2,zz)],.018,METAL)
 report.append({'source_road':wid,'clear_inspection_length_m':length,'sections_3m':segments,'assignment':'Reconstructed facility on mapped road; actual pit number unknown'})
# Excavate the actual ballast mesh, leaving the visible dark bottom below ground rather than a painted slot.
region=unary_union(pitdomains)
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for h in g.geoms for p in polygons(h)] if hasattr(g,'geoms') else []
def append_poly(p,z0,z1,vs,fs):
 for poly in polygons(p):
  for tri in shapely.constrained_delaunay_triangles(poly).geoms:
   coords=list(tri.exterior.coords)[:3];k=len(vs);vs.extend([(x,y,z)for z in [z0,z1]for x,y in coords]);fs.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
  for ring in [poly.exterior]+list(poly.interiors):
   ps=list(ring.coords)
   for a,b in zip(ps,ps[1:]):k=len(vs);vs.extend([(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)]);fs.append((k,k+1,k+2,k+3))
for o in list(s.objects):
 if o.type!='MESH' or not o.name.startswith('Granite ballast formation'):continue
 vv=[o.matrix_world@v.co for v in o.data.vertices];vs=[];fs=[]
 # Compound clipping may already have triangulated this batch. In that case preserve its
 #outside-junction faces and remove only triangles whose centres lie inside pit corridor.
 if 'compound corrected' in o.data.name or len(vv)%8:
  d=o.data
  for poly in d.polygons:
   points=[vv[i] for i in poly.vertices]
   if max(p.z for p in points)-min(p.z for p in points)<.0001:
    footprint=Polygon([(p.x,p.y) for p in points])
    if not footprint.is_valid:footprint=footprint.buffer(0)
    for part in polygons(footprint.difference(region)):
     for tri in shapely.constrained_delaunay_triangles(part).geoms:
      coords=list(tri.exterior.coords)[:3];k=len(vs);vs.extend([(x,y,points[0].z)for x,y in coords]);fs.append((k,k+1,k+2))
   else:
    k=len(vs);vs.extend(points);fs.append(tuple(k+j for j in range(len(points))))
 else:
  for i in range(0,len(vv),8):
   q=vv[i:i+8];p=Polygon([(q[j].x,q[j].y) for j in [0,4,6,2]])
   if not p.is_valid:p=p.buffer(0)
   if not region.intersects(p):k=len(vs);vs.extend(q);fs.extend(tuple(k+j for j in f) for f in F)
   else:append_poly(p.difference(region),min(v.z for v in q),max(v.z for v in q),vs,fs)
 d=bpy.data.meshes.new(o.name+' excavated');d.from_pydata(vs,[],fs);d.update();d.materials.append(B);o.data=d;o.matrix_world.identity()
# Also excavate the underlying site slab so the pit has real visible depth.
for o in list(s.objects):
 if not o.name.startswith('Full metre-scale site ground') or o.type!='MESH':continue
 vv=[o.matrix_world@v.co for v in o.data.vertices];x0,x1=min(p.x for p in vv),max(p.x for p in vv);y0,y1=min(p.y for p in vv),max(p.y for p in vv);terrain=Polygon([(x0,y0),(x1,y0),(x1,y1),(x0,y1)]).difference(region);vs=[];fs=[];append_poly(terrain,min(p.z for p in vv),max(p.z for p in vv),vs,fs)
 d=bpy.data.meshes.new('Site ground with excavated inspection pits');d.from_pydata(vs,[],fs);d.update();d.materials.append(o.data.materials[0]);o.data=d;o.matrix_world.identity()
for (n,mn),(vs,fs) in batches.items():
 d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(n,d);C.objects.link(o);d.materials.append(bpy.data.materials[mn])
qa={'facilities':report,'minimum_walkway_centre_to_any_rail_centreline_m':min(walkclear) if walkclear else None,'walkway_halfwidth_m':.24,'minimum_riser_centre_to_any_rail_centreline_m':min(riserclear) if riserclear else None,'pit_bottom_m':-.49,'avoid_junction_radius_m':60,'original_straight_chord_services_removed':True}
assert len(report)==5 and all(q['clear_inspection_length_m']>100 for q in report), 'Pit coverage unexpectedly incomplete'
(R/'QA_PIT_SERVICES.json').write_text(json.dumps(qa,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True);print('PIT_SERVICES_REPAIRED',json.dumps(qa),flush=True)
