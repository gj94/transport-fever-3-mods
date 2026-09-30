"""Export unambiguous seated-root metadata and separate sleeping-berth references."""
import bpy,json,math
from pathlib import Path
P=Path(__file__).resolve().parent
for v in ['1A','2A','3A','2S','CC','SL','GS']:
 d=P/v;bpy.ops.wm.open_mainfile(filepath=str(d/f'ICF_{v}_master.blend'));bpy.context.view_layer.update();root=bpy.data.objects[f'ICF_{v}_ROOT'];obs=root.children_recursive
 pax=[];berths=[]
 for o in obs:
  if o.name.startswith('PAX_'):pax.append({'name':o.name,'parent':o.parent.name,'animation':'sitting','local_matrix_rows':[list(r) for r in o.matrix_local],'world_position_m':list(o.matrix_world.translation),'yaw_degrees':math.degrees(o.rotation_euler.z),'root_to_pelvis_m':.483,'commercial_capacity_is_separate':True})
  elif o.name.startswith('BERTH_'):berths.append({'name':o.name,'world_position_m':list(o.matrix_world.translation),'reference_only':True,'exclude_from_passenger_export':True})
 (d/'pax_markers.json').write_text(json.dumps(sorted(pax,key=lambda x:x['name']),indent=2));(d/'berth_references.json').write_text(json.dumps(sorted(berths,key=lambda x:x['name']),indent=2));print('MARKERS',v,len(pax),len(berths),flush=True)
