import bpy,os,json
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT,'WAP7_prototype.blend'))
a=bpy.data.collections['WAP7_ASSET'];bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
pts=[];tris=0
for o in a.objects:
 if o.type=='MESH':
  ev=o.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);pts.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
r=json.load(open(os.path.join(OUT,'geometry_report.json')));r.update({'evaluated_triangles':tris,'bounds_m':{'min':lo,'max':hi,'span':[hi[i]-lo[i] for i in range(3)]},'axle_world_centres':{o.name:list(o.matrix_world.translation) for o in a.objects if o.name.startswith('AXLE_')},'bogie_world_centres':{o.name:list(o.matrix_world.translation) for o in a.objects if o.name.startswith('BOGIE_')}})
# Check FBX roundtrip in fresh scene.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(OUT,'WAP7_prototype.fbx'))
r['fbx_roundtrip']={'object_count':len(bpy.context.scene.objects),'axle_pivots':sorted(o.name for o in bpy.context.scene.objects if o.name.startswith('AXLE_')),'bogie_pivots':sorted(o.name for o in bpy.context.scene.objects if o.name.startswith('BOGIE_')),'mesh_count':sum(o.type=='MESH' for o in bpy.context.scene.objects),'contains_presentation':any(o.name.startswith(('Display rail','Studio floor','Three quarter camera')) for o in bpy.context.scene.objects)}
open(os.path.join(OUT,'geometry_report.json'),'w').write(json.dumps(r,indent=2));print(json.dumps(r,indent=2),flush=True)
