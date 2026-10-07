"""Check the formerly open roof crescent and preserve the gangway opening."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1];reports={}
for kind in ['DTC','MC','MC2','TC_CC','TC_EC','NDTC_EC','NDTC_EC2']:
 source=OUT/'cars'/f'VB_{kind}.blend';bpy.ops.wm.open_mainfile(filepath=str(source));dg=bpy.context.evaluated_depsgraph_get();caps=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('VB02_END_continuous_curved_roof_closure')];trees=[BVHTree.FromObject(o,dg) for o in caps];rows=[]
 for sign in [-1] if kind=='DTC' else [-1,1]:
  start=Vector((sign*11.70,0,3.72));direction=Vector((-sign,0,0));roofhit=any(t.ray_cast(start,direction,.30)[0] is not None for t in trees)
  passage=Vector((sign*11.70,0,2.40));blocked=any(t.ray_cast(passage,direction,.30)[0] is not None for t in trees)
  rows.append({'end':sign,'upper_crown_ray_closed':roofhit,'gangway_passage_ray_clear':not blocked});assert roofhit and not blocked,(kind,sign)
 reports[kind]={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'end_caps':len(caps),'checks':rows,'scope':'Upper end-cap geometry rays, not a complete vehicle watertightness or evacuation certification'};print('ROOF_END_QA',kind,'PASS',flush=True)
(OUT/'qa/roof_end_closure.json').write_text(json.dumps(reports,indent=2))
