"""Narrow MYY wall-fixture correction with retained exterior-view lineage."""
import bpy,json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'myy';P=ROOT/'revision_02/myy';P.mkdir(parents=True,exist_ok=True)
for f in ('source','renders','export'):(P/f).mkdir(exist_ok=True)
for f in (OLD/'source').glob('*'):
 if f.is_file():shutil.copy2(f,P/'source'/f.name)
base=OLD/'MYY_coastal_station_v01.blend';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='1fc4b4970aacf67e7e0a77261feaef9135d85bad4cdc371996680e57b5a723a2'
bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene
bx,by,bw,bd=-2.9,-.8,27.5,10.1;fronty=by+bd/2;roomw=bw/3;nbays=7;baywidth=bw/nbays;frontdoors=[bx];changed=[];shifts=[]
for ri in range(3):
 x=bx-bw/2+(ri+.5)*roomw;slots=[x+roomw*f for f in(.28,-.28,.12,-.12,.38,-.38) if all(abs(x+roomw*f-dd)>1.8 for dd in frontdoors)];oldnx=slots[0];oldtx=slots[-1];candidates=[bx-bw/2+j*baywidth for j in range(1,nbays) if x-roomw/2+.85 < bx-bw/2+j*baywidth < x+roomw/2-.85];nx=min(candidates,key=lambda q:abs(q-x));tx=max(candidates,key=lambda q:abs(q-nx));shifts.append({'room_index':ri,'notice_from_x':oldnx,'notice_to_x':nx,'television_from_x':oldtx if ri==1 else None,'television_to_x':tx if ri==1 else None})
 for o in bpy.data.collections['07_FURNISHED_INTERIORS_RECONSTRUCTED'].objects:
  if o.type!='MESH':continue
  isnotice=any(o.name.startswith(n)for n in['Station noticeboard timber frame','Noticeboard felt','Notice sheet','Notice printed line']);istv=ri==1 and any(o.name.startswith(n)for n in['Passenger information television','Television screen'])
  if not(isnotice or istv):continue
  oldx=oldnx if isnotice else oldtx;newx=nx if isnotice else tx;dx=newx-oldx;count=0
  for v in o.data.vertices:
   if abs(v.co.x-oldx)<(.85 if isnotice else .70) and abs(v.co.y-(fronty-.15))<.25:v.co.x+=dx;count+=1
  if count:o.data.update();changed.append({'object':o.name,'room':ri,'vertices_moved':count,'dx_m':dx})
assert sum(x['vertices_moved']for x in changed)==640,changed
S['fixture_revision']='MYYv02: noticeboards and waiting-room television moved to adjacent solid masonry piers; all other geometry/cameras unchanged.';S['base_blend_sha256']=basehash
out=P/'MYY_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),P/'source/repair_architecture_used.py')
qa=json.loads((OLD/'BUILD_QA.json').read_text());qa.update({'revision':'noticeboard placement revision02','base_blend_sha256':basehash,'repair_script_sha256':repairhash});(P/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'changes':changed,'fixture_shifts':shifts,'unchanged':'All rail/platform/building/furniture other than noticeboard/television placement; all cameras and illumination unchanged.','retained_views':['01_full_mapped_layout.png','02_station_and_platforms.png','03_platform_track_details.png','04_facade_and_approach.png'],'rerender_views':['05_ticket_interior.png']};(P/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2))
rp=json.loads((OLD/'RENDER_PROVENANCE.json').read_text());oldrp=dict(rp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
for r in oldrp['renders']:
 if Path(r['file']).name in rev['retained_views']:
  rr=dict(r);rr['source_blend_sha256']=basehash;rr['retained_from_immutable_base']=True;rr['retention_reason']='Internal wall fixtures moved; exterior subject/camera/illumination unchanged and changed fixtures not visible in these exterior views.';shutil.copy2(OLD/r['file'],P/r['file']);rp['renders'].append(rr)
(P/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2))
report=(OLD/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Fixture revision02\nNoticeboard assemblies and the waiting-room television were shifted onto solid masonry piers, clearing the glazed windows. Only the affected interior05 was refreshed; exterior01–04 explicitly retain their base-scene hashes. All rail, building, platform and circulation geometry is unchanged. See ARCHITECTURE_REVISION.json and the exact repair script.\n';(P/'SOURCES_AND_UNCERTAINTIES.md').write_text(report)
print(json.dumps(rev),flush=True)
