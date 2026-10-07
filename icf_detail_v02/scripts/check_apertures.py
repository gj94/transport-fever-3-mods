"""Ray-test structural skin and lining openings, independent of glass/door surfaces."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
folder=Path(bpy.data.filepath).parent;m=json.loads((folder/'manifest.json').read_text());vertices=[];faces=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith(('Pressed bodyside skin','Lined bodyside aperture panel','Pressed window aperture corner infill')):continue
 n=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(n+i for i in p.vertices) for p in o.data.polygons)
tree=BVHTree.FromPolygons(vertices,faces,all_triangles=False)
results=[]
for a in m['window_apertures']:
 if a['y']>0:continue
 for dx,dz in [(0,0),(-a['width']*.3,0),(a['width']*.3,0),(0,a['height']*.3),(0,-a['height']*.3)]:
  x=a['x']+dx;z=a['z']+dz;hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0]
  results.append({'kind':'window','x':x,'z':z,'clear':hit is None})
for x in [-9.12,9.12]:
 for z in [m['dimensions_m']['floor_top']+.10,1.85,2.75,3.18]:
  for dx in [-.30,0,.30]:
   hit=tree.ray_cast(Vector((x+dx,-2,z)),Vector((0,1,0)),4)[0];results.append({'kind':'entrance','x':x+dx,'z':z,'clear':hit is None})
r={'variant':m['variant'],'rays':len(results),'structural_apertures_clear':all(x['clear'] for x in results),'failed':[x for x in results if not x['clear']],'scope':'Structural skin and lining only; actual glazing/door leaves deliberately excluded'}
(folder/'qa'/'aperture_checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
