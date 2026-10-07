"""Write final release hashes after all source/render provenance checks pass."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included(p):return p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.blend1','.blend2'} and p.name not in {'SHA256SUMS','FILE_MANIFEST.json','REBUILD_STATUS.txt'}
assert not json.loads((ROOT/'qa/release_validation.json').read_text())['failures']
files=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if included(p)]
(ROOT/'FILE_MANIFEST.json').write_text(json.dumps({'revision':'Vande Bharat 2.0 full-size detailed source v0.2','files':files,'scope':'Editable authoring sources and real Blender previews. Excludes this manifest and SHA256SUMS to avoid circular hashes; TF3 conversion is separate.'},indent=2)+'\n')
paths=[ROOT/x['path'] for x in files]+[ROOT/'FILE_MANIFEST.json'];(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in sorted(paths)));print('MANIFEST',len(files),'files',sum(x['bytes'] for x in files),'bytes')
