"""Deterministic transport compression; decompression reproduces the exact GLB."""
import gzip,hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent;src=P/'exports/ERS_full_station_v02.glb';dst=src.with_suffix('.glb.gz')
with src.open('rb') as inp,dst.open('wb') as raw:
 with gzip.GzipFile(filename='',mode='wb',fileobj=raw,compresslevel=6,mtime=0) as out:shutil.copyfileobj(inp,out,1024*1024)
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
h=hashlib.sha256()
with gzip.open(dst,'rb') as f:
 for b in iter(lambda:f.read(1048576),b''):h.update(b)
assert h.hexdigest()==digest(src)
q=json.loads((P/'exports/export_manifest.json').read_text());q['compressed_transport']={'path':str(dst.relative_to(P)),'bytes':dst.stat().st_size,'sha256':digest(dst),'decompressed_sha256':h.hexdigest(),'lossless':True};(P/'exports/export_manifest.json').write_text(json.dumps(q,indent=2));print(json.dumps(q['compressed_transport'],indent=2))
