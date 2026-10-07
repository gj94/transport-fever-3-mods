"""Triangle-surface intersection sweep of moving pantograph versus stationary roof gear."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1];reports={}
def under(o,ancestor):
 while o:
  if o==ancestor:return True
  o=o.parent
 return False
def bvh(objects):
 verts=[];faces=[];owners=[];dg=bpy.context.evaluated_depsgraph_get()
 for obj in objects:
  ev=obj.evaluated_get(dg);me=ev.to_mesh();off=len(verts);verts.extend(ev.matrix_world@v.co for v in me.vertices)
  for p in me.polygons:faces.append(tuple(off+i for i in p.vertices));owners.append(obj.name)
  ev.to_mesh_clear()
 return BVHTree.FromPolygons(verts,faces,all_triangles=False),owners
for kind in ['TC_CC','TC_EC']:
 bpy.ops.wm.open_mainfile(filepath=str(OUT/'cars'/f'VB_{kind}.blend'));ctrl=bpy.data.objects['PANTO_CTRL'];lo=bpy.data.objects['PANTO_LOWER_PIVOT'];base=bpy.data.objects['PANTO_BASE']
 moving=[o for o in bpy.data.objects if o.type=='MESH' and (under(o,lo) or o.get('flexible_joint',False) or any(m.type=='HOOK' and m.object and under(m.object,lo) for m in o.modifiers))]
 stationary=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(('VB02_ROOF_HVAC','VB02_ROOF_HV_','VB02_ROOF_VCB','VB02_ROOF_roof_control','VB02_ROOF_roof_anti','VB02_VCB_')) or o.name.startswith('Curved_roof_outer'))]
 static,so=bvh(stationary);hits=[]
 for i in range(101):
  ctrl['extension']=i/100;ctrl.update_tag();bpy.context.view_layer.update();mv,mo=bvh(moving);pairs=mv.overlap(static)
  if pairs:hits.append({'extension':i/100,'pairs':sorted(set((mo[a],so[b]) for a,b in pairs))})
 reports[kind]={'source_sha256':hashlib.sha256((OUT/'cars'/f'VB_{kind}.blend').read_bytes()).hexdigest(),'poses':101,'moving_meshes':len(moving),'stationary_meshes':len(stationary),'surface_intersections':hits,'scope':'Moving arm/head triangle surfaces versus roof shell/HVAC/VCB/bus. Joint-to-joint designed contacts and pneumatic mechanism are excluded. No runtime collision certification.'};print('PANTO_CLEARANCE',kind,len(hits),flush=True)
(OUT/'qa/pantograph_clearance.json').write_text(json.dumps(reports,indent=2));assert not any(r['surface_intersections'] for r in reports.values()),'Pantograph roof intersections found'
