"""Read GLB headers, embedded-resource tables and geometry accessor bounds."""
from pathlib import Path
import json,struct,hashlib,math
R=Path(__file__).resolve().parents[1];O=R/'exchange';results=[]
source_sha=hashlib.sha256((R/'TVC_full_station_v02.blend').read_bytes()).hexdigest()
for row in json.loads((O/'MANIFEST.json').read_text()):
 p=O/row['file'];data=p.read_bytes();magic,version,size=struct.unpack_from('<4sII',data,0);assert magic==b'glTF' and version==2 and size==len(data)
 length,typ=struct.unpack_from('<II',data,12);assert typ==0x4e4f534a;j=json.loads(data[20:20+length]);assert row['source_blend_sha256']==source_sha;assert hashlib.sha256(data).hexdigest()==row['sha256']
 assert all('uri' not in b for b in j.get('buffers',[]))
 assert all('uri' not in im for im in j.get('images',[]))
 vertices=triangles=0
 for m in j.get('meshes',[]):
  for prim in m['primitives']:
   pos=j['accessors'][prim['attributes']['POSITION']];vertices+=pos['count'];assert pos['count']>0
   for v in pos.get('min',[])+pos.get('max',[]):assert math.isfinite(v)
   count=j['accessors'][prim['indices']]['count'] if 'indices' in prim else pos['count']
   if prim.get('mode',4)==4:assert count%3==0;triangles+=count//3
 assert vertices>0 and triangles>0
 results.append({'file':p.name,'bytes':len(data),'nodes':len(j.get('nodes',[])),'meshes':len(j.get('meshes',[])),'vertices_across_primitives':vertices,'triangles':triangles,'images_embedded':len(j.get('images',[])),'external_resources':0,'header_and_bounds':'PASS','sha256':row['sha256']})
report={'source_blend_sha256':source_sha,'parts':len(results),'all_passed':True,'total_triangles':sum(v['triangles'] for v in results),'total_bytes':sum(v['bytes'] for v in results),'coordinate_convention':'All parts share station-local metre coordinates. glTF Y-up export. Import at identity transforms.','material_limit':'Procedural noise/bump shaders may simplify to base colour/roughness. The packed .blend is authoritative.','files':results}
(R/'EXCHANGE_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
