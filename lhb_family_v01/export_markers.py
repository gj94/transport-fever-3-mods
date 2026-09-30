"""Re-export reviewable passenger-root / sleeping-reference data from saved masters."""
import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
for k in ['1A','2A','3A','2S','CC','SL','GS']:
 bpy.ops.wm.open_mainfile(filepath=str(P/'models'/('LHB_'+k+'.blend')))
 root=bpy.data.objects['LHB_'+k+'_ROOT_metres'];pax=sorted([o for o in root.children_recursive if o.type=='EMPTY' and o.name.startswith('PAX_')],key=lambda o:o.name);berths=sorted([o for o in root.children_recursive if o.type=='EMPTY' and o.name.startswith('BERTH_')],key=lambda o:o.name)
 payload={'variant':k,'PAX_character_roots':[{'name':o.name,'parent':o.parent.name,'position_parent_m':list(o.location),'yaw_radians':o.rotation_euler.z,'cushion_top_z_m':1.840,'pose':'sitting'} for o in pax],'BERTH_sleeping_references':[{'name':o.name,'position_parent_m':list(o.location),'berth_type':o['berth_type'],'use_as_seated_passenger':False} for o in berths]}
 (P/'models'/('LHB_'+k+'_markers.json')).write_text(json.dumps(payload,indent=2))
