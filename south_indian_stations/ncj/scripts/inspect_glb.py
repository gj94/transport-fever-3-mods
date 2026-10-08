import json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];out={}
for f in (R/'exports').glob('*.glb'):
 data=f.read_bytes();magic,version,length=struct.unpack_from('<4sII',data);size,kind=struct.unpack_from('<II',data,12);d=json.loads(data[20:20+size]);tri=0;verts=0
 for m in d.get('meshes',[]):
  for p in m.get('primitives',[]):
   verts+=d['accessors'][p['attributes']['POSITION']]['count']
   if 'indices' in p:tri+=d['accessors'][p['indices']]['count']//3
 names=[n.get('name','') for n in d.get('nodes',[])]
 out[f.name]={'valid_glb2':magic==b'glTF' and version==2 and length==len(data),'nodes':len(names),'meshes':len(d.get('meshes',[])),'vertices':verts,'triangles':tri,'materials':len(d.get('materials',[])),'rooftop_mesh_labels':[n for n in names if n.startswith('Shaped ')],'external_buffers':[b.get('uri') for b in d.get('buffers',[]) if b.get('uri')],'file_size_bytes':len(data)}
(R/'EXPORT_QA.json').write_text(json.dumps(out,indent=2,ensure_ascii=False));print(json.dumps(out,indent=2,ensure_ascii=False))
