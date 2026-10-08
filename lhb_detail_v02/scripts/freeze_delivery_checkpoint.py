"""Freeze a curated portable checkpoint; never include stale or low-sample previews.
Usage: python scripts/freeze_delivery_checkpoint.py /absolute/new/checkpoint-dir
Evidence JSON remains byte-exact, including historical execution paths. The manifest retains local transport paths.
"""
from pathlib import Path
import hashlib,json,sys,subprocess
P=Path(__file__).resolve().parent.parent
subprocess.run([sys.executable,str(P/'scripts/build_gallery_index.py')],check=True)
D=Path(sys.argv[1]).resolve();assert not D.exists(),D
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=list(P.glob('*.py'))+[P/'README.md',P/'GALLERY.md',P/'DELIVERY_STATUS.json']+list((P/'docs').glob('*.md'))
paths += list((P/'scripts/render_provenance').glob('*.py'))
paths += [P/'scripts'/n for n in ['verify_lhb_detail.py','test_verify_lhb_detail.py','test_lhb_chair_detail.py','render_final_gallery.py','fix_1a_legend_orientation.py','freeze_delivery_checkpoint.py','checkpoint_render.py','run_checkpoint_renderer.py','render_dependency_identity.py','build_gallery_index.py']]
for k in ['1A','2A','3A','2S','CC','SL','GS']:
 paths += [P/'models'/f'LHB_{k}{suffix}' for suffix in ['.blend','.fbx','_manifest.json','_markers.json']]
 report=P/'qa/source_geometry'/f'LHB_{k}_geometry.json';r=json.loads(report.read_text())
 assert r['status'] in ['pass','pass_with_warnings'] and r['sha256']['blend']==sha(P/'models'/f'LHB_{k}.blend') and r['sha256']['fbx']==sha(P/'models'/f'LHB_{k}.fbx'),k
 paths.append(report)
paths += [P/'qa/source_geometry'/n for n in ['aggregate.json','SUMMARY.md','verifier_selftest.json']]
paths += [P/'qa'/n for n in ['cc_furnishing_checks.json','1A_legend_orientation_patch.json','final_gallery_progress.json','recovery_hash_audit.json']]
completed=[]
for p in (P/'qa').glob('render_*.json'):
 r=json.loads(p.read_text());source=P/r['source'];im=P/r['image']
 if r.get('resolution',[0])[0]<1400 or r.get('samples')!=512 or r.get('source_sha256')!=sha(source) or not im.exists():continue
 assert r['image_sha256']==sha(im)
 assert r.get('adaptive_min_samples',0)>=64 and not r.get('denoising',True) and r.get('actual_geometry_render')
 paths += [p,im];completed.append({'variant':r['variant'],'view':r['view'],'source_sha256':r['source_sha256'],'image_sha256':r['image_sha256']})
files=[]
for source in sorted(set(paths)):
 data=source.read_bytes();rel='lhb_detail_v02/'+str(source.relative_to(P))
 if source.suffix == '.md':
  data=data.decode().replace(str(P)+'/', '').replace(str(P),'lhb_detail_v02').encode()
 target=D/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 files.append({'path':rel,'local_path':str(target),'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),'mode':'100644'})
manifest={'repository':'gj94/transport-fever-3-mods','target_branch':'backup/coach-detail-overnight','base_main':'91bcc2899eeedccb7497374227d1c81562279640','snapshot_root':str(D),'status':'Seven class source/FBX geometry checks pass with disclosed editable-text warnings. Final gallery remains in progress until all 21 intended views are present. No native TF3 conversion or runtime validation.','completed_renders':completed,'files':files}
(D/'manifest.json').write_text(json.dumps(manifest,indent=2));print(D/'manifest.json',len(files),len(completed),flush=True)
