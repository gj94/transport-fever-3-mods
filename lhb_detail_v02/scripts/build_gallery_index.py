"""Build a truthful, source-matched gallery index without starting Blender."""
from pathlib import Path
import hashlib,json,datetime
from gallery_source_revision import resolve
P=Path(__file__).resolve().parent.parent
CLASSES=['1A','CC','3A','2A','SL','2S','GS']
QUEUE=[(k,v) for k in CLASSES for v in ['interior','exterior']]
QUEUE += [('3A','bay'),('CC','chair_detail'),('1A','cabin_entry'),('3A','hvac'),('3A','bogie'),('3A','door'),('3A','toilet')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for k,v in QUEUE:
 record=P/'qa'/f'render_{k}_{v}.json';source=P/'models'/f'LHB_{k}.blend'
 row={'variant':k,'view':v,'status':'pending','current_master_sha256':sha(source)}
 if record.exists():
  r=json.loads(record.read_text());im=P/r['image'];workflow=r.get('sampling_workflow');actual_source,revision=resolve(r)
  valid=(actual_source is not None and im.exists() and r.get('image_sha256')==sha(im) and r.get('samples')==512 and r.get('resolution',[0])[0]>=1400 and r.get('actual_geometry_render') and not r.get('denoising',True))
  if valid and workflow:
   assert workflow['fingerprint']==hashlib.sha256(json.dumps(workflow['spec'],sort_keys=True).encode()).hexdigest(),(k,v,'fingerprint')
   assert workflow['total_uniform_samples']==512 and len(workflow['batches'])==8,(k,v,'samples')
  if valid:row.update(status='complete',source_sha256=r['source_sha256'],source_revision=revision,source_path=str(actual_source.relative_to(P)),image=r['image'],record=str(record.relative_to(P)),image_sha256=r['image_sha256'],resolution=r['resolution'],samples=r['samples'],workflow='uniform512 independent-seed linear EXR average' if workflow else 'adaptive512 maximum',denoising=False)
 rows.append(row)
complete=[r for r in rows if r['status']=='complete']
status={'gallery_status':'complete' if len(complete)==len(QUEUE) else 'in_progress','completed':len(complete),'planned':len(QUEUE),'native_authoring':'Blender .blend, metre-scale class-specific source masters','portable_exchange':'FBX with documented shader/alpha fallback','native_game_runtime':'Not converted or validated in Transport Fever 3','source_geometry':'All seven existing source and FBX checks pass with disclosed editable-font tessellation warnings; verify source report hashes before claiming later edits.','views':rows}
(P/'DELIVERY_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
lines=['# LHB source review gallery','',f"**{len(complete)} of {len(QUEUE)} planned versioned-source final-resolution frames complete.**",'', 'Every linked image is an actual Blender CPU Cycles render of its named source. No image generation or photographic compositing. Uniform checkpointed views average eight independent 64-sample scene-linear EXRs, then apply AgX once. No denoising; some interior grain remains visible.','', 'The sources are editable reference-informed models, not manufacturer CAD or a railway certification. Seated and sleeping markers are authoring references, not validated game passengers. Native Transport Fever 3 conversion, baked game materials, LODs, collision and runtime testing remain outside this package.','', 'The first twenty accepted views retain their exact pre-repair source hashes and are linked to the preserved prior revision. Only the corrected toilet view depicts the latest masters. Later changes are limited to concealed WC seat-ring geometry and paper-holder/tissue mounting; no claim is made that older pixels were rerendered. See [repair evidence](qa/wc_seat_ring_patch.json) and [fixture placement evidence](qa/wc_paper_mount_patch.json).','', '## Seven class interiors and exteriors','']
for k in CLASSES:
 lines.extend(['### '+k,''])
 for r in rows:
  if r['variant']==k and r['view'] in ['interior','exterior']:
   if r['status']=='complete':lines.append(f"- [{r['view'].title()}]({r['image']}) · [source/image/sampling provenance]({r['record']}) · [{r['source_revision']}]({r['source_path']})")
   else:lines.append('- '+r['view'].title()+': pending')
 lines.append('')
lines.extend(['Sleeper corridor frames primarily show layout. The 3A bay view below provides clearer berth-face evidence. 1A is a cabin-facing interior; CC and 2S show their seating arrangement.','', '## Detail views',''])
for r in rows[14:]:
 label=r['variant']+' '+r['view'].replace('_',' ')
 lines.append(f"- [{label}]({r['image']}) · [provenance]({r['record']}) · [{r['source_revision']}]({r['source_path']})" if r['status']=='complete' else '- '+label+': pending')
lines += ['', '## Files and reproducibility','', '- Editable Blender masters, FBX exchange files and matching marker/manifests: [models](models/)', '- Measured source/FBX results: [QA summary](qa/source_geometry/SUMMARY.md)', '- Review history: [iteration log](docs/iteration_log.md)', '- Machine-readable frame status: [delivery status](DELIVERY_STATUS.json)', '- Render-only CC0 environment dependencies use the repository-sibling folder `../wap7_photoreal_v02/environment`; a standalone archive must include these actual files or document the sibling checkout requirement. Absolute scratch symlinks are not portable delivery dependencies.', '- Evidence JSON preserves historical absolute execution paths byte-for-byte to retain valid fingerprints. Those paths describe provenance; they are not required installation destinations.', '', 'Earlier low-sample or stale images may exist in the working tree. Only the versioned-source links above are this gallery.']
(P/'GALLERY.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'complete':len(complete),'planned':len(QUEUE),'status':status['gallery_status']}))
