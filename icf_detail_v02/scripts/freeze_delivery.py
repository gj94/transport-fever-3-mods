"""Freeze a portable intended-delivery manifest after final validation. No uploads."""
from pathlib import Path
import json,hashlib,sys
p=Path(__file__).resolve().parents[1];root=p.parent
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
paths=[]
for f in p.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(p);parts=rel.parts
 if '__pycache__' in parts or '.checkpoints' in parts or 'previews' in parts:continue
 if f.suffix in ['.pyc','.log','.blend1','.blend2']:continue
 if 'renders' in parts and '_final.' not in f.name:continue
 if f.name.endswith('_progress.json') or f.name=='extension_progress.json':continue
 paths.append(f)
paths.append(root/'icf_family_v01/references.md')
for d in json.loads((p/'qa/portable_render_dependencies.json').read_text())['dependencies']:paths.append(root/d['path'])
files=[]
for f in sorted(set(paths)):
 rel=f.relative_to(root).as_posix();b=f.read_bytes();dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 files.append({'path':rel,'local_path':str(dest),'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha':hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest(),'mode':'100644'})
manifest={'scope':'Portable current ICF source, FBX, final gallery and QA; no runtime validation. Excludes transient EXR caches, historical preview PNGs, logs and Blender backup copies.','files':files}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(out/'manifest.json',len(files))
