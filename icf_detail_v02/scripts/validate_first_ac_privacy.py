"""Actual-source top-closure check; no claims of engineering certification."""
import bpy,json,math,hashlib
from pathlib import Path
p=Path(bpy.data.filepath);root=bpy.data.objects['ICF_1A_ROOT']
caps=[o for o in root.children_recursive if '_arched_privacy_bulkhead' in o.name]
corr=[o for o in root.children_recursive if '_corridor_top_privacy_panel' in o.name]
def ceiling(y):return 3.356+.587*math.sqrt(max(0,1-(y/1.556)**2))
errors=[]
for o in caps:
 pts=[o.matrix_world@v.co for v in o.data.vertices];top=[v for v in pts if v.z>3.42]
 if not top or max(abs(v.z-ceiling(v.y)) for v in top)>.005:errors.append(o.name+': ceiling contact')
 if min(v.z for v in pts)>3.42:errors.append(o.name+': lower partition gap')
for o in corr:
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 if min(v.z for v in pts)>3.42 or abs(max(v.z for v in pts)-ceiling(.57))>.005:errors.append(o.name+': vertical closure')
checks={'seven_bulkheads_present':len(caps)==7,'six_corridor_top_panels_present':len(corr)==6,'partition_and_ceiling_contacts':not errors,'capacity_preserved':root['physical_capacity']==18,'berth_count_preserved':root['physical_berths']==18}
r={'variant':'1A','build_pass':root['build_pass'],'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':checks,'errors':errors,'passed':all(checks.values())}
(p.parent/'qa/first_ac_privacy_checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if not r['passed']:raise RuntimeError('First AC privacy closure QA failed')
