"""Fault-injection self-test of the read-only LHB verifier, in disposable memory.
Run: blender -b -t 1 --python scripts/test_verify_lhb_detail.py
No source, model, manifest or export is written.
"""
import importlib.util
import json
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('verifier',P/'verify_lhb_detail.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'models/LHB_3A.blend'),load_ui=False)

def results():
    r,_=v.measure_scene('3A','source',full_topology=False)
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
bpy.data.objects.remove(pax,do_unlink=True)
checks.append({'test':'detect missing passenger despite correct root metadata','passed':results()['PAX_count']=='error'})
out=P.parent/'qa/source_geometry/verifier_selftest.json';out.write_text(json.dumps({'status':'pass' if all(c['passed'] for c in checks) else 'fail','verifier_sha256':v.digest(P/'verify_lhb_detail.py'),'source_3A_sha256':v.digest(P.parent/'models/LHB_3A.blend'),'tests':checks},indent=2));print(out.read_text())
assert all(c['passed'] for c in checks)
