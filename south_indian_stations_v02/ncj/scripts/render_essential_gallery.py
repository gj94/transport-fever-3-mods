"""Render seven final review frames serially; one Blender child, monitored at every frame."""
import subprocess,sys,json,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
code=subprocess.run(['blender','-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/refine_review_cameras.py')],stdout=(R/'refine_review_cameras.log').open('w'),stderr=subprocess.STDOUT).returncode
if code:raise SystemExit(code)
lineage=json.loads((R/'RENDER_PROVENANCE.json').read_text());scenehash=hashlib.sha256((R/'NCJ_full_station_v02.blend').read_bytes()).hexdigest();lineage['current_scene_sha256']=scenehash
for prefix in ['01','10','08','06','05','03','04']:
 # Frame boundaries are the safe place to pause under memory pressure.
 while True:
  mem=dict(x.split(':',1) for x in Path('/proc/meminfo').read_text().splitlines());available=int(mem['MemAvailable'].split()[0])
  if available>=3500000:break
  print('PAUSED_AT_FRAME_BOUNDARY',prefix,'available_KiB',available,flush=True);time.sleep(10)
 print('START_FRAME',prefix,flush=True)
 code=subprocess.run([sys.executable,str(R/'scripts/render_monitored.py'),prefix]).returncode
 if code:raise SystemExit(code)
 matches=list((R/'renders').glob(prefix+'*.png'))
 for p in matches:lineage['views'][p.name]={'status':'Final corrected geometry, current dedicated review viewpoint','samples':128 if prefix in ['03','04'] else 48,'source_scene_sha256':scenehash,'file_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 (R/'RENDER_PROVENANCE.json').write_text(json.dumps(lineage,indent=2))
 print('READY_FRAME',prefix,[p.name for p in matches],flush=True)
