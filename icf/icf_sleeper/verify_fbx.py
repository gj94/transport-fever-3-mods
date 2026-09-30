import bpy, os, json
from mathutils import Vector
D=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(D,'icf_sleeper_prototype.fbx'))
bpy.context.view_layer.update()
vs=[o.matrix_world@Vector(v) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.bound_box]
lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
names={o.name for o in bpy.context.scene.objects}
checks={'roundtrip_bounds_m':{'min':lo,'max':hi},'mesh_count':sum(o.type=='MESH' for o in bpy.context.scene.objects),'length_m':hi[0]-lo[0],'max_z_m':hi[2],'pivots_present':all(n in names for n in ['BOGIE_1_PIVOT','BOGIE_2_PIVOT','BOGIE_1_AXLE_1_ROTATE_Y','BOGIE_1_AXLE_2_ROTATE_Y','BOGIE_2_AXLE_1_ROTATE_Y','BOGIE_2_AXLE_2_ROTATE_Y'])}
assert abs(checks['length_m']-22.297)<.001,checks
assert abs(checks['max_z_m']-4.025)<.001,checks
assert checks['pivots_present'],checks
checks['passed']=True
open(os.path.join(D,'fbx_validation.json'),'w').write(json.dumps(checks,indent=2));print(checks)
