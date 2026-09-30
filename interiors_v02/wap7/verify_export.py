import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(P/'WAP7_interiors_v02.fbx'))
objs=list(bpy.context.scene.objects);mesh=[o for o in objs if o.type=='MESH'];bounds=[]
for o in mesh:
 bounds.extend(o.matrix_world@Vector(v) for v in o.bound_box)
report={'fbx_objects':len(objs),'fbx_meshes':len(mesh),'fbx_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in mesh),'bounds_min':[min(v[i] for v in bounds) for i in range(3)],'bounds_max':[max(v[i] for v in bounds) for i in range(3)],'six_axles':sorted(o.name for o in objs if o.name.startswith('AXLE_')),'two_bogies':sorted(o.name for o in objs if o.name.startswith('BOGIE_')),'axle_world_centres':{o.name:list(o.matrix_world.translation) for o in objs if o.name.startswith('AXLE_')},'two_interiors':sorted(o.name for o in objs if o.name.endswith('_INTERIOR')),'cameras_exported':sum(o.type=='CAMERA' for o in objs),'lights_exported':sum(o.type=='LIGHT' for o in objs),'nonfinite_vertex_count':sum(not all(math.isfinite(c) for c in v.co) for o in mesh for v in o.data.vertices),'texture_images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.type=='IMAGE']}
assert len(report['six_axles'])==6 and len(report['two_bogies'])==2 and len(report['two_interiors'])==2
assert report['cameras_exported']==report['lights_exported']==report['nonfinite_vertex_count']==0
assert len(report['texture_images'])==2 and all(t['size'][0]>0 for t in report['texture_images'])
(P/'fbx_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
