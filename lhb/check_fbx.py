import bpy,json,os
from mathutils import Vector
P=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=P+'/LHB_3A_prototype.fbx')
obs=list(bpy.context.scene.objects);corners=[o.matrix_world@Vector(c) for o in obs if o.type=='MESH' for c in o.bound_box]
r={'roundtrip_import':'PASS','object_count':len(obs),'mesh_count':sum(o.type=='MESH' for o in obs),'presentation_objects':sum(o.name.startswith('DISPLAY_') for o in obs),'bounds_m':{'min':[min(v[i] for v in corners) for i in range(3)],'max':[max(v[i] for v in corners) for i in range(3)]},'evaluated_export_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs if o.type=='MESH')}
assert r['presentation_objects']==0
open(P+'/fbx_validation.json','w').write(json.dumps(r,indent=2));print(r)
