"""Preserve frozen exports with additive colour revisions; fix unfrozen exports before first delivery."""
from pathlib import Path
import sys,json,zipfile,hashlib,shutil,subprocess,datetime
from portable_colors import patch
B=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for code in sys.argv[1:]:
 O=B/'portable_colour_revision_02'/code;palette=json.loads((O/'SOURCE_PALETTE.json').read_text());src=Path(palette['source_blend']);R=src.parent;h=sha(src);assert h==palette['source_blend_sha256'];em=json.loads((R/'exchange/MANIFEST.json').read_text());assert em['source_blend_sha256']==h
 frozen=(R/'DELIVERY_MANIFEST.json').exists();oldzip=R/'exchange'/f'{code}_portable_GLTF.zip';oldraw=R/'exchange'/em['file'];oldbytes=oldraw.read_bytes();assert hashlib.sha256(oldbytes).hexdigest()==em['sha256'];fixed,qa=patch(oldbytes,palette['colors']);qa.update(station=code,source_blend_sha256=h,palette_sha256=sha(O/'SOURCE_PALETTE.json'),source_blend_unchanged=True,old_export_manifest_sha256=sha(R/'exchange/MANIFEST.json'))
 if frozen:
  if (O/'DELIVERY_MANIFEST.json').exists():print('ALREADY_FROZEN',code);continue
  assert oldzip.exists();qa['old_archive_sha256']=sha(oldzip);out=O/f'{code}_portable_colour_v02.zip'
  with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:z.writestr(f'{code}_station_colour_v02.glb',fixed)
  with zipfile.ZipFile(out) as z:assert z.testzip() is None and z.read(f'{code}_station_colour_v02.glb')==fixed
  qa.update(new_archive_sha256=sha(out),new_archive_bytes=out.stat().st_size,lossless_roundtrip_verified=True)
  (O/'COLOUR_QA.json').write_text(json.dumps(qa,indent=2));shutil.copyfile(B/'scripts/portable_colors.py',O/'PATCH_SOURCE.py')
  subprocess.run([sys.executable,str(B.parent/'qa/validate_material_revision.py'),str(oldzip),str(out),'--palette',str(O/'SOURCE_PALETTE.json'),'--source-sha256',h,'--out',str(O/'INDEPENDENT_FORMAT_VALIDATION.json')],check=True)
  (O/'README.md').write_text(f'# {code} portable colour correction\n\nUse {out.name} for the portable model. This additive revision restores explicit base RGB colours read from the exact authoritative Blender scene {h}. Geometry, binary mesh buffers, nodes, transforms, texture references, alpha semantics and all other material fields are unchanged. The original source scene and five rendered views remain valid. Procedural noise and bump remain native Blender features and are not baked. Earlier export files remain immutable historical records.\n')
  original=json.loads((R/'DELIVERY_MANIFEST.json').read_text());retained=[x for x in original['allowlist'] if not x['relative_path'].split('/')[-1].endswith('.zip')];rows=[{'path':str(p.resolve()),'relative_path':str(p.relative_to(B.parent)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file() and p.name!='DELIVERY_MANIFEST.json'];manifest={'station':code,'revision_kind':'portable RGB factors only','source_scene_sha256':h,'original_delivery_manifest':str((R/'DELIVERY_MANIFEST.json').resolve()),'original_delivery_manifest_sha256':sha(R/'DELIVERY_MANIFEST.json'),'retained_assets':retained,'allowlist':rows,'total_new_bytes':sum(x['bytes'] for x in rows),'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2));print('COLOUR_ADDENDUM',code,sha(O/'DELIVERY_MANIFEST.json'),len(qa['changed_materials']),flush=True)
 else:
  assert not (R/'DELIVERY_MANIFEST.json').exists()
  if qa['changed_materials']:
   oldcopy=R/'exchange'/f'{code}_precolour_reference.glb';assert not oldcopy.exists();shutil.copyfile(oldraw,oldcopy);shutil.copyfile(R/'exchange/MANIFEST.json',R/'exchange/PRECOLOUR_MANIFEST.json');oldraw.write_bytes(fixed);em['sha256']=sha(oldraw);em['bytes']=oldraw.stat().st_size;em['colour_preservation']='Absent procedural RGB factors restored from exact authoring defaults; geometry buffers unchanged';(R/'exchange/MANIFEST.json').write_text(json.dumps(em,indent=2));subprocess.run([sys.executable,str(B.parent/'qa/validate_material_revision.py'),str(oldcopy),str(oldraw),'--palette',str(O/'SOURCE_PALETTE.json'),'--source-sha256',h,'--out',str(R/'exchange/COLOUR_VALIDATION.json')],check=True)
  (R/'exchange/COLOUR_PRESERVATION.json').write_text(json.dumps(qa,indent=2));shutil.copyfile(O/'SOURCE_PALETTE.json',R/'exchange/SOURCE_PALETTE.json');print('UNFROZEN_COLOUR_READY',code,len(qa['changed_materials']),flush=True)
 assert sha(src)==h
