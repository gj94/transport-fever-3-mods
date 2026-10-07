"""Resumable actual-Cycles gallery. Source geometry is read-only.
Run after the locked source/FBX QA and immutable source checkpoint are complete.
"""
import hashlib,json,os,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent.parent
QUEUE=[(k,v) for k in ['1A','CC','3A','2A','SL','2S','GS'] for v in ['interior','exterior']]
QUEUE += [('CC','chair_detail'),('1A','cabin_entry'),('3A','hvac'),('3A','bogie'),('3A','door'),('3A','toilet')]
SAMPLES=512;RESOLUTION=1400
STATE=P/'qa/final_gallery_progress.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def complete(k,v):
 p=P/'qa'/f'render_{k}_{v}.json'
 if not p.exists():return False
 r=json.loads(p.read_text());im=P/r['image']
 return (r['source_sha256']==sha(P/'models'/f'LHB_{k}.blend') and im.exists() and r['image_sha256']==sha(im) and r['samples']==SAMPLES and r['resolution'][0]>=RESOLUTION and r.get('adaptive_min_samples',0)>=64 and not r.get('denoising',True) and r.get('actual_geometry_render'))
locked={k:sha(P/'models'/f'LHB_{k}.blend') for k,_ in QUEUE}
progress={'status':'running','renderer':'Blender CPU Cycles','samples':SAMPLES,'minimum_samples':64,'adaptive_threshold':.02,'denoising':False,'cpu_threads':4,'locked_source_sha256':locked,'completed':[],'pending':[]}
def save():
 progress['completed']=[{'variant':k,'view':v} for k,v in QUEUE if complete(k,v)]
 progress['pending']=[{'variant':k,'view':v} for k,v in QUEUE if not complete(k,v)]
 tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(progress,indent=2));tmp.replace(STATE)
try:
 for k,v in QUEUE:
  assert sha(P/'models'/f'LHB_{k}.blend')==locked[k],f'Source changed: {k}'
  if complete(k,v):print('ALREADY_CURRENT',k,v,flush=True);continue
  progress['active']={'variant':k,'view':v};save();print('START_FINAL',k,v,flush=True)
  env=dict(os.environ,LHB_SAMPLES=str(SAMPLES),LHB_RESOLUTION=str(RESOLUTION),LHB_MIN_SAMPLES='64',LHB_THREADS='4',PYTHONUNBUFFERED='1')
  log=P/'qa'/f'final_{k}_{v}.log'
  with log.open('w') as f:subprocess.run(['blender','-b','-t','4','--python',str(P/'render_lhb_detail.py'),'--',k,v],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  assert complete(k,v),f'Output provenance/configuration invalid: {k}/{v}'
  print('FINISHED_FINAL',k,v,flush=True);save()
 progress['status']='complete';progress.pop('active',None);save()
except BaseException as e:
 progress['status']='blocked';progress['error']=str(e);save();raise
