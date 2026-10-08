"""Validate binary packaging/portability without modifying the GLB or source scene."""
import json,struct,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;path=P/'exports/ERS_full_station_v02.glb';data=path.read_bytes();magic,version,length=struct.unpack_from('<4sII',data,0);assert magic==b'glTF' and version==2 and length==len(data)
pos=12;chunks=[];doc=None;binbytes=0
while pos<len(data):
 size,kind=struct.unpack_from('<II',data,pos);pos+=8;assert pos+size<=len(data);payload=data[pos:pos+size];pos+=size;chunks.append({'type':kind,'bytes':size})
 if kind==0x4E4F534A:doc=json.loads(payload.decode('utf-8').rstrip(' \x00'))
 if kind==0x004E4942:binbytes+=size
assert doc is not None
external=[item['uri'] for key in ['buffers','images'] for item in doc.get(key,[]) if 'uri' in item and not item['uri'].startswith('data:')];assert not external
for b in doc.get('buffers',[]):assert b['byteLength']<=binbytes
for view in doc.get('bufferViews',[]):assert view.get('byteOffset',0)+view['byteLength']<=doc['buffers'][view['buffer']]['byteLength']
def finite(x):
 if isinstance(x,float):assert math.isfinite(x)
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,list):
  for v in x:finite(v)
finite(doc)
q={'valid_glb_header':True,'version':version,'bytes':length,'chunks':chunks,'nodes':len(doc.get('nodes',[])),'meshes':len(doc.get('meshes',[])),'materials':len(doc.get('materials',[])),'embedded_images':len(doc.get('images',[])),'external_file_dependencies':external,'finite_json_numbers':True,'sha256':hashlib.sha256(data).hexdigest()};(P/'exports/glb_validation.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
