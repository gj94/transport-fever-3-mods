"""Fault-injection self-test of the read-only LHB verifier, in disposable memory.
Run: blender -b -t 1 --python scripts/test_verify_lhb_detail.py
No source, model, manifest or export is written.
"""
import importlib.util
import json
import os
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('verifier',P/'verify_lhb_detail.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'models/LHB_3A.blend'),load_ui=False)

def results(variant='3A'):
    r,_=v.measure_scene(variant,'source',full_topology=False)
    return {c['name']:c['status'] for c in r['checks']}

checks=[]
baseline=results()
checks.append({'test':'unmodified dimensions, fixture positions and passenger placement','passed':all(baseline[n]=='pass' for n in ['dimension_body_length_m','lavatory_and_basin_actual_placement','PAX_seated_pose_and_single_lower_cushion_support'])})
pax=next(o for o in bpy.data.objects if o.name.startswith('PAX_'))
old=pax.location.z;pax.location.z=3.0
checks.append({'test':'detect upper-height seated passenger root','passed':results()['PAX_seated_pose_and_single_lower_cushion_support']=='error'})
pax.location.z=old
wc=bpy.data.objects['WC_pedestal'];old=wc.location.x;wc.location.x+=8 if wc.location.x>=0 else -8
r=results();checks.append({'test':'detect fixture escaped beyond body','passed':r['lavatory_and_basin_actual_placement']=='error' and r['whole_asset_reasonable_envelope']=='error'});wc.location.x=old
ax=bpy.data.objects['AXLE_FRONT_A_PIVOT'];old=ax.location.x;ax.location.x+=.05
checks.append({'test':'detect wheelbase geometry error despite correct properties','passed':results()['running_gear_geometry_and_parenting']=='error'});ax.location.x=old
# Move the package without changing metadata: the well-depth ray must detect it.
cover=bpy.data.objects['AC_ROOF_end_package'];old=cover.location.z;cover.location.z+=.08
checks.append({'test':'detect a displaced HVAC well floor','passed':results()['HVAC_blind_wells_and_fans_recessed']=='error'});cover.location.z=old
privacy=bpy.data.materials['WC_privacy_frosted_glass'];bs=privacy.node_tree.nodes.get('Principled BSDF');old=bs.inputs['Alpha'].default_value;bs.inputs['Alpha'].default_value=.22
checks.append({'test':'detect privacy glass accidentally assigned clear alpha','passed':results()['WC_glazing_keeps_distinct_privacy_material']=='error'});bs.inputs['Alpha'].default_value=old
bpy.data.objects.remove(pax,do_unlink=True)
checks.append({'test':'detect missing passenger despite correct root metadata','passed':results()['PAX_count']=='error'})
# New non-AC design contracts: validate actual objects, not only saved counts.
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'models/LHB_GS.blend'),load_ui=False)
gs=results('GS')
checks.append({'test':'unmodified GS mirrored banks, fans and transverse racks','passed':all(gs[n]=='pass' for n in ['GS_mirrored_furniture_and_PAX_banks','GS_twenty_transverse_luggage_racks','ceiling_fan_count_and_class_positions'])})
fan=next(o for o in bpy.data.objects if o.name.startswith('FAN_motor'));bpy.data.objects.remove(fan,do_unlink=True)
checks.append({'test':'detect a missing GS fan despite unchanged metadata','passed':results('GS')['ceiling_fan_count_and_class_positions']=='error'})
marker=next(o for o in bpy.data.objects if o.name.startswith('PAX_1_') and '_SIDE_' not in o.name and o.location.y>1)
old=marker.location.y;marker.location.y=-old
checks.append({'test':'detect a GS main-bank passenger reflected to the wrong side','passed':results('GS')['GS_mirrored_furniture_and_PAX_banks']=='error'});marker.location.y=old
rail=next(o for o in bpy.data.objects if o.name.startswith('GS_TRANSVERSE_RACK_rail'))
coords=[x.co.copy() for x in rail.data.vertices];cx=sum(x.x for x in coords)/len(coords);cy=sum(x.y for x in coords)/len(coords)
for vertex,co in zip(rail.data.vertices,coords):vertex.co.x=cx-(co.y-cy);vertex.co.y=cy+(co.x-cx)
rail.data.update()
checks.append({'test':'detect longitudinal rather than transverse rack rail with unchanged count','passed':results('GS')['GS_twenty_transverse_luggage_racks']=='error'})
# Cabin fixture joints must be measured, not merely counted.
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'models/LHB_1A.blend'),load_ui=False)
cabin=results('1A')
checks.append({'test':'unmodified 1A ladder and wall fittings attach','passed':all(cabin[n]=='pass' for n in ['FIRST_ladder_treads_join_both_stiles','FIRST_hooks_and_net_frames_attach_to_partitions'])})
stile=next(o for o in bpy.data.objects if o.name.startswith('FIRST_access_ladder_stile'));old=stile.location.y;stile.location.y+=.4
checks.append({'test':'detect disconnected ladder stile','passed':results('1A')['FIRST_ladder_treads_join_both_stiles']=='error'});stile.location.y=old
hook=next(o for o in bpy.data.objects if o.name.startswith('CABIN_coat_hook_base'));old=hook.location.x;hook.location.x+=.10
checks.append({'test':'detect coat-hook base floating off partition','passed':results('1A')['FIRST_hooks_and_net_frames_attach_to_partitions']=='error'});hook.location.x=old
out=Path(os.environ.get('LHB_VERIFY_SELFTEST_OUTPUT',str(P.parent/'qa/source_geometry/verifier_selftest.json')));out.write_text(json.dumps({'status':'pass' if all(c['passed'] for c in checks) else 'fail','verifier_sha256':v.digest(P/'verify_lhb_detail.py'),'source_3A_sha256':v.digest(P.parent/'models/LHB_3A.blend'),'source_GS_sha256':v.digest(P.parent/'models/LHB_GS.blend'),'source_1A_sha256':v.digest(P.parent/'models/LHB_1A.blend'),'tests':checks},indent=2));print(out.read_text())
assert all(c['passed'] for c in checks)
