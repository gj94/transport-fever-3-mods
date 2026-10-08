"""Run exactly one Blender process and record actual RSS/system memory."""
import subprocess,sys,time,json,resource,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[1:];label=os.environ.get('TVC_RUN_LABEL','monitored_blender')
p=subprocess.Popen(['/usr/bin/blender',*args]);minimum=None;peak=0;records=[];started=time.monotonic();stop_reason=None;min_available=int(os.environ.get('TVC_MIN_AVAILABLE_KIB','0'));max_seconds=int(os.environ.get('TVC_MAX_SECONDS','0'))
while p.poll() is None:
 try:
  mem={line.split(':')[0]:int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemAvailable:','MemTotal:'))};av=mem.get('MemAvailable',0);minimum=av if minimum is None else min(minimum,av)
  if min_available and av<min_available:stop_reason='Available memory safety threshold';p.terminate()
  if max_seconds and time.monotonic()-started>max_seconds:stop_reason='Bounded test time limit';p.terminate()
  status=Path('/proc/%s/status'%p.pid).read_text();rss=next(int(v.split()[1]) for v in status.splitlines() if v.startswith('VmRSS:'));peak=max(peak,rss)
 except (FileNotFoundError,StopIteration):pass
 time.sleep(1)
usage=resource.getrusage(resource.RUSAGE_CHILDREN);result={'command':['/usr/bin/blender',*args],'exit_code':p.returncode,'peak_sampled_rss_kib':peak,'peak_os_rss_kib':usage.ru_maxrss,'minimum_system_available_kib':minimum,'stop_reason':stop_reason}
(R/(label+'_memory.json')).write_text(json.dumps(result,indent=2));print('MEMORY_RESULT',json.dumps(result),flush=True);sys.exit(p.returncode)
