"""Focused source geometry tests for r10 interior support and paired-seat revisions."""
import bpy,json,hashlib
from pathlib import Path
root=next(o for o in bpy.data.objects if o.name.startswith('ICF_') and o.name.endswith('_ROOT'))
v=root['variant'];folder=Path(bpy.data.filepath).parent
meshes=[o for o in root.children_recursive if o.type=='MESH']
def bounds(o):
 p=[o.matrix_world@x.co for x in o.data.vertices]
 return [(min(x[i] for x in p),max(x[i] for x in p)) for i in range(3)]
def intersects(a,b):return all(a[i][0]<=b[i][1]+1e-5 and b[i][0]<=a[i][1]+1e-5 for i in range(3))
checks={};details={}
if v=='1A':
 feet=[o for o in meshes if '_lower_base_foot' in o.name];bases=[bounds(o) for o in meshes if '_lower_berth_base' in o.name]
 floor=bounds(bpy.data.objects['Interior floor seamless vinyl'])
 checks['all_36_lower_base_feet_present']=len(feet)==36
 checks['feet_bridge_floor_and_base']=all(intersects(bounds(o),floor) and any(intersects(bounds(o),b) for b in bases) for o in feet)
 details['base_feet_count']=len(feet)
if v in ['2A','3A','SL']:
 pans=[o for o in meshes if '_support_pan' in o.name and '_side_' in o.name]
 posts=[bounds(o) for o in meshes if '_side_berth_support' in o.name]
 expected={'2A':14,'3A':16,'SL':18}[v]
 checks['side_berth_pans_present']=len(pans)==expected
 checks['side_pans_reach_corner_posts']=all(sum(intersects(bounds(p),b) for b in posts)>=2 for p in pans)
 legs=[o for o in meshes if '_side_lower_floor_leg' in o.name]
 floor=bounds(bpy.data.objects['Interior floor seamless vinyl'])
 checks['side_lower_legs_reach_floor']=all(bounds(o)[2][0]<=floor[2][1]+1e-5 for o in legs)
 details['side_pan_count']=len(pans);details['side_lower_leg_count']=len(legs)
if v in ['2S','GS']:
 prefix='Low-back seat shell shaped upholstery' if v=='2S' else 'GS full-width bench backrest'
 backs=[bounds(o) for o in meshes if o.name.startswith(prefix)]
 rowbounds=[]
 for r in range(18):
  x=-7.14+r*.84+(-.08 if r%2==0 else .08)-(.25 if r%2==0 else -.25)
  found=[b for b in backs if abs((b[0][0]+b[0][1])/2-x)<.06]
  rowbounds.append((min(b[0][0] for b in found),max(b[0][1] for b in found)))
 gaps=[rowbounds[r+1][0]-rowbounds[r][1] for r in range(1,17,2)]
 checks['paired_rear_backrests_separated']=min(gaps)>.009
 details['minimum_paired_back_gap_m']=min(gaps);details['facing_cushion_front_gap_m']=.47
report={'variant':v,'build_pass':root.get('build_pass'),'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'checks':checks,'details':details,'passed':all(checks.values()),'scope':'Static focused source support contacts and paired-seat clearances; no dynamic or human fit certification'}
(folder/'qa/interior_support_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if not report['passed']:raise RuntimeError('Interior support QA failed')
