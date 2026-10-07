"""Write a truthful index containing only completed, current-source final images."""
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1]
views={'1A':['hero','cabin_diagonal','cabin_cutaway','markings'],'2A':['hero','bay','side_berth'],'3A':['hero','bay','side_berth'],'2S':['hero','aisle'],'CC':['hero','aisle','headrest','toilet'],'SL':['hero','bay','side_berth','bogie','entrance'],'GS':['hero','aisle','coupling']}
labels={'hero':'Outdoor exterior','cabin_diagonal':'Private cabin interior','cabin_cutaway':'Cabin inspection cutaway','markings':'Class markings','bay':'Transverse berth bay','side_berth':'Side-berth support inspection','aisle':'Saloon aisle','headrest':'Chair and linen detail','toilet':'Lavatory inspection cutaway','bogie':'Bogie and capacity stencil','entrance':'Entrance detail','coupling':'Uncoupled screw coupling and side buffers'}
rows=[];md=['# ICF detail v02 — actual-model final gallery','', 'Every image below is rendered from its linked current Blender master. These are original 3D assets, not generated illustrations or photographs of a different coach. Source and image SHA-256, renderer/dependency hashes, camera and cutaway scope are in the adjacent JSON sidecar.','', 'Rendering: Blender Cycles CPU, 512 maximum samples, 2% adaptive threshold, minimum 64 samples, no denoising. Hero images are 1600 × 900; interiors and inspection details are 1600 × 1040.','', 'Prototype: representative conventional blue self-generating ICF stock, with screw coupling and side buffers. [Evidence and interpretation](FIDELITY.md). Geometry is authoring quality; native game conversion, animated character fit, WAP7 linkage and runtime performance are unvalidated.','']
complete=0
for v,keys in views.items():
 master=p/v/f'ICF_{v}_master.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest();md += [f'## {v}',f'[Blender master]({v}/ICF_{v}_master.blend) · [FBX]({v}/ICF_{v}.fbx) · [Class manifest]({v}/manifest.json)','']
 for view in keys:
  f=p/v/'renders'/f'{view}_final.json';im=f.with_suffix('.png')
  if not (f.exists() and im.exists()):continue
  d=json.loads(f.read_text())
  if d.get('source_blend_sha256')!=sha or d.get('samples')!=512 or d.get('image_sha256')!=hashlib.sha256(im.read_bytes()).hexdigest():continue
  if view=='toilet' and not d.get('cutaway_wrapper_sha256'):continue
  complete+=1;rel=im.relative_to(p).as_posix();side=f.relative_to(p).as_posix();md += [f'### {labels[view]}',f'[![{v}: {labels[view]}]({rel})]({rel})',f'[Image provenance and exact cutaway disclosure]({side})',''];rows.append({'variant':v,'view':view,'image':rel,'metadata':side,'source_blend_sha256':sha,'image_sha256':d['image_sha256']})
 md.append('')
md.insert(2,f'Completed and verified high-sample views: **{complete}/24**. '+('Full gallery complete.' if complete==24 else 'Gallery production is in progress; missing views are intentionally not linked.'))
(p/'GALLERY.md').write_text('\n'.join(md));(p/'qa/final_gallery_index.json').write_text(json.dumps({'completed_views':complete,'expected_views':24,'images':rows},indent=2));print('GALLERY_INDEX',complete,'of 24')
