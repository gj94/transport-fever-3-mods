"""Three bounded final proof-view revisions; exact native/source lineage is retained."""
import bpy,json,hashlib,shutil,sys,runpy,gc
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];jobs=json.loads((R/'final_camera_revision_jobs.json').read_text())
for job in jobs:
 code=job['code'];old=R/job['base'];p=R/job['target'];p.mkdir(parents=True,exist_ok=True)
 for n in('source','renders','export'):(p/n).mkdir(exist_ok=True)
 for f in (old/'source').glob('*'):
  if f.is_file():shutil.copy2(f,p/'source'/f.name)
 if (old/'ARCHITECTURE_REVISION.json').exists():
  shutil.copy2(old/'ARCHITECTURE_REVISION.json',p/'source/prior_canopy_revision.json');shutil.copy2(old/'source/repair_architecture_used.py',p/'source/prior_canopy_revision_used.py')
 source=old/f'{code}_coastal_station_v01.blend';basehash=hashlib.sha256(source.read_bytes()).hexdigest();assert basehash==job['base_sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;changes=[]
 if code=='KFI':
  roof=bpy.data.objects['Kappil rose sloping veranda roof'];count=0
  for v in roof.data.vertices:
   if abs(v.co.y+5)<.01:v.co.z-=.268;count+=1
  roof.data.update();changes.append({'object':roof.name,'upper_edge_vertices_lowered':count,'dz_m':-.268,'reason':'Keep the photographed blue parapet accents above the canopy attachment.'})
  beam=bpy.data.objects['Kappil rose support beam over peach piers']
  for v in beam.data.vertices:v.co.z-=.15
  beam.data.update();changes.append({'object':beam.name,'dz_m':-.15})
  o=bpy.data.objects['Veranda column'];count=0
  for v in o.data.vertices:
   if v.co.z>3.9:v.co.z=3.85;count+=1
  o.data.update();changes.append({'object':o.name,'top_vertices_lowered':count,'top_z_m':3.85})
 cam=bpy.data.objects['04_FACADE_AND_APPROACH'];oldcam={'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens};cam.location=job['camera_location'];cam.rotation_euler=(Vector(job['camera_target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=job['lens'];scene['proof_view_revision']=job['reason'];scene['base_blend_sha256']=basehash
 out=p/f'{code}_coastal_station_v01.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);repairhash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();shutil.copy2(Path(__file__),p/'source/repair_architecture_used.py');(p/'source/camera_revision_input.json').write_text(json.dumps(job,indent=2))
 qa=json.loads((old/'BUILD_QA.json').read_text());qa.update({'revision':job['reason'],'base_blend_sha256':basehash,'repair_script_sha256':repairhash});(p/'BUILD_QA.json').write_text(json.dumps(qa,indent=2))
 rev={'base_blend_sha256':basehash,'repaired_blend_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'repair_script_sha256':repairhash,'camera04_before':oldcam,'camera04_after':{'location':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens},'geometry_changes':changes,'reason':job['reason'],'retained_views':job['retain'],'rerender_views':job['rerender'],'source_geometry_note':'Track, platform, room and furnishing geometry unchanged. KFI only adjusts high canopy/support attachment; EVA/CRY are camera-only.'};(p/'ARCHITECTURE_REVISION.json').write_text(json.dumps(rev,indent=2))
 rp=json.loads((old/'RENDER_PROVENANCE.json').read_text());oldrp=dict(rp);rp['blend_sha256']=rev['repaired_blend_sha256'];rp['renders']=[]
 for v in oldrp['renders']:
  if Path(v['file']).name in job['retain']:
   rr=dict(v);rr['retained_from_immutable_base']=True;rr['retention_reason']='Unchanged subject/camera/illumination; the revised source-facing proof camera is04. KFI interior is unaffected by the external high canopy adjustment.';shutil.copy2(old/v['file'],p/v['file']);rp['renders'].append(rr)
 (p/'RENDER_PROVENANCE.json').write_text(json.dumps(rp,indent=2));report=(old/'SOURCES_AND_UNCERTAINTIES.md').read_text();report+='\n\n## Final source-facing proof view\n'+job['reason']+' Geometry and camera changes are recorded exactly in ARCHITECTURE_REVISION.json and source/camera_revision_input.json. Retained image subjects have unchanged geometry/camera/lighting and keep their actual source hashes.\n';(p/'SOURCES_AND_UNCERTAINTIES.md').write_text(report);print('CAMERA_REVISION_SAVED',code,rev['repaired_blend_sha256'],flush=True);gc.collect()
# Exact saved-scene material evidence for every preferred final station scene.
w=json.loads((R/'WORKSTATE.json').read_text());preferred=w['preferred_candidate_paths'];preferred.update({j['code']:j['target']for j in jobs});palette_jobs=[]
for code,rel in preferred.items():palette_jobs.append({'station_code':code,'blend_path':str((R/rel/f'{code}_coastal_station_v01.blend').resolve()),'output_path':str((R/'portable_colour_revision_02/palettes'/f'{code}.json').resolve())})
palette_input=R/'portable_colour_revision_02/palette_jobs.json';palette_input.parent.mkdir(exist_ok=True);palette_input.write_text(json.dumps(palette_jobs,indent=2));sys.argv=['extract_blend_palettes.py','--',str(palette_input)];runpy.run_path(str(R/'scripts/extract_blend_palettes.py'),run_name='__main__')
# Export only the three changed native scenes. Colour JSON repair follows outside Blender.
sys.argv=['export_source_cohort.py','--','revision_03:KFI','revision_02:EVA','revision_02:CRY'];runpy.run_path(str(R/'scripts/export_source_cohort.py'),run_name='__main__')
