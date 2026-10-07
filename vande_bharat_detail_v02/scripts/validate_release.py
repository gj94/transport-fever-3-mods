"""Verify final source, QA and real-render provenance after metadata cleanup."""
import hashlib,json
from pathlib import Path
from PIL import Image
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((OUT/p).read_text())
checks={}
for path,h in read('qa/frozen_source_hashes.json')['files'].items():checks[f'frozen_{path}']=sha(OUT/path)==h
sources=read('qa/validation_sources.json')
for kind,r in sources.items():
 checks[f'{kind}_source_hash']=sha(OUT/'cars'/f'VB_{kind}.blend')==r['source_sha256']
 checks[f'{kind}_source_checks']=not r['failures'] and all(r['checks'].values())
for n,seats in [(8,530),(16,1128)]:
 r=read(f'assemblies/VB_{n}_formation.json');checks[f'{n}_formation']=r['formation_cars']==n and r['outer_anchor_span_m']==24*n and r['passenger_seats_prototype_total']==seats
 checks[f'{n}_physical_chairs']=sum(sources[c['type']]['actual_seat_meshes'] for c in r['cars'])==seats
for kind,r in read('qa/pantograph_clearance.json').items():
 checks[f'{kind}_panto_hash']=sha(OUT/'cars'/f'VB_{kind}.blend')==r['source_sha256'];checks[f'{kind}_101_clear_poses']=r['poses']==101 and not r['surface_intersections']
for kind,r in read('qa/roof_end_closure.json').items():
 checks[f'{kind}_endcap_hash']=sha(OUT/'cars'/f'VB_{kind}.blend')==r['source_sha256'];checks[f'{kind}_closed_crown_open_passage']=all(x['upper_crown_ray_closed'] and x['gangway_passage_ray_clear'] for x in r['checks'])
a=read('qa/DTC_accessibility_mesh_clearance.json');checks['accessible_source_hash']=a['source_sha256']==sha(OUT/'cars/VB_DTC.blend');checks['accessible_mesh_clearances']=not a['clearance_hits'] and a['door_clear_opening_between_jambs_m']>1.1 and a['corridor_clear_including_WC_handle_m']>1.15
for kind,r in read('qa/ec_upholstery_refinement.json').items():
 checks[f'{kind}_refined_hash']=r['source_after_sha256']==sha(OUT/'cars'/f'VB_{kind}.blend')
 checks[f'{kind}_refinement_limits']=r['protected_controls_unchanged'] and r['all_seat_envelopes_max_error_m']<1e-6 and r['refinement']['hardware_identical'] and r['passenger_mesh_instances']==52 and r['minimum_adjacent_seat_gap_m']>=0
p=read('qa/portability.json');checks['fresh_directory_portability']=p['fresh_directory_test'] and len(p['files'])==9 and all(not r['missing_dependencies'] and r['sha256']==sha(OUT/r['file']) for r in p['files'])
views='rake8 rake16 formation_length_proof side nose bogie roof pantograph panhead vcb cc ec_front cab cab_controls cab_seats toilet pantry'.split()
for view in views:
 rp=OUT/'qa'/f'render_{view}.json';ip=OUT/'previews'/f'{view}.png';checks[f'{view}_exists']=rp.is_file() and ip.is_file()
 if not checks[f'{view}_exists']:continue
 r=json.loads(rp.read_text());checks[f'{view}_image_hash']=sha(ip)==r.get('image_sha256')
 if r.get('source'):checks[f'{view}_source_hash']=sha(OUT/r['source'])==r['source_sha256']
 for path,h in r.get('library_source_sha256',{}).items():checks[f'{view}_{path}_hash']=sha(OUT/path)==h
 for n,h in r.get('source_formation_reports',{}).items():checks[f'{view}_formation_{n}_hash']=sha(OUT/'assemblies'/f'VB_{n}_formation.json')==h
 with Image.open(ip) as im:im.verify()
checks['no_stale_extra_images']=set(p.stem for p in (OUT/'previews').glob('*.png'))==set(views)
r={'checks':checks,'failures':[k for k,v in checks.items() if not v],'scope':'Exact final source/image provenance, saved geometry QA and portability. Visual quality reviewed separately; no engineering or runtime certification.'};(OUT/'qa/release_validation.json').write_text(json.dumps(r,indent=2));print('RELEASE_CHECKS',len(checks),'FAILURES',r['failures']);assert not r['failures']
