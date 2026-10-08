"""GNU time equivalent using kernel child ru_maxrss; monitor one Blender process, never exports."""
import subprocess,resource,time,json,os,sys,signal,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];view=sys.argv[1];started=time.monotonic();peak=0;minimum_available=10**12;stopped=False
with (R/f'render_{view}_monitored.log').open('w') as log,(R/f'render_{view}_rss.log').open('w') as rsslog:
 p=subprocess.Popen(['blender','-b','-t','4','--python-exit-code','1','--python',str(R/'scripts/render_ncj_full.py'),'--',view],stdout=log,stderr=subprocess.STDOUT)
 while p.poll() is None:
  try:
   d=dict(line.split(':',1) for line in Path(f'/proc/{p.pid}/status').read_text().splitlines() if ':' in line);rss=int(d.get('VmRSS','0 kB').split()[0]);peak=max(peak,rss)
   mem=dict(line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines());avail=int(mem['MemAvailable'].split()[0]);minimum_available=min(minimum_available,avail)
   rsslog.write(f'{time.time():.0f} RSS_KB={rss} PEAK_KB={peak} AVAILABLE_KB={avail}\n');rsslog.flush()
   if avail<550000:
    p.terminate();stopped=True;break
  except FileNotFoundError:pass
  time.sleep(3)
 code=p.wait();usage=resource.getrusage(resource.RUSAGE_CHILDREN)
 result={'view':view,'source_scene_sha256':hashlib.sha256((R/'NCJ_full_station_v02.blend').read_bytes()).hexdigest(),'exit_code':code,'actual_kernel_peak_RSS_KiB':usage.ru_maxrss,'sampled_peak_RSS_KiB':peak,'minimum_system_available_KiB':minimum_available,'wall_seconds':time.monotonic()-started,'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'stopped_for_imminent_memory_pressure':stopped,'measurement':'Linux kernel getrusage(RUSAGE_CHILDREN), one Blender child; GNU time binary unavailable.'}
(R/f'render_{view}_resources.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));sys.exit(0 if code==0 and not stopped else 1)
