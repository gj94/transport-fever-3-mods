"""Add only the source-supported northeast boarding strip; keep all other station objects in place."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B/'revision_02/mqu';src=B/'mqu/MQU_station_v01.blend';h0=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));S=bpy.context.scene;D=json.loads((R/'source/layout.json').read_text());rec=json.loads((R/'source/evidence/MQU_boarding_edge_adoption.json').read_text());old=rec['previous_adopted_polygon'];new=rec['adopted_polygon'];pid=rec['platform_id'];changed=[]
def segdist(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/max(1e-12,dx*dx+dy*dy)));return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def boundarydist(p):return min(segdist(p,a,b) for a,b in zip(old,old[1:]))
def section(poly,x):
 yy=[a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]) for a,b in zip(poly,poly[1:]) if min(a[0],b[0])<=x<max(a[0],b[0]) and abs(a[0]-b[0])>1e-8];return (min(yy),max(yy)) if len(yy)>1 else None
pm=next(p for p in json.loads((R/'source/platform_mesh.json').read_text()) if p['id']==pid)
for name,vs,fs in [('Platform body '+pid,pm['vertices'],pm['faces']),('Platform top '+pid,[(x,y,.964) for x,y in new[:-1]],[list(range(len(new)-1))])]:
 o=S.objects[name];mats=list(o.data.materials);me=bpy.data.meshes.new(name+' completed');me.from_pydata(vs,[],fs);me.update()
 for m in mats:me.materials.append(m)
 o.data=me;changed.append(name)
removed={}
for o in list(S.objects):
 stride=8 if o.name.startswith('Platform white coping fascia') else 16 if o.name.startswith('Yellow platform safety edge') else 0
 if not stride:continue
 erase=set()
 for j in range(0,len(o.data.vertices),stride):
  ids=list(range(j,min(j+stride,len(o.data.vertices))));p=sum((o.data.vertices[k].co for k in ids),Vector())/len(ids)
  if boundarydist((p.x,p.y))<.16:erase.update(ids)
 if not erase:continue
 vs=[];mapping={}
 for v in o.data.vertices:
  if v.index not in erase:mapping[v.index]=len(vs);vs.append(tuple(v.co))
 fs=[tuple(mapping[i] for i in p.vertices) for p in o.data.polygons if not any(i in erase for i in p.vertices)];mats=list(o.data.materials);me=bpy.data.meshes.new(o.name+' retained');me.from_pydata(vs,[],fs);me.update()
 for m in mats:me.materials.append(m)
 o.data=me;removed[o.name]=len(erase)//stride
# Extend existing paving joints; fixtures and bridge landings remain at their verified positions.
joints=0
for o in S.objects:
 if not o.name.startswith('Platform transverse paving joint'):continue
 for j in range(0,len(o.data.vertices),8):
  ids=list(range(j,min(j+8,len(o.data.vertices))));p=sum((o.data.vertices[k].co for k in ids),Vector())/len(ids);s=section(old,p.x);n=section(new,p.x)
  if s and n and s[0]-.01<=p.y<=s[1]+.01:
   for k in ids:o.data.vertices[k].co.y=n[0]+.10 if o.data.vertices[k].co.y<p.y else n[1]-.10
   joints+=1
 o.data.update()
F=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];batches={}
def box(name,p,size,material,ang):
 vs,fs=batches.setdefault((name,material),([],[]));k=len(vs);co,si=math.cos(ang),math.sin(ang)
 for xx,yy,zz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
  x,y=xx*size[0]/2,yy*size[1]/2;vs.append((p[0]+x*co-y*si,p[1]+x*si+y*co,p[2]+zz*size[2]/2))
 fs.extend(tuple(k+i for i in f) for f in F)
def beam(a,b):
 a,b=Vector(a),Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1)));v.normalize();w=u.cross(v);vs,fs=batches.setdefault(('MQU completed yellow platform safety edge','yellow'),([],[]));k=len(vs)
 for p in [a,b]:
  for i in range(8):vs.append(tuple(p+.043*(v*math.cos(i*math.tau/8)+w*math.sin(i*math.tau/8))))
 fs.extend([tuple(k+i for i in range(7,-1,-1)),tuple(k+i for i in range(8,16))]+[(k+i,k+(i+1)%8,k+(i+1)%8+8,k+i+8) for i in range(8)])
for a,b in zip(new,new[1:]):
 dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
 if L<3:continue
 ang=math.atan2(dy,dx);n=max(1,int(L/1.5))
 for j in range(n):
  t=(j+.5)/n;box('MQU completed platform coping',(a[0]+dx*t,a[1]+dy*t,.83),(L/n-.02,.12,.24),'white' if j%5 else 'red',ang)
 beam((a[0],a[1],.985),(b[0],b[1],.985))
for (name,material),(vs,fs) in batches.items():
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials[material]);ob=bpy.data.objects.new(name,me);S.collection.objects.link(ob)
Q=json.loads((R/'QA_BUILD.json').read_text());Q['platform_bounds'][pid]=[min(p[0] for p in new),min(p[1] for p in new),max(p[0] for p in new),max(p[1] for p in new)];Q['boarding_edge_repair']={'platform_id':pid,'added_surface_area_m2':rec['added_surface_area_m2'],'objects_kept_in_place':'All rails, furniture, bridge, building, interior, paths and cameras','removed_old_coping_components':removed,'extended_paving_joint_components':joints};Q['objects']=len(S.objects);Q['meshes']=len([o for o in S.objects if o.type=='MESH']);Q['vertices']=sum(len(o.data.vertices) for o in S.objects if o.type=='MESH');Q['polygons']=sum(len(o.data.polygons) for o in S.objects if o.type=='MESH');(R/'QA_BUILD.json').write_text(json.dumps(Q,indent=2));dest=R/'MQU_station_v01.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True);h1=hashlib.sha256(dest.read_bytes()).hexdigest();(R/'QA_BOARDING_EDGE_REPAIR.json').write_text(json.dumps({'input_source_sha256':h0,'output_source_sha256':h1,**Q['boarding_edge_repair']},indent=2));prov=json.loads((R/'RENDER_PROVENANCE.json').read_text());prov['current_source_scene_sha256']=h1;(R/'RENDER_PROVENANCE.json').write_text(json.dumps(prov,indent=2));(R/'REPAIR_LINEAGE.json').write_text(json.dumps({'station':'MQU','input_source_sha256':h0,'output_source_sha256':h1,'retained_views':[],'rerender_prefixes':['01','02','03','04','05'],'scope':'Conservative full-gallery refresh after additive platform edge completion; all non-platform objects kept in place'},indent=2));print('REPAIRED',h1,removed,joints,flush=True)
