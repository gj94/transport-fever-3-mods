"""Run one exclusive Blender export with actual kernel RSS monitoring, then validate files."""
import subprocess,resource,time,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];started=time.monotonic();peak=0;minimum_available=10**12;stopped=False
with (R/'export_final.log').open('w')as log,(R/'export_rss.log').open('w')as rsslog:
 p=subprocess.Popen(['blender','-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/export_ncj_full.py')],stdout=log,stderr=subprocess.STDOUT)
 while p.poll()is None:
  try:
   d=dict(x.split(':',1)for x in Path(f'/proc/{p.pid}/status').read_text().splitlines()if ':'in x);rss=int(d.get('VmRSS','0 kB').split()[0]);peak=max(peak,rss)
   mem=dict(x.split(':',1)for x in Path('/proc/meminfo').read_text().splitlines());available=int(mem['MemAvailable'].split()[0]);minimum_available=min(minimum_available,available)
   rsslog.write(f'{time.time():.0f} RSS_KiB={rss} AVAILABLE_KiB={available}\n');rsslog.flush()
   if available<550000:p.terminate();stopped=True;break
  except FileNotFoundError:pass
  time.sleep(3)
 code=p.wait();usage=resource.getrusage(resource.RUSAGE_CHILDREN)
report={'exit_code':code,'actual_kernel_peak_RSS_KiB':usage.ru_maxrss,'sampled_peak_RSS_KiB':peak,'minimum_system_available_KiB':minimum_available,'wall_seconds':time.monotonic()-started,'stopped_for_imminent_memory_pressure':stopped,'source_scene_sha256':hashlib.sha256((R/'NCJ_full_station_v02.blend').read_bytes()).hexdigest()}
(R/'QA_EXPORT_RESOURCES.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
if code or stopped:raise SystemExit(code or 1)
raise SystemExit(subprocess.run([sys.executable,str(R/'scripts/validate_ncj_export.py')]).returncode)
