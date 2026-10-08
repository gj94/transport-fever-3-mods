import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'NCJ_full_station_v02.blend'));s=bpy.context.scene
bad=[]
for o in s.objects:
 if o.type=='MESH' and any(not all(math.isfinite(c) for c in v.co) for v in o.data.vertices):bad.append(o.name)
# Path segments at body height: entrance-to-hall, central rear portal and roofed bridge access.
def ray(a,b):
 a,b=Vector(a),Vector(b);delta=b-a;res=s.ray_cast(bpy.context.evaluated_depsgraph_get(),a,delta.normalized(),distance=delta.length)
 return {'from':list(a),'to':list(b),'clear':not res[0],'hit':res[4].name if res[0] else None}
paths={
'entrance_to_hall':ray((0,-6,2),(0,3,2)),
'hall_to_platform_central':ray((0,8,2),(0,12,2)),
'waiting_door':ray((-25,-2,2),(-25,1,2)),
'wc_entrance':ray((-68,0,2),(-68,3,2)),
'bridge_stair_entry_1':ray((-87,15.5,8.3),(-91,15.5,8.3)),
'bridge_stair_entry_23':ray((-87,34.5,8.3),(-91,34.5,8.3))}
report={'unit_system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,'nonfinite_meshes':bad,'objects':len(s.objects),'mesh_count':sum(o.type=='MESH' for o in s.objects),'vertices':sum(len(o.data.vertices) for o in s.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons) for o in s.objects if o.type=='MESH'),'material_count':len(bpy.data.materials),'camera_count':sum(o.type=='CAMERA' for o in s.objects),'packed_fonts':all(f.packed_file or f.filepath=='<builtin>' for f in bpy.data.fonts),'no_rolling_stock':not any(any(x in o.name.lower() for x in ['locomotive','coach body','wagon body','bogie']) for o in s.objects),'walk_circulation_rays':paths,'rail_gauge_m':s['gauge_inner_faces_m'],'render_threads':s.render.threads,'denoise':s.cycles.use_denoising,'simple_turnouts':s.get('physical_turnout_corrected_count'),'compound_treatment':s.get('compound_crossing_treatment'),'OHE_supports':s.get('OHE_supports')}
(R/'QA_VALIDATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
