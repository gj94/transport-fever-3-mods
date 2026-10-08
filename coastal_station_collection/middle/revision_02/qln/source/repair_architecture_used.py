"""Localized historical Kollam entrance-pattern correction from immutable scene032e..."""
import bpy,json,hashlib,shutil,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'qln';P=ROOT/'revision_02/qln';P.mkdir(parents=True,exist_ok=True)
for folder in ('source','renders','export'):(P/folder).mkdir(exist_ok=True)
for f in (OLD/'source').glob('*'):
 if f.is_file():shutil.copy2(f,P/'source'/f.name)
base=OLD/'QLN_coastal_station_v01.blend';basehash=hashlib.sha256(base.read_bytes()).hexdigest();assert basehash=='032e138121ab63188fb703ceb3238d9d33d13232bb1caa9fce7af81d5aa327d1'
bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene
removed=[]
for o in list(S.objects):
 if o.name.startswith('Kollam red-white stepped entry panel'):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections.new('08B_KOLLAM_HISTORICAL_PATTERNED_FACADE_PANELS');S.collection.children.link(col)
red=bpy.data.materials['Oxide red masonry and tile'];white=bpy.data.materials['Chalk white masonry'];created=[];batch={}
def box(n,p,d,m):
 x,y,z=[q/2 for q in d];v=[(p[0]+a,p[1]+b,p[2]+c)for a,b,c in[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]];f=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
 key=(n,m.name)
 if key not in batch:batch[key]=[[],[],m]
 vs,fs,_=batch[key];n0=len(vs);vs.extend(v);fs.extend(tuple(n0+i for i in face)for face in f)
# Two source-observed facade infills flank the central public opening; they are not doors.
# Reconstructed widths match the existing portico and preserve the central public path.
F=1.018;bx=-63;fy=-34;tw=.48;th=.355
for j in range(10):
 for i in range(22):box('Kollam broad left stepped diagonal mosaic', (bx-23.6+(i+.5)*tw,fy-.20,F+(j+.5)*th),(tw,.16,th),red if (i+j)%4<2 else white)
# Right panel is pointed, with a filled red-white pattern, as photographed Sep2020.
for j in range(10):
 half=4.08*(1-(j+.5)/10)
 for i in range(-9,9):
  left=max(i*tw,-half);right=min((i+1)*tw,half)
  if right>left:box('Kollam pointed right stepped diagonal mosaic',(bx+15.8+(left+right)/2,fy-.20,F+(j+.5)*th),(right-left,.16,th),red if (i+j)%4<2 else white)
for (n,mn),(v,f,m) in batch.items():
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);col.objects.link(o);me.materials.append(m);created.append(o.name)
cam=bpy.data.objects['04_FACADE_AND_APPROACH'];oldcam={'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens};cam.location=(-80,-93,13.5);cam.rotation_euler=(Vector((-63,-34,4.9))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=42
S['facade_revision']='QLNv02: filled red-white stepped diagonal rectangle and pointed panel beside historical entrance, based on Sep2020-capture photograph; tighter facade camera04.';S['base_blend_sha256']=basehash
out=P/'QLN_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),P/'source/repair_architecture_used.py')
qa=json.loads((OLD/'BUILD_QA.json').read_text());qa.update({'blend':out.name,'revision':'historical facade panel and camera revision02','base_blend_sha256':basehash,'repair_script_sha256':repairhash,'mesh_objects':sum(o.type=='MESH'for o in S.objects),'total_objects':len(S.objects),'vertices':sum(len(o.data.vertices)for o in S.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons)for o in S.objects if o.type=='MESH')});(P/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'removed_objects':removed,'created_objects':created,'camera04_before':oldcam,'camera04_after':{'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens},'observed_source':'Google Maps Sep2020 capture/Apr2022 header, QLN_google_facade_capture_2020-09.png. Filled broad red-white stepped diagonal rectangle at left, pointed patterned panel at right of portico.','uncertainty':'Panel dimensions and pattern tessellation reconstructed; cladding covers incidental generic openings in these photographed solid facade zones. Central public entrance and remote ramp doorway remain unchanged.','unchanged':'Yard/rail/platform/bridge geometry, upper office and all interior furnishings. Camera04 only changed; surface cladding added at front of entrance-side walls.','retained_views':['03_platform_track_details.png','05_ticket_interior.png'],'rerender_views':['01_full_mapped_layout.png','02_station_and_platforms.png','04_facade_and_approach.png']};(P/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2))
oldrp=json.loads((OLD/'RENDER_PROVENANCE.json').read_text());rp=dict(oldrp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
for r in oldrp['renders']:
 if Path(r['file']).name in rev['retained_views'] and r['source_blend_sha256']==basehash:
  rr=dict(r);rr['source_blend_sha256']=basehash;rr['retained_from_immutable_base']=True;rr['retention_reason']='Entrance-side external cladding is outside this platform/interior camera; subject, camera and illumination unchanged.';shutil.copy2(OLD/r['file'],P/r['file']);rp['renders'].append(rr)
(P/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2))
report=(OLD/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Historical facade revision02\nThe two small placeholder step outlines were replaced by filled red-white stepped-diagonal facade panels: a broad left rectangle and pointed right panel matching the September2020 photograph. These are wall infills, not public doors. The central public path, remote approach ramp and passed upper-office/bridge routes are unchanged. Camera04 is closer for an inspectable central facade; views01,02,04 were rerendered, with unaffected platform03 and interior05 explicitly retaining their immutable source hash. See ARCHITECTURE_REVISION.json and the exact repair script.\n';(P/'SOURCES_AND_UNCERTAINTIES.md').write_text(report)
print('REVISED',json.dumps(rev),flush=True)
