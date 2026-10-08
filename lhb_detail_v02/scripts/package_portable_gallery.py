"""Package an immutable curated checkpoint with real sibling dependencies.
Usage: python scripts/package_portable_gallery.py CHECKPOINT_MANIFEST OUTPUT.zip
Verifies every byte read back from ZIP. Does not publish or modify sources.
"""
from pathlib import Path
import sys,json,hashlib,zipfile
manifest=Path(sys.argv[1]);out=Path(sys.argv[2]);assert not out.exists()
m=json.loads(manifest.read_text());P=Path(__file__).resolve().parent.parent
files={f['path']:Path(f['local_path']) for f in m['files']}
for n in ['dirt_diff_2k.jpg','dirt_disp_2k.exr','dirt_rough_2k.jpg','dirt_nor_gl_2k.jpg','kloofendal_48d_partly_cloudy_puresky_2k.hdr','README.md','dependency_manifest.json']:
 files['wap7_photoreal_v02/environment/'+n]=P.parent/'wap7_photoreal_v02/environment'/n
for n in ['environment_depot.py','common.py']:
 files['vande_bharat_detail_v02/components/'+n]=P.parent/'vande_bharat_detail_v02/components'/n
rows=[]
for name,p in sorted(files.items()):
 b=p.read_bytes();rows.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
expected={f['path']:f['sha256'] for f in m['files']}
assert all(r['sha256']==expected.get(r['path'],r['sha256']) for r in rows)
readme='''LHB editable coach sources and versioned review gallery\n\nOpen lhb_detail_v02/README.md and GALLERY.md first. Current seven Blender/FBX masters contain the approved WC repair. Twenty accepted gallery frames retain actual pre-repair source files/hashes in the included revisions directory. Only the corrected toilet final depicts latest masters. The historical toilet is rejected diagnostic evidence.\n\nThis archive is NOT a native Transport Fever 3 mod. Native conversion, game materials, LOD/collision setup and runtime tests are not performed. Editable-text tessellation warnings and representative geometry limitations are disclosed.\n\nKeep the three included sibling folders together. Source masters have no unpacked external images/fonts or linked libraries. Render-only CC0 environment files are physically included; optional hero-view helper modules are also included. Source rebuilding requires Blender 4.3.2 and the explicit ordered post-build repair steps in README. EXR caches and transient logs are excluded; evidence records preserve their original hashes and absolute historical execution paths, which are not installation destinations.\n'''
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,p in sorted(files.items()):z.write(p,name)
 z.writestr('README_ARCHIVE.txt',readme);z.writestr('ARCHIVE_MANIFEST.json',json.dumps({'files':rows,'native_game_runtime':'Not converted or validated'},indent=2))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for r in rows:
  data=z.read(r['path']);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
r={'status':'pass','archive':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'verified_files':len(rows),'crc_checked':True,'all_embedded_source_files_hash_checked':True,'checkpoint_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()}
out.with_suffix('.verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
