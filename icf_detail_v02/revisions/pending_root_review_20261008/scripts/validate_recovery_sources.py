"""Read-only revalidation of every preserved r12 source after workspace recovery."""
from pathlib import Path
import bpy,hashlib,json,runpy
p=Path(__file__).resolve().parents[1];lock=json.loads((p/'qa/final_geometry_lock.json').read_text());results=[]
for v,expected in lock['source_blend_sha256'].items():
 master=p/v/f'ICF_{v}_master.blend';assert hashlib.sha256(master.read_bytes()).hexdigest()==expected
 bpy.ops.wm.open_mainfile(filepath=str(master))
 for script in ['validate_detail.py','validate_interior_supports.py','check_apertures.py']:
  runpy.run_path(str(p/'scripts'/script),run_name='__main__')
 if v=='1A':runpy.run_path(str(p/'scripts/validate_first_ac_privacy.py'),run_name='__main__')
 assert hashlib.sha256(master.read_bytes()).hexdigest()==expected
 results.append({'variant':v,'source_sha256':expected,'unchanged':True})
(p/'qa/recovery_source_integrity.json').write_text(json.dumps(results,indent=2))
print('RECOVERY_SOURCE_CHECKS_COMPLETE',flush=True)
