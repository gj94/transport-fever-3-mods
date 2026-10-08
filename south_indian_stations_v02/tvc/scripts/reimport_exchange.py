"""Reimport every GLB in isolation, check its metre-scale assembled bounds."""
import bpy,json,math,gc
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'exchange';items=json.loads((O/'MANIFEST.json').read_text());results=[];mins=[float('inf')]*3;maxs=[float('-inf')]*3
for row in items:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 try:bpy.ops.preferences.addon_enable(module='io_scene_gltf2')
 except:pass
 bpy.ops.import_scene.gltf(filepath=str(O/row['file']))
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert objects
 vertices=sum(len(o.data.vertices) for o in objects);assert vertices>0
 lo=[float('inf')]*3;hi=[float('-inf')]*3
 for o in objects:
  for corner in o.bound_box:
   p=o.matrix_world@Vector(corner)
   for i,v in enumerate(p):assert math.isfinite(v);lo[i]=min(lo[i],v);hi[i]=max(hi[i],v)
 for i in range(3):mins[i]=min(mins[i],lo[i]);maxs[i]=max(maxs[i],hi[i])
 results.append({'file':row['file'],'reimport':'PASS','mesh_objects':len(objects),'vertices':vertices,'world_bounds_blender_z_up':[lo,hi]});print('REIMPORT_PASS',row['file'],len(objects),vertices,flush=True);gc.collect()
ext=[maxs[i]-mins[i] for i in range(3)];assert 1500<ext[0]<1800 and 300<ext[1]<600 and 15<ext[2]<40
report={'all_passed':True,'parts':len(results),'assembled_bounds_metres':[mins,maxs],'assembled_dimensions_metres':ext,'note':'Each GLB was imported separately at identity transforms; union of resulting world bounds verifies common metre-scale placement. No source blend was modified.','results':results}
(R/'EXCHANGE_REIMPORT_QA.json').write_text(json.dumps(report,indent=2));print('ALL_REIMPORT_PASS',ext,flush=True)
