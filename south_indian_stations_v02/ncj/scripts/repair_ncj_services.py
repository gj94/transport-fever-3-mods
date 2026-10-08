"""Bury longitudinal utility crossings beneath track formation; no raised trench walls across sleepers."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
raw=json.loads((R/'references/local_geometry.json').read_text());segments=[]
for w in raw:
 if w['tags'].get('railway')=='rail':
  pts=[Vector((x+45,y)) for x,y in w['local']];segments.extend(zip(pts,pts[1:]))
def distance(p):
 p=Vector(p);best=1e9
 for a,b in segments:
  d=b-a;t=max(0,min(1,(p-a).dot(d)/max(1e-9,d.dot(d))));best=min(best,(p-a-t*d).length)
 return best
moved=0
for o in list(s.objects):
 if o.type!='MESH':continue
 if o.name.startswith(('Cable trough concrete lids','Drain crossing grate')) and len(o.data.vertices)%8==0:
  for k in range(0,len(o.data.vertices),8):
   vv=o.data.vertices[k:k+8];p=sum((v.co for v in vv),Vector())/8
   if distance((p.x,p.y))<2.8:
    for v in vv:v.co.z-=.75
    moved+=1
 elif o.name.startswith('Cable inspection chamber') and distance((o.location.x,o.location.y))<2.8:o.location.z-=.75;moved+=1
 elif o.name.startswith(('Open longitudinal drain invert','Drain side wall')):bpy.data.objects.remove(o,do_unlink=True)
C=bpy.data.collections.new('39_SERVICE_CULVERT_CROSSINGS');s.collection.children.link(C);C['scope']='Inferred utility alignment; all proximity crossings explicitly depressed beneath track formation.'
M=bpy.data.materials['Weathered concrete'];D=bpy.data.materials['Drain algae'];verts={};faces={}
def box(p,sz,m):
 v,f=verts.setdefault(m.name,[]),faces.setdefault(m.name,[]);k=len(v);x,y,z=[q/2 for q in sz]
 v.extend([(p[0]+a,p[1]+b,p[2]+c) for a,b,c in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]]);f.extend([tuple(k+j for j in q) for q in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]])
culverts=[]
for yy in [9,117]:
 for x in range(-670,510,4):
  buried=min(distance((xx,yy)) for xx in [x-2,x,x+2])<2.9;drop=.85 if buried else 0
  box((x,yy,-.02-drop),(3.995,.65,.08),D)
  for dy in [-.4,.4]:box((x,yy+dy,.08-drop),(3.995,.15,.32),M)
  if buried:
   box((x,yy,-.49),(3.995,1,.16),M);culverts.append([x,yy])
for mn,vs in verts.items():
 d=bpy.data.meshes.new('Drain interrupted below railway '+mn);d.from_pydata(vs,[],faces[mn]);d.update();o=bpy.data.objects.new(d.name,d);C.objects.link(o);d.materials.append(bpy.data.materials[mn])
(R/'QA_SERVICE_CROSSINGS.json').write_text(json.dumps({'buried_trough_or_grate_components':moved,'buried_culvert_segments':culverts,'crossing_cover_top_m':-.41,'sleeper_bottom_m':.21,'status':'Generic utility culverts reconstructed; no visible raised longitudinal walls across rail sleepers'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'),compress=True);print('SERVICE_CULVERTS_SAVED',moved,len(culverts))
