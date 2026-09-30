"""Mesh-surface interference check between moving panto and fixed roof equipment."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'WAG9_master.blend'));bpy.context.view_layer.update()
asset=list(bpy.data.collections['WAG9_ASSET'].objects)
def bvh(objects):
 vs=[];fs=[];owners=[]
 for o in objects:
  offset=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles()
  for p in o.data.loop_triangles:fs.append(tuple(offset+i for i in p.vertices));owners.append(o.name)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True,epsilon=0.000001),owners
static=[o for o in asset if o.type=='MESH' and not o.name.startswith('PANTO_') and min((o.matrix_world@v.co).z for v in o.data.vertices)>3.70]
fixed,owners=bvh(static);report={'fixed_roof_meshes':len(static),'tests':[],'collisions':[]}
for i in range(101):
 for side,e in [('FRONT',i/100),('REAR',1-i/100)]:
  c=bpy.data.objects['PANTO_'+side+'_CTRL'];c['extension']=e;c.update_tag()
 bpy.context.view_layer.update()
 for side in ('FRONT','REAR'):
  moving=[o for o in bpy.data.objects['PANTO_'+side+'_LOWER_PIVOT'].children_recursive if o.type=='MESH'];tree,names=bvh(moving);pairs=tree.overlap(fixed);distinct=sorted(set((names[a],owners[b]) for a,b in pairs))
  report['tests'].append({'sample':i,'pantograph':side,'surface_intersections':len(pairs),'object_pairs':distinct})
  if pairs:report['collisions'].append({'sample':i,'pantograph':side,'pairs':distinct})
report['passed']=not report['collisions'];(P/'qa/roof_interference_validation.json').write_text(json.dumps(report,indent=2));print('ROOF_INTERFERENCE',report['passed'],report['collisions'][:8]);assert report['passed']
