"""Read-only source/image/cache/dependency audit; writes only audit evidence.
Run after all gallery rendering. This is not native game validation.
"""
from pathlib import Path
import hashlib,json
from PIL import Image
P=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
queue=[(k,v) for k in ['1A','CC','3A','2A','SL','2S','GS'] for v in ['interior','exterior']]+[('3A','bay'),('CC','chair_detail'),('1A','cabin_entry'),('3A','hvac'),('3A','bogie'),('3A','door'),('3A','toilet')]
report={'status':'pass','native_game_runtime':'Not converted or validated in Transport Fever 3','sources':[],'views':[],'external_dependencies':[],'limitations':['Editable-font tessellation warnings remain in source/FBX reports.','Close-range CC tray and armrest bevels show faceting.','Undenoised interior renders retain grain.','Checkpoint spec.camera_matrix retains a pre-evaluation saved transform and is not a verified evaluated camera matrix; per-view camera_xyz/lens are checked against the renderer configuration and reviewed pixels.']}
for k in ['1A','2A','3A','2S','CC','SL','GS']:
 r=json.loads((P/'qa/source_geometry'/f'LHB_{k}_geometry.json').read_text());assert r['status'] in ('pass','pass_with_warnings')
 for ext in ['blend','fbx']:assert r['sha256'][ext]==sha(P/'models'/f'LHB_{k}.{ext}')
 report['sources'].append({'variant':k,'status':r['status'],'sha256':r['sha256']})
deps={}
for k,v in queue:
 f=P/'qa'/f'render_{k}_{v}.json';r=json.loads(f.read_text());im=P/r['image'];w=r['sampling_workflow'];spec=w['spec'];fp=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()
 assert r['source_sha256']==sha(P/r['source']) and r['image_sha256']==sha(im)==w['image_sha256']
 assert r['samples']==512 and r['actual_geometry_render'] and not r['denoising']
 assert w['total_uniform_samples']==512 and len(w['batches'])==8 and not w['adaptive_sampling'] and fp==w['fingerprint']
 with Image.open(im) as image:assert image.size==(1400,840);image.verify()
 cache=P/'previews/.checkpoints'/im.stem
 for i,b in enumerate(w['batches']):
  assert b['fingerprint']==fp and b['samples']==64 and b['seed']==104729*(i+1)+17 and b['sha256']==sha(cache/b['file'])
 assert w['combined_linear_sha256']==sha(cache/'combined_linear.exr')
 ident=spec['identity']
 assert ident['renderer_sha256']==sha(P/'render_lhb_detail.py')
 for name,d in ident['presentation_modules'].items():
  candidates=[p for p in P.rglob('*.py') if p.name==name or p.parent.name=='render_provenance']
  if not any(sha(p)==d['sha256'] for p in candidates):
   p=Path(d['resolved_path']);assert p.exists() and sha(p)==d['sha256'];rel='/'.join(p.parts[p.parts.index('vande_bharat_detail_v02'):]);deps[rel]={'path':rel,'sha256':d['sha256'],'size':p.stat().st_size}
 for name,d in ident['loaded_image_dependencies'].items():
  p=P.parent/'wap7_photoreal_v02/environment'/name;assert p.exists() and sha(p)==d['sha256']
  rel='wap7_photoreal_v02/environment/'+name;deps[rel]={'path':rel,'sha256':d['sha256'],'size':p.stat().st_size}
 expected=(20,-30,8.5) if v=='exterior' else ((-7.18,.25,2.55) if k=='1A' else ((-7.94,.70,2.64) if k in ['2A','3A','SL','GS'] else (-8.75,-.23 if k=='CC' else 0,2.63))) if v=='interior' else {'bay':(-.15,1.45,2.57),'chair_detail':(-8.72,-.05,2.35),'cabin_entry':(-7.15,-1.30,2.59),'hvac':(12,-4.8,6.7),'bogie':(10.7,-5.5,1.7),'door':(14,-7,3.30),'toilet':(10.0,.73,2.76)}[v]
 assert all(abs(a-b)<1e-5 for a,b in zip(r['camera_xyz'],expected))
 lens=48 if v=='exterior' else (17 if k=='1A' else 22) if v=='interior' else {'bay':19,'chair_detail':25,'cabin_entry':19,'hvac':54,'bogie':46,'door':45,'toilet':18}[v]
 assert abs(r['camera_lens_mm']-lens)<1e-5
 report['views'].append({'camera_xyz_verified':r['camera_xyz'],'camera_lens_mm':r['camera_lens_mm'],'checkpoint_matrix_scope':'historical pre-evaluation metadata, not verified evaluated transform','variant':k,'view':v,'record_sha256':sha(f),'image_sha256':sha(im),'cached_batches_verified':8,'fingerprint':fp})
report['external_dependencies']=list(deps.values());report['complete_views']=len(report['views'])
out=P/'qa/final_delivery_audit.json';out.write_text(json.dumps(report,indent=2)+'\n');print(out,report['status'],len(report['views']))
