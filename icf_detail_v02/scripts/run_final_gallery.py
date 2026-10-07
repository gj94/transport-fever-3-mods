"""Resumable high-sample gallery from frozen, pixel-reviewed source masters.
One Blender process, four CPU threads, 512 max samples, 2% adaptive threshold,
64 minimum samples, no denoiser. Every output retains a source/image hash sidecar.
"""
from pathlib import Path
import os,subprocess,json,hashlib,datetime
p=Path(__file__).resolve().parents[1]
views={'1A':['hero','cabin_diagonal','cabin_cutaway','markings'],'2A':['hero','bay','side_berth'],'3A':['hero','bay','side_berth'],'2S':['hero','aisle'],'CC':['hero','aisle','headrest','toilet'],'SL':['hero','bay','side_berth','bogie','entrance'],'GS':['hero','aisle','coupling']}
# Finish complete exterior + interior coverage first, then selected close details.
jobs=[(v,view) for stage in [0,1] for v,keys in views.items() for view in (keys[:2] if stage==0 else keys[2:])]
lock=json.loads((p/'qa/final_geometry_lock.json').read_text())
for v,view in jobs:
 master=p/v/f'ICF_{v}_master.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest()
 assert sha==lock['source_blend_sha256'][v],f'Geometry changed after approval: {v}'
 sidecar=p/v/'renders'/f'{view}_final.json'
 renderer_hash=hashlib.sha256((p/'scripts/render_detail.py').read_bytes()).hexdigest()
 try:r=json.loads(sidecar.read_text())
 except (FileNotFoundError,json.JSONDecodeError):r={}
 if r.get('source_blend_sha256')==sha and r.get('renderer_script_sha256')==renderer_hash and r.get('samples')==512 and r.get('adaptive_min_samples')==64 and sidecar.with_suffix('.png').exists() and (view!='toilet' or r.get('cutaway_wrapper_sha256')==hashlib.sha256((p/'scripts/render_toilet_detail.py').read_bytes()).hexdigest()):
  if hashlib.sha256(sidecar.with_suffix('.png').read_bytes()).hexdigest()==r.get('image_sha256'):continue
 env=dict(os.environ,ICF_RENDER_SUFFIX='final',ICF_RENDER_THREADS='4',ICF_RENDER_SAMPLES='512',ICF_INTERIOR_SAMPLES='512',ICF_ADAPTIVE_THRESHOLD='0.02',ICF_ADAPTIVE_MIN_SAMPLES='64',ICF_RENDER_WIDTH='1600',ICF_RENDER_HEIGHT='900' if view=='hero' else '1040')
 state={'variant':v,'view':view,'status':'rendering','source_sha256':sha,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(p/'qa/final_render_progress.json').write_text(json.dumps(state,indent=2))
 with (p/'qa'/f'render_{v}_{view}_final.log').open('w') as f:
  result=subprocess.run(['blender','-b',str(master),'-t','4','--python-exit-code','1','--python',str(p/'scripts'/('render_toilet_detail.py' if view=='toilet' else 'render_detail.py')),'--',view],env=env,stdout=f,stderr=subprocess.STDOUT)
 if result.returncode or not sidecar.exists():raise RuntimeError(f'Render failed: {v} {view}')
 r=json.loads(sidecar.read_text());assert r['source_blend_sha256']==sha and r['samples']==512 and r['adaptive_min_samples']==64
 state['status']='complete';(p/'qa/final_render_progress.json').write_text(json.dumps(state,indent=2));print('FINAL_READY',v,view,str(sidecar),flush=True)
print('ALL_FINAL_PROOFS_COMPLETE',flush=True)
