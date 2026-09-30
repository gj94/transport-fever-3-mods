import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=(Path(__file__).resolve().parents[2]/'cars/VB_DTC.blend');bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update()
opaque=[];glass=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 verts=[o.matrix_world@v.co for v in o.data.vertices];faces=[];gfaces=[]
 for f in o.data.polygons:
  m=o.data.materials[f.material_index] if len(o.data.materials)>f.material_index else None
  bsdf=m.node_tree.nodes.get('Principled BSDF') if m and m.use_nodes else None
  trans=bool(bsdf and bsdf.inputs.get('Transmission Weight') and bsdf.inputs['Transmission Weight'].default_value>.5)
  (gfaces if trans else faces).append(tuple(f.vertices))
 if faces:opaque.append((o.name,BVHTree.FromPolygons(verts,faces,all_triangles=False)))
 if gfaces:glass.append((o.name,BVHTree.FromPolygons(verts,gfaces,all_triangles=False)))
def hits(origin,direction,trees):
 out=[]
 for name,tree in trees:
  point,normal,index,dist=tree.ray_cast(origin,direction,20)
  if point is not None:out.append({'object':name,'distance':dist,'point':list(point)})
 return sorted(out,key=lambda a:a['distance'])
origins={'left_proposed_eye':Vector((6.43,-.73,2.48)),'right_proposed_eye':Vector((6.43,.73,2.48)),'central_review_eye':Vector((6.43,0,2.48))}
report={'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rays':[],'scope':'Opaque forward visibility only; transparent glass excluded from occlusion, reported separately. No TF3 camera/avatar/render-material certification.'}
for name,origin in origins.items():
 for yaw in (-5,0,5):
  for pitch in (0,5,10):
   ya=math.radians(yaw);pi=math.radians(pitch);d=Vector((math.cos(pi)*math.cos(ya),math.cos(pi)*math.sin(ya),math.sin(pi)))
   report['rays'].append({'eye':name,'origin':list(origin),'yaw_deg':yaw,'pitch_deg':pitch,'opaque_hits':hits(origin,d,opaque),'glass_hits':hits(origin,d,glass)})
out=(Path(__file__).resolve().parent/'independent_cab_visibility.json');out.write_text(json.dumps(report,indent=2));print('CAB_RAYS',[(r['eye'],r['yaw_deg'],r['pitch_deg'],[h['object'] for h in r['opaque_hits'][:2]],[h['object'] for h in r['glass_hits'][:2]]) for r in report['rays']])
