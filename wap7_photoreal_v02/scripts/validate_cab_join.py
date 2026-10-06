"""Run against the combined master; no save, no changes to its source file."""
import bpy, importlib.util, json, hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cab_interiors',P/'components/cab_interiors.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
source_path=Path(bpy.data.filepath)
def file_hash(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
source_sha=file_hash(source_path)
report={'source_file_sha256_before':source_sha,'source_blend':bpy.data.filepath,'tests':[],'scope':'Read-only test of saved combined geometry; doors temporarily posed in memory only'}
for index,e in[(1,1),(2,-1)]:
 original_angle=float(bpy.data.objects[f'CABV02_{index}_Rear_door_hinge'].get('open_angle_deg',0))
 c.set_rear_door_angle(index,90)
 dg=bpy.context.evaluated_depsgraph_get();tests=[]
 for y in[-.25,0,.25]:
  for z in[1.73,2.05,2.40,2.75,3.10,3.42]:
   a=Vector((e*6.80,e*y,z));direction=Vector((e,0,0));distance=1.13
   hit,point,normal,face,obj,matrix=bpy.context.scene.ray_cast(dg,a,direction,distance=distance)
   tests.append({'y':e*y,'z':z,'clear':not hit,'hit':obj.name if hit else None,'point':list(point) if hit else None})
 cab_clearance=[]
 # A 600mm edge/centre band, offset25mm away from the open door leaf.
 for y in[-.325,-.025,.275]:
  for z in[1.653,2.05,2.40,2.75,3.10,3.480]:
   a=Vector((e*7.17,e*y,z));direction=Vector((e,0,0))
   hit,point,normal,face,obj,matrix=bpy.context.scene.ray_cast(dg,a,direction,distance=.76)
   cab_clearance.append({'y':e*y,'z':z,'clear':not hit,'hit':obj.name if hit else None,'point':list(point) if hit else None})
 machinery_headroom=[]
 for y in[-.25,0,.25]:
  hit,point,normal,face,obj,matrix=bpy.context.scene.ray_cast(dg,Vector((e*6.80,e*y,3.470)),Vector((e,0,0)),distance=.37)
  machinery_headroom.append({'y':e*y,'z':3.470,'clear':not hit,'hit':obj.name if hit else None,'point':list(point) if hit else None})
 report['tests'].append({'cab':index,'rays':tests,'all_18_passage_lines_clear':all(t['clear'] for t in tests),'cab_600mm_edge_and_center_rays':cab_clearance,'cab_clearance_ray_band_center_offset_m':-.025,'cab_clearance_pass':all(t['clear'] for t in cab_clearance),'machinery_headroom_rays':machinery_headroom,'machinery_headroom_pass':all(t['clear'] for t in machinery_headroom)})
 c.set_rear_door_angle(index,original_angle)
report['pass']=all(t['all_18_passage_lines_clear'] and t['cab_clearance_pass'] and t['machinery_headroom_pass'] for t in report['tests'])
report['source_file_sha256_after']=file_hash(source_path);report['source_file_unchanged']=report['source_file_sha256_after']==source_sha
report['pass']=report['pass'] and report['source_file_unchanged']
(P/'qa/cab/combined_join_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
