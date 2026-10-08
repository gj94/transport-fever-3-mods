"""Class-specific r11 privacy closure. Leaves the six r10 producers and masters unchanged.
Usage: blender -b -t 4 --python scripts/build_1a_r11.py
"""
from pathlib import Path
import sys,json,hashlib,datetime,math
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as b
old_manifest=json.loads((b.g.OUT/'1A/manifest.json').read_text())
b.BUILD_PASS='r11-1A'
original_finish=b.g.DETAIL_HOOK

def close_privacy():
 original_finish();g=b.g
 def ceiling(y):return 3.356+.587*math.sqrt(max(0,1-(y/1.556)**2))
 def cap(name,x):
  # Closed thin laminate prism follows the actual arched inner roof, with a tiny seam overlap.
  section=[(-1.50,3.414),(.58,3.414)]+[(.58-j*2.08/48,ceiling(.58-j*2.08/48)+.003) for j in range(49)]
  n=len(section);verts=[(xx,y,z) for xx in [x-.025,x+.025] for y,z in section]
  faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  ob=g.mesh(name+'_arched_privacy_bulkhead',verts,faces,g.CREAM,g.INTERIOR);ob['component']='first_ac_privacy_closure'
 start=-7.5
 for name,length in [('A',3),('B',3),('C',2),('D',2),('E',2),('F',3)]:
  cap('Cabin_'+name,start)
  top=ceiling(.57)+.003
  ob=g.box('Cabin_'+name+'_corridor_top_privacy_panel',(start+length/2,.57,(3.414+top)/2),(length,.045,top-3.414),g.CREAM,g.INTERIOR);ob['component']='first_ac_privacy_closure'
  start+=length
 cap('Cabin_F_end',7.5)
b.g.DETAIL_HOOK=close_privacy
manifest=b.g.build('1A',False)
# Preserve explanatory metadata while replacing every measured value from the new build.
old_manifest.update(manifest);old_manifest['build_pass']=b.BUILD_PASS
old_manifest['build_source_sha256']=dict(b.SOURCE_HASHES,**{Path(__file__).name:hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
old_manifest['texture_source_sha256']=b.TEXTURE_HASHES;old_manifest['build_time_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
old_manifest['detail_scope']=old_manifest.get('detail_scope',[])+['First-AC cabin/coupe bulkheads and corridor wall tops closed to arched ceiling']
old_manifest['rebuild_command']='blender -b -t 4 --python icf_detail_v02/scripts/build_1a_r11.py'
(b.g.OUT/'1A/manifest.json').write_text(json.dumps(old_manifest,indent=2))
