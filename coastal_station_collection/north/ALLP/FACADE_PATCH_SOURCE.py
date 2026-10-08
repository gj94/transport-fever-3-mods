import bpy,sys,json,math,hashlib,ast
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));sc=bpy.context.scene;D=json.load(open(P/'references/plan.json'));bx,by=D['main_building']['center'];DEP=D['main_building']['width'];SIDE=D['main_building']['public_side'];COL=None;CAT=None;BATCH={};M={'ivory':bpy.data.materials['ivory']};master=P/'BUILD_SOURCE.py';tree=ast.parse(master.read_text());names={'coll','mesh','batchgeom','box','beam','loc','b0','be0'};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(master),'exec'));changed=[]
for o in sc.objects:
 if o.name=='Alappuzha raised-name panel':
  o.location.x+=SIDE*.45;changed.append({'object':o.name,'translation_x':SIDE*.45})
for col in list(bpy.data.collections):
 if not col.name.startswith('04 |'):continue
 for ob in list(col.objects):
  if ob.type!='MESH' or not any(ob.name.endswith('/ '+m)for m in ['glass','wood','dark','ivory']):continue
  me=ob.data;parent=list(range(len(me.vertices)))
  def find(a):
   while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
   return a
  for e in me.edges:
   a,b=e.vertices;ra,rb=find(a),find(b)
   if ra!=rb:parent[rb]=ra
  groups={}
  for v in me.vertices:groups.setdefault(find(v.index),[]).append(v.index)
  remove=set()
  for ids in groups.values():
   vs=[me.vertices[i].co for i in ids];us=[v.y-by for v in vs];vvs=[(v.x-bx)*SIDE for v in vs];uc=sum(us)/len(us)
   if min(vvs)>DEP/2-.10 and max(vvs)<DEP/2+.30 and any(abs(uc-c)<1.90 for c in[-9.5,9.5]) and min(v.z for v in vs)>1.90 and max(v.z for v in vs)<4.35:remove.update(ids)
  if remove:
   keep=[v for v in me.vertices if v.index not in remove];imap={v.index:i for i,v in enumerate(keep)};new=bpy.data.meshes.new(me.name+' screened bays');new.from_pydata([tuple(v.co)for v in keep],[],[tuple(imap[i]for i in f.vertices)for f in me.polygons if not any(i in remove for i in f.vertices)]);new.update()
   for m in me.materials:new.materials.append(m)
   ob.data=new;changed.append({'object':ob.name,'removed_screen_bay_vertices':len(remove)})
coll('04A | Alappuzha photo-derived perforated screen bays')
for pu in[-9.5,9.5]:
 pv=DEP/2+.20
 for du in[-1.62,1.62]:b0('Screen border',pu+du,pv,3.30,.13,.15,1.72,M['ivory'])
 for z in[2.44,4.16]:b0('Screen border',pu,pv,z,3.37,.15,.13,M['ivory'])
 for a in range(7):
  for b in range(4):
   u=pu+(a-3)*.45;z=2.65+b*.43
   for da,db in[((-.20,0),(0,.19)),((0,.19),(.20,0)),((.20,0),(0,-.19)),((0,-.19),(-.20,0))]:be0('Cream geometric perforated block',(u+da[0],pv,z+da[1]),(u+db[0],pv,z+db[1]),.080,M['ivory'])
for(cat,mn),g in BATCH.items():COL=g['col'];mesh(cat+' / '+mn,g['v'],g['f'],g['m'])
out=P/'ALLP_coastal_station_v02.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);q.update({'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'facade_refinement':{'source_blend_sha256':sha,'source_blend_file':src.name,'details':'Upper station-name panel moved clear of projecting slab; two screened bays replace generic panes with perforated geometry.','changed_existing_objects':changed,'all_other_geometry_unchanged':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('ALLP_PATCH_DONE',q['blend_sha256'],changed)
