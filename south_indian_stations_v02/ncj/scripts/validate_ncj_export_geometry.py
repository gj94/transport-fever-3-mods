"""Check every exported floating-point accessor and every declared accessor byte range."""
import json,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'exports/NCJ_full_station_v02.glb'
with p.open('rb')as f:
 f.seek(12);n,k=struct.unpack('<II',f.read(8));doc=json.loads(f.read(n));n,k=struct.unpack('<II',f.read(8));start=f.tell();assert k==0x004E4942
sizes={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4};dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT2':4,'MAT3':9,'MAT4':16};float_values=0;float_accessors=0
with p.open('rb')as f:
 for i,a in enumerate(doc.get('accessors',[])):
  if 'bufferView'not in a:continue
  v=doc['bufferViews'][a['bufferView']];element=sizes[a['componentType']]*dims[a['type']];stride=v.get('byteStride',element);bo=a.get('byteOffset',0);count=a['count'];needed=bo+(max(0,count-1)*stride+element if count else 0);assert needed<=v['byteLength'],f'accessor{i} range overrun'
  if a['componentType']!=5126:continue
  float_accessors+=1;f.seek(start+v.get('byteOffset',0)+bo);data=f.read(max(0,count-1)*stride+element)
  if stride==element:
   for (x,)in struct.iter_unpack('<f',data):assert math.isfinite(x),f'accessor{i} nonfinite';float_values+=1
  else:
   fmt='<'+str(dims[a['type']])+'f'
   for j in range(count):
    values=struct.unpack_from(fmt,data,j*stride);assert all(math.isfinite(x)for x in values);float_values+=len(values)
report={'all_accessor_byte_ranges_valid':True,'all_exported_float_values_finite':True,'float_accessors_checked':float_accessors,'float_values_checked':float_values,'position_accessors':len({p['attributes']['POSITION']for m in doc['meshes']for p in m['primitives']if 'POSITION'in p['attributes']})}
(R/'QA_EXPORT_GEOMETRY.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
