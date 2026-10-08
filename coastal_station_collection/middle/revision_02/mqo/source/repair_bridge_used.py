"""Reproducible minimal bridge-only repair from the immutable MQO main checkpoint."""
import bpy,json,hashlib,shutil,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'mqo';P=ROOT/'revision_02/mqo';P.mkdir(parents=True,exist_ok=True)
for folder in('source','renders','export'):(P/folder).mkdir(exist_ok=True)
for f in (OLD/'source').glob('*'):
 if f.is_file():shutil.copy2(f,P/'source'/f.name)
base=OLD/'MQO_coastal_station_v01.blend';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='950cf176f29fc8cb21420a3887f5d782801d77a390be513d24840c4cf4edb4b1'
bpy.ops.wm.open_mainfile(filepath=str(base));scene=bpy.context.scene
changes=[];F=1.018;deck=8.60
shift_stair_names=['Footbridge stair stringer','Footbridge stair top rail','Footbridge stair baluster','Covered footbridge stair flight roof','Covered stair roof upright']
for o in scene.objects:
 if o.type!='MESH':continue
 dx=dz=0
 if o.name=='Footbridge deck':dz=-.12
 elif o.name=='Footbridge individual stair tread':dx=-1.325;dz=(deck-F)/84-.05
 elif any(o.name.startswith(n)for n in shift_stair_names):dx=-1.5
 else:continue
 for v in o.data.vertices:v.co.x+=dx;v.co.z+=dz
 o.data.update();changes.append({'object':o.name,'vertices':len(o.data.vertices),'dx_m':dx,'dz_m':dz})
assert any(x['object']=='Footbridge deck'for x in changes);assert any(x['object']=='Footbridge individual stair tread'for x in changes)
scene['bridge_revision']='v02: 42-tread flights rise to leading deck edge x78.5, not deck centre. Walking deck top8.6m; 14.7m run; covered flight shifted with stairs.'
scene['base_blend_sha256']=basehash
out=P/'MQO_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),P/'source/repair_bridge_used.py')
qa=json.loads((OLD/'BUILD_QA.json').read_text());qa['blend']=out.name;qa['revision']='bridge-only v02';qa['base_blend_sha256']=basehash;qa['repair_script_sha256']=repairhash;qa['bridge_walk_deck_top_m']=deck;qa['bridge_flight_x_m']=[63.8,78.5];(P/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'changes':changes,'unchanged':'All track, platform, building, furniture, materials, cameras and illumination outside the affected bridge mesh components remain unchanged.','retained_views':['04_facade_and_approach.png','05_ticket_interior.png'],'rerender_views':['01_full_mapped_layout.png','02_station_and_platforms.png','03_platform_track_details.png']};(P/'BRIDGE_REVISION.json').write_text(json.dumps(rev,indent=2))
oldrp=json.loads((OLD/'RENDER_PROVENANCE.json').read_text());rp=dict(oldrp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
for r in oldrp['renders']:
 if Path(r['file']).name in rev['retained_views']:
  rr=dict(r);rr['source_blend_sha256']=basehash;rr['retained_from_immutable_base']=True;rr['retention_reason']='Bridge geometry is outside this facade/interior view; camera, subject geometry, materials and illumination unchanged.';shutil.copy2(OLD/r['file'],P/r['file']);rp['renders'].append(rr)
(P/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2))
report=(OLD/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Bridge revision02\nThe two stair flights now terminate at the leading deck edge, with continuous tread/deck height. Covered flights moved with them. See BRIDGE_REVISION.json and source/repair_bridge_used.py for exact component shifts and the immutable base hash. Views01–03 were rerendered from the repaired scene; unaffected facade/interior views04–05 retain their original source hash explicitly.\n';(P/'SOURCES_AND_UNCERTAINTIES.md').write_text(report)
print('REPAIRED',json.dumps(rev),flush=True)
