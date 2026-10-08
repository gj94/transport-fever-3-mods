"""One Blender child at a time; request a clean render-boundary stop on pressure."""
import subprocess,time,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
jobs=[['build_ers_full.py','build_delivery.log'],['render_review.py','render_delivery_proof.log','--','13','04']]
if '--gallery' in sys.argv:jobs=[['render_review.py','render_delivery_gallery.log','--','01','02','03','05','06','07','08','09','10','11']]
if '--remaining' in sys.argv:jobs=[['render_review.py','render_delivery_remaining.log','--','04','06','07','08','09','10','11']]
if '--export' in sys.argv:jobs=[['export_asset.py','export_delivery.log'],['validate_asset.py','validate_delivery.log'],['validate_flight_clearance.py','flight_clearance_delivery.log']]
(P/'runtime_idle.flag').unlink(missing_ok=True)
with (P/'runtime_rss.jsonl').open('a') as stats:
 for job in jobs:
  args=['/usr/bin/blender','-b','-t','4','--python',str(P/job[0])]+job[2:]
  with (P/job[1]).open('w') as log:
   child=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
   while child.poll() is None:
    rss=0;available=0
    try:
     for line in Path('/proc/'+str(child.pid)+'/status').read_text().splitlines():
      if line.startswith('VmRSS:'):rss=int(line.split()[1])
     for line in Path('/proc/meminfo').read_text().splitlines():
      if line.startswith('MemAvailable:'):available=int(line.split()[1])
    except FileNotFoundError:pass
    data={'unix_time':time.time(),'pid':child.pid,'stage':job[0],'rss_kb':rss,'mem_available_kb':available}
    stats.write(json.dumps(data)+'\n');stats.flush();(P/'runtime_status.json').write_text(json.dumps(data))
    if available and available<1200000:
     (P/'STOP_AFTER_FRAME').write_text('Memory pressure: '+str(available)+' kB available')
     if job[0]!='render_review.py':child.terminate();break
    time.sleep(5)
   code=child.wait()
   if code:raise SystemExit(code)
  if (P/'STOP_AFTER_FRAME').exists():break
(P/'runtime_idle.flag').write_text('No active Blender child')
