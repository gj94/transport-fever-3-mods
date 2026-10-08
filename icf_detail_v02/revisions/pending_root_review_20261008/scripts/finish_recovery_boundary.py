"""Preserve active checkpoint identity, attest dependencies, switch only after completed image."""
from pathlib import Path
import hashlib,json,time,datetime,os,shutil
p=Path(__file__).resolve().parents[1]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
active=p/'scripts/run_checkpoint_renderer.py';successor=p/'scripts/run_checkpoint_renderer_externaldeps.py'
manifest=p/'1A/renders/.checkpoints/cabin_diagonal_final/manifest.json'
spec=json.loads(manifest.read_text())['spec']
expected={Path(k):v for k,v in spec['identity']['presentation_modules'].items()}
expected[p/'1A/ICF_1A_master.blend']=spec['identity']['source_sha256']
expected[p/'scripts/render_detail.py']=spec['identity']['renderer_sha256']
assert all(sha(f)==v for f,v in expected.items())
report={'time_started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'active_fingerprint':json.loads(manifest.read_text())['fingerprint'],'dependency_sha256':{str(k):v for k,v in expected.items()},'before_all_match':True,'after_all_match':None,'switch_complete':False}
report_path=p/'qa/recovery_boundary_attestation.json';report_path.write_text(json.dumps(report,indent=2))
side=p/'1A/renders/cabin_diagonal_final.json'
while not side.exists():time.sleep(.25)
d=json.loads(side.read_text());assert sha(side.with_suffix('.png'))==d['image_sha256'];assert all(sha(f)==v for f,v in expected.items())
assert d['sampling_workflow']['fingerprint']==report['active_fingerprint']
old=p/'qa/frozen_renderer_versions'/('run_checkpoint_renderer_'+sha(active)+'.py');old.parent.mkdir(exist_ok=True);shutil.copy2(active,old)
tmp=active.with_suffix('.tmp');shutil.copy2(successor,tmp);os.replace(tmp,active)
report.update(after_all_match=True,switch_complete=True,time_finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=d['image_sha256'],preserved_original_wrapper=str(old.relative_to(p)),successor_wrapper_sha256=sha(active))
report_path.write_text(json.dumps(report,indent=2));print('SAFE_FRAME_BOUNDARY_SWITCH_COMPLETE',flush=True)
