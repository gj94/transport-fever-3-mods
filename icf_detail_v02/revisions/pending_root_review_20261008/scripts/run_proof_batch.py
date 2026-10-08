"""Resumable actual-model proof generation; runs one resource-bounded Blender at a time."""
import os,subprocess,json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1]
views={'1A':['exterior','cabin_diagonal','cabin_cutaway'],'2A':['exterior','bay'],'3A':['exterior','bay'],'2S':['exterior','aisle'],'CC':['exterior','aisle'],'SL':['exterior','bay'],'GS':['exterior','aisle']}
suffix=os.environ.get('ICF_RENDER_SUFFIX','r10_review')
for variant,keys in views.items():
 master=P/variant/f'ICF_{variant}_master.blend'
 sha=hashlib.sha256(master.read_bytes()).hexdigest()
 for view in keys:
  sidecar=P/variant/'renders'/f'{view}_{suffix}.json'
  try:old=json.loads(sidecar.read_text())
  except (FileNotFoundError,json.JSONDecodeError):old={}
  if old.get('source_blend_sha256')==sha and sidecar.with_suffix('.png').exists():continue
  state={'variant':variant,'view':view,'suffix':suffix,'source_sha256':sha,'status':'rendering','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  (P/'qa/render_progress.json').write_text(json.dumps(state,indent=2))
  env=os.environ.copy();env['ICF_RENDER_SUFFIX']=suffix
  with (P/'qa'/f'render_{variant}_{view}_{suffix}.log').open('w') as f:
   result=subprocess.run(['blender','-b',str(master),'-t',os.environ.get('ICF_RENDER_THREADS','4'),'--python',str(P/'scripts/render_detail.py'),'--',view],env=env,stdout=f,stderr=subprocess.STDOUT)
  if result.returncode or not sidecar.exists():raise RuntimeError(f'Render failed: {variant} {view}')
  state['status']='complete';(P/'qa/render_progress.json').write_text(json.dumps(state,indent=2))
  print('PROOF_READY',variant,view,str(sidecar),flush=True)
print('ALL_PROOFS_COMPLETE',flush=True)
