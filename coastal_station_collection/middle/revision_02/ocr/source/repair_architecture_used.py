"""Narrow OCR noticeboard correction with retained exterior-view lineage."""
import bpy,json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'ocr';P=ROOT/'revision_02/ocr';P.mkdir(parents=True,exist_ok=True)
for f in ('source','renders','export'):(P/f).mkdir(exist_ok=True)
for f in (OLD/'source').glob('*'):
 if f.is_file():shutil.copy2(f,P/'source'/f.name)
base=OLD/'OCR_coastal_station_v01.blend';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='4650621b0a296ec30fc488b63ba13ae8cefae1df7edf6f2bef0fd6d248aaa3f8'
bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene
oldx=-1-18.8/2+18.8/6+(18.8/3)*.28;newx=-1-18.8/2+18.8/5;dx=newx-oldx;y=7.1+9.1/2-.15;changed=[]
for o in bpy.data.collections['07_FURNISHED_INTERIORS_RECONSTRUCTED'].objects:
 if o.type!='MESH' or not any(o.name.startswith(n) for n in ['Station noticeboard timber frame','Noticeboard felt','Notice sheet','Notice printed line']):continue
 count=0
 for v in o.data.vertices:
  if abs(v.co.x-oldx)<.85 and abs(v.co.y-y)<.15:v.co.x+=dx;count+=1
 if count:o.data.update();changed.append({'object':o.name,'vertices_moved':count,'dx_m':dx})
assert len(changed)==4 and sum(x['vertices_moved']for x in changed)==208,changed
S['fixture_revision']='OCRv02: ticket-room noticeboard moved from window overlap to adjacent solid masonry pier; all other geometry/cameras unchanged.';S['base_blend_sha256']=basehash
out=P/'OCR_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),P/'source/repair_architecture_used.py')
qa=json.loads((OLD/'BUILD_QA.json').read_text());qa.update({'revision':'noticeboard placement revision02','base_blend_sha256':basehash,'repair_script_sha256':repairhash});(P/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'changes':changed,'noticeboard_old_centre_m':[oldx,y,2.918],'noticeboard_new_centre_m':[newx,y,2.918],'unchanged':'All rail/platform/building/furniture other than one noticeboard assembly; all cameras and illumination unchanged.','retained_views':['01_full_mapped_layout.png','02_station_and_platforms.png','03_platform_track_details.png','04_facade_and_approach.png'],'rerender_views':['05_ticket_interior.png']};(P/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2))
rp=json.loads((OLD/'RENDER_PROVENANCE.json').read_text());oldrp=dict(rp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
for r in oldrp['renders']:
 if Path(r['file']).name in rev['retained_views']:
  rr=dict(r);rr['source_blend_sha256']=basehash;rr['retained_from_immutable_base']=True;rr['retention_reason']='One internal ticket-room noticeboard moved; exterior subject/camera/illumination unchanged and noticeboard not visible in these exterior views.';shutil.copy2(OLD/r['file'],P/r['file']);rp['renders'].append(rr)
(P/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2))
report=(OLD/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Fixture revision02\nOne ticket-room noticeboard assembly was shifted onto the adjacent solid masonry pier, clearing the blue glazed window. Only the affected interior05 was refreshed; exterior01–04 explicitly retain their base-scene hashes. All rail, building, platform and circulation geometry is unchanged. See ARCHITECTURE_REVISION.json and the exact repair script.\n';(P/'SOURCES_AND_UNCERTAINTIES.md').write_text(report)
print(json.dumps(rev),flush=True)
