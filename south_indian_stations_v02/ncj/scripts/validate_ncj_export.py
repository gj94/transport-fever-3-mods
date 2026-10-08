"""Validate the complete GLB container, data ranges and compressed delivery without loading Blender."""
import json,struct,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'exports/NCJ_full_station_v02.glb';size=p.stat().st_size
with p.open('rb') as f:
 magic,version,declared=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2 and declared==size
 chunks=[];doc=None;binary=0
 while f.tell()<size:
  length,kind=struct.unpack('<II',f.read(8));chunks.append({'type':kind,'bytes':length});assert f.tell()+length<=size
  if kind==0x4E4F534A:doc=json.loads(f.read(length).decode('utf8'))
  elif kind==0x004E4942:binary=length;f.seek(length,1)
  else:f.seek(length,1)
assert doc and doc['asset']['version']=='2.0'
buffers=doc.get('buffers',[]);assert len(buffers)==1 and 'uri' not in buffers[0] and buffers[0]['byteLength']<=binary
for view in doc.get('bufferViews',[]):assert view.get('buffer',0)==0 and view.get('byteOffset',0)+view['byteLength']<=buffers[0]['byteLength']
for accessor in doc.get('accessors',[]):
 if 'bufferView' in accessor:assert 0<=accessor['bufferView']<len(doc['bufferViews'])
assert not any(n.get('name','').startswith('Review') for n in doc.get('nodes',[])), 'Nonphysical review annotation leaked into export'
z=R/'exports/NCJ_full_station_v02_GLTF.zip'
with zipfile.ZipFile(z)as a:
 assert a.testzip() is None
 assert a.namelist()==[p.name]
 assert a.getinfo(p.name).file_size==size
 def digest_stream(stream):
  h=hashlib.sha256()
  while block:=stream.read(4*1024*1024):h.update(block)
  return h.hexdigest()
 with p.open('rb')as f:rawhash=digest_stream(f)
 with a.open(p.name)as f:assert digest_stream(f)==rawhash
report={'glb_bytes':size,'glb_sha256':rawhash,'zip_bytes':z.stat().st_size,'zip_sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'source_blend_sha256':hashlib.sha256((R/'NCJ_full_station_v02.blend').read_bytes()).hexdigest(),'GLB_version':version,'container_length_matches':True,'buffer_ranges_valid':True,'ZIP_CRC_and_roundtrip_hash_valid':True,'node_count':len(doc.get('nodes',[])),'mesh_count':len(doc.get('meshes',[])),'material_count':len(doc.get('materials',[])),'nonphysical_review_nodes':0,'external_buffer_URIs':0,'chunks':chunks}
(R/'QA_EXPORT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
