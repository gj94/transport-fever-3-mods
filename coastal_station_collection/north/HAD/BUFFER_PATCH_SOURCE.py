import bpy,json,sys,hashlib,math
from pathlib import Path
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));fix=json.load(open(P/'references/bufferstop_correction.json'));x,y=fix['source_endpoint_xy'];dx,dy=fix['translation_xy'];changed=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('01 | Mapped railway infrastructure / '):continue
 if not any(o.name.endswith(s)for s in ['railweb','red','white']):continue
 count=0
 for v in o.data.vertices:
  if math.hypot(v.co.x-x,v.co.y-y)<3:
   v.co.x+=dx;v.co.y+=dy;count+=1
 if count:changed.append({'object':o.name,'vertices_moved':count})
assert changed and sum(r['vertices_moved']for r in changed)==32,changed
out=P/'HAD_coastal_station_v02.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);q.update({'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'bufferstop_patch':{'source_blend_sha256':sha,'source_blend_file':src.name,'changed_objects':changed,'translation_xy':fix['translation_xy'],'retreat_m':fix['retreat_m'],'all_other_geometry_unchanged':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('BUFFER_PATCH_DONE',q['blend_sha256'],changed)
