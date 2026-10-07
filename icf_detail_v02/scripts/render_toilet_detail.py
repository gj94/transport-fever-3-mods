"""Toilet cutaway wrapper: hide controls/labels that are attached to hidden doors.
This is presentation-only. The source master and FBX are never changed.
"""
from pathlib import Path
import bpy,sys,runpy,json,hashlib,os
wrapper_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
hidden=[]
for ob in bpy.data.objects:
 if ob.name.startswith(('Lavatory inside pull','Lavatory rotary latch plate','Lavatory occupied indicator','Lavatory style label')) and not ob.hide_render:
  ob.hide_render=True;hidden.append(ob.name)
runpy.run_path(str(Path(__file__).with_name('render_detail.py')),run_name='__main__')
p=Path(bpy.data.filepath).parent/'renders'/('toilet_'+os.environ.get('ICF_RENDER_SUFFIX','proof')+'.json')
r=json.loads(p.read_text());r['cutaway_wrapper_sha256']=wrapper_sha;r['additional_cutaway_mesh_names']=hidden;r['hidden_mesh_count']+=len(hidden);r['cutaway_scope']='Lavatory door leaves, headers and attached pulls, latch plates, occupancy indicators and labels only';p.write_text(json.dumps(r,indent=2))
