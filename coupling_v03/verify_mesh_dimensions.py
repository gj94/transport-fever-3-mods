"""Independent fresh FBX geometry dimensions check."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
out={}
for k,stem in [('wap7','WAP7_coupling_v03'),('icf','ICF_sleeper_CBC_retrofit_v03')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(P/k/(stem+'.fbx')));bpy.context.view_layer.update()
 expected=json.loads((P/k/'geometry_validation.json').read_text());checks={}
 for n,ref in dict(expected['head_bounds'],**expected['buffer_bounds']).items():
  o=bpy.data.objects[n];v=[o.matrix_world@Vector(p) for p in o.bound_box];b=[[min(x[i] for x in v),max(x[i] for x in v)] for i in range(3)];err=max(abs(b[i][j]-ref[i][j]) for i in range(3) for j in range(2));assert err<1e-5,(n,err)
  if n.startswith(('Buffer plate','Buffer head','Buffer housing','Buffer shank')):
   assert abs(abs(sum(b[1])/2)-.978)<1e-5,(n,b);assert abs(sum(b[2])/2-1.105)<1e-5
  if n.endswith('closed_knuckle_head'):assert abs(sum(b[2])/2-1.105)<1e-5
  checks[n]={'bounds_m':b,'bounds_max_error_m':err}
 anchors=[bpy.data.objects['COUPLING_'+n] for n in ['FRONT','REAR']];span=(anchors[0].matrix_world.translation-anchors[1].matrix_world.translation).length
 assert abs(span-expected['anchor_span_m'])<1e-5
 out[k]={'span_m':span,'buffer_centres_and_head_heights_pass':True,'checks':checks}
(P/'fresh_fbx_geometry_validation.json').write_text(json.dumps(out,indent=2));print('FRESH_MESH_DIMENSIONS_PASS')
