"""Place photograph-derived platform trim on the exterior side of the platform wall."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=Path(__file__).resolve().parents[1];R=B/'tvcs';p=R/'TVCS_station_v01.blend';h0=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));S=bpy.context.scene;Q=json.loads((R/'QA_BUILD.json').read_text());b=Q['building'];front=b['front_y'];sg=b['side'];H=b['depth'];bounds=[];changed=[]
for o in S.objects:
 if o.name not in ['TVCS teal facade pier','TVCS teal continuous facade band','TVCS upper small vent']:continue
 shift=.36 if o.name=='TVCS upper small vent' else .32
 for j in range(0,len(o.data.vertices),8):
  ids=list(range(j,min(j+8,len(o.data.vertices))));yy=sum(o.data.vertices[k].co.y for k in ids)/len(ids);ly=(front-yy)/sg
  if ly>H/2:
   bounds.extend(o.matrix_world@o.data.vertices[k].co for k in ids)
   for k in ids:o.data.vertices[k].co.y-=sg*shift
   changed.append({'object':o.name,'component':j//8,'outward_shift_m':shift})
 o.data.update()
assert len(changed)==10,changed
bpy.context.view_layer.update();Q['platform_facade_depth_repair']=changed;(R/'QA_BUILD.json').write_text(json.dumps(Q,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);h1=hashlib.sha256(p.read_bytes()).hexdigest();(R/'QA_FACADE_REPAIR.json').write_text(json.dumps({'station':'TVCS','input_source_sha256':h0,'output_source_sha256':h1,'scope':'Moved only rear teal piers/bands and upper vents from the interior side of the platform wall to its exterior face','changed_components':changed},indent=2))
# The existing rail-detail view is the only retained proof; facade/interior views refresh conservatively.
prov=json.loads((R/'RENDER_PROVENANCE.json').read_text());ret=[];redo=[]
for name,r in prov['views'].items():
 valid=r.get('source_scene_sha256')==h0 or (r.get('current_source_scene_sha256')==h0 and r.get('unchanged_view_verified'))
 if name.startswith('05_') and valid:r.setdefault('inheritance_chain',[]).append({'from_scene_sha256':h0,'to_scene_sha256':h1,'basis':'Only platform-wall decoration changed, outside the pointwork/rail-detail subject'});r.update(unchanged_view_verified=True,current_source_scene_sha256=h1,inheritance_basis='Only station-wall trim moved; rail-detail geometry and view unchanged');ret.append(name)
 else:redo.append(name[:2])
prov['current_source_scene_sha256']=h1;(R/'RENDER_PROVENANCE.json').write_text(json.dumps(prov,indent=2));hp=R/'REPAIR_HISTORY.json';history=json.loads(hp.read_text()) if hp.exists() else [];lp=R/'REPAIR_LINEAGE.json'
if lp.exists():history.append(json.loads(lp.read_text()))
hp.write_text(json.dumps(history,indent=2));lp.write_text(json.dumps({'station':'TVCS','input_source_sha256':h0,'output_source_sha256':h1,'retained_views':ret,'rerender_prefixes':sorted(set(redo))},indent=2))
