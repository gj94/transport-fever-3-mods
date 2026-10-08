import bpy,sys,json,hashlib,time,struct,zipfile,os
from pathlib import Path
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();src=P/json.load(open(P/'QA_BUILD.json'))['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type in {'MESH','CURVE','FONT'}:o.select_set(True)
(P/'exports').mkdir(exist_ok=True);out=P/'exports'/(src.stem+'.glb');t=time.time();bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_extras=True,export_yup=True)
b=out.read_bytes();ml,ver,length=struct.unpack('<4sII',b[:12]);assert ml==b'glTF' and ver==2 and length==len(b);jl=struct.unpack('<I',b[12:16])[0];j=json.loads(b[20:20+jl]);a=j.get('accessors',[])
r={'source_blend':src.name,'source_blend_sha256':sha,'source_unchanged':sha==hashlib.sha256(src.read_bytes()).hexdigest(),'export':str(out.relative_to(P)),'export_sha256':hashlib.sha256(b).hexdigest(),'export_bytes':len(b),'export_seconds':round(time.time()-t,2),'gltf_version':j['asset']['version'],'meshes':len(j.get('meshes',[])),'nodes':len(j.get('nodes',[])),'materials':len(j.get('materials',[])),'images_embedded':all('bufferView' in x for x in j.get('images',[])),'external_uris':[x.get('uri') for x in j.get('buffers',[])+j.get('images',[]) if x.get('uri')],'valid_header_and_json':True}
(P/'QA_EXPORT.json').write_text(json.dumps(r,indent=2));print('EXPORT_COMPLETE',json.dumps(r),flush=True)
