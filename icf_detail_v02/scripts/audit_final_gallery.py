"""Non-Blender current-source provenance and final gallery completeness audit."""
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1]
views={'1A':['hero','cabin_diagonal','cabin_cutaway','markings'],'2A':['hero','bay','side_berth'],'3A':['hero','bay','side_berth'],'2S':['hero','aisle'],'CC':['hero','aisle','headrest','toilet'],'SL':['hero','bay','side_berth','bogie','entrance'],'GS':['hero','aisle','coupling']}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
lock=json.loads((p/'qa/final_geometry_lock.json').read_text());rows=[];sources=[]
for v,keys in views.items():
 master=p/v/f'ICF_{v}_master.blend';m=json.loads((p/v/'manifest.json').read_text())
 sources.append({'variant':v,'locked_blend':sha(master)==lock['source_blend_sha256'][v],'locked_fbx':sha(p/v/f'ICF_{v}.fbx')==lock['fbx_sha256'][v],'current_producer_hashes':all(sha(p/'scripts'/n)==h for n,h in m['build_source_sha256'].items())})
 for view in keys:
  f=p/v/'renders'/f'{view}_final.json';im=f.with_suffix('.png');checks={}
  if f.exists() and im.exists():
   d=json.loads(f.read_text());checks={'current_source':d.get('source_blend_sha256')==sha(master),'current_renderer':d.get('renderer_script_sha256')==sha(p/'scripts/render_detail.py'),'image_hash':d.get('image_sha256')==sha(im),'512_samples':d.get('samples')==512,'adaptive_2_percent':d.get('adaptive_threshold')==.02,'minimum_64':d.get('adaptive_min_samples')==64,'no_denoising':d.get('denoising') is False,'four_threads':d.get('render_threads')==4,'width_1600':d.get('resolution',[0])[0]==1600,'presentation_hashes_current':all(sha(p/'scripts'/n)==h for n,h in d.get('presentation_source_sha256',{}).items())}
   if view=='toilet':checks['attached_door_fittings_hidden_with_cutaway']=d.get('cutaway_wrapper_sha256')==sha(p/'scripts/render_toilet_detail.py') and bool(d.get('additional_cutaway_mesh_names'))
   env=d.get('presentation_environment') or {};deps=env.get('external_dependency_sha256',{});checks['external_dependencies_current']=all(sha(p.parent/n)==h for n,h in deps.items())
  rows.append({'variant':v,'view':view,'exists':bool(checks),'checks':checks,'passed':bool(checks) and all(checks.values())})
r={'source_checks':sources,'views':rows,'expected_views':len(rows),'complete_views':sum(x['passed'] for x in rows),'all_sources_unchanged':all(all(v for k,v in s.items() if k!='variant') for s in sources),'passed':all(x['passed'] for x in rows) and all(all(v for k,v in s.items() if k!='variant') for s in sources)}
(p/'qa/final_gallery_audit.json').write_text(json.dumps(r,indent=2));print(json.dumps({'views':r['complete_views'],'expected':r['expected_views'],'sources_unchanged':r['all_sources_unchanged'],'passed':r['passed']}))
