"""Immutable regional catalogue linking authoritative sources and effective corrected portable exports."""
from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for station in json.loads((B/'stations.json').read_text()):
 c=station['station_code'];R=B/c.lower();rev=B/'revision_02'/c.lower()
 if (rev/f'{c}_station_v01.blend').exists():R=rev
 mp=R/'DELIVERY_MANIFEST.json';m=json.loads(mp.read_text());q=json.loads((R/'QA_BUILD.json').read_text());d=json.loads((R/'source/layout.json').read_text());a=B/'portable_colour_revision_02'/c/'DELIVERY_MANIFEST.json';portable=R/'exchange'/f'{c}_portable_GLTF.zip';export=json.loads((R/'exchange/MANIFEST.json').read_text());entry={'code':c,'name':station['station_name'],'source_blend':str((R/f'{c}_station_v01.blend').relative_to(B.parent)),'source_scene_sha256':m['source_scene_sha256'],'delivery_manifest':str(mp.relative_to(B.parent)),'delivery_manifest_sha256':sha(mp),'gallery':[x['relative_path'] for x in m['allowlist'] if x['relative_path'].endswith('.png')],'platform_bodies':q['model_platform_bodies'],'reported_platform_positions':q['reported_platform_faces'],'nominal_gauge_m':1.676,'units':'metres','source_road_pieces_not_certified_physical_road_count':q['source_road_pieces'],'source_rail_bounds_xy':q['rail_bounds_xy'],'no_trains':q['no_trains'],'source_and_uncertainty_notes':str((R/'SOURCES.json').relative_to(B.parent))}
 if a.exists():
  aq=json.loads((a.parent/'COLOUR_QA.json').read_text());portable=a.parent/f'{c}_portable_colour_v02.zip';entry['colour_revision_manifest']=str(a.relative_to(B.parent));entry['colour_revision_manifest_sha256']=sha(a);entry['effective_glb_sha256']=aq['new_glb_sha256']
 else:entry['effective_glb_sha256']=export['sha256']
 entry['effective_portable_archive']=str(portable.relative_to(B.parent));entry['effective_portable_archive_sha256']=sha(portable);assert len(entry['gallery'])==5;rows.append(entry)
assert len(rows)==19
out=B/'FINAL_CATALOG.json';assert not out.exists(),'Preserve frozen catalogue';out.write_text(json.dumps({'region':'Southern coastal route','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'station_count':19,'gallery_count':95,'quality_gate':'Independent exact-scene, source/pixel and portable-export reports are tracked separately; this catalogue does not assert publication approval.','portable_colour_note':'The effective archive points to the additive colour revision for the thirteen earlier packages, and to the first corrected export for the six later packages. Source scenes and galleries are unchanged by RGB-only export correction.','stations':rows},indent=2));print(out,sha(out))
