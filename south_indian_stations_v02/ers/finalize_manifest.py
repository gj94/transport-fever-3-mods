"""Write delivery hashes only after frozen-scene proofs/export/validation agree."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
scene_hash=sha(P/'ERS_full_station_v02.blend')
lineage=json.loads((P/'scene_lineage.json').read_text());assert lineage['corrected_scene_sha256']==scene_hash
ancestor=lineage['parent_scene_sha256'];inherited={'01_West_architecture','02_Ticket_hall','03_Waiting_hall','05_Track_turnouts','13_Turnout_frog_detail'}
required=[f'{i:02d}' for i in range(1,12)]+['13'];proofs=[]
for prefix in required:
 pp=next((P/'renders').glob(prefix+'_*.proof.json'));q=json.loads(pp.read_text());assert q['source_blend_sha256']==scene_hash or (q['source_blend_sha256']==ancestor and q['image'][:-4] in inherited),(prefix,'unexplained stale scene');assert sha(P/'renders'/q['image'])==q['image_sha256'],(prefix,'changed image');proofs.append(q)
review=json.loads((P/'visual_review.json').read_text());assert review['scene_sha256']==scene_hash
for proof in proofs:assert review['reviews'][proof['image'][:-4]]['status']=='accepted',proof['image']
export=json.loads((P/'exports/export_manifest.json').read_text());assert export['source_blend_sha256']==scene_hash and export['source_file_unchanged'];assert sha(P/export['export'])==export['export_sha256']
glbcheck=json.loads((P/'exports/glb_validation.json').read_text());assert glbcheck['valid_glb_header'] and not glbcheck['external_file_dependencies'];assert glbcheck['sha256']==export['export_sha256']
transport=export['compressed_transport'];assert sha(P/transport['path'])==transport['sha256'] and transport['decompressed_sha256']==export['export_sha256']
validation=json.loads((P/'qa_validation.json').read_text());assert validation['source_blend_sha256']==scene_hash;assert not validation['unpacked_file_images'];assert not validation['obsolete_rail_overlay_objects'];assert validation['all_route_flange_interior_overlap_m2']<1e-8
names=['ERS_full_station_v02.blend','build_ers_full.py','add_details.py','refine_pointwork.py','finish_crossing_castings.py','prepare_rail_solids.py','verify_rail_geometry.py','render_review.py','export_asset.py','validate_asset.py','validate_glb.py','package_export.py','make_signs.py','make_coverage_plan.py','finalize_manifest.py','requirements-preprocess.txt','README.md','SOURCES.md','COVERAGE.md','DIMENSIONS.csv','QA.md','DELIVERABLES.txt','scene_lineage.json','flight_clearance_validation.json','validate_flight_clearance.py','visual_review.json','run_monitored.py','qa_build.json','qa_validation.json','track_network.json','physical_pointwork.json','references/osm_rail.json','references/osm_review.png']
files=[P/n for n in names]
for pattern in ['textures/*.png','geometry/*.json','exports/*.glb','exports/*.glb.gz','exports/export_manifest.json','exports/glb_validation.json','renders/*.png','renders/*.proof.json','renders/12_*.svg']:files+=list(P.glob(pattern))
files=sorted(set(files));records=[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
flight=json.loads((P/'flight_clearance_validation.json').read_text());assert flight['source_blend_sha256']==scene_hash and flight['pass']
manifest={'scene_lineage':{'parent':ancestor,'corrected':scene_hash,'inherited_unaffected_views':sorted(inherited)},'asset':'ERS full station v02','source_blend_sha256':scene_hash,'architectural_baseline':'2017 photographs','yard_basis':'Mixed-date OSM map reconstruction','engineering_certified':False,'rolling_stock':0,'metres_per_unit':1,'gauge_m':1.676,'files':records,'proof_count':len(proofs),'validation':'All 12 render proofs bind to the corrected scene or its explicitly recorded fixture-only parent for unaffected views; affected views and GLB bind to corrected scene. Rail/channel, packed-image and full-flight clearance checks pass.'}
(P/'MANIFEST.json').write_text(json.dumps(manifest,indent=2));records.append({'path':'MANIFEST.json','sha256':sha(P/'MANIFEST.json')});(P/'SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['path']+'\n' for r in records));print(json.dumps({'files':len(records),'source_blend_sha256':scene_hash,'proof_count':len(proofs)},indent=2))
