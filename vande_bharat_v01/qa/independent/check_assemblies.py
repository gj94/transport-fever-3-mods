import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[2];reports=[]
for n in (8,16):
 bpy.ops.wm.open_mainfile(filepath=str(base/'assemblies'/f'VB_{n}_car.blend'));bpy.context.view_layer.update()
 cars=sorted([o for o in bpy.context.scene.objects if o.instance_type=='COLLECTION'],key=lambda o:o.location.x);rows=[]
 for car in cars:
  anchors=[]
  for o in car.instance_collection.all_objects:
   if o.type=='EMPTY' and o.name.startswith('COUPLING_'):
    w=car.matrix_world@o.matrix_world;anchors.append({'name':o.name,'p':w.translation.copy(),'normal':(w.to_3x3()@Vector((1,0,0))).normalized()})
  anchors.sort(key=lambda a:a['p'].x);assert len(anchors)==2
  roots=[o for o in car.instance_collection.all_objects if o.type=='EMPTY' and not o.parent and 'ROOT' in o.name]
  assert len(roots)==1
  kind=roots[0]['asset_type'];rows.append({'instance':car.name,'kind':kind,'left':anchors[0],'right':anchors[1]})
 joins=[]
 for a,b in zip(rows,rows[1:]):
  error=(a['right']['p']-b['left']['p']).length;dot=a['right']['normal'].dot(b['left']['normal']);assert error<1e-5 and abs(dot+1)<1e-5;joins.append({'pair':[a['instance'],b['instance']],'position_error_m':error,'outward_normal_dot':dot})
 mins=[float('inf')]*3;maxs=[-float('inf')]*3;instances=0
 for inst in bpy.context.evaluated_depsgraph_get().object_instances:
  if inst.object.type!='MESH':continue
  instances+=1
  for v in inst.object.data.vertices:
   p=inst.matrix_world@v.co
   for i in range(3):mins[i]=min(mins[i],p[i]);maxs[i]=max(maxs[i],p[i])
 length=maxs[0]-mins[0];assert length<320
 reports.append({'cars':n,'linked_sources_found':all(Path(bpy.path.abspath(l.filepath)).is_file() for l in bpy.data.libraries),'car_types':[r['kind'] for r in rows],'mesh_instances':instances,'actual_vertex_bounds_m':[mins,maxs],'visible_length_m':length,'total_platform_margin_m':320-length,'anchor_span_m':rows[-1]['right']['p'].x-rows[0]['left']['p'].x,'joins':joins})
(Path(__file__).resolve().parent/'independent_assemblies.json').write_text(json.dumps(reports,indent=2));print('ASSEMBLY_QA',[(r['cars'],r['visible_length_m'],max(j['position_error_m'] for j in r['joins'])) for r in reports])
