"""Current-source targeted review after the seven-class overview gallery."""
from pathlib import Path
import subprocess,os,json,hashlib,datetime
p=Path(__file__).resolve().parents[1]
qa=p/'1A/qa'
for name in ['geometry_checks.json','interior_support_checks.json','first_ac_privacy_checks.json']:
 assert json.loads((qa/name).read_text())['passed'],name
assert json.loads((qa/'aperture_checks.json').read_text())['structural_apertures_clear']
f=json.loads((qa/'fbx_fresh_import.json').read_text());assert f['source_passed'] and f['fbx_passed']
assert json.loads((p/'1A/manifest.json').read_text())['build_pass']=='r11-1A'
jobs=[('1A','hero','r11_review'),('1A','cabin_diagonal','r11_review'),('1A','cabin_cutaway','r11_review'),('CC','headrest','r10_review'),('2A','side_berth','r10_review'),('3A','side_berth','r10_review'),('SL','side_berth','r10_review'),('SL','bogie','r10_review'),('GS','coupling','r10_review'),('CC','toilet','r10_review'),('SL','entrance','r10_review'),('1A','markings','r11_review')]
for v,view,suffix in jobs:
 master=p/v/f'ICF_{v}_master.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest();sidecar=p/v/'renders'/f'{view}_{suffix}.json'
 if sidecar.exists() and json.loads(sidecar.read_text()).get('source_blend_sha256')==sha:continue
 env=dict(os.environ,ICF_RENDER_SUFFIX=suffix,ICF_RENDER_THREADS='4')
 state={'variant':v,'view':view,'suffix':suffix,'source_sha256':sha,'status':'rendering','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(p/'qa/extension_progress.json').write_text(json.dumps(state,indent=2))
 with (p/'qa'/f'render_{v}_{view}_{suffix}.log').open('w') as f:r=subprocess.run(['blender','-b',str(master),'-t','4','--python',str(p/'scripts/render_detail.py'),'--',view],env=env,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode or not sidecar.exists():raise RuntimeError((v,view))
 print('PROOF_READY',v,view,str(sidecar),flush=True)
 state['status']='complete';(p/'qa/extension_progress.json').write_text(json.dumps(state,indent=2))
print('EXTENSION_PROOFS_COMPLETE',flush=True)
