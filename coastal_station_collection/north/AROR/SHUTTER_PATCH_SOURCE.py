import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(sys.argv[sys.argv.index('--')+1]).resolve();q=json.load(open(P/'QA_BUILD.json'));src=P/q['blend_file'];sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));changed=[]
for o in bpy.context.scene.objects:
 if not o.name.startswith('Aroor hinged wooden shutter'):continue
 angle=o.rotation_euler.z;center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices);rot=Matrix.Rotation(angle,3,'Z')
 for v in o.data.vertices:v.co=center+rot@(v.co-center)
 o.rotation_euler=(0,0,0);changed.append({'object':o.name,'hinged_leaf_center':list(center),'rotation_radians':angle})
assert changed
out=P/'AROR_coastal_station_v02.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);q.update({'blend_file':out.name,'blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'blend_bytes':out.stat().st_size,'shutter_patch':{'source_blend_sha256':sha,'source_blend_file':src.name,'reason':'Wood shutter geometry was rotated about global origin; now each leaf rotates about its own window center.','changed_objects':changed,'all_other_geometry_unchanged':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}});(P/'QA_BUILD.json').write_text(json.dumps(q,indent=2));print('AROR_SHUTTERS_FIXED',q['blend_sha256'],len(changed))
