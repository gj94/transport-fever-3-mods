"""Read-only source and sibling presentation-dependency verification from any cwd."""
from pathlib import Path
import json,hashlib,sys
p=Path(__file__).resolve().parents[1]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
lock=json.loads((p/'qa/final_geometry_lock.json').read_text());errors=[];sources=[]
for v,h in lock['source_blend_sha256'].items():
 for ext,expected in [('blend',h),('fbx',lock['fbx_sha256'][v])]:
  f=p/v/(f'ICF_{v}_master.blend' if ext=='blend' else f'ICF_{v}.fbx')
  ok=f.is_file() and sha(f)==expected;sources.append({'path':str(f.relative_to(p.parent)),'hash_matches':ok})
  if not ok:errors.append('Missing or changed '+str(f))
 if not (p/v/f'ICF_{v}.fbm').is_dir():errors.append('Missing FBX texture folder for '+v)
deps=json.loads((p/'qa/portable_render_dependencies.json').read_text());dep_checks=[]
for d in deps['dependencies']:
 f=p.parent/d['path'];ok=f.is_file() and sha(f)==d['sha256'];dep_checks.append({'path':d['path'],'hash_matches':ok})
 if not ok:errors.append('Missing or changed preview dependency '+d['path'])
ref=p.parent/deps['required_reference_ledger'];ref_ok=ref.is_file() and (not deps.get('reference_ledger_sha256') or sha(ref)==deps['reference_ledger_sha256'])
if not ref_ok:errors.append('Missing or changed reference ledger '+str(ref))
print(json.dumps({'reference_ledger_available_and_verified':ref_ok,'passed':not errors,'sources':sources,'presentation_dependencies':dep_checks,'errors':errors,'scope':'File integrity and preview dependency availability only; see per-class QA for geometry and export checks. No game/runtime claim.'},indent=2))
sys.exit(0 if not errors else 1)
