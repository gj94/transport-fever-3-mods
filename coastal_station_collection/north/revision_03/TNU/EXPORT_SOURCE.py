import bpy,sys,json,hashlib,time,struct,math
from pathlib import Path
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));(P/'exports').mkdir(exist_ok=True);exports=[];inventories=[]
for key,name in [('historical_scene_name','TNU_historical_2016_unplaced'),('mapped_scene_name','TNU_mapped_corridor_unverified_remnants')]:
 s=bpy.data.scenes[q[key]];bpy.context.window.scene=s;bpy.ops.object.select_all(action='DESELECT');coords=[];meshes=[]
 for o in s.objects:
  if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
  if o.type=='MESH':
   meshes.append(o)
   coords.extend([tuple(o.matrix_world@v.co)for v in o.data.vertices])
 assert all(math.isfinite(x)for c in coords for x in c)
 inv={'scene':s.name,'unit_system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'objects':len(s.objects),'meshes':len(meshes),'vertices':sum(len(o.data.vertices)for o in meshes),'bounds_min':[min(c[i]for c in coords)for i in range(3)],'bounds_max':[max(c[i]for c in coords)for i in range(3)],'georeferenced':key=='mapped_scene_name','finite':True,'no_stock_name_candidates':[o.name for o in s.objects if any(x in o.name.lower()for x in ['locomotive','wagon','trainset','rolling stock'])]};inventories.append(inv)
 if key=='historical_scene_name':
  from mathutils import Vector
  hit,location,normal,index,obj,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((0,-8,1.8)),Vector((0,1,0)),distance=13);inv['central_entry_ray']={'clear':not hit,'hit_object':obj.name if hit else None};assert not hit
 out=P/'exports'/(name+'.glb');t=time.time();bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True,export_yup=True);b=out.read_bytes();magic,ver,length=struct.unpack('<4sII',b[:12]);assert magic==b'glTF'and ver==2 and length==len(b);jl=struct.unpack('<I',b[12:16])[0];j=json.loads(b[20:20+jl]);assert len(j.get('scenes',[]))==1 and j['scenes'][0]['name']==s.name;expected={o.name for o in s.objects if o.type in {'MESH','CURVE','FONT'}};assert all(n.get('name')in expected for n in j.get('nodes',[]));exports.append({'scene':s.name,'export':str(out.relative_to(P)),'export_sha256':hashlib.sha256(b).hexdigest(),'export_bytes':len(b),'source_blend_sha256':sha,'images_embedded':all('bufferView'in x for x in j.get('images',[])),'external_uris':[x.get('uri')for x in j.get('buffers',[])+j.get('images',[])if x.get('uri')],'valid_header_and_json':True,'scene_isolation':{'scene_count':len(j['scenes']),'scene_name':j['scenes'][0]['name'],'node_count':len(j.get('nodes',[])),'all_nodes_from_intended_scene':True},'seconds':round(time.time()-t,2)})
r=exports[0].copy();r.update({'source_blend':src.name,'source_unchanged':sha==hashlib.sha256(src.read_bytes()).hexdigest(),'additional_exports':exports[1:]});(P/'QA_EXPORT.json').write_text(json.dumps(r,indent=2));(P/'QA_SCENE.json').write_text(json.dumps({'source_blend_sha256':sha,'scenes':inventories,'all_packed_images':all(i.packed_file or i.source in {'GENERATED','VIEWER'}for i in bpy.data.images),'status':'Two-scene inspection: closed historical study unplaced; separate mapped corridor.'},indent=2));print('TNU_EXPORT_DONE',r)
