"""Remove reconstructed decorative/furniture obstructions from real entry gaps; preserve hut architecture."""
import bpy,json,sys,hashlib,ast,math
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));CODE=q['station_code'];assert CODE in ['CHPD','TMPY'];src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));sc=bpy.context.scene;D=json.load(open(P/'references/plan.json'));bx,by=D['main_building']['center'];SIDE=D['main_building']['public_side'];DEP=max(7,D['main_building']['width']);LEN=max(12,D['main_building']['length']);changed=[]
for col in bpy.data.collections:
 if not col.name.startswith('04 |'):continue
 for ob in list(col.objects):
  if ob.type!='MESH':continue
  if CODE=='CHPD'and not ob.name.endswith('/ peach'):continue
  if CODE=='TMPY'and not any(ob.name.endswith('/ '+m)for m in ['red','stone']):continue
  me=ob.data;parent=list(range(len(me.vertices)))
  def find(a):
   while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
   return a
  for e in me.edges:
   a,b=e.vertices;ra,rb=find(a),find(b)
   if ra!=rb:parent[rb]=ra
  groups={}
  for v in me.vertices:groups.setdefault(find(v.index),[]).append(v.index)
  remove=set();parts=[]
  for ids in groups.values():
   vs=[me.vertices[i].co for i in ids];center=sum(vs,Vector())/len(vs);u=center.y-by;v=(center.x-bx)*SIDE;z=center.z;du=max(t.y for t in vs)-min(t.y for t in vs);dz=max(t.z for t in vs)-min(t.z for t in vs)
   match=False
   if CODE=='CHPD':match=abs(u)<.01 and abs(abs(v)-(DEP/2+.16))<.01 and abs(z-1.85)<.01 and abs(du-LEN)<.02 and abs(dz-.8)<.01
   else:
    at_v=abs(v-(DEP/2+1.0))<.01
    match=at_v and ((abs(u-.4)<.01 and abs(z-1.95)<.01 and abs(du-2.7)<.01)or(any(abs(u-t)<.01 for t in[-.6,1.4])and abs(z-1.70)<.01 and abs(du-.3)<.01))
   if match:remove.update(ids);parts.append({'center_local_uvz':[u,v,z],'vertices':len(ids)})
  if remove:
   keep=[v for v in me.vertices if v.index not in remove];imap={v.index:i for i,v in enumerate(keep)};new=bpy.data.meshes.new(me.name+' clear entry');new.from_pydata([tuple(v.co)for v in keep],[],[tuple(imap[i]for i in f.vertices)for f in me.polygons if not any(i in remove for i in f.vertices)]);new.update()
   for m in me.materials:new.materials.append(m)
   ob.data=new;changed.append({'object':ob.name,'removed_vertices':len(remove),'parts':parts})
assert sum(x['removed_vertices']for x in changed)==(16 if CODE=='CHPD'else 24),changed
if CODE=='CHPD':
 COL=None;CAT=None;BATCH={};master=P/'BUILD_SOURCE.py';tree=ast.parse(master.read_text());names={'coll','mesh','batchgeom','box','loc','b0'};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(master),'exec'));coll('04B | Cheppad lower band respects entry gap');M=bpy.data.materials['peach'];EH=1.7
 for v in[-DEP/2-.16,DEP/2+.16]:
  for sg in[-1,1]:le=LEN/2-EH;u=sg*(EH+le/2);b0('Salmon band beside entrance',u,v,1.85,le,.08,.8,M)
 for(cat,mn),g in BATCH.items():COL=g['col'];mesh(cat+' / '+mn,g['v'],g['f'],g['m'])
out=P/(CODE+'_coastal_station_v02.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);q.update({'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'object_count':len(sc.objects),'mesh_objects':sum(o.type=='MESH'for o in sc.objects),'mesh_vertices':sum(len(o.data.vertices)for o in sc.objects if o.type=='MESH'),'mesh_faces':sum(len(o.data.polygons)for o in sc.objects if o.type=='MESH'),'entry_clearance_patch':{'source_blend_sha256':sha,'source_blend_file':src.name,'changed_components':changed,'details':'Decorative lower band split at the actual entrance gap.'if CODE=='CHPD'else'Removed generic reconstructed bench and two pedestals from the tiny photographed porch landing; hut, canopy, steps and interior furniture retained.','all_other_geometry_unchanged':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('ENTRY_CLEARED',CODE,q['blend_sha256'])
