"""Read/reopen QA and reusable Asset Browser collection tags; no geometry changes."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sc=bpy.context.scene
for c in bpy.data.collections:
 if c.name.startswith(('01_','02_','03_','04_')):
  c.asset_mark();c['dimension_basis']='photo-inferred / game-adjusted; no station-specific survey dimensions'
  if c.asset_data:c.asset_data.description='TVC November 2022 heritage study; see README for measured versus inferred boundaries.'
bpy.data.collections['04_MODULAR_PLATFORM_CANOPY_DEMONSTRATOR'].instance_offset=(0,19,0)
rails=sorted([o for o in sc.objects if o.name.startswith('Rail head')],key=lambda o:o.location.y)
gap=rails[1].location.y-rails[0].location.y-.068
assert abs(gap-1.676)<1e-6, gap
assert sc.unit_settings.scale_length==1
assert sc['flank_proportion_review_applied']
missing=[]
for i in bpy.data.images:
 if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists():missing.append(i.filepath)
assert not missing,missing
bpy.ops.wm.save_as_mainfile(filepath=str(R/'TVC_heritage_2022_v1.blend'))
p=R/'qa_geometry.json';d=json.loads(p.read_text());d.update({'final_reopen_audit':'passed','rail_inner_gauge_checked_m':round(gap,6),'asset_browser_collections':4,'missing_external_images':missing});p.write_text(json.dumps(d,indent=2));print('TVC FINAL AUDIT PASSED',len(sc.objects), 'objects; gauge',gap)
